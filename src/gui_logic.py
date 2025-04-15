import os
import sys
import threading
import platform
import subprocess
import pprint
import glob
import ttkbootstrap as ttk
from tkinter import filedialog, messagebox, Toplevel, Listbox, Scrollbar, simpledialog
from catalogo import carregar_planilha, gerar_catalogo, gerar_catalogo_personalizado
from gui_components import criar_janela, criar_layout, criar_status_box, criar_botoes
from utils import get_base_path

# Diretório persistente para armazenar dados (planilha, imagens, modelos)
user_docs = os.path.join(os.path.expanduser("~"), "Documents", "GeradorCatalogo")
os.makedirs(user_docs, exist_ok=True)

# Diretórios para imagens dentro do diretório do usuário
image_folders = {
    "catalogo_principal": os.path.join(user_docs, "images", "catalogo_principal"),
    "catalogo_secundario": os.path.join(user_docs, "images", "catalogo_secundario"),
}

# Caminho para a planilha (em user_docs)
excel_file = os.path.join(user_docs, "data", "Planilha_Catalogo_2025.ods")

# Diretório de saída para os catálogos (na Área de Trabalho)
output_dir = os.path.join(os.path.expanduser("~"), "Desktop", "Catálogos")
os.makedirs(output_dir, exist_ok=True)

# Carrega a planilha
df, codigo_coluna, preco_colunas = carregar_planilha(excel_file)

def load_catalog_groups():
    """
    Tenta carregar o arquivo persistente de modelos em Documents.
    Se existir, retorna os valores carregados; caso contrário,
    retorna os valores padrão do módulo catalog_groups em src.
    """
    persistent_path = os.path.join(user_docs, "catalog_groups.py")
    if os.path.exists(persistent_path):
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("catalog_groups", persistent_path)
            cg_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cg_module)
            return cg_module.GRUPOS_PRINCIPAL, cg_module.GRUPOS_SECUNDARIO
        except Exception as e:
            print("Erro ao carregar catalog_groups do Documents:", e)
    try:
        from catalog_groups import GRUPOS_PRINCIPAL as default_principal, GRUPOS_SECUNDARIO as default_secundario
    except ImportError:
        default_principal, default_secundario = {}, {}
    return default_principal, default_secundario

# Carrega os modelos persistentes (ou os padrões, se não existir o arquivo persistente)
GRUPOS_PRINCIPAL, GRUPOS_SECUNDARIO = load_catalog_groups()

def atualizar_status(status_text, mensagem, log_type="default"):
    """Atualiza a área de status/logs na interface gráfica com cores definidas."""
    if status_text:
        if "processamento" not in status_text.tag_names():
            status_text.tag_config("processamento", foreground="#F5F5F5")
        if "sucesso" not in status_text.tag_names():
            status_text.tag_config("sucesso", foreground="#58D68D")
        if "erro" not in status_text.tag_names():
            status_text.tag_config("erro", foreground="#E74C3C")
        if "informacao" not in status_text.tag_names():
            status_text.tag_config("informacao", foreground="#3498DB")
        if "alerta" not in status_text.tag_names():
            status_text.tag_config("alerta", foreground="#F1C40F")
        if "default" not in status_text.tag_names():
            status_text.tag_config("default", foreground="#FFFFFF")
        
        status_text.config(state="normal")
        status_text.insert("end", mensagem + "\n", log_type)
        status_text.config(state="disabled")
        status_text.see("end")

def escolher_caminho_padrao(nome_padrao):
    """Cria uma janela para escolher onde salvar o arquivo, com o caminho padrão em output_dir."""
    caminho_selecionado = None

    def confirmar():
        nonlocal caminho_selecionado
        caminho_selecionado = entry_path.get()
        root_dialog.destroy()

    root_dialog = ttk.Toplevel()
    root_dialog.title("Salvar Arquivo")
    root_dialog.geometry("500x200")
    root_dialog.resizable(False, False)
    root_dialog.configure(bg="#222")
    ttk.Label(root_dialog, text="Escolha o local para salvar:", bootstyle="light").pack(pady=10)
    frame = ttk.Frame(root_dialog, bootstyle="dark")
    frame.pack(pady=5, padx=10, fill="x")
    entry_path = ttk.Entry(frame, bootstyle="dark", width=50)
    entry_path.insert(0, os.path.join(output_dir, nome_padrao))
    entry_path.pack(side="left", expand=True, fill="x", padx=5)
    def escolher_pasta():
        path = filedialog.askdirectory(initialdir=output_dir)
        if path:
            entry_path.delete(0, "end")
            entry_path.insert(0, os.path.join(path, nome_padrao))
    ttk.Button(frame, text="📂", command=escolher_pasta, bootstyle="info").pack(side="right")
    ttk.Button(root_dialog, text="Confirmar", command=confirmar, bootstyle="success").pack(pady=10)
    root_dialog.grab_set()
    root_dialog.wait_window()
    return caminho_selecionado

