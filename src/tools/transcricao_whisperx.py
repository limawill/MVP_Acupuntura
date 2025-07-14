import os
import time
import whisperx
import torch
from dotenv import load_dotenv
from pyannote.audio import Pipeline
from src.gui.loading_screen import LoadingScreen


class TranscricaoAudio:
    def __init__(self):
        load_dotenv()
        self.model_name = os.getenv("WHISPER_MODEL", "small")
        self.folder_audio = os.getenv("FOLDER_AUDIO", "src/audio")
        self.language = os.getenv("WHISPER_LANGUAGE", "pt")
        self.destino_folder = "src/transcricao"
        self.model = None
        self.align_model = None
        self.diarization_pipeline = None
        self.loading_screen = None
        self.hf_token = os.getenv("HF_TOKEN")

        os.makedirs(self.destino_folder, exist_ok=True)

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

        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"

        try:
            progress_callback(10, "Carregando modelo WhisperX...")
            self.model = whisperx.load_model(
                self.model_name,
                device=device,
                compute_type=compute_type,
                language=self.language,
            )
            progress_callback(20, "Modelo carregado.")

            progress_callback(25, "Carregando modelo de alinhamento...")
            self.align_model, self.align_metadata = whisperx.load_align_model(
                language_code=self.language, device=device
            )
            progress_callback(28, "Modelo de alinhamento carregado.")

            progress_callback(30, "Carregando pipeline de diarização...")
            self.diarization_pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization", use_auth_token=self.hf_token
            ).to(torch.device(device))
            progress_callback(35, "Pipeline de diarização carregado.")

            # Buscar apenas arquivos que terminam com _completo.wav
            list_audio_files = [
                f for f in os.listdir(self.folder_audio) 
                if f.endswith("_completo.wav")
            ]

            if not list_audio_files:
                progress_callback(
                    0, "Erro: Nenhum arquivo _completo.wav encontrado na pasta de áudio."
                )
                print("[⚠️] Dica: Certifique-se de que o áudio foi gravado e combinado corretamente.")
                return None

            total_files = len(list_audio_files)
            print(f"[INFO] Encontrados {total_files} arquivos _completo.wav para processar.")
            
            # Listar arquivos que serão processados
            if total_files > 0:
                print("[INFO] Arquivos a serem transcritos:")
                for i, filename in enumerate(list_audio_files, 1):
                    print(f"  {i}. {filename}")
            else:
                print("[INFO] Nenhum arquivo _completo.wav encontrado.")
                print("[INFO] Arquivos .wav disponíveis na pasta:")
                all_wav_files = [
                    f for f in os.listdir(self.folder_audio) 
                    if f.endswith(".wav")
                ]
                for f in all_wav_files:
                    print(f"  - {f}")
                return None

            for i, audio_filename in enumerate(list_audio_files):
                current_file_path = os.path.join(self.folder_audio, audio_filename)
                progress_prefix = f"[{i + 1}/{total_files}]"
                print(f"\n{progress_prefix} Processando: {audio_filename}")

                progress_callback(
                    40 + int(i * (60 / total_files * 0.1)),
                    f"{progress_prefix} Carregando áudio...",
                )
                audio = whisperx.load_audio(current_file_path)

                progress_callback(
                    40 + int(i * (60 / total_files * 0.2)),
                    f"{progress_prefix} Transcrevendo áudio...",
                )
                result = self.model.transcribe(
                    audio,
                    batch_size=16,
                )

                try:
                    progress_callback(
                        40 + int(i * (60 / total_files * 0.3)),
                        f"{progress_prefix} Melhorando timestamps...",
                    )
                    result = whisperx.align(
                        result["segments"],
                        self.align_model,
                        self.align_metadata,
                        audio,
                        device,
                        return_char_alignments=False,
                    )
                    progress_callback(
                        40 + int(i * (60 / total_files * 0.4)),
                        f"{progress_prefix} Timestamps melhorados.",
                    )
                except Exception as align_error:
                    progress_callback(
                        40 + int(i * (60 / total_files * 0.4)),
                        f"{progress_prefix} Alinhamento falhou, continuando...",
                    )
                    print(
                        f"[⚠️] Alinhamento falhou para {audio_filename}: {align_error}"
                    )

                progress_callback(
                    40 + int(i * (60 / total_files * 0.5)),
                    f"{progress_prefix} Diarizando falantes...",
                )
                try:
                    diarization = self.diarization_pipeline(current_file_path)

                    progress_callback(
                        40 + int(i * (60 / total_files * 0.7)),
                        f"{progress_prefix} Associando falas...",
                    )

                    diarization_segments = []
                    for turn, _, speaker in diarization.itertracks(yield_label=True):
                        diarization_segments.append(
                            {"start": turn.start, "end": turn.end, "speaker": speaker}
                        )

                    for segment in result["segments"]:
                        seg_start = segment["start"]
                        seg_end = segment["end"]
                        seg_mid = (seg_start + seg_end) / 2

                        best_speaker = "UNKNOWN"
                        best_overlap = 0

                        for dia_seg in diarization_segments:
                            if dia_seg["start"] <= seg_mid <= dia_seg["end"]:
                                overlap_start = max(seg_start, dia_seg["start"])
                                overlap_end = min(seg_end, dia_seg["end"])
                                overlap = max(0, overlap_end - overlap_start)

                                if overlap > best_overlap:
                                    best_overlap = overlap
                                    best_speaker = dia_seg["speaker"]

                        segment["speaker"] = best_speaker

                    progress_callback(
                        40 + int(i * (60 / total_files * 0.8)),
                        f"{progress_prefix} Diarização concluída.",
                    )

                except Exception as diarization_error:
                    progress_callback(
                        40 + int(i * (60 / total_files * 0.8)),
                        f"{progress_prefix} Diarização falhou, usando segmentação...",
                    )
                    print(
                        f"[⚠️] Diarização falhou para {audio_filename}: "
                        f"{diarization_error}"
                    )

                    self._segmentar_por_pausas(result["segments"])
                    progress_callback(
                        40 + int(i * (60 / total_files * 0.9)),
                        f"{progress_prefix} Segmentação por pausas concluída.",
                    )

                progress_callback(
                    100,
                    f"{progress_prefix} Transcrição finalizada para {audio_filename}!",
                )

                self._salvar_transcricao_melhorada(result, audio_filename)

            progress_callback(100, "Todos os arquivos processados!")
            return True

        except Exception as e:
            progress_callback(0, f"Erro fatal: {str(e)}")
            print(f"[❌] Erro fatal: {e}")
            return None

    def _salvar_transcricao_melhorada(self, result, nome_arquivo_original):
        os.makedirs(self.destino_folder, exist_ok=True)
        nome_txt = os.path.splitext(nome_arquivo_original)[0] + "_transcrito.txt"
        caminho_txt = os.path.join(self.destino_folder, nome_txt)

        with open(caminho_txt, "w", encoding="utf-8") as f:
            f.write("TRANSCRIÇÃO MELHORADA COM DIARIZAÇÃO\n")
            f.write("=" * 50 + "\n\n")
            f.write("INSTRUÇÕES:\n")
            f.write("- Cada linha é uma fala separada\n")
            f.write(
                "- Pausas maiores que 2 segundos podem indicar mudança de falante\n"
            )
            f.write("- Substitua Speaker_XX pelos nomes reais\n")
            f.write("=" * 50 + "\n\n")

            current_speaker = None
            speaker_map = {}

            for segment in result["segments"]:
                original_speaker_label = segment.get("speaker", "UNKNOWN")

                if original_speaker_label not in speaker_map:
                    speaker_map[original_speaker_label] = (
                        f"Pessoa{len(speaker_map) + 1}"
                    )

                display_speaker = speaker_map[original_speaker_label]

                start_min = int(segment["start"] // 60)
                start_sec = int(segment["start"] % 60)
                end_min = int(segment["end"] // 60)
                end_sec = int(segment["end"] % 60)

                timestamp = (
                    f"{start_min:02d}:{start_sec:02d}-{end_min:02d}:{end_sec:02d}"
                )

                if current_speaker != display_speaker:
                    if current_speaker is not None:
                        f.write("\n")
                    f.write(f"--- {display_speaker} ---\n")
                    current_speaker = display_speaker

                f.write(f"[{timestamp}] {segment['text'].strip()}\n")

            f.write("\n" + "=" * 50 + "\n")
            f.write("RESUMO DOS FALANTES:\n")
            for original, mapped in speaker_map.items():
                f.write(f"  {mapped} = {original}\n")

        print(f"[💾] Transcrição salva em: {caminho_txt}")

    def _segmentar_por_pausas(self, segments):
        current_speaker_idx = 1
        speaker_map = {1: "Pessoa1"}

        for i, segment in enumerate(segments):
            if i == 0:
                segment["speaker"] = speaker_map[current_speaker_idx]
                continue

            pausa = segment["start"] - segments[i - 1]["end"]

            if pausa > 2.0:
                current_speaker_idx = 2 if current_speaker_idx == 1 else 1
                if current_speaker_idx not in speaker_map:
                    speaker_map[current_speaker_idx] = f"Pessoa{current_speaker_idx}"
            segment["speaker"] = speaker_map[current_speaker_idx]
