import os
import re
import json
import ollama
import logging
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Optional
from src.tools.redis_connection import RedisConnection


logger = logging.getLogger(__name__)
redis = RedisConnection()


class OllamaClient:
    """
    Cliente para interagir com o servidor Ollama.
    Configurado para usar o modelo deepseek-r1 por padrão.
    """

    def __init__(self):
        # Carregar variáveis de ambiente
        load_dotenv()
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.client = ollama.Client(host=self.ollama_url)
        self.model_name = os.getenv("MODEL_NAME", "deepseek-r1")

    def _converte_transcricao(self, transcricao: Path) -> str:
        """Converte o conteúdo do arquivo de transcrição em uma string.

        Args:
            transcricao (Path): Caminho do arquivo com a transcrição.

        Returns:
            str: Conteúdo da transcrição.

        Raises:
            FileNotFoundError: Se o arquivo não existir.
            ValueError: Se o arquivo estiver vazio.
        """
        if not transcricao.is_file():
            raise FileNotFoundError(
                f"Arquivo de transcrição não encontrado: {transcricao}"
            )
        with open(transcricao, "r", encoding="utf-8") as f:
            conteudo_transcricao = f.read().strip()
        if not conteudo_transcricao:
            raise ValueError(f"Transcrição em {transcricao} está vazia.")
        return conteudo_transcricao

    def _converte_perguntas(self, caminho_perguntas: Path) -> str:
        """Converte o conteúdo do arquivo de perguntas em uma string formatada.

        Args:
            caminho_perguntas (Path): Caminho do arquivo JSON com as perguntas.

        Returns:
            str: Perguntas formatadas como **Pergunta:** [texto].

        Raises:
            FileNotFoundError: Se o arquivo não existir.
            ValueError: Se o arquivo for inválido ou vazio.
        """
        if not caminho_perguntas.is_file():
            raise FileNotFoundError(
                f"Arquivo de perguntas não encontrado: {caminho_perguntas}"
            )
        with open(caminho_perguntas, "r", encoding="utf-8") as f:
            dados_perguntas = json.load(f)
        if not dados_perguntas or not isinstance(dados_perguntas, dict):
            raise ValueError(
                f"Arquivo de perguntas em {caminho_perguntas} é inválido ou vazio."
            )
        perguntas_formatadas = "\n".join(
            f"**Pergunta:** {dados['pergunta']}"
            for id_pergunta, dados in dados_perguntas.items()
        )
        return perguntas_formatadas.strip()

    def _converte_questionario(self, key_redis: str) -> str:
        """
        Recupera um questionário do Redis e o converte em uma string JSON formatada.

        Args:
            key_redis (str): A chave do Redis para o questionário.

        Returns:
            str: O dicionário do questionário em formato de string JSON.

        Raises:
            ValueError: Se o questionário não for encontrado no Redis.
        """
        questionario = redis.get_value(key_redis)
        if not questionario:
            logger.error(f"Questionário não encontrado para o UUID: {key_redis}")
            raise ValueError(f"Questionário não encontrado para o UUID: {key_redis}")

        # Converte o dicionário em uma string JSON formatada
        # `indent=2` para legibilidade e `ensure_ascii=False` para caracteres especiais
        questionario_string = json.dumps(questionario, indent=2, ensure_ascii=False)

        return questionario_string

    def _monta_mensagem_relatorio(self, key_redis: str) -> str:
        conteudo_questionario_json = self._converte_questionario(key_redis)

        instrucoes = f"""
        **CONTEXTO:**
        Você é um assistente de IA especializado em gerar relatórios de pacientes para 
        consultas de acupuntura.
        Sua tarefa é criar um relatório profissional e conciso com base em dados de um 
        questionário validado.

        **INSTRUÇÕES:**
        1.  **Fonte de Dados:** Utilize **exclusivamente** as informações fornecidas no dicionário JSON abaixo. Ignore qualquer conhecimento externo.
        2.  **Formato do Relatório:** O relatório deve ser organizado em seções lógicas para facilitar a leitura.
        3.  **Análise Adicional:** Você tem permissão para incluir suas impressões ou análises baseadas em Medicina Tradicional Chinesa (MTC), mas **TODA e QUALQUER** informação que seja uma interpretação sua (ou seja, não esteja explicitamente no JSON) deve ser marcada com colchetes `[ ]`.
        4.  **Respostas NDA:** Ignore as perguntas cujas respostas são "NDA".

        ---

        **MODELO DE RELATÓRIO:**

        **RELATÓRIO DO PACIENTE**

        **1. Dados Pessoais:**
        - **Nome:** [Resposta para a pergunta "Qual seu nome completo?"]
        - **Idade:** [Resposta para a pergunta "Qual a idade atual do paciente?"]
        - **Gênero:** [Resposta para a pergunta "Qual é o gênero do paciente?"]
        - **Ocupação:** [Resposta para a pergunta "Qual é a ocupação/profissão do paciente?"]

        **2. Queixas Principais e Sintomas:**
        - [Resuma a resposta da pergunta "Descreva em detalhes os sintomas e problemas relatados pelo paciente.".]
        - [Inclua a intensidade da dor, se houver na resposta "Qual a intensidade da dor na escala EVA (0-10)?"]

        **3. Histórico de Saúde:**
        - **Saúde Familiar:** [Resuma as respostas sobre o histórico de saúde da família.]
        - **Uso de Medicamentos:** [Resposta da pergunta "Quais medicamentos, fitoterápicos, florais ou outros produtos o paciente está usando atualmente?"]

        **4. Análise e Observações (MTC):**
        - [Use a resposta da pergunta "Outras Informações" para incluir detalhes relevantes.]
        - [Inclua suas impressões com base nos dados fornecidos, marcadas com colchetes `[ ]`.]

        ---

        **DADOS DO QUESTIONÁRIO EM JSON:**
        {conteudo_questionario_json}
        """

        mensagem = f"{instrucoes.strip()}"

        return mensagem

    def _monta_mensagem(self, transcricao: Path, caminho_perguntas: Path) -> str:
        """Monta a requisição para o servidor Ollama com instruções,
        transcrição e perguntas.

        Args:
            transcricao (Path): Caminho do arquivo com a transcrição.
            caminho_perguntas (Path): Caminho do arquivo com as perguntas.

        Returns:
            str: Mensagem formatada.

        Raises:
            FileNotFoundError: Se os arquivos não existirem.
            ValueError: Se os arquivos estiverem vazios.
        """
        conteudo_transcricao = self._converte_transcricao(transcricao)
        conteudo_perguntas = self._converte_perguntas(caminho_perguntas)

        instrucoes = """
Você é um assistente de IA especializado em transcrever e extrair informações de áudios de consultas de acupuntura. 
Sua única fonte de informação é a transcrição fornecida. Não utilize conhecimento prévio ou externo. 
Responda apenas às perguntas listadas abaixo. Se uma pergunta não puder ser respondida com base na transcrição 
(incluindo casos de informações ambíguas ou incompletas), responda 'NDA' (No Data Available).

**FORMATO DAS RESPOSTAS:**
Use o formato abaixo para cada pergunta. Pule exatamente duas linhas após cada resposta.
**Pergunta:** [Sua resposta aqui, baseada EXCLUSIVAMENTE na transcrição, em no máximo 50 palavras]

**EXEMPLO DE SAÍDA ESPERADA:**
**Pergunta:** Qual o nome completo do paciente?  
[Nome do paciente, se encontrado na transcrição]  

**Pergunta:** Qual a idade do paciente?  
[Idade do paciente, se encontrada na transcrição]  
"""

        mensagem = f"{instrucoes.strip()}\n\n**TRANSCRIÇÃO FORNECIDA:**\n{conteudo_transcricao}\n\n**PERGUNTAS A SEREM RESPONDIDAS:**\n{conteudo_perguntas}"
        logger.info(f"Mensagem montada com {len(mensagem)} caracteres.")
        return mensagem

    def _monta_prompt(self, mensagem: str) -> List[Dict[str, str]]:
        """Monta o prompt para o modelo a partir da mensagem fornecida.

        Args:
            mensagem (str): A mensagem a ser enviada ao modelo.

        Returns:
            List[Dict[str, str]]: Lista de mensagens no formato esperado pelo Ollama.
        """
        mensagens = [
            {
                "role": "system",
                "content": "Responda todas as perguntas de forma concisa e direta. NUNCA inclua seu processo de pensamento ou qualquer metadado, como blocos <think>...</think>. Forneça APENAS a resposta final.",
            },
            {
                "role": "user",
                "content": mensagem.strip(),
            },
        ]
        return mensagens

    def _ollama_talk(self, mensagens: List[Dict[str, str]]) -> str:
        """Envia mensagens para o modelo Ollama e retorna a resposta.

        Args:
            mensagens (List[Dict[str, str]]): Lista de mensagens a serem enviadas.

        Returns:
            str: Resposta do modelo.

        Raises:
            ollama.OllamaError: Se houver erro na comunicação com o Ollama.
        """
        try:
            logger.info(
                f"Enviando mensagem para o modelo '{self.model_name}' em {self.ollama_url}..."
            )
            response = self.client.chat(
                model=self.model_name,
                messages=mensagens,
                # stream=True,  # Descomente para resposta em tempo real, se desejar
                # options={'temperature': 0.8}  # Ajuste a criatividade, se necessário
            )
            resposta_do_modelo = response["message"]["content"]
            logger.info(f"Resposta recebida: {resposta_do_modelo}")
            return resposta_do_modelo
        except ollama.OllamaError as e:
            logger.error(f"Erro ao interagir com o Ollama: {e}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado em _ollama_talk: {e}")
            raise

    def _limpa_relatorio(self, resposta: str) -> str:
        """
        Remove informações desnecessárias do relatório.

        Args:
            resposta (str): O relatório a ser limpo.

        Returns:
            str: O relatório limpo.
        """
        resposta_limpa = re.sub(r"<think>.*?</think>", "", resposta, flags=re.DOTALL)
        return resposta_limpa

    def _data_clean(self, resposta: str) -> str:
        """
        Remove o bloco <think> e os marcadores de pergunta/colchetes.

        Args:
            resposta (str): Resposta bruta da LLM contendo <think>
            e perguntas/respostas.

        Returns:
            str: String limpa com apenas as perguntas e respostas.
        """
        # 1. Remove o bloco <think> e todo o seu conteúdo
        resposta_limpa = re.sub(r"<think>.*?</think>", "", resposta, flags=re.DOTALL)

        # 2. Remove o marcador '**Pergunta:**'
        resposta_limpa = re.sub(
            r"^\s*\*\*(.*?):\*\*\s*", r"\1\n", resposta_limpa, flags=re.MULTILINE
        )

        # 3. Remove os colchetes '[', ']' do início e do fim das frases
        resposta_limpa = resposta_limpa.replace("[", "").replace("]", "")

        # 4. Remove linhas vazias adicionais que podem ter sido criadas
        linhas_limpas = [
            linha.strip() for linha in resposta_limpa.split("\n") if linha.strip()
        ]

        return "\n".join(linhas_limpas)

    def _insere_redis(self, resposta: str, uuid: str) -> str:

        dict_resposta_novo = self._string_to_dict(self._data_clean(resposta))
        dict_resposta = redis.get_value(uuid)

        if redis.delete_key(uuid) == 1:
            logger.info("Concatenando os dicionarios")
            if dict_resposta is not None and dict_resposta_novo is not None:
                dict_concatenados = dict_resposta | dict_resposta_novo
                logger.info(f"dict_concatenados: {dict_concatenados}")

            # logger.info(f"Dados sendo inseridos no Redis: {dict_resposta_novo}")
            json_sucess = self._preencher_template_json(
                dict_concatenados,
                "/media/Dados/MVP_Acupuntura/src/models/perguntas_estruturadas.json",
                "/tmp/teste_inserir_redis.json",
            )

            # carrega o arquivo em memoria
            with open(json_sucess, "r", encoding="utf-8") as f:
                template_completo = json.load(f)

            # Itera sobre cada item do dicionário
            for key, value in template_completo.items():
                if value.get("resposta") == "":
                    value["resposta"] = "NDA"

            key_redis = redis.set_value(template_completo)
            if key_redis:
                logger.info(f"Dados atualizados no Redis para UUID: {uuid}")

        return key_redis

    def _string_to_dict(self, resposta_filtrada: str) -> dict:
        """
        Converte uma string com perguntas e respostas em linhas
        alternadas em um dicionário.

        Args:
            resposta_filtrada (str): String com perguntas em uma linha e respostas
            na linha seguinte.

        Returns:
            dict: Dicionário com perguntas como chaves e respostas como valores.
        """
        resultado = {}
        linhas = [
            linha.strip() for linha in resposta_filtrada.split("\n") if linha.strip()
        ]

        # Itera sobre as linhas em pares
        for i in range(0, len(linhas), 2):
            if i + 1 < len(linhas):
                pergunta = linhas[i]
                resposta = linhas[i + 1]
                resultado[pergunta] = resposta

        return resultado

    def _preencher_template_json(
        self, respostas_llm: dict, caminho_template: str, caminho_saida: str
    ) -> str:
        """
        Carrega um arquivo JSON de template, preenche os campos 'resposta'
        com base nas perguntas correspondentes em um dicionário de respostas,
        e salva o resultado em um novo arquivo JSON.

        Args:
            respostas_llm (dict): Dicionário com as perguntas e respostas da LLM.
            caminho_template (str): Caminho para o arquivo JSON de template.
            caminho_saida (str): Caminho para o arquivo JSON de saída.
        """
        try:
            # 1. Abre e carrega o arquivo JSON de template em memória
            with open(caminho_template, "r", encoding="utf-8") as f:
                template_completo = json.load(f)

            # 2. Faz uma cópia do template para não modificar o original
            # (Embora não seja estritamente necessário aqui, é uma boa prática)
            template_preenchido = template_completo.copy()

            # 3. Itera sobre o template e preenche as respostas
            # A chave de busca é a pergunta do template
            for chave_id, dados_pergunta in template_preenchido.items():
                pergunta = dados_pergunta["pergunta"]

                # Verifica se a pergunta do template existe nas respostas da LLM
                if pergunta in respostas_llm:
                    resposta_encontrada = respostas_llm[pergunta]
                    dados_pergunta["resposta"] = resposta_encontrada
                    logger.info(f"[✅] Pergunta '{pergunta}' preenchida.")
                else:
                    # Se não encontrar, a resposta permanece vazia ou pode
                    # ser preenchida com um marcador
                    # Para este exemplo, deixamos como está ('')
                    logger.info(
                        f"[⚠️] Pergunta '{pergunta}' não encontrada nas respostas da LLM."
                    )

            # 4. Salva o dicionário preenchido em um novo arquivo JSON
            with open(caminho_saida, "w", encoding="utf-8") as f:
                json.dump(template_preenchido, f, ensure_ascii=False, indent=2)

            logger.info(f"\n[✨] Arquivo preenchido salvo em: {caminho_saida}")
            return caminho_saida

        except FileNotFoundError:
            logger.error(f"Erro: O arquivo '{caminho_template}' não foi encontrado.")
            return ""
        except json.JSONDecodeError:
            logger.error(f"Erro: O arquivo '{caminho_template}' não é um JSON válido.")
            return ""
        except Exception as e:
            logger.error(f"Ocorreu um erro inesperado: {e}")
            return ""

    def inicio_llm(
        self,
        uuid: str,
        transcricao: Path,
        questionario: Path,
        bool_relatorio: bool = False,
    ) -> str:
        """
        Inicia o processo de interação com o modelo LLM e retorna a resposta.

        Args:
            transcricao (Path): Caminho para o arquivo de transcrição.
            questionario (Path): Caminho para o arquivo de questionário.

        Returns:
            str: Resposta do modelo LLM.

        Raises:
            FileNotFoundError: Se os arquivos não existirem.
            ValueError: Se os arquivos estiverem vazios.
            Exception: Erros gerais da interação com Ollama.
        """
        if bool_relatorio:
            logger.info("Gerando relatório...")
            mensagem = self._monta_mensagem_relatorio(uuid)
        else:
            mensagem = self._monta_mensagem(transcricao, questionario)

        prompt = self._monta_prompt(mensagem)
        resposta = self._ollama_talk(prompt)
        if bool_relatorio:
            return_llm = self._limpa_relatorio(resposta)
        else:
            return_llm = self._insere_redis(resposta, uuid)

        return return_llm