def abrir_janela_de_ordenacao(grupos_dict, ao_confirmar):
    """
    Exibe uma janela para reordenar os grupos definidos em grupos_dict,
    utilizando uma cópia dos dados para não alterar o dicionário original.
    Permite também remover itens temporariamente para a geração do catálogo.
    :param grupos_dict: dicionário (ex.: GRUPOS_PRINCIPAL ou GRUPOS_SECUNDARIO)
    :param ao_confirmar: função callback que recebe a lista de grupos ordenados
    """
    # Cria uma cópia dos nomes dos grupos (apenas as chaves) para operar na interface
    grupos_temp = list(grupos_dict.keys())

    win = Toplevel()
    win.title("Ordenar Grupos")
    win.geometry("250x420")
    win.resizable(False, False)

    # Título da janela
    lbl_title = ttk.Label(win, text="Ordenar Grupos", font=("Helvetica", 14, "bold"))
    lbl_title.pack(pady=(10, 5))

    # Frame principal com padding
    main_frame = ttk.Frame(win, bootstyle="dark")
    main_frame.pack(padx=15, pady=10, fill="both", expand=True)

    # Frame da Listbox
    frame_list = ttk.Frame(main_frame, bootstyle="dark")
    frame_list.pack(side="left", fill="both", expand=True)

    listbox = Listbox(frame_list, bg="#3a3a3a", fg="white", font=("Arial", 10),
                      bd=0, highlightthickness=0, relief="flat")
    listbox.pack(side="left", fill="both", expand=True)

    scrollbar = Scrollbar(frame_list, bg="#555", troughcolor="#444", bd=0, highlightthickness=0)
    scrollbar.pack(side="right", fill="y")
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)

    # Insere os grupos na Listbox
    for grupo in grupos_temp:
        listbox.insert("end", grupo)

    # Frame dos botões de ação centralizados
    frame_buttons = ttk.Frame(main_frame, bootstyle="dark", width=50)
    frame_buttons.pack(side="left", fill="y", padx=(10, 0))
    frame_buttons.pack_propagate(False)

    # Spacer superior (frame vazio com fundo igual)
    spacer_top = ttk.Frame(frame_buttons, bootstyle="dark")
    spacer_top.pack(expand=True, fill="both")

    def mover_cima():
        idx = listbox.curselection()
        if not idx:
            return
        i = idx[0]
        if i == 0:
            return
        texto = listbox.get(i)
        listbox.delete(i)
        listbox.insert(i - 1, texto)
        listbox.select_set(i - 1)

    def mover_baixo():
        idx = listbox.curselection()
        if not idx:
            return
        i = idx[0]
        if i == listbox.size() - 1:
            return
        texto = listbox.get(i)
        listbox.delete(i)
        listbox.insert(i + 1, texto)
        listbox.select_set(i + 1)

    def remover_item():
        idx = listbox.curselection()
        if not idx:
            return
        listbox.delete(idx[0])

    btn_up = ttk.Button(frame_buttons, text="▲", command=mover_cima, bootstyle="info", width=3)
    btn_up.pack(pady=5)
    btn_down = ttk.Button(frame_buttons, text="▼", command=mover_baixo, bootstyle="info", width=3)
    btn_down.pack(pady=5)
    btn_remove = ttk.Button(frame_buttons, text="✕", command=remover_item, bootstyle="danger", width=2)
    btn_remove.pack(pady=5)

    # Spacer inferior (frame vazio com fundo igual)
    spacer_bottom = ttk.Frame(frame_buttons, bootstyle="dark")
    spacer_bottom.pack(expand=True, fill="both")

    def confirmar():
        ordem = [listbox.get(i) for i in range(listbox.size())]
        ao_confirmar(ordem)
        win.destroy()

    btn_confirm = ttk.Button(win, text="Confirmar", command=confirmar, bootstyle="success", width=15)
    btn_confirm.pack(side="bottom", pady=20)

    win.grab_set()
    win.mainloop()

