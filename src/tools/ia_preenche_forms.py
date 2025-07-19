import os
from openai import OpenAI
from dotenv import load_dotenv


# Carregar variáveis do arquivo .env
load_dotenv()

# Obter a lista de pastas da variável de ambiente
api_key = os.getenv("DS_TOKEN")
base_url = os.getenv("BASE_URL")

client = OpenAI(api_key=api_key, base_url=base_url)

response = client.chat.completions.create(
    model="deepseek/deepseek-r1:free",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    stream=False,
)

print(response.choices[0].message.content)
