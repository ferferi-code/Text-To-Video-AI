import os
import asyncio
from utility.config import get_config

async def generate_audio(script, output_filename):
    config = get_config()
    tts_provider = config.get_tts_provider()
    
    if tts_provider == 'edgetts':
        from utility.tts.edgetts_tts import generate_audio as edgetts_audio
        voice = config.get_tts_voice()
        await edgetts_audio(script, output_filename, voice)
        
    elif tts_provider == 'elevenlabs':
        from utility.tts.elevenlabs_tts import generate_audio as elevenlabs_audio
        voice_id = config.get_tts_voice()
        elevenlabs_audio(script, output_filename, voice_id)
        
    elif tts_provider == 'local':
        from utility.tts.local_tts import generate_audio as local_audio
        voice_preset = os.getenv('LOCAL_TTS_VOICE', 'v2/en_speaker_6')
        local_audio(script, output_filename, voice_preset)
        
    else:
        raise ValueError(f"Unknown TTS provider: {tts_provider}")
