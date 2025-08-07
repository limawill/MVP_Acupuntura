import logging
import platform
import tkinter as tk
from tkinter import messagebox, ttk
from src.tools.transcricao import TranscricaoAudio
from src.setup_audio.rec_audio import GravadorAudio
from src.tools.redis_connection import RedisConnection


logger = logging.getLogger(__name__)

redis = RedisConnection()
transcricao = TranscricaoAudio()


class Application(tk.Tk):

    def __init__(self):
        self.tempo_segundos = 0
        self.timer_id = None
        super().__init__()
        self.gravador = GravadorAudio()
        self.title("Gravação de Sessão - Acupuntura")
        self.geometry("495x360")
        self.configure(bg="#f0f0f0")
        self.resizable(False, False)
        self.sexo_options = ["Masculino", "Feminino", "Outro"]

        # Remove o botão de maximizar (apenas minimizar e fechar)
        if platform.system() == "Windows":
            self.attributes("-toolwindow", 1)

        # Título
        title = tk.Label(
            self,
            text="🧘 Sessão de Atendimento",
            font=("Helvetica", 16, "bold"),
            bg="#f0f0f0",
        )
        title.pack(pady=10)

        # =========================================================================
        # Novo Frame para os campos de entrada, usando grid para alinhamento
        # =========================================================================
        campos_frame = tk.Frame(self, bg="#f0f0f0")
        campos_frame.pack(padx=20)

        # Campo de nome do paciente
        tk.Label(
            campos_frame, text="Nome do paciente:", font=("Helvetica", 12), bg="#f0f0f0"
        ).grid(row=0, column=0, columnspan=3, sticky="w")
        self.nome_entry = tk.Entry(campos_frame, font=("Helvetica", 12))
        self.nome_entry.grid(row=1, column=0, columnspan=3, sticky="we", pady=5)

        # Labels dos novos campos
        tk.Label(
            campos_frame, text="Idade:", font=("Helvetica", 12), bg="#f0f0f0"
        ).grid(row=2, column=0, sticky="w", padx=(0, 5))
        tk.Label(campos_frame, text="Sexo:", font=("Helvetica", 12), bg="#f0f0f0").grid(
            row=2, column=1, sticky="w", padx=5
        )
        tk.Label(
            campos_frame, text="Profissão:", font=("Helvetica", 12), bg="#f0f0f0"
        ).grid(row=2, column=2, sticky="w", padx=5)

        # Campos de entrada
        self.idade_entry = tk.Entry(campos_frame, font=("Helvetica", 12), width=10)
        self.idade_entry.grid(row=3, column=0, sticky="we", padx=(0, 5), pady=(0, 10))

        self.sexo_var = tk.StringVar()
        self.sexo_combobox = ttk.Combobox(
            campos_frame, textvariable=self.sexo_var, values=self.sexo_options, width=15
        )
        self.sexo_combobox.grid(row=3, column=1, sticky="we", padx=5, pady=(0, 10))
        self.sexo_combobox.set("Selecione...")

        self.profissao_entry = tk.Entry(campos_frame, font=("Helvetica", 12), width=20)
        self.profissao_entry.grid(
            row=3, column=2, sticky="we", padx=(5, 0), pady=(0, 10)
        )
        # =========================================================================

        # Botões com ícones e texto
        self.botoes_frame = tk.Frame(self, bg="#f0f0f0")
        self.botoes_frame.pack(pady=20)

        self.btn_gravar = tk.Button(
            self.botoes_frame, text="🎤 Iniciar", width=12, font=("Helvetica", 11)
        )
        self.btn_gravar.config(command=self.iniciar_gravacao)
        self.btn_gravar.grid(row=0, column=0, padx=5)

        self.btn_pausar = tk.Button(
            self.botoes_frame,
            text="⏸️ Pausar",
            width=12,
            font=("Helvetica", 11),
            state="disabled",
        )
        self.btn_pausar.config(command=self.pausar_gravacao)
        self.btn_pausar.grid(row=0, column=1, padx=5)

        self.btn_retomar = tk.Button(
            self.botoes_frame,
            text="▶️ Retomar",
            width=12,
            font=("Helvetica", 11),
            state="disabled",
        )
        self.btn_retomar.config(command=self.retomar_gravacao)  # Vincular comando
        self.btn_retomar.grid(row=1, column=0, padx=5, pady=10)

        self.btn_parar = tk.Button(
            self.botoes_frame,
            text="⏹️ Parar",
            width=12,
            font=("Helvetica", 11),
            state="disabled",
        )
        self.btn_parar.config(command=self.parar_gravacao)  # Vincular comando
        self.btn_parar.grid(row=1, column=1, padx=5, pady=10)

        # Status da gravação
        self.status_label = tk.Label(
            self,
            text="Status: Aguardando",
            font=("Helvetica", 11, "italic"),
            fg="gray",
            bg="#f0f0f0",
        )
        self.status_label.pack(pady=10)
        self.tempo_label = tk.Label(
            self,
            text="⏱️ Tempo: 00:00",
            font=("Helvetica", 11, "italic"),
            fg="black",
            bg="#f0f0f0",
        )
        self.tempo_label.pack(pady=5)

    def iniciar_gravacao(self):
        nome_paciente = self.nome_entry.get().strip()
        profissao_paciente = self.profissao_entry.get().strip()
        sexo_paciente = self.sexo_var.get()
        if not nome_paciente:
            self.status_label.config(
                text="Por favor, insira o nome do paciente.", fg="red"
            )
            return
        if not profissao_paciente:
            self.status_label.config(
                text="Por favor, insira a profissão do paciente.", fg="red"
            )
            return
        if sexo_paciente == "Selecione..." or not sexo_paciente:
            self.status_label.config(
                text="Por favor, selecione o sexo do paciente.", fg="red"
            )
            return

        self.gravador.iniciar_gravacao(nome_paciente)
        self.status_label.config(text="Status: Gravando...", fg="green")
        self.tempo_segundos = 0
        self.atualizar_tempo()
        self.btn_gravar.config(state="disabled")
        self.btn_pausar.config(state="normal")
        self.btn_parar.config(state="normal")

    def atualizar_tempo(self):
        minutos = self.tempo_segundos // 60
        segundos = self.tempo_segundos % 60
        self.tempo_label.config(text=f"⏱️ Tempo: {minutos:02d}:{segundos:02d}")
        self.tempo_segundos += 1
        self.timer_id = self.after(1000, self.atualizar_tempo)

    def parar_tempo(self):
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None

    def pausar_gravacao(self):
        self.gravador.pausar_gravacao()
        self.status_label.config(text="Status: Pausado", fg="orange")
        self.parar_tempo()
        # Desabilitar "Pausar" e habilitar "Retomar"
        self.btn_pausar.config(state="disabled")
        self.btn_parar.config(state="disabled")
        self.btn_retomar.config(state="normal")

    def retomar_gravacao(self):
        nome_paciente = self.nome_entry.get().strip()
        if not nome_paciente:
            self.status_label.config(
                text="Por favor, insira o nome do paciente.", fg="red"
            )
            return
        self.gravador.retomar_gravacao(nome_paciente)
        self.status_label.config(text="Status: Gravando...", fg="green")
        self.atualizar_tempo()
        # Desabilitar "Retomar" e habilitar "Pausar" e "Parar"
        self.btn_retomar.config(state="disabled")
        self.btn_pausar.config(state="normal")
        self.btn_parar.config(state="normal")

    def parar_gravacao(self):
        nome_paciente = self.nome_entry.get().strip()
        sexo_paciente = self.sexo_var.get()
        profissao_paciente = self.profissao_entry.get().strip()

        dados_paciente = {
            "nome": nome_paciente,
            "sexo": sexo_paciente,
            "profissao": profissao_paciente,
        }

        self.gravador.parar_gravacao(self.nome_entry.get().strip())
        self.status_label.config(text="Status: Parado", fg="gray")
        self.parar_tempo()
        # Reabilitar "Iniciar" e desabilitar "Pausar", "Retomar" e "Parar"
        self.btn_gravar.config(state="normal")
        self.btn_pausar.config(state="disabled")
        self.btn_retomar.config(state="disabled")
        self.btn_parar.config(state="disabled")
        self.nome_entry.delete(0, tk.END)
        self.profissao_entry.delete(0, tk.END)
        self.sexo_combobox.set("Selecione...")

        key = redis.set_value(dados_paciente)
        logger.info(f"Dados salvos no Redis com chave: {key}")
        if not key:
            self.status_label.config(text="Erro ao salvar dados no Redis.", fg="red")
            return

        if transcricao.carregar_modelo(key):
            logger.info("Modelo carregado e transcrição com sucesso")
            self.status_label.config(
                text="Transcrição iniciada com sucesso!", fg="green"
            )
            from src.gui.questionario import carregar_perguntas

            carregar_perguntas()

            self.destroy()

        else:
            logger.error("Erro ao carregar modelo ou iniciar transcrição")
            self.status_label.config(text="Erro ao iniciar transcrição.", fg="red")
            messagebox.showerror(
                "Erro de Transcrição", "Erro na transcrição ou processamento do áudio."
            )
            # Fechar a janela
            self.destroy()
