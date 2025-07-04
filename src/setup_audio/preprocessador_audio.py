import os
import numpy as np
import soundfile as sf
import noisereduce as nr
from scipy.signal import butter, lfilter
from pydub import AudioSegment, effects, silence


class PreprocessadorAudio:
    """
    Pipeline completo de pré-processamento de áudio:
    1. Redução de ruído
    2. Normalização de volume
    3. (Opcional) Corte de silêncios
    4. (Opcional) Realce da faixa vocal com filtro passa-faixa
    """

    def __init__(self, cortar_silencios=False, realce_vocal=False):
        self.cortar_silencios = cortar_silencios
        self.realce_vocal = realce_vocal

    def processar(self, caminho_audio: str) -> str:
        """
        Processa o áudio e salva no mesmo local com sufixo _normalizado.wav

        Args:
            caminho_audio (str): Caminho do arquivo original WAV.

        Returns:
            str: Caminho do arquivo processado.
        """
        if not os.path.exists(caminho_audio):
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho_audio}")

        print(f"[🔊] Pré-processando: {caminho_audio}")
        nome, ext = os.path.splitext(caminho_audio)
        caminho_saida = f"{nome}_normalizado{ext}"

        # 1. Redução de ruído
        data, rate = sf.read(caminho_audio)
        reduzido = nr.reduce_noise(y=data, sr=rate)

        # 2. Normalização (via pydub)
        temp_wav = nome + "_temp.wav"
        sf.write(temp_wav, reduzido, rate)
        audio = AudioSegment.from_wav(temp_wav)
        audio = effects.normalize(audio)

        # 3. (Opcional) Corte de silêncios
        if self.cortar_silencios:
            partes = silence.split_on_silence(
                audio, min_silence_len=500, silence_thresh=-40
            )
            if partes:
                audio = sum(partes)

        # 4. (Opcional) Realce vocal com filtro passa-faixa
        if self.realce_vocal:
            samples = np.array(audio.get_array_of_samples()).astype(np.float32)
            samples = self._filtro_passa_faixa(samples, rate, 300, 3400)
            sf.write(caminho_saida, samples, rate)
        else:
            audio.export(caminho_saida, format="wav")

        os.remove(temp_wav)
        print(f"[✅] Áudio salvo em: {caminho_saida}")
        return caminho_saida

    def _filtro_passa_faixa(self, dados, taxa, lowcut, highcut, ordem=5):
        """
        Aplica um filtro bandpass na faixa vocal (300–3400 Hz).
        """
        nyq = 0.5 * taxa
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(ordem, [low, high], btype="band")
        return lfilter(b, a, dados)
