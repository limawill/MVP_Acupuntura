import tkinter as tk
import json


def carregar_perguntas():
    with open("src/models/perguntas_estruturadas_20250805.json", "r") as f:
        return json.load(f)


# Criar a janela principal
root = tk.Tk()
root.title("Questionário - Paciente")

# Obter dimensões da tela e maximizar com margem
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
# Subtrair uma margem (ex.: 40 pixels para a barra de título e bordas)
root.geometry(f"{screen_width}x{screen_height - 40}")

# Carregar perguntas do JSON
perguntas = carregar_perguntas()

# Criar Canvas e Scrollbar
canvas = tk.Canvas(root)
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

# Configurar a rolagem
scrollable_frame.bind(
    "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

# Posicionar os elementos
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Adicionar perguntas e campos dinamicamente
for pergunta_id, dados in perguntas.items():
    frame = tk.Frame(scrollable_frame)
    frame.pack(fill=tk.X, pady=2, padx=5)
    tk.Label(frame, text=f"{pergunta_id}: {dados['pergunta']}").pack(side=tk.LEFT)
    entry = tk.Entry(frame, width=50)
    entry.pack(side=tk.RIGHT, padx=5)

# Frame para agrupar os botões
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# Botão para fechar
tk.Button(button_frame, text="Gerar relatório", width=16, command=root.destroy).pack(
    padx=5, pady=2
)
tk.Button(button_frame, text="Salvar", width=16, command=root.destroy).pack(
    padx=5, pady=2
)
tk.Button(button_frame, text="Fechar", width=16, command=root.destroy).pack(
    padx=5, pady=2
)

# Iniciar a interface
root.mainloop()
