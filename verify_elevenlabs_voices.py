"""Script to verify ElevenLabs voices and get current voice IDs.
Run this to ensure your fallback voices are valid.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

if not ELEVENLABS_API_KEY:
    print("❌ ELEVENLABS_API_KEY not found in environment!")
    print("Please set it in your .env file or environment variables.")
    exit(1)

print("🔍 Fetching available voices from ElevenLabs...")
print("=" * 60)

try:
    response = requests.get(
        "https://api.elevenlabs.io/v1/voices",
        headers={"xi-api-key": ELEVENLABS_API_KEY},
        timeout=10
    )
    
    if response.status_code != 200:
        print(f"❌ API Error: {response.status_code}")
        print(response.text)
        exit(1)
    
    data = response.json()
    voices = data.get("voices", [])
    
    print(f"✅ Found {len(voices)} voices in your account\n")
    
    # Categorize voices
    premade = []
    cloned = []
    
    for voice in voices:
        voice_id = voice.get("voice_id")
        name = voice.get("name")
        category = voice.get("category", "unknown")
        
        if category == "premade":
            premade.append((name, voice_id))
        else:
            cloned.append((name, voice_id))
    
    # Display pre-made voices (safe for fallbacks)
    print("🎤 PRE-MADE VOICES (Safe for Fallbacks):")
    print("-" * 60)
    if premade:
        for name, vid in premade:
            print(f"  • {name:20} → {vid}")
    else:
        print("  ⚠️  No pre-made voices found!")
    
    print("\n")
    
    # Display cloned voices
    print("🔊 YOUR CLONED VOICES:")
    print("-" * 60)
    if cloned:
        for name, vid in cloned:
            print(f"  • {name:20} → {vid}")
    else:
        print("  (No cloned voices yet)")
    
    print("\n")
    print("=" * 60)
    print("📋 RECOMMENDED FALLBACK VOICES FOR engine.py:")
    print("=" * 60)
    
    if len(premade) >= 4:
        print("self.fallback_voices = [")
        for i, (name, vid) in enumerate(premade[:4]):
            print(f'    "{vid}",  # {name}')
        print("]")
    else:
        print("⚠️  You have fewer than 4 pre-made voices.")
        print("Using all available:")
        print("self.fallback_voices = [")
        for name, vid in premade:
            print(f'    "{vid}",  # {name}')
        print("]")
    
    print("\n")
    
    # Check current usage
    print("=" * 60)
    print("📊 API USAGE CHECK:")
    print("=" * 60)
    
    try:
        usage_response = requests.get(
            "https://api.elevenlabs.io/v1/user",
            headers={"xi-api-key": ELEVENLABS_API_KEY},
            timeout=10
        )
        
        if usage_response.status_code == 200:
            user_data = usage_response.json()
            subscription = user_data.get("subscription", {})
            
            character_count = subscription.get("character_count", 0)
            character_limit = subscription.get("character_limit", 0)
            
            if character_limit > 0:
                usage_percent = (character_count / character_limit) * 100
                print(f"Characters used: {character_count:,} / {character_limit:,}")
                print(f"Usage: {usage_percent:.1f}%")
                
                if usage_percent > 80:
                    print("⚠️  Warning: Over 80% usage!")
                elif usage_percent > 50:
                    print("⚠️  Moderate usage")
                else:
                    print("✅ Good usage level")
            else:
                print("Character usage data not available")
        else:
            print(f"Could not fetch usage data: {usage_response.status_code}")
    
    except Exception as e:
        print(f"Error checking usage: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Verification complete!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
