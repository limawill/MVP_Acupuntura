import os
import logging
from logging.handlers import (
    RotatingFileHandler,
)  # <-- Importação para rotação de arquivos


def setup_logging():
    """
    Configura o sistema de log da aplicação.
    Logs serão escritos em 'logs/app_log.log' e também exibidos no console.
    """
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, "mvp_acupuntura.log")

    # Obter o logger raiz. Isso garante que a configuração afete todos os loggers.
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)  # Nível mínimo para todo o sistema de log

    # Limpa handlers existentes para evitar duplicação em chamadas múltiplas (útil em testes)
    if root_logger.handlers:
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

    # Formato das mensagens de log
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s -> %(name)s - %(filename)s -> %(message)s",
        datefmt="%Y-%m-%d %H:%M",
    )

    # --- Handler para o arquivo de log com rotação ---
    # RotatingFileHandler: cria um novo arquivo quando o log atinge um certo tamanho
    # e mantém um número limitado de arquivos antigos.
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=5 * 1024 * 1024,  # 5 MB por arquivo
        backupCount=5,  # Mantém 5 arquivos de backup (total de 6 arquivos: 1 ativo + 5 backups)
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)  # Nível para o arquivo de log
    root_logger.addHandler(file_handler)

    # --- Handler para o console (StreamHandler) ---
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)  # Usa o mesmo formato para consistência
    console_handler.setLevel(logging.INFO)  # Nível para o console
    root_logger.addHandler(console_handler)

    # Opcional: Para capturar logs de bibliotecas de terceiros (como requests, urllib3, etc.)
    # Se você quiser suprimir logs muito verbosos de bibliotecas, pode fazer assim:
    # logging.getLogger('urllib3').setLevel(logging.NÃO_LOG) # ou logging.WARNING, logging.ERROR
    # logging.getLogger('requests').setLevel(logging.NÃO_LOG)

    # Log de confirmação da configuração
    logging.getLogger(__name__).info("Sistema de log configurado.")
