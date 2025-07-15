#!/usr/bin/env python3
"""
Teste específico para verificar estrutura do resultado WhisperX
"""

import sys
import os
import warnings
sys.path.append('/media/Dados/MVP_Acupuntura')

# Suprimir warnings
warnings.filterwarnings("ignore")

from src.tools.transcricao import TranscricaoAudio
import whisperx
import torch

def testar_estrutura_resultado():
    """Testa a estrutura do resultado do WhisperX"""
    
    print("🧪 TESTE DA ESTRUTURA DO RESULTADO WHISPERX")
    print("=" * 60)
    
    # Verificar arquivos disponíveis
    t = TranscricaoAudio()
    arquivos_completo = [f for f in os.listdir(t.folder_audio) if '_completo' in f]
    
    print(f"📁 Pasta de áudio: {t.folder_audio}")
    print(f"🎵 Arquivos _completo encontrados: {arquivos_completo}")
    
    if not arquivos_completo:
        print("❌ Nenhum arquivo _completo encontrado para testar!")
        return
    
    arquivo_teste = arquivos_completo[0]
    caminho_arquivo = os.path.join(t.folder_audio, arquivo_teste)
    
    print(f"\n🔍 Testando com arquivo: {arquivo_teste}")
    
    try:
        # Carregar modelo
        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"
        
        print(f"⚙️  Carregando modelo {t.model_name} no {device}...")
        model = whisperx.load_model(
            t.model_name,
            device=device,
            compute_type=compute_type,
            language=t.language,
        )
        
        print("📻 Carregando áudio...")
        audio = whisperx.load_audio(caminho_arquivo)
        
        print("🎤 Transcrevendo (teste)...")
        result = model.transcribe(audio, batch_size=16)
        
        print("📊 ESTRUTURA DO RESULTADO:")
        print(f"Tipo: {type(result)}")
        print(f"Chaves: {list(result.keys()) if isinstance(result, dict) else 'Não é dict'}")
        
        if isinstance(result, dict):
            for key, value in result.items():
                print(f"  {key}: {type(value)} - {len(value) if hasattr(value, '__len__') else 'N/A'}")
                
                # Se for segments, mostrar estrutura do primeiro
                if key == 'segments' and isinstance(value, list) and len(value) > 0:
                    print(f"    Primeiro segment: {list(value[0].keys())}")
        
        print("\n✅ Teste concluído!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    testar_estrutura_resultado()
