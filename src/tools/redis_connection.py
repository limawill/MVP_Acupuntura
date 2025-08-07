import json
import os
from typing import Optional
import uuid
import redis
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class RedisConnection:
    """Classe para gerenciar conexões com o Redis."""

    def __init__(self):
        """Inicializa a classe carregando variáveis de ambiente."""
        load_dotenv()
        self.config = {
            "host": os.getenv("REDIS_HOST"),
            "port": int(os.getenv("REDIS_PORT", "6379")),
            "db": int(os.getenv("REDIS_DB", "0")),
            "decode_responses": True,  # Retorna strings em vez de bytes
        }
        self.client = None

    def gera_id_usuario(self):
        """Gera um ID único para o usuário."""
        return str(uuid.uuid4())

    def connect(self):
        """Estabelece a conexão com o Redis."""
        try:
            if self.client is None:
                self.client = redis.Redis(**self.config)
                self.client.ping()  # Testa a conexão
                logger.info("Conexão com Redis estabelecida com sucesso.")
            return self.client
        except redis.RedisError as e:
            logger.error("Erro ao conectar ao Redis: %s", e)
            raise

    def disconnect(self):
        """Fecha a conexão com o Redis, se aberta."""
        try:
            if self.client is not None:
                self.client.close()
                self.client = None
                logger.info("Conexão com Redis fechada.")
        except redis.RedisError as e:
            logger.error("Erro ao desconectar do Redis: %s", e)
            raise

    def set_value(self, value: dict, ex: Optional[int] = None) -> str:
        """Define um valor no Redis com chave e expiração opcional (em segundos)."""
        try:
            self.connect()
            if self.client:
                key = self.gera_id_usuario()
                dados_json = json.dumps(value)
                self.client.set(key, dados_json, ex=ex)
                return key
        except redis.RedisError as e:
            logger.error("Erro ao definir valor no Redis: %s", e)
            return ""

    def get_value(self, key):
        """Recupera um valor do Redis pela chave."""
        try:
            self.connect()
            if self.client:
                return self.client.get(key)
        except redis.RedisError as e:
            logger.error("Erro ao recuperar valor do Redis: %s", e)
            raise

    def __enter__(self):
        """Permite uso com 'with' statement."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Garante desconexão ao sair do 'with' statement."""
        self.disconnect()
