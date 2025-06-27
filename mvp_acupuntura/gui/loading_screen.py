import threading
import tkinter as tk
from tkinter import ttk


class LoadingScreen(tk.Tk):
    """
    Janela principal que exibe o progresso da transcrição.
    """

    def __init__(self, transcritor):
        super().__init__()
        self.transcritor = transcritor
        self.title("Transcrição em Andamento")
        self.geometry("300x170")
        self.configure(bg="#f0f0f0")
        self.resizable(False, False)

        # Título
        tk.Label(
            self,
            text="Transcrevendo Áudio...",
            font=("Helvetica", 12, "bold"),
            bg="#f0f0f0",
        ).pack(pady=10)

        # Frame para barra de progresso + porcentagem centralizada
        self.progresso_frame = tk.Frame(self, bg="#f0f0f0")
        self.progresso_frame.pack(pady=5)

        # Barra de progresso
        self.progresso = ttk.Progressbar(
            self.progresso_frame, orient="horizontal", length=250, mode="determinate"
        )
        self.progresso.pack()

        # Label sobreposta com a porcentagem
        self.percent_label = tk.Label(
            self.progresso_frame,
            text="0%",
            font=("Helvetica", 10, "bold"),
            bg="#d9d9d9",  # Cor de fundo semelhante à progressbar
            fg="black",
        )
        self.percent_label.place(relx=0.5, rely=0.5, anchor="center")

        # Status abaixo da barra
        self.status_label = tk.Label(
            self, text="Aguardando...", font=("Helvetica", 10), bg="#f0f0f0"
        )
        self.status_label.pack(pady=5)

        # Botão Cancelar
        self.btn_cancelar = tk.Button(
            self,
            text="Cancelar",
            width=10,
            font=("Helvetica", 10),
            command=self.cancelar,
        )
        self.btn_cancelar.pack(pady=10)

    def atualizar_progresso(self, valor, mensagem):
        """Atualiza a barra, a porcentagem e o status."""
        self.progresso["value"] = valor
        self.percent_label.config(text=f"{int(valor)}%")
        self.status_label.config(text=mensagem)
        self.update_idletasks()

    def iniciar_transcricao(self):
        """Inicia a transcrição em thread paralela."""
        self.btn_cancelar.config(state="normal")
        threading.Thread(target=self.executar_transcricao, daemon=True).start()

    def executar_transcricao(self):
        """Executa a transcrição e fecha após concluir."""
        texto = self.transcritor.transcrever_audio()
        if texto:
            self.status_label.config(text="Transcrição concluída!")
        else:
            self.status_label.config(text="Erro na transcrição.")
        self.after(2000, self.destroy)

    def cancelar(self):
        """Cancela a transcrição e fecha a janela."""
        self.status_label.config(text="Cancelado pelo usuário.")
        self.after(1000, self.destroy)
