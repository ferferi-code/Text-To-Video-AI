import os
import subprocess
import shutil

def apply_audio_ducking(voiceover_path: str, music_path: str, output_path: str = "mixed_audio.wav"):
    """
    Applies professional sidechain compression (Audio Ducking) using FFmpeg.
    Lowers music volume when voice is present, raises it when silent.
    """
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        print("[AudioDucker] FFmpeg not found. Falling back to simple volume reduction.")
        return _simple_mix(voiceover_path, music_path, output_path)

    print("[AudioDucker] Applying professional sidechain ducking...")
    
    # FFmpeg sidechaincompress filter
    # [0:a] = Music, [1:a] = Voice
    # sidechaincompress: threshold=0.003 (very sensitive), ratio=20 (strong ducking)
    cmd = [
        ffmpeg_path, "-y",
        "-i", music_path,
        "-i", voiceover_path,
        "-filter_complex", 
        "[0:a][1:a]sidechaincompress=threshold=0.003:ratio=20:attack=0.05:release=0.5[ducked];"
        "[ducked]volume=0.4[bg];" # Lower overall background volume to 40%
        "[1:a][bg]amix=duration=first:dropout_transition=2",
        "-c:a", "pcm_s16le", # High quality WAV
        output_path
    ]
    
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[AudioDucker] Successfully ducked and mixed audio to {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"[AudioDucker] FFmpeg ducking failed: {e}. Falling back to simple mix.")
        return _simple_mix(voiceover_path, music_path, output_path)

def _simple_mix(voiceover_path: str, music_path: str, output_path: str):
    """Fallback simple mix if FFmpeg filter fails."""
    from moviepy.editor import AudioFileClip, CompositeAudioClip
    from moviepy.audio.fx.audio_loop import audio_loop
    
    voice = AudioFileClip(voiceover_path)
    music = AudioFileClip(music_path)
    
    if music.duration < voice.duration:
        music = audio_loop(music, duration=voice.duration)
    else:
        music = music.set_duration(voice.duration)
        
    music = music.volumex(0.15) # Simple 15% volume
    final = CompositeAudioClip([voice, music])
    final.write_audiofile(output_path, fps=44100, nbytes=2, codec='pcm_s16le')
    return output_path
