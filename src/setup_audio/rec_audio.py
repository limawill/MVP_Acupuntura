import os
from pydub import AudioSegment
import numpy as np
import sounddevice as sd
from datetime import datetime
import scipy.io.wavfile as wavfile
from ..tools.tools_system import SetupSystem
from .preprocessador_audio import PreprocessadorAudio


system_control = SetupSystem()


class GravadorAudio:
    def __init__(self, taxa_amostragem=44100, canais=1):
        self.fs = taxa_amostragem
        self.canais = canais
        self.gravando = False
        self.audio_data = []
        self.stream = None
        self.nome_paciente = None
        self.output_dir = os.getenv("FOLDER_AUDIO", "audio")

    def iniciar_gravacao(self, nome_paciente: str):
        if self.gravando:
            print("[!] Já está gravando.")
            return

        self.nome_paciente = system_control.text_underline(nome_paciente)
        self.audio_data = []
        self.gravando = True

        def callback(indata, frames, time, status):
            if self.gravando:
                self.audio_data.append(indata.copy())

        self.stream = sd.InputStream(
            samplerate=self.fs, channels=self.canais, dtype="int16", callback=callback
        )
        self.stream.start()
        print("[✅] Gravação iniciada com sucesso.")

    def pausar_gravacao(self):
        if not self.gravando:
            print("[!] Não está gravando para pausar.")
            return

        self.gravando = False
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        # Salvar o áudio capturado
        self._salvar_audio()
        print("[⏸️] Gravação pausada.")

    def retomar_gravacao(self, nome_paciente: str):
        if self.gravando:
            print("[!] Já está gravando.")
            return

        self.nome_paciente = nome_paciente
        self.gravando = True

        def callback(indata, frames, time, status):
            if self.gravando:
                self.audio_data.append(indata.copy())

        self.stream = sd.InputStream(
            samplerate=self.fs, channels=self.canais, dtype="int16", callback=callback
        )
        self.stream.start()
        print("[▶️] Gravação retomada com sucesso.")

    def parar_gravacao(self, nome_paciente: str):
        if not self.gravando:
            print("[!] Não está gravando para parar.")
            return

        self.gravando = False
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        # Salvar o áudio capturado
        self._salvar_audio()
        self.audio_data = []  # Limpar dados após salvar
        print("[⏹️] Gravação parada.")
        # self._combinar_audio(nome_paciente)

    def _salvar_audio(self):
        if not self.audio_data:
            print("[!] Nenhum áudio para salvar.")
            return

        # Concatenar os dados de áudio
        audio_array = np.concatenate(self.audio_data, axis=0)

        # Gerar nome do arquivo com paciente e timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"{self.nome_paciente}_{timestamp}.wav"
        caminho_arquivo = os.path.join(self.output_dir, nome_arquivo)

        # Salvar como arquivo WAV
        wavfile.write(caminho_arquivo, self.fs, audio_array)
        print(f"[💾] Áudio salvo em: {caminho_arquivo}")

    def _combinar_audio(self, nome_paciente: str):
        """
        Combina dois arrays de áudio.
        """
        # pre_audio = PreprocessadorAudio()
        arquivos = [
            os.path.join(self.output_dir, f)
            for f in os.listdir(self.output_dir)
            if f.endswith(".wav")
        ]
        print(arquivos)
        arquivos.sort()  # Ordenar os arquivos para garantir a ordem correta
        print(arquivos)
