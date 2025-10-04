"""
Quick test to verify .env loading and recording state logic.
Run this before starting Streamlit to verify environment setup.
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

# Test 1: Load .env
print("=" * 60)
print("TEST 1: Loading .env file")
print("=" * 60)
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
    print("✅ python-dotenv loaded successfully")
except ImportError as e:
    print(f"❌ python-dotenv not installed: {e}")
    sys.exit(1)

# Test 2: Check critical environment variables
print("\n" + "=" * 60)
print("TEST 2: Environment Variables")
print("=" * 60)
critical_vars = {
    "ELEVENLABS_API_KEY": os.getenv("ELEVENLABS_API_KEY"),
    "DEBUG_LOGGING": os.getenv("DEBUG_LOGGING"),
    "VOCALBRAND_OFFLINE": os.getenv("VOCALBRAND_OFFLINE"),
    "AUTO_FFMPEG": os.getenv("AUTO_FFMPEG"),
}

for var, value in critical_vars.items():
    status = "✅" if value else "⚠️"
    display_val = value[:20] + "..." if value and len(value) > 20 else (value or "NOT SET")
    print(f"{status} {var}: {display_val}")

# Test 3: Import app modules
print("\n" + "=" * 60)
print("TEST 3: Module Imports")
print("=" * 60)
try:
    import streamlit as st
    print("✅ streamlit imported")
except ImportError as e:
    print(f"❌ streamlit: {e}")

try:
    from engine import VocalBrandEngine
    print("✅ engine.VocalBrandEngine imported")
except ImportError as e:
    print(f"❌ engine: {e}")

try:
    from auth import init_db
    print("✅ auth.init_db imported")
except ImportError as e:
    print(f"❌ auth: {e}")

try:
    from utils.audio_utils import validate_audio_bytes
    print("✅ utils.audio_utils imported")
except ImportError as e:
    print(f"❌ utils.audio_utils: {e}")

# Test 4: Database initialization
print("\n" + "=" * 60)
print("TEST 4: Database Check")
print("=" * 60)
db_path = os.getenv("DATABASE_URL", "sqlite:///vocalbrand.db").replace("sqlite:///", "")
if os.path.exists(db_path):
    size_kb = os.path.getsize(db_path) / 1024
    print(f"✅ Database exists: {db_path} ({size_kb:.1f} KB)")
else:
    print(f"⚠️  Database not yet created: {db_path}")
    print("   (Will be auto-created on first app run)")

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
if critical_vars["DEBUG_LOGGING"] == "1":
    print("✅ DEBUG_LOGGING is ON - you will see detailed recording state")
else:
    print("⚠️  DEBUG_LOGGING is OFF - set to '1' in .env for debugging")

if critical_vars["ELEVENLABS_API_KEY"]:
    if critical_vars["ELEVENLABS_API_KEY"].startswith("sk_"):
        print("✅ ElevenLabs API key format looks correct")
    else:
        print("⚠️  ElevenLabs API key doesn't start with 'sk_' (might be test key)")
else:
    print("❌ ELEVENLABS_API_KEY not set - cloning will use offline fallback")

print("\n🚀 Ready to start Streamlit!")
print("   Run: streamlit run app.py")
print("=" * 60)
