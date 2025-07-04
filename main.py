import os
from dotenv import load_dotenv
from src.gui.tela_inicial import Application
from src.tools.setup_folders import SetupFolders

# from src.tools.transcricao_whisperx import TranscricaoAudio
# from src.tools.transcricao_simples import TranscricaoAudioSimples


load_dotenv()


def main():
    """
    Main function to set up the project structure.
    """
    setup = SetupFolders()
    tela = Application()
    # transcricao = TranscricaoAudio()

    # Check if the project structure is correct
    if not setup.verifica_estutura():
        print("Project structure is incorrect. Please check the setup.")
        return

    # Proceed with the rest of the application logic
    tela.mainloop()
    # transcricao.carregar_modelo()


if __name__ == "__main__":
    main()
