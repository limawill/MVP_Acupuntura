import os
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt
from pydub import AudioSegment


class PreprocessadorAudio:
    """
    Classe simples para realce de voz em gravações de entrevistas.
    Foca apenas em melhorar a clareza da voz humana.
    """

    def __init__(self):
        pass

    def processar(self, caminho_audio: str) -> str:
        """
        Processa o áudio para realçar a voz humana.

        Args:
            caminho_audio (str): Caminho do arquivo original WAV.

        Returns:
            str: Caminho do arquivo processado.
        """
        if not os.path.exists(caminho_audio):
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho_audio}")

        print(f"[🎤] Processando voz: {caminho_audio}")
        nome, ext = os.path.splitext(caminho_audio)
        caminho_saida = f"{nome}_normalizado{ext}"

        try:
            # 1. Carregar áudio
            data, rate = sf.read(caminho_audio)
            
            # Converter para mono se necessário
            if len(data.shape) > 1:
                data = np.mean(data, axis=1)
            
            print(f"[📊] Taxa: {rate}Hz, Duração: {len(data)/rate:.1f}s")
            
            # 2. Aplicar filtro para realce de voz
            print("[�] Realçando frequências da voz...")
            voz_realcada = self._realcar_voz(data, rate)
            
            # 3. Normalização suave
            print("[📢] Ajustando volume...")
            voz_normalizada = self._normalizar_suave(voz_realcada)
            
            # 4. Salvar
            sf.write(caminho_saida, voz_normalizada, rate)
            
            print(f"[✅] Voz realçada salva em: {caminho_saida}")
            return caminho_saida
            
        except Exception as e:
            print(f"[❌] Erro: {e}")
            # Copia o original se der erro
            import shutil
            shutil.copy2(caminho_audio, caminho_saida)
            return caminho_saida

    def _realcar_voz(self, data, rate):
        """
        Aplica filtros para realçar a voz humana (300-3400 Hz).
        """
        # Filtro passa-faixa para voz
        voz_filtrada = self._filtro_voz(data, rate, 300, 3400)
        
        # Realce adicional na faixa crítica da voz (1000-2000 Hz)
        realce = self._filtro_realce(data, rate, 1000, 2000)
        
        # Combinar: 70% filtro principal + 30% realce
        resultado = 0.7 * voz_filtrada + 0.3 * realce
        
        return resultado

    def _filtro_voz(self, data, rate, freq_baixa, freq_alta):
        """
        Filtro passa-faixa para isolar frequências da voz.
        """
        nyq = rate / 2
        low = freq_baixa / nyq
        high = freq_alta / nyq
        
        # Usar SOS (Second-Order Sections) - mais estável
        sos = butter(4, [low, high], btype='band', output='sos')
        filtrado = sosfilt(sos, data)
        
        return filtrado

    def _filtro_realce(self, data, rate, freq_baixa, freq_alta):
        """
        Filtro para realçar frequências específicas da voz.
        """
        nyq = rate / 2
        low = freq_baixa / nyq
        high = freq_alta / nyq
        
        # Filtro mais suave para realce
        sos = butter(2, [low, high], btype='band', output='sos')
        realcado = sosfilt(sos, data)
        
        return realcado

    def _normalizar_suave(self, data):
        """
        Normalização suave para não distorcer.
        """
        # Encontrar o pico
        peak = np.max(np.abs(data))
        
        if peak == 0:
            return data
        
        # Normalizar para 70% do máximo (-3dB aproximadamente)
        target = 0.7
        normalized = data * (target / peak)
        
        # Aplicar compressão suave nos picos
        threshold = 0.8
        mask = np.abs(normalized) > threshold
        normalized[mask] = np.sign(normalized[mask]) * (
            threshold + (np.abs(normalized[mask]) - threshold) * 0.3
        )
        
        return normalized
