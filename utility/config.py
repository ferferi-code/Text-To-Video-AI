import os
from dotenv import load_dotenv
from typing import Optional, Literal, List
from openai import OpenAI

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class ConfigurationError(Exception):
    pass

class Config:
    _instance: Optional['Config'] = None

    def __new__(cls) -> 'Config':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        load_dotenv()
        self._validate_env_file()
        self._validate_configuration()
        self._llm_client = None
        self._initialized = True

    def _validate_env_file(self) -> None:
        env_path = os.path.join(os.getcwd(), '.env')
        if not os.path.exists(env_path):
            raise ConfigurationError(
                ".env file not found. Please create a .env file based on .env.example\n"
                f"Expected location: {env_path}"
            )

    def _validate_configuration(self) -> None:
        errors = []
        llm_provider = os.getenv('LLM_PROVIDER', 'auto').lower()
        valid_providers = ['auto', 'openrouter', 'openai', 'groq', 'gemini', 'local']
        
        if llm_provider not in valid_providers:
            errors.append(
                f"Invalid LLM_PROVIDER: '{llm_provider}'. Must be one of: {', '.join(valid_providers)}"
            )

        has_any_key = bool(
            os.getenv('OPENROUTER_API_KEY') or 
            os.getenv('OPENAI_API_KEY') or 
            os.getenv('GROQ_API_KEY') or 
            os.getenv('GEMINI_API_KEY')
        )
        if not has_any_key:
            errors.append("At least one LLM API key (OPENROUTER, OPENAI, GROQ, or GEMINI) must be provided.")

        if not os.getenv('PEXELS_API_KEY') and not os.getenv('MUAPI_API_KEY'):
            errors.append("Missing required API key: PEXELS_API_KEY or MUAPI_API_KEY must be provided")

        stt_provider = os.getenv('STT_PROVIDER', 'whisper').lower()
        if stt_provider not in ['whisper', 'deepgram']:
            errors.append(f"Invalid STT_PROVIDER: '{stt_provider}'. Must be one of: whisper, deepgram")
        elif stt_provider == 'deepgram' and not os.getenv('DEEPGRAM_API_KEY'):
            errors.append("Missing required API key: DEEPGRAM_API_KEY")

        tts_provider = os.getenv('TTS_PROVIDER', 'edgetts').lower()
        if tts_provider not in ['edgetts', 'elevenlabs', 'local']:
            errors.append(f"Invalid TTS_PROVIDER: '{tts_provider}'. Must be one of: edgetts, elevenlabs, local")
        elif tts_provider == 'edgetts' and not os.getenv('EDGETTS_VOICE'):
            errors.append("Missing required configuration: EDGETTS_VOICE")
        elif tts_provider == 'elevenlabs':
            if not os.getenv('ELEVENLABS_API_KEY'):
                errors.append("Missing required API key: ELEVENLABS_API_KEY")
            if not os.getenv('ELEVENLABS_VOICE_ID'):
                errors.append("Missing required configuration: ELEVENLABS_VOICE_ID")

        if errors:
            error_message = "Configuration validation failed:\n\n" + "\n".join(f"  - {err}" for err in errors)
            raise ConfigurationError(error_message)

    def get_llm_provider(self) -> str:
        return os.getenv('LLM_PROVIDER', 'auto').lower()

    def get_llm_models(self, provider: str) -> List[str]:
        if provider == 'openrouter':
            return [
                os.getenv('OPENROUTER_MODEL', 'openai/gpt-4o'),
                'meta-llama/llama-3.3-70b-instruct',
                'google/gemini-2.0-flash-exp:free',
                'mistralai/mistral-large',
                'qwen/qwen-2.5-72b-instruct',
                'deepseek/deepseek-chat'
            ]
        elif provider == 'openai':
            return [os.getenv('OPENAI_MODEL', 'gpt-4o'), 'gpt-4o-mini', 'gpt-4-turbo']
        elif provider == 'groq':
            return [os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile'), 'llama-3.1-70b-versatile', 'mixtral-8x7b-32768']
        elif provider == 'gemini':
            return [os.getenv('GEMINI_MODEL', 'gemini-1.5-flash'), 'gemini-1.5-pro', 'gemini-1.5-flash-8b']
        elif provider == 'local':
            return ['Qwen/Qwen2.5-1.5B-Instruct']
        raise ConfigurationError(f"Unknown LLM provider: {provider}")

    def get_llm_client(self, provider: str = None):
        if provider is None:
            provider = self.get_llm_provider()
            if provider == 'auto':
                provider = 'openrouter'
            
        if provider == 'openrouter':
            return OpenAI(
                api_key=os.getenv('OPENROUTER_API_KEY'),
                base_url="https://openrouter.ai/api/v1",
                default_headers={"HTTP-Referer": "https://colab.google", "X-Title": "Colab-T2V"}
            )
        elif provider == 'openai':
            return OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        elif provider == 'groq':
            if not GROQ_AVAILABLE:
                raise ConfigurationError("Groq library not installed.")
            return Groq(api_key=os.getenv('GROQ_API_KEY'))
        elif provider == 'gemini':
            if not GEMINI_AVAILABLE:
                raise ConfigurationError("Gemini library not installed.")
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
            return genai
        elif provider == 'local':
            return "local_client"
        raise ConfigurationError(f"Unknown LLM provider: {provider}")

    def get_llm_model(self, provider: str = None) -> str:
        if provider is None:
            provider = self.get_llm_provider()
        models = self.get_llm_models(provider)
        return models[0] if models else 'gpt-4o'

    def get_stt_provider(self) -> str:
        return os.getenv('STT_PROVIDER', 'whisper').lower()

    def get_tts_provider(self) -> str:
        return os.getenv('TTS_PROVIDER', 'edgetts').lower()

    def get_tts_voice(self) -> str:
        provider = self.get_tts_provider()
        if provider == 'edgetts':
            return os.getenv('EDGETTS_VOICE', 'en-US-GuyNeural')
        elif provider == 'elevenlabs':
            return os.getenv('ELEVENLABS_VOICE_ID', '21m00Tcm4TlvDq8ikWAM')
        elif provider == 'local':
            return os.getenv('LOCAL_TTS_VOICE', 'v2/en_speaker_6')
        raise ConfigurationError(f"Unknown TTS provider: {provider}")

    def get_pexels_api_key(self) -> str:
        key = os.getenv('PEXELS_API_KEY')
        if not key:
            raise ConfigurationError("PEXELS_API_KEY not found in .env file")
        return key

    def get_video_orientation(self) -> bool:
        orientation = os.getenv('VIDEO_ORIENTATION', 'portrait').lower()
        if orientation not in ['portrait', 'landscape']:
            raise ConfigurationError(f"Invalid VIDEO_ORIENTATION: '{orientation}'")
        return orientation == 'landscape'

    def get_deepgram_api_key(self) -> str:
        key = os.getenv('DEEPGRAM_API_KEY')
        if not key:
            raise ConfigurationError("DEEPGRAM_API_KEY not found in .env file")
        return key

    def get_elevenlabs_api_key(self) -> str:
        key = os.getenv('ELEVENLABS_API_KEY')
        if not key:
            raise ConfigurationError("ELEVENLABS_API_KEY not found in .env file")
        return key

    def get_captions_enabled(self) -> bool:
        return os.getenv('CAPTIONS_ENABLED', 'true').lower() == 'true'

    def get_caption_font_size(self) -> int:
        return int(os.getenv('CAPTION_FONT_SIZE', '100'))

    def get_caption_font_color(self) -> str:
        return os.getenv('CAPTION_FONT_COLOR', 'yellow').lower()

    def get_caption_stroke_width(self) -> int:
        return int(os.getenv('CAPTION_STROKE_WIDTH', '4'))

    def get_caption_stroke_color(self) -> str:
        return os.getenv('CAPTION_STROKE_COLOR', 'black').lower()

    def get_caption_position(self) -> str:
        position = os.getenv('CAPTION_POSITION', 'bottom_center').lower()
        valid_positions = ['center', 'top', 'bottom', 'bottom_center', 'bottom_left', 'bottom_right']
        if position not in valid_positions:
            raise ConfigurationError(f"Invalid CAPTION_POSITION: '{position}'")
        return position

    def get_caption_font_face(self) -> str:
        return os.getenv('CAPTION_FONT_FACE', 'Arial-Bold')

    def get_caption_style(self) -> str:
        style = os.getenv('CAPTION_STYLE', 'hormozi').lower()
        valid_styles = ['hormozi', 'card', 'neon', 'minimal', 'karaoke', 'comic']
        if style not in valid_styles:
            return 'hormozi'
        return style

def get_config() -> Config:
    try:
        return Config()
    except ConfigurationError as e:
        print(f"\n{'='*70}\nERROR: Configuration Failed\n{'='*70}\n{str(e)}\nPlease fix these issues and try again.\n{'='*70}\n")
        raise
