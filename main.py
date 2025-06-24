from src.gui.tela_inicial import Application
from src.tools.setup_folders import SetupFoldersError


def main():
    """
    Main function to set up the project structure.
    """
    setup = SetupFoldersError()
    tela = Application()

    # Check if the project structure is correct
    if not setup.verifica_estutura():
        print("Project structure is incorrect. Please check the setup.")
        return

    # Proceed with the rest of the application logic
    print("Project structure is correct. Proceeding with the application...")
    tela.mainloop()


if __name__ == "__main__":
    main()
