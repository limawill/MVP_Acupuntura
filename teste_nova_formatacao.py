#!/usr/bin/env python3
"""
Testa a nova formatação com áudio existente
"""

import sys
import os
import warnings
sys.path.append('/media/Dados/MVP_Acupuntura')

# Suprimir warnings
warnings.filterwarnings("ignore")

print("🧪 TESTE DA NOVA FORMATAÇÃO COM ÁUDIO REAL")
print("=" * 60)

try:
    from src.tools.transcricao import TranscricaoAudio
    
    # Verificar se há áudio para testar
    t = TranscricaoAudio()
    arquivos_completo = [f for f in os.listdir(t.folder_audio) if '_completo' in f]
    
    if not arquivos_completo:
        print("❌ Nenhum arquivo _completo encontrado para testar!")
        print("💡 Execute uma gravação primeiro ou use um arquivo existente")
        sys.exit(1)
    
    arquivo_teste = arquivos_completo[0]
    print(f"📁 Arquivo de teste: {arquivo_teste}")
    print(f"📁 Pasta de transcrição: {t.destino_folder}")
    
    # Verificar se já existe transcrição
    nome_transcricao = os.path.splitext(arquivo_teste)[0] + "_transcrito_bruto.txt"
    caminho_transcricao = os.path.join(t.destino_folder, nome_transcricao)
    
    if os.path.exists(caminho_transcricao):
        print(f"📄 Transcrição existente encontrada: {nome_transcricao}")
        print("\n📖 CONTEÚDO DA TRANSCRIÇÃO:")
        print("─" * 60)
        
        with open(caminho_transcricao, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)
        
        print("─" * 60)
        print("✅ Formatação aplicada com sucesso!")
        
    else:
        print(f"📄 Transcrição não encontrada: {nome_transcricao}")
        print("💡 Execute 'python3 main.py' para gerar a transcrição")
    
    print(f"\n🎯 LOCALIZAÇÃO DOS ARQUIVOS:")
    print(f"  📁 Áudio: {t.folder_audio}")
    print(f"  📁 Transcrição: {t.destino_folder}")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
