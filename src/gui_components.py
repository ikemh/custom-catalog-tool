import os
import sys
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk  # Necessário para PhotoImage

def resource_path(relative_path: str) -> str:
    """
    Retorna o caminho absoluto do recurso, considerando se está congelado
    via PyInstaller (executável) ou rodando em modo de desenvolvimento.
    """
    try:
        # Se estivermos executando dentro de um executável PyInstaller,
        # sys._MEIPASS existe
        base_path = sys._MEIPASS
    except AttributeError:
        # Caso contrário, usar o diretório atual
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def criar_janela():
    """Cria a janela principal da aplicação."""
    root = ttk.Window(themename="darkly")
    root.title("Gerador de Catálogo")
    root.geometry("700x500")
    root.resizable(False, False)
    return root

def criar_layout(root):
    frame_menu = ttk.Frame(root, width=220, padding=10)
    frame_menu.pack(side=LEFT, fill=Y, padx=10, pady=10)

    frame_main = ttk.Frame(root, padding=20, bootstyle="dark")
    frame_main.pack(side=RIGHT, expand=True, fill=BOTH)

    return frame_menu, frame_main

def criar_status_box(frame_main):
    """Cria a caixa de status/logs."""
    status_text = ttk.Text(frame_main, height=15, wrap="word",
                           state="disabled", background="#222", foreground="white")
    status_text.pack(fill=BOTH, expand=True, padx=10, pady=10)
    return status_text

def criar_botoes(frame_menu, callbacks):
    """
    Cria os botões do menu lateral dividindo-os em duas seções
    e colocando o logo no fim.
    """
    # Define um estilo customizado para alinhar o texto à esquerda
    style = ttk.Style()
    style.configure("Left.TButton", anchor="w", padding=(10, 5))
    
    # Container principal para os botões e o logo
    frame_buttons = ttk.Frame(frame_menu)
    frame_buttons.pack(expand=True, fill=BOTH)
    
    # Título e divisor
    titulo = ttk.Label(frame_buttons, text="Menu de Ferramentas",
                       anchor="center", font=("Helvetica", 12, "bold"))
    titulo.pack(pady=(0, 5))
    separator = ttk.Separator(frame_buttons, orient="horizontal")
    separator.pack(fill="x", pady=(0, 10))
    
    # Seção superior: botões
    frame_top = ttk.Frame(frame_buttons)
    frame_top.pack(side=TOP, fill=X)
        
    ttk.Button(
        frame_top,
        text="⛏ Gerar Catálogo Principal",
        command=callbacks["principal"],
        bootstyle="info-outline",
        width=30,
    ).pack(pady=8)

    ttk.Button(
        frame_top,
        text="⛏ Gerar Catálogo Secundário",
        command=callbacks["secundario"],
        bootstyle="danger-outline",
        width=30,
    ).pack(pady=8)

    ttk.Button(
        frame_top,
        text="⧉ Abrir Planilha",
        command=callbacks["abrir_planilha"],
        bootstyle="success-outline",
        width=30
    ).pack(pady=8)

    ttk.Button(
        frame_top,
        text="☰ Reorganizar PDF",
        command=callbacks["reorganizar_pdf"],
        bootstyle="warning-outline",
        width=30
    ).pack(pady=8)

    ttk.Button(
        frame_top,
        text="✎ Gerenciar Modelos",
        command=callbacks["gerenciar_modelos"],
        bootstyle="light-outline",
        width=30,
    ).pack(pady=8)
    
    # Novo botão: Adicionar Máscara em Imagem (botão com estilo diferenciado)
    ttk.Button(
        frame_top,
        text="Adicionar Máscara em Imagens",
        command=callbacks["converter_fotos"],
        bootstyle="secondary",
        width=30,
    ).pack(pady=8)
    
    # Espaço para o logo: posicionado ao final do menu (parte inferior do frame_buttons)
    frame_logo = ttk.Frame(frame_buttons)
    frame_logo.pack(side=BOTTOM, fill=X, pady=10)
    
    # Carrega o logo usando a função resource_path
    logo_path = resource_path("logo.png")
    logo_image = tk.PhotoImage(file=logo_path)
    # Armazena a referência para evitar que o garbage collector remova a imagem
    frame_logo.logo_image = logo_image
    logo_label = ttk.Label(frame_logo, image=logo_image)
    logo_label.pack()
