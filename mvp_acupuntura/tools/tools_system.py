import os
import shutil
from dotenv import load_dotenv


class SetupSystem:

    def clear_files_audio(self, list_files: list, output_dir: str) -> None:
        """
        Limpa os arquivos de áudio especificados na lista.

        Args:
            list_files (list): Lista de caminhos de arquivos de áudio a serem removidos.
        """
        for arquivo in list_files:
            caminho_arquivo = os.path.join(output_dir, arquivo)
            try:
                os.remove(caminho_arquivo)
                print(f"[🗑️] Arquivo {arquivo} apagado.")
            except Exception as e:
                print(f"[!] Erro ao apagar {arquivo}: {e}")

    def text_underline(self, text: str) -> str:
        """
        Substitui espaços por underline em uma string.

        Args:
            text (str): Texto original.

        Returns:
            str: Texto com espaços substituídos por underlines.
        """
        return text.replace(" ", "_")
