import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERRO: GEMINI_API_KEY não foi encontrada no arquivo .env")
    raise SystemExit


client = genai.Client(api_key=api_key)


response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="Responda apenas: conexão com Gemini funcionando."
)


print(response.text)