def salvar_modelos(grupos_principal, grupos_secundario, status_text=None):
    """
    Salva os dicionários de grupos no arquivo catalog_groups.py.
    O arquivo será sobrescrito com os estados atuais dos dicionários.
    Esse arquivo é gravado no diretório persistente (user_docs).
    """
    path = os.path.join(user_docs, "catalog_groups.py")
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("# Arquivo catalog_groups.py\n\n")
            f.write("GRUPOS_PRINCIPAL = ")
            f.write(pprint.pformat(grupos_principal, indent=4, sort_dicts=False))
            f.write("\n\n")
            f.write("GRUPOS_SECUNDARIO = ")
            f.write(pprint.pformat(grupos_secundario, indent=4, sort_dicts=False))
            f.write("\n")
        if status_text:
            atualizar_status(status_text, f"Modelos salvos com sucesso em: {path}", "sucesso")
    except Exception as e:
        if status_text:
            atualizar_status(status_text, f"Erro ao salvar modelos: {e}", "erro")
        else:
            print(f"Erro ao salvar modelos: {e}")

def gerenciar_modelos(status_text):
    """
    Abre uma janela para gerenciar os modelos definidos.
    Permite visualizar, adicionar, remover e editar grupos para os catálogos.
    """
    win = Toplevel()
    win.title("Gerenciar Modelos")
    win.geometry("400x500")
    win.resizable(False, False)
    win.configure(bg="#222")
    
    atualizar_status(status_text, "🔧 Interface de gerenciamento de modelos aberta.", "informacao")
    
    notebook = ttk.Notebook(win)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Abas para os modelos principal e secundário
    frame_principal = ttk.Frame(notebook, bootstyle="dark")
    frame_secundario = ttk.Frame(notebook, bootstyle="dark")
    
    notebook.add(frame_principal, text="Principal")
    notebook.add(frame_secundario, text="Secundário")
    
    def criar_interface_modelos(frame, grupos, status_text):
        """
        Cria a interface de gerenciamento para uma aba, exibindo os grupos e permitindo
        adicionar, remover e editar. Atualiza o status com as ações realizadas.
        """
        lb = Listbox(frame, bg="#333", fg="white", font=("Arial", 10), selectbackground="#555", relief="flat")
        lb.pack(fill="both", expand=True, padx=10, pady=10)
        for nome, codigos in grupos.items():
            lb.insert("end", f"{nome} : {codigos[0] if codigos else ''}")
        
        btn_frame = ttk.Frame(frame, bootstyle="dark")
        btn_frame.pack(pady=5)
        
        def adicionar_modelo():
            nome = simpledialog.askstring("Adicionar Modelo", "Digite o nome do grupo:", parent=win)
            if not nome:
                atualizar_status(status_text, "⚠ Nenhum nome informado para o modelo.", "alerta")
                return
            codigo = simpledialog.askstring("Adicionar Modelo", "Digite o código (com prefixo) para o grupo:", parent=win)
            if not codigo:
                atualizar_status(status_text, "⚠ Nenhum código informado para o modelo.", "alerta")
                return
            grupos[nome] = [codigo]
            lb.insert("end", f"{nome} : {codigo}")
            salvar_modelos(GRUPOS_PRINCIPAL, GRUPOS_SECUNDARIO, status_text)
            atualizar_status(status_text, f"✅ Modelo '{nome}' adicionado com sucesso.", "sucesso")
        
        def remover_modelo():
            selected = lb.curselection()
            if not selected:
                messagebox.showwarning("Aviso", "Nenhum modelo selecionado.", parent=win)
                atualizar_status(status_text, "⚠ Nenhum modelo selecionado para remoção.", "alerta")
                return
            index = selected[0]
            item = lb.get(index)
            nome = item.split(" : ")[0]
            if nome in grupos:
                del grupos[nome]
            lb.delete(index)
            salvar_modelos(GRUPOS_PRINCIPAL, GRUPOS_SECUNDARIO, status_text)
            atualizar_status(status_text, f"✅ Modelo '{nome}' removido com sucesso.", "sucesso")
        
        def editar_modelo():
            selected = lb.curselection()
            if not selected:
                messagebox.showwarning("Aviso", "Nenhum modelo selecionado.", parent=win)
                atualizar_status(status_text, "⚠ Nenhum modelo selecionado para edição.", "alerta")
                return
            index = selected[0]
            item = lb.get(index)
            partes = item.split(" : ")
            if len(partes) < 2:
                messagebox.showwarning("Aviso", "Formato inválido.", parent=win)
                atualizar_status(status_text, "⚠ Formato inválido para edição de modelo.", "alerta")
                return
            old_nome = partes[0]
            old_codigo = partes[1]
            new_nome = simpledialog.askstring("Editar Modelo", "Digite o novo nome do grupo:", initialvalue=old_nome, parent=win)
            if new_nome is None:
                return
            new_codigo = simpledialog.askstring("Editar Modelo", "Digite o novo código (com prefixo) para o grupo:", initialvalue=old_codigo, parent=win)
            if new_codigo is None:
                return
            if old_nome in grupos:
                del grupos[old_nome]
            grupos[new_nome] = [new_codigo]
            lb.delete(index)
            lb.insert(index, f"{new_nome} : {new_codigo}")
            salvar_modelos(GRUPOS_PRINCIPAL, GRUPOS_SECUNDARIO, status_text)
            atualizar_status(status_text, f"✅ Modelo '{old_nome}' editado para '{new_nome}' com sucesso.", "sucesso")
        
        ttk.Button(btn_frame, text="Adicionar", command=adicionar_modelo, bootstyle="success").grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Remover", command=remover_modelo, bootstyle="danger").grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Editar", command=editar_modelo, bootstyle="primary").grid(row=0, column=2, padx=5)
    
    criar_interface_modelos(frame_principal, GRUPOS_PRINCIPAL, status_text)
    criar_interface_modelos(frame_secundario, GRUPOS_SECUNDARIO, status_text)
    
    win.grab_set()
    win.mainloop()

