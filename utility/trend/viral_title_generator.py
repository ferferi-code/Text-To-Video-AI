import random
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Global variables to load model only once
_model = None
_tokenizer = None

def get_raw_trend():
    """Fetches a raw trending topic from global markets."""
    try:
        from pytrends.request import TrendReq
        regions = ['united_states', 'united_kingdom', 'canada', 'australia', 'india']
        pytrends = TrendReq(hl='en-US', tz=360)
        trends = pytrends.trending_searches(pn=random.choice(regions)).head(15)[0].tolist()
        return random.choice(trends).title()
    except Exception:
        return "Artificial Intelligence advancements"

def _load_local_model():
    """Loads the local LLM automatically. Downloads weights on first run."""
    global _model, _tokenizer
    if _model is None or _tokenizer is None:
        print("[LocalLLM] Loading viral title generator model (downloading on first run)...")
        model_id = "Qwen/Qwen2.5-0.5B-Instruct"
        
        # Determine device (GPU if available, else CPU)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[LocalLLM] Using device: {device}")
        
        _tokenizer = AutoTokenizer.from_pretrained(model_id)
        _model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            device_map="auto" if device == "cuda" else None
        )
        if device == "cpu":
            _model = _model.to(device)
        print("[LocalLLM] Model loaded successfully.")

def generate_viral_title_with_local_llm(raw_topic: str) -> str:
    """
    Uses a local LLM to generate a highly clickable, 2026-standard viral video title.
    Fully automated: downloads model weights automatically on first execution.
    """
    try:
        _load_local_model()
        
        system_prompt = (
            "You are an expert YouTube and TikTok viral content strategist in 2026. "
            "Generate ONE highly clickable, viral video title based on the user's topic. "
            "GOLDEN RULES: 1. Curiosity Gap. 2. Specificity (use numbers). 3. Emotional trigger. "
            "4. Brevity (under 60 characters). 5. No misleading clickbait. "
            "OUTPUT FORMAT: Return ONLY the title. No quotes, no explanations."
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate a viral video title about: {raw_topic}"}
        ]
        
        text = _tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        model_inputs = _tokenizer([text], return_tensors="pt").to(_model.device)
        
        generated_ids = _model.generate(
            **model_inputs,
            max_new_tokens=30,
            temperature=0.8,
            top_p=0.9,
            do_sample=True
        )
        
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        
        title = _tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0].strip().strip('"').strip("'")
        
        # Validation
        if len(title) < 10 or len(title) > 80:
            raise ValueError("Generated title length is out of bounds.")
            
        return title

    except Exception as e:
        print(f"⚠️ Local LLM generation failed ({e}). Falling back to rule-based generator.")
        return _fallback_viral_title(raw_topic)

def _fallback_viral_title(raw_topic: str) -> str:
    """Fallback in case local LLM fails."""
    templates = [
        f"The SHOCKING Truth About {raw_topic} Nobody Talks About",
        f"7 Mind-Blowing Facts About {raw_topic} You Won't Believe",
        f"Why Everyone Is Suddenly Obsessed With {raw_topic}",
        f"The Dark Side of {raw_topic} Exposed",
        f"I Tried {raw_topic} for 24 Hours and This Happened"
    ]
    return random.choice(templates)
