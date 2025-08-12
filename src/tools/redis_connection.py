import os
import json
import uuid
import redis
import logging
from dotenv import load_dotenv
from typing import Optional, cast

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
                dados_json = json.dumps(value, ensure_ascii=False)
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
                valor = self.client.get(key)
                if valor is not None:
                    # Garante que o valor é decodificado de bytes para string
                    if isinstance(valor, bytes):
                        valor_str = valor.decode("utf-8")
                    else:
                        valor_str = str(valor)  # Caso já seja string por algum motivo
                    return json.loads(valor_str)
                return None
        except (redis.RedisError, json.JSONDecodeError) as e:
            logger.error("Erro ao recuperar ou desserializar valor do Redis: %s", e)
            raise

    def delete_key(self, key_uuid: str) -> int:
        """
        Deleta uma chave específica do Redis.

        Args:
            key_uuid (str): A chave a ser deletada.

        Returns:
            int: O número de chaves deletadas (0 ou 1).
        """
        try:
            self.connect()
            if self.client is None:
                logger.error("Erro: Cliente Redis não inicializado.")
                return 0
            return cast(int, self.client.delete(key_uuid))
        except redis.RedisError as e:
            logger.error("Erro ao deletar a chave %s do Redis: %s", key_uuid, e)
            return 0  # Retorna 0 se houver erro
        finally:
            self.disconnect()

    def update_value(self, key: str, dados: dict) -> bool:
        """
        Atualiza um valor no Redis adicionando novos pares chave-valor
        ao hash existente, sem perder dados anteriores.

        Args:
            key (str): Chave do hash no Redis.
            dados (dict): Dicionário com novos pares chave-valor a serem adicionados.

        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário.
        """
        try:
            self.connect()
            if self.client:
                # Recupera o valor existente (se houver)
                valor_existente = self.client.get(key)
                if valor_existente is not None:
                    if isinstance(valor_existente, bytes):
                        valor_existente = valor_existente.decode("utf-8")
                    elif not isinstance(valor_existente, str):
                        logger.warning(
                            f"Tipo inesperado para valor existente: {type(valor_existente)}. Convertendo para string."
                        )
                        valor_existente = str(valor_existente)
                    dados_existentes = json.loads(valor_existente)
                else:
                    dados_existentes = {}

                # Mescla os dicionários, preservando os dados existentes
                dados_atualizados = {**dados_existentes, **dados}

                # Salva o dicionário atualizado de volta no Redis
                self.client.set(key, json.dumps(dados_atualizados, ensure_ascii=False))
                logger.info(
                    f"Hash atualizado no Redis para chave {key}: {list(dados_atualizados.keys())[:5]}..."
                )
                return True
        except (redis.RedisError, json.JSONDecodeError) as e:
            logger.error(f"Erro ao atualizar valor no Redis para chave {key}: {e}")
            return False

    def __enter__(self):
        """Permite uso com 'with' statement."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Garante desconexão ao sair do 'with' statement."""
        self.disconnect()
