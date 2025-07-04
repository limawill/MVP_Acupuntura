import platform
import tkinter as tk
from src.setup_audio.rec_audio import GravadorAudio


class Application(tk.Tk):

    def __init__(self):
        self.tempo_segundos = 0
        self.timer_id = None
        super().__init__()
        self.gravador = GravadorAudio()
        self.title("Gravação de Sessão - Acupuntura")
        self.geometry("400x350")
        self.configure(bg="#f0f0f0")
        self.resizable(False, False)

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

        # Campo de nome do paciente
        tk.Label(
            self, text="Nome do paciente:", font=("Helvetica", 12), bg="#f0f0f0"
        ).pack()
        self.nome_entry = tk.Entry(self, font=("Helvetica", 12), width=30)
        self.nome_entry.pack(pady=5)

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
        if not nome_paciente:
            self.status_label.config(
                text="Por favor, insira o nome do paciente.", fg="red"
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
        self.gravador.parar_gravacao(self.nome_entry.get().strip())
        self.status_label.config(text="Status: Parado", fg="gray")
        self.parar_tempo()
        # Reabilitar "Iniciar" e desabilitar "Pausar", "Retomar" e "Parar"
        self.btn_gravar.config(state="normal")
        self.btn_pausar.config(state="disabled")
        self.btn_retomar.config(state="disabled")
        self.btn_parar.config(state="disabled")
        self.nome_entry.delete(0, tk.END)
        # Fechar a janela
        self.destroy()
