import os, sys, subprocess, random

def get_viral_topic():
    print("\n🔍 Scanning global viral trends (US, UK, CA, AU, IN)...")
    try:
        from pytrends.request import TrendReq
        # Randomly pick a major global market for diverse topics
        regions = ['united_states', 'united_kingdom', 'canada', 'australia', 'india']
        pytrends = TrendReq(hl='en-US', tz=360)
        trends = pytrends.trending_searches(pn=random.choice(regions)).head(15)[0].tolist()
        
        # 20 Research-Backed Viral Title Templates
        templates = [
            "The SHOCKING Truth About {topic} That Nobody Talks About",
            "10 Mind-Blowing Facts About {topic} You Won't Believe",
            "Why Everyone Is Suddenly Talking About {topic}",
            "The Dark Side of {topic} Exposed",
            "I Tried {topic} for 24 Hours and This Happened...",
            "Stop Ignoring {topic} (Here’s Exactly Why)",
            "The Untold Story of {topic} That Will Change Your Perspective",
            "7 Secrets About {topic} Experts Don't Want You to Know",
            "Is {topic} Actually a Scam? The Truth Revealed",
            "How {topic} Is Quietly Taking Over the World",
            "What Nobody Tells You About {topic}",
            "The Future of {topic} (It’s Not What You Think)",
            "Why {topic} Is the Biggest Trend of 2024",
            "I Spent 100 Hours Studying {topic} - Here’s What I Learned",
            "The Science Behind {topic} Explained in 60 Seconds",
            "Top 5 {topic} Myths That Are Completely False",
            "Why You Should Never Trust {topic} (And What to Do Instead)",
            "The Insane History of {topic} in Under a Minute",
            "How to Master {topic} Like a Pro (Beginner's Guide)",
            "The {topic} Conspiracy: What They Are Hiding From You"
        ]
        
        topic = random.choice(trends).title()
        title = random.choice(templates).format(topic=topic)
        print(f"✅ Found {len(trends)} trends. Generated viral title.\n")
        return title
        
    except Exception as e:
        print(f"⚠️ Trend fetch failed. Using fallback viral topic.\n")
        return "10 Mind-Blowing Facts About AI Technology You Won't Believe"

def main():
    print("=" * 50)
    print(" 🎬 Free AI Video Studio - Quick Start")
    print("=" * 50)
    print("1. Enter topic manually")
    print("2. Auto-generate from Global Viral Trends")
    
    choice = input("\nChoose (1 or 2): ").strip()
    
    if choice == '1':
        topic = input("📝 Enter your topic: ").strip() or "5 amazing facts about space"
    elif choice == '2':
        topic = get_viral_topic()
    else:
        topic = input("📝 Enter your topic: ").strip() or "5 amazing facts about space"

    print(f"\n🚀 Generating video for: '{topic}'")
    print("=" * 50)
    
    try:
        subprocess.run([sys.executable, "app.py", topic], check=True)
        print("\n✅ Pipeline finished successfully!")
    except subprocess.CalledProcessError:
        print("\n❌ Error during generation. Check logs above.")
    except KeyboardInterrupt:
        print("\n\n⚠️ Process interrupted.")

if __name__ == "__main__":
    main()
