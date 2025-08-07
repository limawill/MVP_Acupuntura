import os
import ollama
from dotenv import load_dotenv

# ==================================
# 1. Carregar variáveis de ambiente
# ==================================
# Isso garante que as informações de configuração sejam lidas do seu arquivo .env
load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL_NAME = os.getenv(
    "MODEL_NAME", "deepseek-r1"
)  # Padrão para deepseek-r1, mas pode ser llama2

# ==================================
# 2. Configurar e instanciar o cliente Ollama
# ==================================
# A instância do cliente se conecta ao servidor Ollama na URL especificada.
client = ollama.Client(host=OLLAMA_URL)


# ==================================
# 3. Fazer a requisição
# ==================================
# O método chat() é ideal para interações de conversa, como o seu MVP.
def main():
    try:
        # Define a mensagem que será enviada para o modelo
        mensagens = [
            {
                "role": "system",
                "content": "Responda todas as perguntas de forma concisa e direta. NUNCA inclua seu processo de pensamento ou qualquer metadado, como blocos <think>...</think>. Forneça APENAS a resposta final.",
            },
            {
                "role": "user",
                "content": "Qual foi a minha duvida anterior? e o que eu pedi? Por favor, responda de forma direta e objetiva.",
            },
        ]

        print(f"Enviando mensagem para o modelo '{MODEL_NAME}' em {OLLAMA_URL}...")

        # Envia a requisição
        response = client.chat(
            model=MODEL_NAME,
            messages=mensagens,
            # stream=True,  # Opcional: use para receber a resposta em tempo real
            # options={'temperature': 0.8} # Opcional: ajuste a criatividade do modelo
        )

        # A resposta completa está em 'response'
        # A mensagem do assistente está em 'response['message']['content']'
        resposta_do_modelo = response["message"]["content"]

        print("\n--- Resposta do Modelo ---")
        print(resposta_do_modelo)
        print("--------------------------")

    except ollama.OllamaError as e:
        print(f"Erro ao interagir com o Ollama: {e}")
        print(
            "Verifique se o servidor Ollama está em execução e se o modelo está baixado."
        )

    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")


if __name__ == "__main__":
    main()
