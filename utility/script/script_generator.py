import json
import re
from utility.config import get_config, ConfigurationError

def clean_markdown(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'_(.*?)_', r'\1', text)
    text = re.sub(r'`(.*?)`', r'\1', text)
    text = re.sub(r'`.*?`', '', text, flags=re.DOTALL)
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def generate_script(topic):
    config = get_config()
    user_provider = config.get_llm_provider()
    
    if user_provider == 'auto':
        # Local is the ultimate fallback
        providers_to_try = ['openrouter', 'gemini', 'groq', 'openai', 'local']
    else:
        all_providers = ['openrouter', 'gemini', 'groq', 'openai', 'local']
        providers_to_try = [user_provider] + [p for p in all_providers if p != user_provider]

    last_error = None

    for provider in providers_to_try:
        try:
            client = config.get_llm_client(provider=provider)
            models_to_try = config.get_llm_models(provider=provider)
            
            print(f"\n🔄 Attempting to generate script using Provider: {provider.upper()}")
            print(f"📋 Available models to try: {', '.join(models_to_try[:3])}...")

            for model in models_to_try:
                try:
                    print(f"   Trying model: {model} ...")
                    
                    prompt = (
                        """You are a seasoned content writer for a YouTube Shorts channel, specializing in facts videos. 
                        Your facts shorts are concise, each lasting less than 50 seconds (approximately 140 words). 
                        They are incredibly engaging and original. When a user requests a specific type of facts short, you will create it.
                        For instance, if the user asks for: Weird facts
                        You would produce content like this:
                        Weird facts you don't know:
                        - Bananas are berries, but strawberries aren't.
                        - A single cloud can weigh over a million pounds.
                        - There's a species of jellyfish that is biologically immortal.
                        - Honey never spoils; archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still edible.
                        - The shortest war in history was between Britain and Zanzibar on August 27, 1896. Zanzibar surrendered after 38 minutes.
                        - Octopuses have three hearts and blue blood.
                        You are now tasked with creating the best short script based on the user's requested type of 'facts'.
                        Keep it brief, highly interesting, and unique.
                        Strictly output the script in a JSON format like below, and only provide a parsable JSON object with the key 'script'.
                        # Output
                        {"script": "Here is the script ..."}
                        """
                    )

                    if provider == 'gemini':
                        content = _call_gemini(client, model, topic, prompt)
                    elif provider == 'local':
                        from utility.llm.local_llm_client import generate_local_response
                        content = generate_local_response(prompt, topic)
                    else:
                        content = _call_openai_compatible(client, model, topic, prompt)

                    text = content
                    for prefix in ['content:', 'content =', 'content: ', 'content=']:
                        if text.startswith(prefix):
                            text = text[len(prefix):].strip()
                            break

                    json_start = text.find('{')
                    json_end = text.rfind('}')
                    if json_start == -1 or json_end == -1:
                        raise ValueError("No valid JSON found in response")

                    script_text = text[json_start:json_end+1]
                    script = json.loads(script_text)["script"]
                    script = clean_markdown(script)
                    
                    print(f"  ✅ SUCCESS! Script generated using {provider.upper()} with model: {model}\n")
                    return script

                except Exception as e:
                    print(f"  ⚠️ Model '{model}' failed. Error: {str(e)[:100]}...")
                    print("  ➡️ Trying next model in the list...\n")
                    last_error = e
                    continue
            
            print(f"❌ All models for {provider.upper()} failed. Moving to next provider...\n")

        except ConfigurationError as e:
            print(f"⚠️ Skipping {provider.upper()} due to configuration error: {e}\n")
            last_error = e
            continue
        except Exception as e:
            print(f"⚠️ Unexpected error with {provider.upper()}: {e}\n")
            last_error = e
            continue

    print("❌ CRITICAL: All LLM providers and their models have failed.")
    raise last_error

def _call_openai_compatible(client, model, topic, prompt):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": topic}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

def _call_gemini(client, model_name, topic, prompt):
    model = client.GenerativeModel(model_name)
    response = model.generate_content(
        contents=[{"role": "user", "parts": [{"text": f"{prompt}\n\nTopic: {topic}"}]}],
        generation_config={
            "temperature": 0.7,
            "top_p": 0.8,
            "max_output_tokens": 8192,
        }
    )
    text = response.text
    if text.startswith('```json'):
        text = text[7:]
    if text.startswith('```'):
        text = text[3:]
    if text.endswith('```'):
        text = text[:-3]
    return text.strip()
