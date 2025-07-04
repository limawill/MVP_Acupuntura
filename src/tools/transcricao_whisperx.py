import os
import time
import whisperx
import torch
from dotenv import load_dotenv
from pyannote.audio import Pipeline
from mvp_acupuntura.gui.loading_screen import LoadingScreen


class TranscricaoAudio:
    def __init__(self):
        load_dotenv()
        self.model_name = os.getenv("WHISPER_MODEL", "small")
        self.folder_audio = os.getenv("FOLDER_AUDIO", "audio")
        self.language = os.getenv("WHISPER_LANGUAGE", "pt")
        self.destino_file = "transcricao"
        self.model = None
        self.align_model = None
        self.diarization_pipeline = None
        self.loading_screen = None
        self.hf_token = os.getenv("HF_TOKEN")

        if not all([self.model_name, self.folder_audio, self.hf_token]):
            raise ValueError("⚠️ Variáveis de ambiente não definidas corretamente.")

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
            progress_callback(10, "Carregando modelo WhisperX...")
            self.model = whisperx.load_model(
                self.model_name,
                device=device,
                compute_type=compute_type
            )
            progress_callback(20, "Modelo carregado.")

            # Verifica arquivos
            list_audio = [f for f in os.listdir(self.folder_audio) if f.endswith(".wav")]
            if not list_audio or len(list_audio) > 1:
                progress_callback(0, "Erro: Nenhum ou múltiplos arquivos.")
                return None

            audio_file = os.path.join(self.folder_audio, list_audio[0])
            
            # 2. Carrega áudio
            progress_callback(30, "Carregando áudio...")
            audio = whisperx.load_audio(audio_file)

            # 3. Transcrição inicial simplificada
            progress_callback(40, "Transcrevendo áudio...")
            result = self.model.transcribe(
                audio, 
                batch_size=16,
                language=self.language
            )

            # 4. Alinhamento para melhorar timestamps (opcional)
            try:
                progress_callback(50, "Melhorando timestamps...")
                self.align_model, metadata = whisperx.load_align_model(
                    language_code=result["language"], 
                    device=device
                )
                
                result = whisperx.align(
                    result["segments"], 
                    self.align_model, 
                    metadata, 
                    audio, 
                    device, 
                    return_char_alignments=False
                )
                progress_callback(55, "Timestamps melhorados.")
            except Exception as align_error:
                progress_callback(55, "Alinhamento falhou, continuando...")
                print(f"[⚠️] Alinhamento falhou: {align_error}")

            # 5. Diarização com tratamento robusto
            progress_callback(60, "Diarizando falantes...")
            try:
                if not self.diarization_pipeline:
                    # Usar modelo mais leve e compatível
                    self.diarization_pipeline = Pipeline.from_pretrained(
                        "pyannote/speaker-diarization", 
                        use_auth_token=self.hf_token
                    )
                
                # Executar diarização
                diarization = self.diarization_pipeline(audio_file)
                
                # 6. Método alternativo de atribuição de falantes
                progress_callback(80, "Associando falas manualmente...")
                
                # Converter diarização para lista de segmentos
                diarization_segments = []
                for turn, _, speaker in diarization.itertracks(yield_label=True):
                    diarization_segments.append({
                        'start': turn.start,
                        'end': turn.end,
                        'speaker': speaker
                    })
                
                # Atribuir falantes manualmente
                for segment in result["segments"]:
                    seg_start = segment["start"]
                    seg_end = segment["end"]
                    seg_mid = (seg_start + seg_end) / 2  # Ponto médio do segmento
                    
                    best_speaker = "UNKNOWN"
                    best_overlap = 0
                    
                    for dia_seg in diarization_segments:
                        # Verificar se o ponto médio está dentro do segmento de diarização
                        if dia_seg['start'] <= seg_mid <= dia_seg['end']:
                            # Calcular sobreposição
                            overlap_start = max(seg_start, dia_seg['start'])
                            overlap_end = min(seg_end, dia_seg['end'])
                            overlap = max(0, overlap_end - overlap_start)
                            
                            if overlap > best_overlap:
                                best_overlap = overlap
                                best_speaker = dia_seg['speaker']
                    
                    segment["speaker"] = best_speaker
                
                progress_callback(90, "Diarização concluída.")
                
            except Exception as diarization_error:
                progress_callback(70, "Diarização falhou, usando segmentação por pausas...")
                print(f"[⚠️] Diarização falhou: {diarization_error}")
                
                # Método alternativo: segmentar por pausas longas
                self._segmentar_por_pausas(result["segments"])
                progress_callback(90, "Segmentação por pausas concluída.")

            progress_callback(100, "Transcrição finalizada!")

            # 7. Salva resultado melhorado
            self._salvar_transcricao_melhorada(result, list_audio[0])
            
            return result

        except Exception as e:
            progress_callback(0, f"Erro: {str(e)}")
            print(f"[❌] Erro: {e}")
            return None

    def _salvar_transcricao_melhorada(self, result, nome_arquivo):
        """Salva transcrição com melhor formatação e separação."""
        os.makedirs(self.destino_file, exist_ok=True)
        nome_txt = os.path.splitext(nome_arquivo)[0] + "_melhorado.txt"
        caminho_txt = os.path.join(self.destino_file, nome_txt)

        with open(caminho_txt, "w", encoding="utf-8") as f:
            f.write("TRANSCRIÇÃO MELHORADA COM DIARIZAÇÃO\n")
            f.write("=" * 50 + "\n\n")
            f.write("INSTRUÇÕES:\n")
            f.write("- Cada linha é uma fala separada\n") 
            f.write("- Pausas maiores que 500ms criam nova linha\n")
            f.write("- Substitua Speaker_XX pelos nomes reais\n")
            f.write("=" * 50 + "\n\n")
            
            current_speaker = None
            speaker_counter = {}
            
            for segment in result["segments"]:
                # Mapear speakers para nomes amigáveis
                original_speaker = segment.get("speaker", "UNKNOWN")
                if original_speaker not in speaker_counter:
                    speaker_counter[original_speaker] = f"Pessoa{len(speaker_counter) + 1}"
                
                speaker = speaker_counter[original_speaker]
                
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
                    f.write(f"--- {speaker} ---\n")
                    current_speaker = speaker
                
                # Escrever fala
                f.write(f"[{timestamp}] {segment['text'].strip()}\n")
            
            # Resumo dos falantes
            f.write("\n" + "=" * 50 + "\n")
            f.write("RESUMO DOS FALANTES:\n")
            for original, mapped in speaker_counter.items():
                f.write(f"{mapped} = {original}\n")

        print(f"[💾] Transcrição melhorada salva em: {caminho_txt}")

    def _segmentar_por_pausas(self, segments):
        """Método alternativo: segmenta falantes baseado em pausas."""
        current_speaker = "Pessoa1"
        speaker_counter = 1
        
        for i, segment in enumerate(segments):
            if i == 0:
                segment["speaker"] = current_speaker
                continue
            
            # Calcular pausa entre segmentos
            pausa = segment["start"] - segments[i-1]["end"]
            
            # Se pausa > 2 segundos, provavelmente mudou de falante
            if pausa > 2.0:
                speaker_counter = 2 if speaker_counter == 1 else 1
                current_speaker = f"Pessoa{speaker_counter}"
            
            segment["speaker"] = current_speaker
