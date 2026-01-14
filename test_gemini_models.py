from google import genai

client = genai.Client(
    api_key="AIzaSyA-wbm4CPmGo4pIaRV-PXkI16o29LTkfBU"
)

print("\n=== AVAILABLE MODELS ===\n")

for m in client.models.list():
    print(m.name)
