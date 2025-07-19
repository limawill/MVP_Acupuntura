import os
import time
import logging
import requests
import subprocess
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class SetupSystem:

    def __init__(self) -> None:
        load_dotenv()
        self.ollama_base_url = os.getenv("OLLAMA_URL", "http://localhost:11434")

    def clear_files_audio(self, list_files: list) -> None:
        """
        Limpa os arquivos de áudio especificados na lista.

        Args:
            list_files (list): Lista de caminhos de arquivos de áudio a serem removidos.
        """
        for arquivo in list_files:
            caminho_arquivo = os.path.join(arquivo)
            try:
                os.remove(caminho_arquivo)
                logger.info(f"[🗑️] Arquivo {arquivo} apagado.")
            except Exception as e:
                logger.error(f"[!] Erro ao apagar {arquivo}: {e}")

    def text_underline(self, text: str) -> str:
        """
        Substitui espaços por underline em uma string.

        Args:
            text (str): Texto original.

        Returns:
            str: Texto com espaços substituídos por underlines.
        """
        logger.info(f"[INFO] Substituindo espaços por underlines no texto: {text}")
        return text.replace(" ", "_")

    def verificar_ollama_online(self, timeout=5):
        """
        Verifica se o servidor Ollama está online e respondendo à API.

        Args:
            timeout (int): Tempo máximo em segundos para esperar pela resposta.

        Returns:
            bool: True se o Ollama estiver online e respondendo, False caso contrário.
        """

        check_url = f"{self.ollama_base_url}/api/tags"

        logger.info(f"Verificando se Ollama está online em: {self.ollama_base_url}...")
        try:
            # Faz uma requisição GET simples
            response = requests.get(check_url, timeout=timeout)

            # Se o status code for 200 (OK), o Ollama está respondendo.
            if response.status_code == 200:
                logger.info("Ollama está online e respondendo.")
                return True
            else:
                logger.warning(f"Ollama respondeu com status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            logger.error(f"Ollama não está acessível na URL {self.ollama_base_url}.")
            return False
        except requests.exceptions.Timeout:
            logger.error(
                f"Tempo limite esgotado ao tentar conectar ao Ollama ({timeout}s)"
            )
            return False
        except Exception as e:
            logger.error(f"Erro inesperado ao verificar Ollama: {e}")
            return False

    def iniciar_ollama_servidor(self):
        """
        Tenta iniciar o servidor Ollama usando 'ollama serve'.
        Retorna True se conseguir iniciar (ou se já estiver rodando),
        False caso contrário.
        """
        if self.verificar_ollama_online():
            logger.info("Ollama já está online. Não é necessário iniciar.")
            return True

        logger.info("Tentando iniciar o servidor Ollama...")
        try:
            logger.info("Executando 'ollama serve'. Por favor, aguarde alguns segundos")
            process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,  # Redireciona stdout para /dev/null
                stderr=subprocess.DEVNULL,  # Redireciona stderr para /dev/null
                start_new_session=True,
            )  # Desvincula o processo do pai (o script Python)

            # Damos um tempo para o Ollama inicializar
            time.sleep(10)  # Dê uns 10 segundos, pode ajustar

            if self.verificar_ollama_online():
                logger.info("Ollama iniciado com sucesso!")
                return True
            else:
                logger.warning(
                    "Ollama não iniciou ou não está respondendo após a tentativa."
                )
                return False
        except FileNotFoundError:
            logger.error("Comando 'ollama' não encontrado.")
            return False
        except Exception as e:
            logger.error(f"Falha ao tentar iniciar o Ollama: {e}")
            return False
