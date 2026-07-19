import os
import torch
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write

# Global model instance to prevent reloading
_model = None

def get_music_model():
    global _model
    if _model is None:
        print("[LocalMusic] Loading MusicGen model (downloading ~1GB on first run)...")
        # Using 'melody' or 'medium' model. 'small' is faster but lower quality.
        _model = MusicGen.get_pretrained('small')
        _model.set_generation_params(duration=45) # Generate 45 seconds
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _model = _model.to(device)
        print(f"[LocalMusic] Model loaded on {device}.")
    return _model

def generate_local_music(topic: str, orientation_landscape: bool, output_path: str = "local_bg_music.wav"):
    """
    Generates 2026-standard background music based on the topic and video type.
    """
    model = get_music_model()
    
    # 2026 Trending Prompts based on video orientation and topic
    if orientation_landscape:
        # Cinematic, Epic, Documentary style for long-form
        prompt = f"cinematic ambient orchestral, hans zimmer style, epic swell, documentary background music, no vocals, {topic}"
    else:
        # Lo-fi, Synthwave, Phonk for Shorts/Reels
        prompt = f"lo-fi hip hop beat, chill synthwave, minimal, 90 bpm, youtube shorts background music, no vocals, {topic}"
        
    print(f"[LocalMusic] Generating music with prompt: '{prompt}'")
    
    descriptions = [prompt]
    wav = model.generate(descriptions)
    
    # Save the generated audio
    for idx, one_wav in enumerate(wav):
        audio_write(
            dst_folder=os.path.dirname(output_path) or '.',
            base_name=os.path.splitext(os.path.basename(output_path))[0],
            strategy='clip',
            sample_rate=model.sample_rate,
            audio=one_wav.cpu(),
        )
        
    # The library saves as .wav by default, ensure it matches our expected path
    base_name = os.path.splitext(os.path.basename(output_path))[0]
    generated_file = f"{base_name}.wav"
    if os.path.exists(generated_file) and generated_file != output_path:
        os.replace(generated_file, output_path)
        
    print(f"[LocalMusic] Music saved to {output_path}")
    return output_path
