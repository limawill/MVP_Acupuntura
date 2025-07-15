#!/usr/bin/env python3
"""
Teste para verificar a busca por arquivos _completo.wav
"""

import os
import sys
sys.path.append('/media/Dados/MVP_Acupuntura')

from src.tools.transcricao_whisperx import TranscricaoAudio


def teste_busca_arquivos():
    """Testa se o sistema está buscando apenas arquivos _completo.wav"""
    
    print("🧪 TESTE DA BUSCA POR ARQUIVOS _completo.wav")
    print("=" * 60)
    
    # Criar instância do transcritor
    transcritor = TranscricaoAudio()
    
    # Verificar pasta de áudio
    pasta_audio = transcritor.folder_audio
    print(f"📁 Pasta de áudio: {pasta_audio}")
    
    if not os.path.exists(pasta_audio):
        print(f"❌ Pasta {pasta_audio} não existe!")
        return
    
    # Listar todos os arquivos .wav
    todos_wav = [f for f in os.listdir(pasta_audio) if f.endswith('.wav')]
    print(f"\n📄 Todos os arquivos .wav ({len(todos_wav)}):")
    for i, arquivo in enumerate(todos_wav, 1):
        print(f"  {i}. {arquivo}")
    
    # Listar apenas arquivos _completo.wav
    arquivos_completo = [f for f in os.listdir(pasta_audio) if f.endswith('_completo.wav')]
    print(f"\n🎯 Arquivos _completo.wav ({len(arquivos_completo)}):")
    for i, arquivo in enumerate(arquivos_completo, 1):
        print(f"  {i}. {arquivo}")
    
    # Verificar se há arquivos para transcrever
    if arquivos_completo:
        print(f"\n✅ Sistema vai processar {len(arquivos_completo)} arquivo(s):")
        for arquivo in arquivos_completo:
            print(f"  - {arquivo}")
    else:
        print(f"\n⚠️ Nenhum arquivo _completo.wav encontrado!")
        print("💡 Dica: Execute uma gravação completa para gerar o arquivo _completo.wav")
        
        if todos_wav:
            print("\n🔍 Arquivos .wav disponíveis que NÃO serão processados:")
            for arquivo in todos_wav:
                if not arquivo.endswith('_completo.wav'):
                    print(f"  - {arquivo}")


if __name__ == "__main__":
    teste_busca_arquivos()
