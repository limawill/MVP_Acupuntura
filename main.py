import os
from dotenv import load_dotenv
from mvp_acupuntura.gui.tela_inicial import Application
from mvp_acupuntura.tools.setup_folders import SetupFoldersError

# from mvp_acupuntura.tools.transcricao_whisperx import TranscricaoAudio
# from mvp_acupuntura.tools.transcricao_simples import TranscricaoAudioSimples


load_dotenv()


def main():
    """
    Main function to set up the project structure.
    """
    setup = SetupFoldersError()
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
