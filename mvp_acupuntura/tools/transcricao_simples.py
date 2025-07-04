import os
import time
import whisperx
import torch
from dotenv import load_dotenv
from mvp_acupuntura.gui.loading_screen import LoadingScreen


class TranscricaoAudioSimples:
    """Versão simplificada sem diarização complexa."""
    
    def __init__(self):
        load_dotenv()
        self.model_name = os.getenv("WHISPER_MODEL", "small")
        self.folder_audio = os.getenv("FOLDER_AUDIO", "audio")
        self.language = os.getenv("WHISPER_LANGUAGE", "pt")
        self.destino_file = "transcricao"
        self.model = None
        self.loading_screen = None

        if not all([self.model_name, self.folder_audio]):
            raise ValueError("⚠️ Variáveis de ambiente não definidas.")

    def carregar_modelo(self):
        self.loading_screen = LoadingScreen(transcritor=self)
        self.loading_screen.iniciar_transcricao()
        self.loading_screen.mainloop()

    def transcrever_audio(self):
        def progress_callback(valor, mensagem):
            if self.loading_screen:
                self.loading_screen.atualizar_progresso(valor, mensagem)

        device = "cpu"
        compute_type = "int8"

        try:
            # 1. Carrega modelo WhisperX
            progress_callback(20, "Carregando modelo WhisperX...")
            self.model = whisperx.load_model(
                self.model_name,
                device=device,
                compute_type=compute_type
            )
            progress_callback(40, "Modelo carregado.")

            # Verifica arquivos
            list_audio = [f for f in os.listdir(self.folder_audio) if f.endswith(".wav")]
            if not list_audio or len(list_audio) > 1:
                progress_callback(0, "Erro: Nenhum ou múltiplos arquivos.")
                return None

            audio_file = os.path.join(self.folder_audio, list_audio[0])
            
            # 2. Carrega áudio
            progress_callback(50, "Carregando áudio...")
            audio = whisperx.load_audio(audio_file)

            # 3. Transcrição
            progress_callback(60, "Transcrevendo áudio...")
            result = self.model.transcribe(
                audio, 
                batch_size=16,
                language=self.language
            )

            # 4. Segmentação inteligente por pausas
            progress_callback(80, "Identificando falantes por pausas...")
            self._identificar_falantes_por_pausas(result["segments"])

            progress_callback(100, "Transcrição finalizada!")

            # 5. Salva resultado
            self._salvar_transcricao_simples(result, list_audio[0])
            
            return result

        except Exception as e:
            progress_callback(0, f"Erro: {str(e)}")
            print(f"[❌] Erro: {e}")
            return None

    def _identificar_falantes_por_pausas(self, segments):
        """Identifica falantes baseado em pausas e duração das falas."""
        if not segments:
            return
        
        current_speaker = "Terapeuta"  # Assume que primeiro é terapeuta
        speaker_counter = 1
        
        for i, segment in enumerate(segments):
            if i == 0:
                segment["speaker"] = current_speaker
                continue
            
            # Calcular pausa entre segmentos
            pausa = segment["start"] - segments[i-1]["end"]
            duracao_atual = segment["end"] - segment["start"]
            duracao_anterior = segments[i-1]["end"] - segments[i-1]["start"]
            
            # Regras para mudança de falante:
            # 1. Pausa longa (> 1.5s)
            # 2. Mudança drástica na duração da fala
            # 3. Alternância natural em entrevistas
            
            mudou_falante = False
            
            if pausa > 1.5:  # Pausa longa
                mudou_falante = True
            elif abs(duracao_atual - duracao_anterior) > 2.0:  # Mudança drástica
                mudou_falante = True
            elif i % 2 == 1 and pausa > 0.8:  # Alternância em perguntas curtas
                mudou_falante = True
            
            if mudou_falante:
                current_speaker = "Paciente" if current_speaker == "Terapeuta" else "Terapeuta"
            
            segment["speaker"] = current_speaker

    def _salvar_transcricao_simples(self, result, nome_arquivo):
        """Salva transcrição com identificação simples."""
        os.makedirs(self.destino_file, exist_ok=True)
        nome_txt = os.path.splitext(nome_arquivo)[0] + "_simples.txt"
        caminho_txt = os.path.join(self.destino_file, nome_txt)

        with open(caminho_txt, "w", encoding="utf-8") as f:
            f.write("TRANSCRIÇÃO COM IDENTIFICAÇÃO INTELIGENTE\n")
            f.write("=" * 50 + "\n\n")
            f.write("MÉTODO: Identificação por pausas e padrões de fala\n")
            f.write("EDITÁVEL: Use Ctrl+H para substituir Terapeuta/Paciente\n")
            f.write("=" * 50 + "\n\n")
            
            current_speaker = None
            
            for segment in result["segments"]:
                speaker = segment.get("speaker", "Desconhecido")
                
                # Formatar tempo
                start_min = int(segment["start"] // 60)
                start_sec = int(segment["start"] % 60)
                end_min = int(segment["end"] // 60)
                end_sec = int(segment["end"] % 60)
                
                timestamp = f"{start_min:02d}:{start_sec:02d}-{end_min:02d}:{end_sec:02d}"
                
                # Adicionar separador visual quando muda de falante
                if current_speaker != speaker:
                    if current_speaker is not None:
                        f.write("\n")
                    f.write(f"=== {speaker} ===\n")
                    current_speaker = speaker
                
                # Escrever fala
                f.write(f"[{timestamp}] {segment['text'].strip()}\n")
            
            # Estatísticas
            f.write("\n" + "=" * 50 + "\n")
            f.write("ESTATÍSTICAS:\n")
            speakers = [seg.get("speaker", "Desconhecido") for seg in result["segments"]]
            for speaker in set(speakers):
                count = speakers.count(speaker)
                f.write(f"{speaker}: {count} falas\n")

        print(f"[💾] Transcrição simples salva em: {caminho_txt}")
