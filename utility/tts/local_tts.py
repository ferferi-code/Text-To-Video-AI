import os
from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io.wavfile import write as write_wav
from utility.tts.emotion_analyzer import add_emotion_tags

def generate_audio(script, output_path, voice_preset="v2/en_speaker_6"):
    print("[LocalTTS] Preloading Bark models (first time may take 1-2 minutes)...")
    preload_models()
    
    print("[LocalTTS] Analyzing emotions and injecting tone tags...")
    script_with_emotions = add_emotion_tags(script)
    print(f"[LocalTTS] Processed script preview: {script_with_emotions[:150]}...")
    
    print("[LocalTTS] Generating expressive audio...")
    audio_array = generate_audio(
        script_with_emotions, 
        history_prompt=voice_preset,
        temp=0.7
    )
    
    write_wav(output_path, SAMPLE_RATE, audio_array)
    print(f"[LocalTTS] Audio saved to {output_path}")
    return output_path
