import time
import os
import tempfile
import zipfile
import platform
import subprocess
from moviepy.editor import (AudioFileClip, CompositeVideoClip, CompositeAudioClip, ImageClip,
TextClip, VideoFileClip)
from moviepy.audio.fx.audio_loop import audio_loop
from moviepy.audio.fx.audio_normalize import audio_normalize
import requests
from utility.config import get_config

def download_file(url, filename):
    with open(filename, 'wb') as f:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        f.write(response.content)

def search_program(program_name):
    try:
        search_cmd = "where" if platform.system() == "Windows" else "which"
        return subprocess.check_output([search_cmd, program_name]).decode().strip()
    except subprocess.CalledProcessError:
        return None

def get_program_path(program_name):
    program_path = search_program(program_name)
    return program_path

def get_output_media(audio_file_path, timed_captions, background_video_data, video_server, background_music_path=None):
    config = get_config()
    
    render_engine = os.getenv('RENDER_ENGINE', 'moviepy').lower()
    if render_engine == 'remotion':
        print("[RenderEngine] Routing compilation to React/Remotion renderer...")
        from utility.render.remotion_renderer import render_with_remotion
        return render_with_remotion(
            audio_file_path=audio_file_path,
            timed_captions=timed_captions,
            background_video_data=background_video_data,
            background_music_path=background_music_path
        )

    OUTPUT_FILE_NAME = "rendered_video.mp4"
    magick_path = get_program_path("magick")
    if magick_path:
        os.environ['IMAGEMAGICK_BINARY'] = magick_path
    else:
        os.environ['IMAGEMAGICK_BINARY'] = '/usr/bin/convert'

    visual_clips = []
    for (t1, t2), video_url in background_video_data:
        video_filename = tempfile.NamedTemporaryFile(delete=False).name
        download_file(video_url, video_filename)
        video_clip = VideoFileClip(video_filename)
        video_clip = video_clip.set_start(t1)
        video_clip = video_clip.set_end(t2)
        visual_clips.append(video_clip)

    audio_clips = []
    audio_file_clip = AudioFileClip(audio_file_path)
    audio_clips.append(audio_file_clip)

    if background_music_path and os.path.exists(background_music_path):
        try:
            bg_music_clip = AudioFileClip(background_music_path)
            bg_music_clip = bg_music_clip.volumex(0.12)
            if bg_music_clip.duration < audio_file_clip.duration:
                bg_music_clip = audio_loop(bg_music_clip, duration=audio_file_clip.duration)
            else:
                bg_music_clip = bg_music_clip.set_duration(audio_file_clip.duration)
            audio_clips.append(bg_music_clip)
            print("[RenderEngine] Successfully loaded and mixed background music.")
        except Exception as e:
            print(f"[RenderEngine] Error loading/mixing background music: {e}")

    if config.get_captions_enabled():
        from utility.captions.caption_styler import get_caption_clips
        for (t1, t2), text in timed_captions:
            new_clips = get_caption_clips(text, t1, t2, config)
            visual_clips.extend(new_clips)

    video = CompositeVideoClip(visual_clips)
    if audio_clips:
        audio = CompositeAudioClip(audio_clips)
        video.duration = audio.duration
        video.audio = audio

    video.write_videofile(OUTPUT_FILE_NAME, codec='libx264', audio_codec='aac', fps=25, preset='veryfast')

    for (t1, t2), video_url in background_video_data:
        video_filename = tempfile.NamedTemporaryFile(delete=False).name
        if os.path.exists(video_filename):
            os.remove(video_filename)

    return OUTPUT_FILE_NAME
