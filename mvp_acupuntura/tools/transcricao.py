import os
import time
import whisper
from dotenv import load_dotenv
from mvp_acupuntura.gui.loading_screen import LoadingScreen


class TranscricaoAudio:
    """
    Classe para transcrição de áudio usando o modelo WhisperX com diarização.
    """

    def __init__(self):
        load_dotenv()
        self.model_name = os.getenv("WHISPER_MODEL", "small")
        self.folder_audio = os.getenv("FOLDER_AUDIO", "audio")
        self.language = os.getenv("WHISPER_LANGUAGE", "pt")
        self.destino_file = "transcricao"
        self.model = None
        self.align_model = None
        self.diarize_model = None
        self.loading_screen = None

        if not self.model_name:
            raise ValueError("O modelo Whisper não está definido no .env.")
        if not self.folder_audio:
            raise ValueError("A pasta de áudio não está definida no .env.")

    def carregar_modelo(self):
        """Cria a janela de carregamento e inicia a transcrição."""
        self.loading_screen = LoadingScreen(transcritor=self)
        self.loading_screen.iniciar_transcricao()
        self.loading_screen.mainloop()

    def transcrever_audio(self):
        """Transcreve o áudio e atualiza a barra de progresso."""

        def progress_callback(valor, mensagem):
            if self.loading_screen:
                self.loading_screen.atualizar_progresso(valor, mensagem)

        # Carrega modelo Whisper
        if not self.model:
            progress_callback(10, "Carregando modelo Whisper...")
            time.sleep(1)
            self.model = whisper.load_model(self.model_name)
            progress_callback(30, "Modelo carregado.")

        # Verifica arquivos de áudio
        list_audio = [f for f in os.listdir(self.folder_audio) if f.endswith(".wav")]
        if not list_audio or len(list_audio) > 1:
            progress_callback(0, "Erro: Nenhum ou múltiplos arquivos encontrados.")
            return None

        audio_file = os.path.join(self.folder_audio, list_audio[0])
        progress_callback(40, "Iniciando transcrição...")

        result = self.model.transcribe(audio_file, language=self.language, verbose=True)

        # Simula progresso visual
        total_steps = 6
        for i in range(total_steps):
            time.sleep(1)
            progress_value = 40 + ((i + 1) * (60 // total_steps))
            progress_callback(
                progress_value, f"Transcrevendo... ({i + 1}/{total_steps})"
            )

        progress_callback(100, "Transcrição concluída!")

        # Salva resultado
        os.makedirs(self.destino_file, exist_ok=True)
        nome_txt = os.path.splitext(list_audio[0])[0] + ".txt"
        caminho_txt = os.path.join(self.destino_file, nome_txt)
        with open(caminho_txt, "w", encoding="utf-8") as f:
            f.write(result["text"])

        print(f"[💾] Transcrição salva em: {caminho_txt}")
        return result["text"]
