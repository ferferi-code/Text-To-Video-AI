import os
import asyncio
import argparse
import requests
import imageio_ffmpeg

# Automatically register imageio-ffmpeg binary
ffmpeg_exe_src = imageio_ffmpeg.get_ffmpeg_exe()
bin_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin")
os.makedirs(bin_dir, exist_ok=True)
ffmpeg_exe_dest = os.path.join(bin_dir, "ffmpeg.exe")
if not os.path.exists(ffmpeg_exe_dest):
    print(f"[Pipeline] Copying bundled ffmpeg to local bin: {ffmpeg_exe_src} -> {ffmpeg_exe_dest}")
    import shutil
    shutil.copy2(ffmpeg_exe_src, ffmpeg_exe_dest)
if bin_dir not in os.environ["PATH"]:
    os.environ["PATH"] = bin_dir + os.pathsep + os.environ["PATH"]

from utility.script.script_generator import generate_script
from utility.audio.audio_generator import generate_audio
from utility.captions.timed_captions_generator import generate_timed_captions
from utility.video.background_video_generator import generate_video_url
from utility.render.render_engine import get_output_media
from utility.video.video_search_query_generator import getVideoSearchQueriesTimed, merge_empty_intervals
from utility.config import get_config
from utility.pipeline_manager import PipelineManager
from utility.muapi_client import MuapiClient

