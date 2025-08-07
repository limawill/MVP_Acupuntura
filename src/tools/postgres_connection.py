import os
import logging
import psycopg2
from typing import Dict, Any
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class PostgresConnection:
    """Classe para gerenciar conexões com o banco de dados PostgreSQL."""

    def __init__(self):
        """Inicializa a classe carregando variáveis de ambiente."""

        load_dotenv()
        self.config: Dict[str, Any] = {
            "host": os.getenv("POSTGRES_HOST", "localhost"),
            "port": int(os.getenv("POSTGRES_PORT", "5432")),
            "database": os.getenv("POSTGRES_DB", "mvp_acupuntura"),
            "user": os.getenv("POSTGRES_USER", "postgres"),
            "password": os.getenv("POSTGRES_PASSWORD", ""),
        }
        self.connection = None
        self.cursor = None

    def connect_postgres(self):
        """Estabelece a conexão com o PostgreSQL."""
        try:
            if self.connection is None or self.connection.closed:
                self.connection = psycopg2.connect(**self.config)
                self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
                logger.info("Conexão com o PostgreSQL estabelecida com sucesso.")
            return self.connection
        except psycopg2.Error as e:
            logger.error("Erro ao conectar ao PostgreSQL: %s", e)
            return None

    def disconnect_postgres(self):
        """Fecha a conexão e o cursor, se abertos."""
        try:
            if self.cursor is not None:
                self.cursor.close()
                self.cursor = None
            if self.connection is not None and not self.connection.closed:
                self.connection.close()
                self.connection = None
                logger.info("Conexão com PostgreSQL fechada.")
        except psycopg2.Error as e:
            logger.error("Erro ao desconectar do PostgreSQL: %s", e)
            raise

    def execute_query(self, query, params=None):
        """Executa uma query e retorna os resultados."""
        try:
            self.connect_postgres()
            if self.cursor is None:  # Adicione uma verificação de segurança
                raise psycopg2.Error("Cursor não está inicializado após conexão.")

            self.cursor.execute(query, params)
            if query.strip().upper().startswith("SELECT"):
                return self.cursor.fetchall()
            if self.connection:
                self.connection.commit()
            return None
        except psycopg2.Error as e:
            logger.error("Erro ao executar query:  %s", e)
            if self.connection:
                self.connection.rollback()
            raise
        finally:
            self.disconnect_postgres()

    def __enter__(self):
        """Permite uso com 'with' statement."""
        self.connect_postgres()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Garante desconexão ao sair do 'with' statement."""
        self.disconnect_postgres()