def converter_fotos_interativo(status_text):
    """
    Permite selecionar interativamente uma imagem base (máscara) e um diretório com imagens a serem editadas.
    As imagens resultantes serão salvas em um subdiretório "saida" dentro do diretório selecionado.
    """
    from PIL import Image
    # Seleciona a máscara
    caminho_mascara = filedialog.askopenfilename(
        title="Selecione a imagem de máscara",
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")]
    )
    if not caminho_mascara:
        atualizar_status(status_text, "Operação cancelada: máscara não selecionada.", "alerta")
        return

    # Seleciona o diretório de imagens a serem editadas
    pasta_imagens = filedialog.askdirectory(title="Selecione o diretório com as imagens a editar")
    if not pasta_imagens:
        atualizar_status(status_text, "Operação cancelada: diretório de imagens não selecionado.", "alerta")
        return

    # Define o diretório de saída dentro do diretório selecionado
    pasta_saida = os.path.join(pasta_imagens, "saida")
    if not os.path.exists(pasta_saida):
        os.makedirs(pasta_saida)

    atualizar_status(status_text, f"Iniciando processamento de imagens na pasta: {pasta_imagens}", "informacao")

    try:
        # Abre a máscara original (em RGBA)
        mascara_original = Image.open(caminho_mascara).convert("RGBA")

        # Obtém os arquivos com extensões .JPG e .jpg
        arquivos = []
        for ext in ("*.JPG", "*.jpg"):
            arquivos.extend(glob.glob(os.path.join(pasta_imagens, ext)))
        if not arquivos:
            atualizar_status(status_text, "Nenhuma imagem encontrada no diretório selecionado.", "alerta")
            return

        total = len(arquivos)
        contador = 0
        for caminho_imagem in arquivos:
            imagem = Image.open(caminho_imagem).convert("RGBA")
            if imagem.size != mascara_original.size:
                try:
                    mascara = mascara_original.resize(imagem.size, Image.Resampling.LANCZOS)
                except AttributeError:
                    mascara = mascara_original.resize(imagem.size, Image.ANTIALIAS)
            else:
                mascara = mascara_original
            imagem_resultante = Image.alpha_composite(imagem, mascara)
            imagem_resultante = imagem_resultante.convert("RGB")
            nome_arquivo = os.path.basename(caminho_imagem)
            caminho_saida_final = os.path.join(pasta_saida, nome_arquivo)
            imagem_resultante.save(caminho_saida_final, "JPEG")
            contador += 1
            atualizar_status(status_text, f"Processado: {nome_arquivo} ({contador}/{total})", "informacao")
        atualizar_status(status_text, "Processamento concluído.", "sucesso")
    except Exception as e:
        atualizar_status(status_text, f"Erro no processamento: {e}", "erro")

