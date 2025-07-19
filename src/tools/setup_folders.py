import os
import shutil
import logging
from dotenv import load_dotenv


class SetupFolders:
    """
    Classe responsável por configurar e validar a estrutura de pastas do sistema.

    Esta classe realiza as seguintes operações:
    1. Carrega a configuração de pastas de um arquivo .env
    2. Verifica a existência das pastas especificadas
    3. Cria pastas que não existem
    4. Limpa o conteúdo de pastas não vazias
    5. Mantém pastas vazias intactas

    Atributos:
        Nenhum atributo público é mantido diretamente na classe.

    Métodos:
        verifica_estutura(): Executa o processo completo de verificação e
        preparação das pastas.
    """

    def verifica_estutura(self) -> bool:
        """
        Verifica e prepara a estrutura de pastas conforme definido no
        arquivo .env.

        Este método realiza as seguintes ações sequenciais para cada
        pasta especificada:
        - Carrega a lista de pastas da variável de ambiente FOLDERS
        - Normaliza os caminhos das pastas
        - Cria pastas que não existem no sistema de arquivos
        - Para pastas existentes:
            * Verifica se é um diretório válido
            * Remove todo o conteúdo se a pasta não estiver vazia
            * Mantém o estado se a pasta já estiver vazia
        - Retorna o status geral da operação

        Retorno:
            bool:
                - True se todas as pastas foram verificadas/preparadas
                com sucesso
                - False se ocorrer algum erro (variável não definida ou
                caminho inválido)

        Exceções:
            Nenhuma exceção é levantada diretamente, mas erros do sistema
            podem ocorrer durante operações de I/O.

        Exemplo de uso:
            setup = SetupFolders()
            sucesso = setup.verifica_estutura()
            if sucesso:
                print("Sistema pronto para iniciar")
            else:
                print("Falha na configuração das pastas")

        Notas:
            - A variável FOLDERS no .env deve ser uma string com nomes de
            pastas separados por vírgulas
            - Pastas são criadas com permissões padrão do sistema
            - Conteúdo removido não pode ser recuperado (exclusão permanente)
            - Links simbólicos são tratados como arquivos (removidos, mas
            não seguidos)
        """

        # Carregar variáveis do arquivo .env
        load_dotenv()

        # Obter a lista de pastas da variável de ambiente
        folders_str = os.getenv("FOLDERS")

        if not folders_str:
            logger.error("Variável FOLDERS não encontrada no .env")
            return False

        # Processar a string para lista de pastas
        folders = [f.strip() for f in folders_str.split(",") if f.strip()]

        for folder in folders:
            # Criar pasta na raiz do projeto (não dentro de mvp_acupuntura/)
            folder_path = os.path.normpath(folder)

            # Criar pasta se não existir
            if not os.path.exists(folder_path):
                os.makedirs(folder_path, exist_ok=True)
                logger.info(f"Pasta criada: {folder_path}")
                continue

            # Verificar se é um diretório
            if not os.path.isdir(folder_path):
                logger.error(f"Erro: '{folder_path}' não é um diretório")
                return False

            # Limpar pasta se não estiver vazia
            if os.listdir(folder_path):
                logger.info(f"Limpando pasta: {folder_path}")

                # Remover todo o conteúdo preservando a pasta
                for item in os.listdir(folder_path):
                    item_path = os.path.join(folder_path, item)

                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
            else:
                logger.info(f"Pasta já vazia: {folder_path}")

        logger.info("Todas as pastas foram verificadas e preparadas")
        return True
