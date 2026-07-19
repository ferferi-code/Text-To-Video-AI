import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

_model = None
_tokenizer = None
# Using 1.5B parameter model. It is small (<1.5GB) but much better at JSON formatting than 0.5B.
MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"

def load_local_model():
    global _model, _tokenizer
    if _model is None or _tokenizer is None:
        print("[LocalLLM] Loading local fallback model (downloading weights on first run)...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[LocalLLM] Using device: {device}")
        
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        _model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            device_map="auto" if device == "cuda" else None
        )
        if device == "cpu":
            _model = _model.to(device)
        print("[LocalLLM] Local model loaded successfully and cached in memory.")

def generate_local_response(system_prompt, user_prompt):
    load_local_model()
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    text = _tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    
    model_inputs = _tokenizer([text], return_tensors="pt").to(_model.device)
    
    generated_ids = _model.generate(
        **model_inputs,
        max_new_tokens=512,
        temperature=0.7,
        top_p=0.9,
        do_sample=True
    )
    
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]
    
    return _tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
