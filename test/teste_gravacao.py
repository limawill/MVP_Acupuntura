#!/usr/bin/env python3
"""
Teste da lógica de gravação com pause/resume
"""

import sys
import time
sys.path.append('/media/Dados/MVP_Acupuntura')

from src.setup_audio.rec_audio import GravadorAudio


def teste_gravacao():
    """Testa a lógica de gravação, pause e resume"""
    
    print("🧪 TESTE DA LÓGICA DE GRAVAÇÃO")
    print("=" * 50)
    
    # Criar gravador
    gravador = GravadorAudio()
    nome_paciente = "Teste_Usuario"
    
    # Teste 1: Iniciar gravação
    print("\n1. Iniciando gravação...")
    gravador.iniciar_gravacao(nome_paciente)
    print(f"Status: {gravador.get_status()}")
    print(f"Stats: {gravador.get_stats()}")
    
    # Simular gravação por 2 segundos
    print("Simulando gravação por 2 segundos...")
    time.sleep(2)
    
    # Teste 2: Pausar gravação
    print("\n2. Pausando gravação...")
    gravador.pausar_gravacao()
    print(f"Status: {gravador.get_status()}")
    print(f"Stats: {gravador.get_stats()}")
    
    # Teste 3: Tentar pausar novamente (deve dar erro)
    print("\n3. Tentando pausar novamente...")
    gravador.pausar_gravacao()
    
    # Teste 4: Retomar gravação
    print("\n4. Retomando gravação...")
    gravador.retomar_gravacao(nome_paciente)
    print(f"Status: {gravador.get_status()}")
    print(f"Stats: {gravador.get_stats()}")
    
    # Simular mais gravação
    print("Simulando mais gravação por 2 segundos...")
    time.sleep(2)
    
    # Teste 5: Parar gravação
    print("\n5. Parando gravação...")
    gravador.parar_gravacao(nome_paciente)
    print(f"Status: {gravador.get_status()}")
    print(f"Stats: {gravador.get_stats()}")
    
    # Teste 6: Limpar sessão
    print("\n6. Limpando sessão...")
    gravador.limpar_sessao()
    print(f"Stats: {gravador.get_stats()}")
    
    print("\n✅ Teste da lógica concluído!")


if __name__ == "__main__":
    teste_gravacao()
