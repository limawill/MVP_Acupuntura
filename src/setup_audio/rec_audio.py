import os
import numpy as np
import sounddevice as sd
from datetime import datetime
from pydub import AudioSegment
import scipy.io.wavfile as wavfile
from src.tools.tools_system import SetupSystem


system_control = SetupSystem()


class GravadorAudio:
    def __init__(self, taxa_amostragem=44100, canais=1):
        self.fs = taxa_amostragem
        self.canais = canais
        self.gravando = False
        self.pausado = False
        self.audio_data = []
        self.stream = None
        self.nome_paciente = None
        self.output_dir = os.getenv("FOLDER_AUDIO", "audio")
        self.arquivos_gravados = []  # Lista de arquivos da sessão

    def iniciar_gravacao(self, nome_paciente: str):
        if self.gravando:
            print("[!] Já está gravando.")
            return

        self.nome_paciente = system_control.text_underline(nome_paciente)
        self.audio_data = []  # Limpar dados anteriores
        self.pausado = False
        self.arquivos_gravados = []  # Reset da lista de arquivos
        self.gravando = True

        def callback(indata, frames, time, status):
            if self.gravando and not self.pausado:
                self.audio_data.append(indata.copy())

        self.stream = sd.InputStream(
            samplerate=self.fs, channels=self.canais, dtype="int16", callback=callback
        )
        self.stream.start()
        print(f"[✅] Gravação iniciada para {nome_paciente}.")

    def pausar_gravacao(self):
        if not self.gravando:
            print("[!] Não está gravando para pausar.")
            return

        if self.pausado:
            print("[!] Já está pausado.")
            return

        self.pausado = True

        # Salvar o áudio capturado até agora
        arquivo_salvo = self._salvar_audio()
        if arquivo_salvo:
            self.arquivos_gravados.append(arquivo_salvo)

        # Limpar buffer para próxima gravação
        self.audio_data = []
        print("[⏸️] Gravação pausada e áudio salvo.")

    def retomar_gravacao(self, nome_paciente: str):
        if not self.gravando:
            print("[!] Não está gravando para retomar.")
            return

        if not self.pausado:
            print("[!] Não está pausado para retomar.")
            return

        self.pausado = False
        print("[▶️] Gravação retomada com sucesso.")

    def parar_gravacao(self, nome_paciente: str):
        if not self.gravando:
            print("[!] Não está gravando para parar.")
            return

        self.gravando = False
        self.pausado = False

        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        # Salvar o áudio final se houver dados
        if self.audio_data:
            arquivo_salvo = self._salvar_audio()
            if arquivo_salvo:
                self.arquivos_gravados.append(arquivo_salvo)

        # Limpar dados após salvar
        self.audio_data = []
        print(f"[⏹️] Gravação parada. {len(self.arquivos_gravados)} arquivos salvos.")

        # Opcionalmente combinar todos os arquivos em um só
        if len(self.arquivos_gravados) > 1:
            print("[🔄] Combinando arquivos...")
            self._combinar_audio(nome_paciente)
        else:
            caminho_arquivo_original = self.arquivos_gravados[0]

            # Verificar se o arquivo existe
            if not os.path.exists(caminho_arquivo_original):
                print(f"[❌] Arquivo único não encontrado: {caminho_arquivo_original}")
                return None

            print("[✅] Apenas um arquivo de áudio encontrado. Renomeando...")

            # Gerar o novo nome com '_completo' e o timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_tratado = system_control.text_underline(nome_paciente)

            # Separar o nome do arquivo da extensão para adicionar o sufixo
            nome_base, extensao = os.path.splitext(
                os.path.basename(caminho_arquivo_original)
            )

            novo_nome = f"{nome_tratado}_{timestamp}_completo.wav"
            novo_caminho = os.path.join(self.output_dir, novo_nome)

            # Renomear o arquivo
            try:
                os.rename(caminho_arquivo_original, novo_caminho)
                print(f"[✅] Áudio renomeado e salvo em: {novo_caminho}")
                return novo_caminho
            except OSError as e:
                print(f"[❌] Erro ao renomear o arquivo: {e}")
                return None

    def _salvar_audio(self):
        if not self.audio_data:
            print("[!] Nenhum áudio para salvar.")
            return None

        # Concatenar os dados de áudio
        audio_array = np.concatenate(self.audio_data, axis=0)

        # Gerar nome do arquivo com paciente e timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        parte = len(self.arquivos_gravados) + 1
        nome_arquivo = f"{self.nome_paciente}_{timestamp}_parte{parte}.wav"
        caminho_arquivo = os.path.join(self.output_dir, nome_arquivo)

        # Salvar como arquivo WAV
        wavfile.write(caminho_arquivo, self.fs, audio_array)
        print(f"[💾] Áudio salvo em: {caminho_arquivo}")
        return caminho_arquivo

    def _combinar_audio(self, nome_paciente: str):
        """
        Combina múltiplos arquivos de áudio em um único arquivo.
        """
        if not self.arquivos_gravados:
            print("[!] Nenhum arquivo para combinar.")
            return

        print(f"[🔄] Combinando {len(self.arquivos_gravados)} arquivos...")

        # Carregar todos os arquivos
        segmentos = []
        for arquivo in self.arquivos_gravados:
            if os.path.exists(arquivo):
                segmento = AudioSegment.from_wav(arquivo)
                segmentos.append(segmento)
                print(f"[📂] Carregado: {os.path.basename(arquivo)}")
            else:
                print(f"[❌] Arquivo não encontrado: {arquivo}")

        if not segmentos:
            print("[❌] Nenhum segmento válido para combinar.")
            return

        # Combinar todos os segmentos
        audio_combinado = segmentos[0]
        for segmento in segmentos[1:]:
            audio_combinado += segmento

        # Salvar arquivo combinado
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_tratado = system_control.text_underline(nome_paciente)
        nome_combinado = f"{nome_tratado}_{timestamp}_completo.wav"
        caminho_combinado = os.path.join(self.output_dir, nome_combinado)

        audio_combinado.export(caminho_combinado, format="wav")
        print(f"[✅] Áudio combinado salvo em: {caminho_combinado}")

        # Opcional: remover arquivos individuais
        # for arquivo in self.arquivos_gravados:
        #     if os.path.exists(arquivo):
        #         os.remove(arquivo)
        #         print(f"[🗑️] Removido: {os.path.basename(arquivo)}")

        return caminho_combinado

    def get_status(self):
        """Retorna o status atual da gravação."""
        if not self.gravando:
            return "parado"
        elif self.pausado:
            return "pausado"
        else:
            return "gravando"

    def get_stats(self):
        """Retorna estatísticas da gravação atual."""
        return {
            "status": self.get_status(),
            "arquivos_gravados": len(self.arquivos_gravados),
            "duracao_buffer": len(self.audio_data) / self.fs if self.audio_data else 0,
            "nome_paciente": self.nome_paciente,
        }

    def limpar_sessao(self):
        """Limpa todos os dados da sessão atual."""
        if self.gravando:
            print("[!] Pare a gravação antes de limpar a sessão.")
            return

        self.audio_data = []
        self.arquivos_gravados = []
        self.nome_paciente = None
        self.pausado = False
        print("[🧹] Sessão limpa com sucesso.")