def gerar_principal_interativo(status_text):
    output_path = escolher_caminho_padrao("Catalogo_Principal.pdf")
    if not output_path:
        return
    atualizar_status(status_text, "⚙️ Iniciando geração interativa do Catálogo Principal...", "processamento")
    atualizar_status(status_text, f"📁 Caminho para salvar definido: {output_path}", "informacao")
    def ao_confirmar(ordem_grupos):
        def processar():
            from catalogo import gerar_catalogo_personalizado
            result = gerar_catalogo_personalizado(
                "catalogo_principal",
                image_folders["catalogo_principal"],
                output_path,
                df, codigo_coluna, preco_colunas,
                grupos_ordenados=ordem_grupos,
                grupos_dict=GRUPOS_PRINCIPAL,
                position="left",
                style="principal",   # Especifica o estilo para catálogo principal (dourado)
                status_text=status_text
            )
            if result:
                atualizar_status(status_text, "✅ Catálogo Principal gerado com sucesso!", "sucesso")
            else:
                atualizar_status(status_text, "Operação cancelada.", "alerta")
        threading.Thread(target=processar, daemon=True).start()
    abrir_janela_de_ordenacao(GRUPOS_PRINCIPAL, ao_confirmar)

def gerar_secundario_interativo(status_text):
    output_path = escolher_caminho_padrao("Catalogo_Secundario.pdf")
    if not output_path:
        return
    atualizar_status(status_text, "⚙️ Iniciando geração interativa do Catálogo Secundário...", "processamento")
    atualizar_status(status_text, f"📁 Caminho para salvar definido: {output_path}", "informacao")
    def ao_confirmar(ordem_grupos):
        def processar():
            from catalogo import gerar_catalogo_personalizado
            result = gerar_catalogo_personalizado(
                "catalogo_secundario",
                image_folders["catalogo_secundario"],
                output_path,
                df, codigo_coluna, preco_colunas,
                grupos_ordenados=ordem_grupos,
                grupos_dict=GRUPOS_SECUNDARIO,
                position="right",
                style="secundario",   # Especifica o estilo para catálogo secundário (vermelho esperado)
                status_text=status_text
            )
            if result:
                atualizar_status(status_text, "✅ Catálogo Secundário gerado com sucesso!", "sucesso")
            else:
                atualizar_status(status_text, "Operação cancelada.", "alerta")
        threading.Thread(target=processar, daemon=True).start()
    abrir_janela_de_ordenacao(GRUPOS_SECUNDARIO, ao_confirmar)

def abrir_planilha(status_text):
    """Abre a planilha no programa padrão do sistema."""
    if os.path.exists(excel_file):
        try:
            if platform.system() == "Windows":
                os.startfile(excel_file)
            elif platform.system() == "Darwin":
                subprocess.run(["open", excel_file])
            else:
                subprocess.run(["xdg-open", excel_file])
            atualizar_status(status_text, "📂 Planilha aberta com sucesso.", "sucesso")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir a planilha:\n{e}")
            atualizar_status(status_text, f"⚠ Erro ao abrir planilha: {e}", "erro")
    else:
        messagebox.showerror("Erro", "O arquivo Planilha_Catalogo_2025.ods não foi encontrado.")
        atualizar_status(status_text, "⚠ Erro: Planilha não encontrada.", "erro")

def abrir_reorganizador_pdf(status_text):
    """Abre o novo PDF Reorganizer."""
    atualizar_status(status_text, "🖼 Abrindo Reorganizador de PDF...", "informacao")
    try:
        exe_path = os.path.join(os.path.dirname(sys.executable), "pdf_reorganizer.exe")
        subprocess.Popen([exe_path])
        atualizar_status(status_text, "✅ Reorganizador de PDF iniciado.", "sucesso")
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível abrir o reorganizador de PDF:\n{e}")
        atualizar_status(status_text, f"⚠ Erro ao abrir reorganizador de PDF: {e}", "erro")

def iniciar_interface():
    """Inicializa a interface gráfica e conecta os botões às funções."""
    root = criar_janela()
    frame_menu, frame_main = criar_layout(root)
    status_text = criar_status_box(frame_main)
    callbacks = {
        "principal": lambda: gerar_principal_interativo(status_text),
        "secundario": lambda: gerar_secundario_interativo(status_text),
        "abrir_planilha": lambda: abrir_planilha(status_text),
        "reorganizar_pdf": lambda: abrir_reorganizador_pdf(status_text),
        "gerenciar_modelos": lambda: gerenciar_modelos(status_text),
        "converter_fotos": lambda: threading.Thread(target=converter_fotos_interativo, args=(status_text,), daemon=True).start()
    }
    criar_botoes(frame_menu, callbacks)
    root.mainloop()

if __name__ == "__main__":
    iniciar_interface()
