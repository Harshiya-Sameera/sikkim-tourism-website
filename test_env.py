import os
# If you use a .env file, uncomment the following two lines:
# from dotenv import load_dotenv
# load_dotenv()

def test_google_maps_config():
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if api_key:
        # Show first 4 and last 4 characters to verify it's the right key
        masked_key = f"{api_key[:4]}...{api_key[-4:]}"
        print(f"✅ Success! API Key found: {masked_key}")
        print(f"Key length: {len(api_key)} characters")
    else:
        print("❌ Error: GOOGLE_MAPS_API_KEY not found in environment.")

if __name__ == "__main__":
    test_google_maps_config()
