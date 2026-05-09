from dotenv import load_dotenv
import os

load_dotenv()

key = os.getenv("OPENAI_API_KEY")

print("Key exists:", key is not None)
print("Key prefix:", key[:10] if key else None)
print("Key length:", len(key) if key else None)