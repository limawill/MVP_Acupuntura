# 🎤 MVP Acupuntura - Sistema de Gravação e Transcrição

Sistema completo para gravação, processamento e transcrição automática de áudios para entrevistas e consultas de acupuntura.

## 📋 Funcionalidades

### 🎙️ **Gravação Inteligente**

- Gravação com controles de **Iniciar**, **Pausar**, **Retomar** e **Parar**
- Sistema de **pause/resume** que gera arquivos separados por sessão
- Combinação automática de múltiplos arquivos em um único `_completo.wav`
- Pré-processamento de áudio com realce de voz e normalização

### 🤖 **Transcrição Automática**

- Transcrição usando **WhisperX** (otimizado e preciso)
- Diarização de falantes com **pyannote.audio**
- Separação automática de falantes (Pessoa1, Pessoa2, etc.)
- Fallback inteligente para segmentação por pausas
- Suporte a múltiplos idiomas (configurável)

### 🖥️ **Interface Gráfica**

- Interface moderna com **CustomTkinter**
- Tela de carregamento com progresso em tempo real
- Feedback visual para todas as operações
- Controles intuitivos de gravação

### 📁 **Estrutura Organizada**

- Pastas automáticas para áudio, transcrição e output
- Nomenclatura padronizada com timestamps
- Arquivos editáveis e bem formatados

## 🚀 Instalação

### 1. **Dependências do Sistema**

**Linux (Ubuntu/Debian):**

```bash
sudo apt update
sudo apt install ffmpeg portaudio19-dev python3-dev build-essential
```

**Linux (Fedora/CentOS):**

```bash
sudo dnf install ffmpeg portaudio-devel python3-devel gcc gcc-c++
```

**macOS:**

```bash
brew install ffmpeg portaudio
```

**Windows:**

