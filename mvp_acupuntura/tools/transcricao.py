import os
import whisper
from dotenv import load_dotenv


class TranscricaoAudio:
    """
    Classe para transcrição de áudio usando o modelo Whisper.

    A classe carrega o modelo Whisper e fornece métodos para transcrever arquivos de áudio.

    Notas:
        - O modelo Whisper deve ser instalado via pip: `pip install git+
    """

    def __init__(self):
        """
        Inicializa a classe e carrega o modelo Whisper.

        O modelo é carregado na inicialização da classe, permitindo que seja usado
        imediatamente após a instância ser criada.
        """
        self.model = "medium"

        if not self.model:
            raise ValueError("O modelo Whisper não está definido no arquivo .env.")
        self.folder_audio = os.getenv("FOLDER_AUDIO")
        if not self.folder_audio:
            raise ValueError("A pasta de áudio não está definida no arquivo .env.")
        self.language = os.getenv("WHISPER_LANGUAGE", "pt")

    def carregar_modelo(self):
        """
        Carrega o modelo Whisper.

        O modelo pode ser 'tiny', 'base', 'small', 'medium' ou 'large'.
        O tamanho do modelo afeta a precisão e os recursos necessários.
        """
        print("Carregando o modelo Whisper...")
        print(f"Modelo Whisper selecionado: {self.model}")
        model = whisper.load_model(self.model)
        list_audio = [f for f in os.listdir(self.folder_audio) if f.endswith(".wav")]
        print(f"Arquivos de áudio encontrados: {list_audio}")

        if not list_audio or len(list_audio) > 1:
            print("Nenhum arquivo de áudio encontrado ou compactação não ocorreu.")
            return None

        audio_filename_to_transcribe = list_audio[0]
        # Use os.path.join para criar o caminho completo
        full_audio_file_path = os.path.join(
            self.folder_audio, audio_filename_to_transcribe
        )

        print(f"Transcrevendo o áudio de: {full_audio_file_path}...")

        # whisper audio/arquivo.wav --language Portuguese --model medium
        result = model.transcribe(full_audio_file_path, language="pt", verbose=True)

        # 4. Imprimir a transcrição
        print("\n--- Transcrição ---")
        print(result["text"])
        print("-------------------\n")
