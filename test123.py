from huggingface_hub import HfApi
import os


# Get token from environment (NEVER hardcode it)
HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    print("❌ Set HF_TOKEN environment variable")
    exit(1)

try:
    api = HfApi()
    user = api.whoami(token=HF_TOKEN)
    print(f"✅ Authenticated as: {user['name']}")
    print(f"Account type: {user.get('type', 'FREE')}")
    print(f"Email verified: {user.get('emailVerified', False)}")
except Exception as e:
    print(f"❌ Authentication failed: {e}")