- Instale o [ffmpeg](https://ffmpeg.org/download.html)
- Instale o [Microsoft Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

### 2. **Configuração Python**

```bash
# Clonar o repositório
git clone https://github.com/limawill/MVP_Acupuntura.git
cd MVP_Acupuntura

# Criar ambiente virtual
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Ou usar versões compatíveis (recomendado)
pip install -r requirements_fixed.txt
```

### 3. **Configuração de Ambiente**

Crie um arquivo `.env` na raiz do projeto:

```bash
# Configuração WhisperX
WHISPER_MODEL=large
WHISPER_LANGUAGE=pt

# Configuração pastas
FOLDER_AUDIO=src/audio
FOLDER_SCRIPTS=src/scripts
FOLDER_OUTPUT=src/output
FOLDER_TRANSCRICAO=src/transcricao

# Token Hugging Face (para diarização)
HF_TOKEN=seu_token_aqui
```

**Para obter o token Hugging Face:**

1. Acesse [huggingface.co](https://huggingface.co/)
2. Crie uma conta gratuita
3. Vá em Settings > Access Tokens
4. Crie um novo token
5. Aceite os termos do modelo `pyannote/speaker-diarization`

## 🎯 Como Usar

### 1. **Executar o Sistema**

```bash
python3 main.py
```

### 2. **Fluxo de Trabalho**

1. **Iniciar Gravação**: Digite o nome do paciente e clique em "Iniciar"
2. **Controlar Gravação**: Use os botões para pausar/retomar conforme necessário
3. **Parar Gravação**: Finalize quando terminar a consulta
4. **Transcrever**: O sistema processará automaticamente o áudio `_completo.wav`
5. **Resultado**: Encontre a transcrição em `src/transcricao/`

### 3. **Estrutura de Arquivos Gerados**

```
src/
├── audio/
│   ├── Paciente_20250715_140530_parte1.wav
│   ├── Paciente_20250715_140545_parte2.wav
│   └── Paciente_20250715_140600_completo.wav  ← Processado
├── transcricao/
│   ├── Paciente_20250715_140600_completo_transcrito.txt
│   └── Paciente_20250715_140600_completo_transcrito_bruto.txt
└── output/
    └── ...
```

## 🛠️ Estrutura do Projeto

```
MVP_Acupuntura/
├── main.py                      # Ponto de entrada principal
├── requirements.txt             # Dependências padrão
├── requirements_fixed.txt       # Versões compatíveis
├── .env                         # Configurações
├── src/
│   ├── config/                  # Configurações
│   │   ├── __init__.py
│   │   └── warnings_config.py   # Supressão de warnings
│   ├── gui/                     # Interface gráfica
│   │   ├── __init__.py
│   │   ├── tela_inicial.py      # Tela principal
│   │   └── loading_screen.py    # Tela de carregamento
│   ├── setup_audio/             # Sistema de gravação
│   │   ├── __init__.py
│   │   ├── rec_audio.py         # Gravador principal
│   │   └── preprocessador_audio.py  # Processamento
│   ├── tools/                   # Ferramentas
│   │   ├── __init__.py
│   │   ├── setup_folders.py     # Configuração de pastas
│   │   ├── tools_system.py      # Utilidades
│   │   ├── transcricao_whisperx.py  # Transcrição completa
│   │   └── transcricao.py       # Transcrição simples
│   ├── audio/                   # Áudios gravados
│   ├── transcricao/             # Transcrições geradas
│   └── output/                  # Arquivos de saída
└── test/                        # Testes
    ├── teste_gravacao.py
    ├── teste_transcricao_simples.py
    └── ...
```

## 🔧 Configuração Avançada

### **Modelos WhisperX Disponíveis**

- `tiny`: Mais rápido, menor precisão
- `base`: Equilibrado
- `small`: Boa precisão
- `medium`: Melhor precisão
- `large`: Máxima precisão (recomendado)

### **Idiomas Suportados**

- `pt`: Português
- `en`: Inglês
- `es`: Espanhol
- `fr`: Francês
- [Lista completa](https://github.com/openai/whisper#available-models-and-languages)

### **Resolução de Problemas**

#### **Warnings de Compatibilidade**

O sistema inclui supressão automática de warnings conhecidos. Para debug:

```bash
DEBUG=true python3 main.py
SHOW_VERSIONS=true python3 main.py
```

#### **Versões Incompatíveis**

```bash
# Verificar versões
python3 check_versions.py

# Corrigir automaticamente
chmod +x fix_versions.sh
./fix_versions.sh
```

#### **Problemas de Áudio**

```bash
# Testar sistema de áudio
python3 -c "import sounddevice as sd; print(sd.query_devices())"

# Testar gravação
python3 teste_gravacao.py
```

## 📊 Testes

```bash
# Teste completo do sistema
python3 test_system.py

# Teste de gravação
python3 teste_gravacao.py

# Teste de transcrição
python3 teste_transcricao_simples.py

# Teste de estrutura WhisperX
python3 teste_estrutura_whisperx.py
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🆘 Suporte

- **Issues**: [GitHub Issues](https://github.com/limawill/MVP_Acupuntura/issues)
- **Documentação**: Veja os arquivos `.md` na raiz do projeto
- **Logs**: Consulte os logs detalhados durante a execução

## 🎯 Roadmap

- [ ] Suporte a múltiplos formatos de áudio
- [ ] Interface web opcional
- [ ] Integração com sistemas de prontuário
- [ ] Análise de sentimentos
- [ ] Exportação para diferentes formatos
- [ ] Backup automático na nuvem

---

**Desenvolvido com ❤️ para profissionais de acupuntura**

### Fluxo de Trabalho:

```
1. INICIAR GRAVAÇÃO
   ┌─────────────────────────────────────────────────────────────┐
   │ • Limpa audio_data[]                                        │
   │ • Limpa arquivos_gravados[]                                 │
   │ • gravando = True, pausado = False                          │
   │ • Cria stream de áudio                                      │
   │ • Callback só grava se (gravando = True AND pausado = False)│
   └─────────────────────────────────────────────────────────────┘
                                │
                                ▼
2. PAUSAR GRAVAÇÃO
   ┌─────────────────────────────────────────────────────────────┐
   │ • pausado = True (callback para de gravar)                 │
   │ • Salva audio_data atual como arquivo_parte1.wav           │
   │ • Adiciona arquivo à lista arquivos_gravados[]             │
   │ • Limpa audio_data[] para próxima gravação                 │
   │ • Stream continua ativo mas não grava                      │
   └─────────────────────────────────────────────────────────────┘
                                │
                                ▼
3. RETOMAR GRAVAÇÃO
   ┌─────────────────────────────────────────────────────────────┐
   │ • pausado = False (callback volta a gravar)                │
   │ • Continua gravando em audio_data[] limpo                  │
   │ • Não cria novo stream, usa o existente                    │
   └─────────────────────────────────────────────────────────────┘
                                │
                                ▼
4. PARAR GRAVAÇÃO
   ┌─────────────────────────────────────────────────────────────┐
   │ • gravando = False, pausado = False                        │
   │ • Salva audio_data final como arquivo_parteN.wav           │
   │ • Fecha stream                                             │
   │ • Opcional: Combina todos os arquivos em um só             │
   │ • Limpa tudo                                               │
   └─────────────────────────────────────────────────────────────┘
```
