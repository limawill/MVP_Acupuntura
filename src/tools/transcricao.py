import os
import time
import torch
import logging
import whisperx
from dotenv import load_dotenv
from src.gui.loading_screen import LoadingScreen

logger = logging.getLogger(__name__)


class TranscricaoAudio:
    """
    Classe para transcrição de áudio focada em alta qualidade usando o WhisperX,
    sem diarização ou alinhamento de falantes.
    """

    def __init__(self):
        load_dotenv()
        self.model_name = os.getenv(
            "WHISPER_MODEL", "large"
        )  # Mantendo o modelo large para melhor qualidade
        self.folder_audio = os.getenv("FOLDER_AUDIO", "src/audio")
        self.language = os.getenv("WHISPER_LANGUAGE", "pt")
        self.destino_folder = "src/transcricao"
        self.model = None
        self.loading_screen = None
        # Removendo: self.hf_token = os.getenv("HF_TOKEN") # Não precisamos mais do token para pyannote

        os.makedirs(self.destino_folder, exist_ok=True)

        # Atualizando a validação das variáveis de ambiente
        if not all([self.model_name, self.folder_audio]):
            raise ValueError(
                "⚠️ Variáveis de ambiente WHISPER_MODEL ou FOLDER_AUDIO não definidas corretamente no .env."
            )

    def carregar_modelo(self):
        """Cria a janela de carregamento e inicia a transcrição."""
        self.loading_screen = LoadingScreen(transcritor=self)
        self.loading_screen.iniciar_transcricao()
        self.loading_screen.mainloop()

    def transcrever_audio(self):
        """
        Transcreve os arquivos de áudio filtrados por '_completo' usando WhisperX,
        focando apenas na transcrição do texto.
        """

        def progress_callback(valor, mensagem):
            if self.loading_screen:
                self.loading_screen.atualizar_progresso(valor, mensagem)

        device = "cuda" if torch.cuda.is_available() else "cpu"
        # Usar float16 para CUDA e int8 para CPU para melhor performance/compatibilidade
        compute_type = "float16" if device == "cuda" else "int8"

        try:
            progress_callback(10, "Carregando modelo WhisperX para transcrição...")
            self.model = whisperx.load_model(  # Ainda usando whisperx para otimização
                self.model_name,
                device=device,
                compute_type=compute_type,
                language=self.language,
            )
            progress_callback(30, "Modelo WhisperX carregado.")
            logger.info(
                f"[INFO] Modelo WhisperX '{self.model_name}' carregado com sucesso."
            )

            # Filtrar arquivos que contêm "_completo"
            list_audio_files = [
                f
                for f in os.listdir(self.folder_audio)
                if f.endswith(".wav") and "_completo" in f
            ]

            if not list_audio_files:
                progress_callback(
                    0,
                    "Erro: Nenhum arquivo .wav com '_completo' encontrado na pasta de áudio.",
                )
                logger.info(
                    "Nenhum arquivo .wav com '_completo' encontrado para processar."
                )
                return None

            total_files = len(list_audio_files)
            logger.info(
                f"Encontrados {total_files} arquivo(s) com '_completo' para processar."
            )

            for i, audio_filename in enumerate(list_audio_files):
                current_file_path = os.path.join(self.folder_audio, audio_filename)
                progress_prefix = f"[{i + 1}/{total_files}]"
                logger.info(f"\n{progress_prefix} Processando: {audio_filename}")

                progress_callback(
                    40 + int(i * (60 / total_files * 0.1)),
                    f"{progress_prefix} Carregando áudio...",
                )
                audio = whisperx.load_audio(current_file_path)

                progress_callback(
                    40 + int(i * (60 / total_files * 0.2)),
                    f"{progress_prefix} Transcrevendo áudio...",
                )
                # Transcrição principal sem alinhamento ou diarização aqui
                result = self.model.transcribe(
                    audio,
                    batch_size=16,
                )

                # Debug: verificar estrutura do resultado
                logger.debug(f"Chaves disponíveis no resultado: {list(result.keys())}")

                # Não há mais passos de alinhamento ou diarização aqui.
                # O resultado já contém os 'segments' que precisamos.

                progress_callback(
                    100,
                    f"{progress_prefix} Transcrição finalizada para {audio_filename}!",
                )

                self._salvar_transcricao_pura(
                    result, audio_filename
                )  # Novo nome de método

            progress_callback(100, "Todos os arquivos de áudio completos processados!")
            return True

        except Exception as e:
            progress_callback(0, f"Erro fatal durante a transcrição: {str(e)}")
            logger.error(f"Erro fatal: {e}")
            return None

    def _salvar_transcricao_pura(self, result, nome_arquivo_original):
        """Salva o resultado da transcrição pura em um arquivo de texto."""
        os.makedirs(self.destino_folder, exist_ok=True)
        nome_txt = (
            os.path.splitext(nome_arquivo_original)[0] + "_transcrito_bruto.txt"
        )  # Sufixo mais claro
        caminho_txt = os.path.join(self.destino_folder, nome_txt)

        with open(caminho_txt, "w", encoding="utf-8") as f:
            # WhisperX sempre retorna resultado com 'segments'
            if "segments" in result and result["segments"]:
                # Combinar texto de todos os segmentos
                texto_completo = ""
                for segment in result["segments"]:
                    if "text" in segment:
                        texto_completo += segment["text"].strip() + " "

                if texto_completo:
                    f.write(texto_completo.strip())
                else:
                    f.write("❌ Erro: Segmentos não contêm texto válido.")
                    primeiro_seg = (
                        result["segments"][0] if result["segments"] else "Vazio"
                    )
                    logger.debug(f"Primeiro segmento: {primeiro_seg}")
            else:
                f.write("❌ Erro: Resultado não contém 'segments' ou está vazio.")
                logger.debug(f"Chaves do resultado: {list(result.keys())}")

        logger.info(f"Transcrição salva em: {caminho_txt}")
