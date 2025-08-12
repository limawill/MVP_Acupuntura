import os
import json
import shutil
import logging
import tempfile
import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import messagebox
from src.tools.ia_preenche_forms import OllamaClient
from src.tools.redis_connection import RedisConnection


logger = logging.getLogger(__name__)
llm_question = OllamaClient()


class Questionario:
    def __init__(self, uuid: str, loading_screen_instance=None):
        self.uuid = uuid
        self.loading_screen = loading_screen_instance
        self.entry_widgets = {}  # Armazena os widgets de entrada
        self.perguntas = self.carrega_info_redis()  # Carrega perguntas do Redis
        self.questao_salva = False
        self.relatorio_button = None

    def carrega_info_redis(self) -> dict:
        """
        Carrega informações do Redis para o UUID fornecido.

        Returns:
            dict: Dicionário com perguntas e respostas.
        """
        try:
            redis_conn = RedisConnection()
            info = redis_conn.get_value(self.uuid)
            if not info:
                logger.warning(
                    f"Nenhuma informação encontrada no Redis para UUID: {self.uuid}"
                )
                return {}

            return info
        except Exception as e:
            logger.error(f"Erro ao carregar dados do Redis para UUID {self.uuid}: {e}")
            return {}

    def _fill_entries_from_redis(self):
        """
        Preenche os campos de entrada com os dados de resposta do Redis.
        """
        for pergunta_id, dados in self.perguntas.items():
            entry = self.entry_widgets.get(pergunta_id)
            if entry:
                resposta = dados.get("resposta", "NDA")
                entry.insert(0, resposta)

    def salvar_respostas(self):
        """
        Salva as respostas dos campos de entrada no Redis.
        """
        try:
            redis_conn = RedisConnection()
            dados_atualizados = {}
            for id_pergunta, entry in self.entry_widgets.items():
                resposta = entry.get()
                dados_atualizados[id_pergunta] = {
                    "pergunta": self.perguntas[id_pergunta]["pergunta"],
                    "resposta": resposta if resposta else "NDA",
                }
            redis_conn.update_value(self.uuid, dados_atualizados)
            logger.info(f"Respostas salvas no Redis para UUID: {self.uuid}")
            messagebox.showinfo("Sucesso", "Respostas salvas com sucesso!")
            self.questao_salva = True
            # Habilita o botão de relatório após o salvamento
            if self.relatorio_button:
                self.relatorio_button["state"] = tk.NORMAL
        except Exception as e:
            logger.error(f"Erro ao salvar respostas no Redis: {e}")
            messagebox.showerror("Erro", "Falha ao salvar respostas.")

    def gerar_relatorio(self):
        """
        Gera um relatório com base nas respostas atuais e salva em um arquivo.
        """
        try:
            key_redis_llm = llm_question.inicio_llm(
                self.uuid,
                Path("/tmp/"),
                Path("/tmp/"),
                True,
            )
            if key_redis_llm:
                self._abrir_relatorio_no_libreoffice(key_redis_llm)
            else:
                messagebox.showerror("Erro", "Falha ao gerar relatório.")

        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {e}")
            messagebox.showerror("Erro", "Falha ao gerar relatório.")

    def _abrir_relatorio_no_libreoffice(self, conteudo_relatorio: str) -> None:
        """
        Cria um arquivo temporário com o conteúdo do relatório e o abre
        com o LibreOffice.

        Args:
            conteudo_relatorio (str): A string de texto do relatório a ser exibida.
        """
        try:
            # 1. Encontrar o caminho do executável do LibreOffice
            caminho_libreoffice = shutil.which("libreoffice")

            if not caminho_libreoffice:
                raise FileNotFoundError(
                    "O executável do LibreOffice não foi encontrado no PATH."
                )

            # 2. Criar um arquivo temporário para o relatório
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".odt", delete=False, encoding="utf-8"
            ) as f:
                f.write(conteudo_relatorio)
                caminho_arquivo = f.name

            # 3. Definir o comando para abrir o arquivo com o LibreOffice Writer
            # A flag '--writer' é a chave para abrir como processador de texto
            comando = [caminho_libreoffice, "--writer", caminho_arquivo]

            # 4. Chamar o LibreOffice com o subprocess
            subprocess.Popen(comando)

            logger.info(
                f"Relatório salvo em '{caminho_arquivo}' e aberto no LibreOffice."
            )

        except FileNotFoundError as e:
            logger.error(f"Erro: {e}")
        except Exception as e:
            logger.error(f"Ocorreu um erro ao abrir o LibreOffice: {e}")

    def gera_tela_questionario(self):
        """
        Gera a tela do questionário com base nos dados do Redis.
        """
        root = tk.Tk()
        root.title("Questionário - Paciente")

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.geometry(f"{screen_width}x{screen_height - 40}")

        if not self.perguntas:
            messagebox.showerror("Erro", "Nenhuma pergunta encontrada no Redis.")
            root.destroy()
            if self.loading_screen:
                self.loading_screen.destroy()
            return

        canvas = tk.Canvas(root)
        scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        for pergunta_id, dados in self.perguntas.items():
            frame = tk.Frame(scrollable_frame)
            frame.pack(fill=tk.X, pady=2, padx=5)
            tk.Label(frame, text=f"{pergunta_id}: {dados['pergunta']}").pack(
                side=tk.LEFT
            )
            entry = tk.Entry(frame, width=100)
            entry.pack(side=tk.RIGHT, padx=5)
            self.entry_widgets[pergunta_id] = entry

        self._fill_entries_from_redis()

        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        self.relatorio_button = tk.Button(
            button_frame,
            text="Gerar relatório",
            width=16,
            command=self.gerar_relatorio,
            state=tk.DISABLED,
        )
        self.relatorio_button.pack(padx=5, pady=2)

        tk.Button(
            button_frame, text="Salvar", width=16, command=self.salvar_respostas
        ).pack(padx=5, pady=2)

        tk.Button(button_frame, text="Fechar", width=16, command=root.destroy).pack(
            padx=5, pady=2
        )

        if self.loading_screen:
            self.loading_screen.destroy()

        root.mainloop()