def download_file(url, filename):
    print(f"[Pipeline] Downloading: {url} -> {filename}")
    with open(filename, 'wb') as f:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        f.write(response.content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a video from a topic.")
    parser.add_argument("topic", type=str, help="The topic for the video")
    args = parser.parse_args()
    
    config = get_config()
    orientation_landscape = config.get_video_orientation()
    aspect_ratio = "16:9" if orientation_landscape else "9:16"
    
    manager = PipelineManager(args.topic)
    topic = manager.get_data("topic")
    
    muapi_api_key = os.getenv("MUAPI_API_KEY")
    use_muapi = bool(muapi_api_key)
    
    # 1. Generate Script
    if manager.get_stage() == "1_script":
        print("\n--- STAGE 1: Generating Script ---")
        script = generate_script(topic)
        print(f"Generated Script: {script}")
        manager.update_data("script", script)
        manager.set_stage("2_voiceover")

    # 2. Generate Voiceover
    if manager.get_stage() == "2_voiceover":
        print("\n--- STAGE 2: Generating Voiceover ---")
        script = manager.get_data("script")
        voiceover_filename = "audio_tts.wav"
        asyncio.run(generate_audio(script, voiceover_filename))
        print(f"Generated voiceover saved to: {voiceover_filename}")
        manager.update_data("voiceover_path", voiceover_filename)
        manager.set_stage("3_timed_captions")

    # 3. Generate Timed Captions
    if manager.get_stage() == "3_timed_captions":
        print("\n--- STAGE 3: Generating Timed Captions ---")
        voiceover_filename = manager.get_data("voiceover_path")
        timed_captions = generate_timed_captions(voiceover_filename)
        print(f"Generated timed captions: {timed_captions}")
        manager.update_data("timed_captions", timed_captions)
        manager.set_stage("4_background_music")

    # 4. Generate Background Music (Muapi OR Local MusicGen)
    if manager.get_stage() == "4_background_music":
        print("\n--- STAGE 4: Generating Background Music ---")
        music_path = "background_music.wav"
        
        if use_muapi:
            try:
                client = MuapiClient()
                music_style = "instrumental upbeat corporate synth background music" if orientation_landscape else "instrumental emotional cinematic background music"
                request_id = client.trigger_suno_music(prompt=topic, style=music_style)
                urls = client.poll_prediction(request_id)
                music_url = urls[0]
                download_file(music_url, music_path)
                print(f"Muapi Suno music generated and saved to: {music_path}")
            except Exception as e:
                print(f"⚠️ Error generating music via Muapi: {e}. Falling back to Local MusicGen.")
                use_muapi = False # Force fallback
                
        if not use_muapi:
            print("Using Local AI (MusicGen) for 2026-standard background music...")
            from utility.music.local_music_generator import generate_local_music
            generate_local_music(topic, orientation_landscape, output_path=music_path)
            
        manager.update_data("background_music_path", music_path)
        manager.set_stage("4.5_audio_ducking")

    # 4.5. Apply Audio Ducking (Crucial for 2026 standards)
    if manager.get_stage() == "4.5_audio_ducking":
        print("\n--- STAGE 4.5: Applying Audio Ducking ---")
        voiceover_path = manager.get_data("voiceover_path")
        music_path = manager.get_data("background_music_path")
        
        if music_path and os.path.exists(music_path):
            from utility.audio.audio_ducker import apply_audio_ducking
            mixed_audio_path = "mixed_final_audio.wav"
            apply_audio_ducking(voiceover_path, music_path, output_path=mixed_audio_path)
            manager.update_data("voiceover_path", mixed_audio_path) # Replace voiceover with mixed audio for renderer
            print("Audio ducking applied successfully.")
        else:
            print("No background music found. Skipping ducking.")
            
        manager.set_stage("5_ai_video_broll")

    # 5. Generate Timed B-roll Videos
    if manager.get_stage() == "5_ai_video_broll":
        print("\n--- STAGE 5: Sourcing Timed B-Roll Videos ---")
        script = manager.get_data("script")
        timed_captions = manager.get_data("timed_captions")
        search_terms = getVideoSearchQueriesTimed(script, timed_captions)
        background_video_urls = manager.get_data("background_video_urls") or []
        
        model_name = os.getenv("MUAPI_VIDEO_MODEL", "veo3-fast-text-to-video")
        
        if use_muapi:
            client = MuapiClient()
            print(f"Generating B-Roll clips using Muapi model '{model_name}'...")
            start_index = len(background_video_urls)
            for i, ((t1, t2), queries) in enumerate(search_terms):
                if i < start_index: continue
                prompt = queries[0] if queries else topic
                print(f"\nGenerating Clip {i+1}/{len(search_terms)}...")
                try:
                    request_id = client.trigger_video_generation(model_name, prompt, aspect_ratio=aspect_ratio)
                    urls = client.poll_prediction(request_id)
                    background_video_urls.append([[t1, t2], urls[0]])
                    manager.update_data("background_video_urls", background_video_urls)
                except Exception as e:
                    print(f"⚠️ Muapi failed. Falling back to Pexels.")
                    fallback_urls = generate_video_url([[[t1, t2], queries]], "pexel", orientation_landscape=orientation_landscape)
                    if fallback_urls and fallback_urls[0][1]:
                        background_video_urls.append(fallback_urls[0])
                        manager.update_data("background_video_urls", background_video_urls)
        else:
            print("Using stock Pexels API for B-roll...")
            background_video_urls = generate_video_url(search_terms, "pexel", orientation_landscape=orientation_landscape)
            manager.update_data("background_video_urls", background_video_urls)
            
        manager.set_stage("6_render")

    # 6. Render final composite video
    if manager.get_stage() == "6_render":
        print("\n--- STAGE 6: Rendering Final Video ---")
        voiceover_path = manager.get_data("voiceover_path") # This is now the mixed/ducked audio
        timed_captions = manager.get_data("timed_captions")
        background_video_urls = manager.get_data("background_video_urls")
        
        background_video_urls = merge_empty_intervals(background_video_urls)
        
        if background_video_urls:
            print("Compiling media files...")
            video_output = get_output_media(
                audio_file_path=voiceover_path,
                timed_captions=timed_captions,
                background_video_data=background_video_urls,
                video_server="pexel",
                background_music_path=None # Music is already mixed in voiceover_path
            )
            print(f"\nSUCCESS! Final video saved as '{video_output}'")
            manager.update_data("video_path", video_output)
            manager.set_stage("completed")
        else:
            print("Error: No background video clips found. Cannot render.")

    if manager.get_stage() == "completed":
        print("\nPipeline execution complete! Resetting checkpoint...")
        if os.path.exists("pipeline_checkpoint.json"):
            try:
                os.remove("pipeline_checkpoint.json")
            except Exception as e:
                print(f"Error cleaning up checkpoint: {e}")
