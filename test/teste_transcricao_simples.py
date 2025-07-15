#!/usr/bin/env python3
"""
Teste simples para verificar funcionamento da transcrição corrigida
"""

import sys
import os
import warnings
sys.path.append('/media/Dados/MVP_Acupuntura')

# Suprimir warnings
warnings.filterwarnings("ignore")

print("🧪 TESTE SIMPLES DA TRANSCRIÇÃO CORRIGIDA")
print("=" * 50)

try:
    from src.tools.transcricao import TranscricaoAudio
    
    # Criar instância
    t = TranscricaoAudio()
    print("✅ Instância criada com sucesso")
    
    # Verificar arquivos
    arquivos = os.listdir(t.folder_audio)
    completos = [f for f in arquivos if '_completo' in f]
    
    print(f"📁 Pasta: {t.folder_audio}")
    print(f"🎵 Arquivos _completo: {completos}")
    
    if completos:
        print(f"✅ Pronto para transcrever: {completos[0]}")
    else:
        print("⚠️  Nenhum arquivo _completo encontrado")
        
    print("\n🎯 Para testar a transcrição, execute:")
    print("python3 main.py")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
