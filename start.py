import os
import sys
import subprocess

def main():
    print("=" * 60)
    print(" 🎬 Free AI Video Studio - Quick Start")
    print("=" * 60)
    print("1. Enter topic manually")
    print("2. Auto-generate using Local AI (Viral 2026 Standards)")
    print("=" * 60)
    
    choice = input("\nChoose (1 or 2): ").strip()
    
    if choice == '1':
        topic = input("📝 Enter your topic: ").strip()
        if not topic:
            topic = "5 amazing facts about space exploration"
    elif choice == '2':
        print("\n🔍 Fetching global trends and generating viral title via Local LLM...")
        from utility.trend.viral_title_generator import get_raw_trend, generate_viral_title_with_local_llm
        
        raw_topic = get_raw_trend()
        print(f"📌 Raw Trend Selected: '{raw_topic}'")
        print("🧠 Local AI is crafting the perfect viral title (this takes ~2-5 seconds)...")
        
        topic = generate_viral_title_with_local_llm(raw_topic)
        print(f"🚀 AI-Generated Viral Title: '{topic}'\n")
    else:
        print("❌ Invalid choice. Defaulting to manual mode.")
        topic = input("📝 Enter your topic: ").strip() or "5 amazing facts about space exploration"

    print("=" * 60)
    print(f"🎬 Starting video generation pipeline for: '{topic}'")
    print("=" * 60)
    
    try:
        subprocess.run([sys.executable, "app.py", topic], check=True)
        print("\n✅ Pipeline execution finished successfully!")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ An error occurred during video generation. Exit code: {e.returncode}")
    except KeyboardInterrupt:
        print("\n\n⚠️ Process interrupted by user.")

if __name__ == "__main__":
    main()
