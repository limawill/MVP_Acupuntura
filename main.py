import logging
from dotenv import load_dotenv
from src.gui.tela_inicial import Application
from src.tools.tools_system import SetupSystem
from src.tools.setup_folders import SetupFolders
from src.tools.logging_config import setup_logging
from src.tools.transcricao import TranscricaoAudio

load_dotenv()

# Iniciando logging
setup_logging()
logger = logging.getLogger(__name__)


def main():
    """
    Main function to set up the project structure.
    """
    setup = SetupFolders()
    tools_system = SetupSystem()
    tela = Application()
    transcricao = TranscricaoAudio()

    # Check if the project structure is correct
    if not setup.verifica_estutura():
        logger.error("Project structure is incorrect. Please check the setup.")
        return

    logger.info("Iniciando a aplicação MVP Acupuntura.")
    if tools_system.iniciar_ollama_servidor():
        # Proceed with the rest of the application logic
        tela.mainloop()
        transcricao.carregar_modelo()


if __name__ == "__main__":
    main()
