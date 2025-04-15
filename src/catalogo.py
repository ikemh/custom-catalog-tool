import os
import re
import pandas as pd
from fpdf import FPDF
from tkinter import messagebox
from pdf_utils import processar_imagem, adicionar_pagina_com_imagem_simples
from catalog_groups import GRUPOS_PRINCIPAL, GRUPOS_SECUNDARIO
from utils import get_base_path  # Função para obter o caminho base

def get_documents_folder():
    """
    Retorna o caminho para a pasta "GeradorCatalogo" dentro dos Documentos do usuário.
    Se a pasta não existir, ela será criada.
    """
    docs = os.path.join(os.path.expanduser("~"), "Documents", "GeradorCatalogo")
    os.makedirs(docs, exist_ok=True)
    return docs

def get_user_data_folder():
    """
    Retorna o caminho para a pasta "data" dentro da pasta de documentos do usuário.
    Se a pasta não existir, ela será criada.
    """
    data_folder = os.path.join(get_documents_folder(), "data")
    os.makedirs(data_folder, exist_ok=True)
    return data_folder

def carregar_planilha(excel_file):
    excel_file = os.path.normpath(excel_file)
    # Se o arquivo não existir no caminho informado, tenta buscar na pasta de dados do usuário
    if not os.path.exists(excel_file):
        data_folder = get_user_data_folder()
        excel_file = os.path.join(data_folder, "Planilha_Catalogo_2025.ods")
    try:
        sheets = pd.read_excel(excel_file, sheet_name=None, engine="odf")
        df = sheets[list(sheets.keys())[0]]
        df.columns = df.iloc[3].astype(str).str.strip()
        df = df.iloc[4:].reset_index(drop=True)
        codigo_coluna = df.columns[4]

          # Debug: imprime os códigos únicos lidos da planilha
        df[codigo_coluna] = df[codigo_coluna].astype(str).str.strip().str.upper()
        print("Códigos únicos da planilha:", df[codigo_coluna].unique())

        preco_colunas = df.columns[12:19].tolist()
        return df, codigo_coluna, preco_colunas
    except FileNotFoundError:
        messagebox.showerror("Erro", f"Erro: O arquivo {excel_file} não foi encontrado.")
        return None, None, None
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar planilha: {str(e)}")
        return None, None, None

def get_prices_for_code(df, codigo_coluna, preco_colunas, code):
    # Normaliza o código de busca: remove espaços e converte para maiúsculas.
    search_code = str(code).strip().upper()
    
    # Normaliza a coluna de código da planilha
    df[codigo_coluna] = df[codigo_coluna].astype(str).str.strip().str.upper()
    
    # Cria uma expressão regular para casar o início do valor com o código procurado
    regex = re.compile(f"^{re.escape(search_code)}$")
    
    # Filtra as linhas onde o código começa com o search_code
    row = df[df[codigo_coluna].apply(lambda x: bool(regex.match(x)))]
    
    if row.empty:
        return {col: "N/A" for col in preco_colunas}
    
    return {col: f'{row[col].values[0]:.2f}' for col in preco_colunas}

def desenhar_cabecalho(pdf, table_x, table_y, total_width, cell_height, header_fill_color, header_text_color):
    """
    Desenha o cabeçalho da tabela.
    """
    pdf.set_xy(table_x, table_y)
    pdf.set_fill_color(*header_fill_color)
    pdf.set_text_color(*header_text_color)
    pdf.set_draw_color(218, 218, 218)
    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(total_width, cell_height, "Preços/Unidade", border=1, align='C', fill=True)
    pdf.ln(cell_height)

def desenhar_linhas_tabela(pdf, table_x, cell_height, cell_width_left, cell_width_right, preco_colunas, prices):
    """
    Desenha as linhas da tabela com efeito zebra.
    """
    pdf.set_text_color(48, 48, 48)
    pdf.set_font("Arial", size=14)
    fill = False
    for col in preco_colunas:
        pdf.set_x(table_x)
        if fill:
            pdf.set_fill_color(248, 248, 248)  # Cinza muito claro
        else:
            pdf.set_fill_color(255, 255, 255)    # Branco
        pdf.cell(cell_width_left, cell_height, col, border=1, align='L', fill=True)
        pdf.cell(cell_width_right, cell_height, f"R$ {prices[col]}", border=1, align='R', fill=True)
        pdf.ln(cell_height)
        fill = not fill

def gerar_catalogo(catalogo, image_folder, output_file, df, codigo_coluna, preco_colunas, position="left", status_text=None):
    """
    Gera o catálogo principal.
    Cabeçalho: fundo escuro e título em dourado (#F2D377).
    """
    pdf = None
    image_folder = os.path.normpath(image_folder)
    image_files = sorted(
        [f for f in os.listdir(image_folder) if f.lower().endswith((".jpg", ".png"))]
    )
    total_images = len(image_files)
    if not image_files:
        messagebox.showwarning("Aviso", f"Nenhuma imagem encontrada em {image_folder}.")
        return False

    if status_text:
        status_text.config(state="normal")
        status_text.insert("end", f"📄 Iniciando geração do catálogo: {catalogo} ({total_images} imagens)\n")
        status_text.config(state="disabled")
        status_text.see("end")

    for index, image_file in enumerate(image_files, start=1):
        image_path = os.path.normpath(os.path.join(image_folder, image_file))
        product_code = os.path.splitext(image_file)[0].split(' ')[0]
        if "capa" in product_code.lower():
            prices = {col: "N/A" for col in preco_colunas}
        else:
            prices = get_prices_for_code(df, codigo_coluna, preco_colunas, product_code)
        if os.path.exists(image_path):
            if status_text:
                status_text.config(state="normal")
                status_text.insert("end", f"🔄 [{index}/{total_images}] Processando {image_file}\n")
                status_text.config(state="disabled")
                status_text.see("end")
            img = processar_imagem(image_path)
            width, height = img.size
            cell_height = 26
            table_x = 0 if position == "left" else width - 0
            offset_vertical = 0
            table_y = 0
            cell_width_left = 135
            cell_width_right = 80
            total_width = cell_width_left + cell_width_right

            # Adiciona a página com a imagem sem cabeçalho
            pdf = adicionar_pagina_com_imagem_simples(pdf, img)
            # Apenas desenha a tabela se pelo menos um valor for diferente de "N/A"
            if not all(value == "N/A" for value in prices.values()):
                desenhar_cabecalho(pdf, table_x, table_y, total_width, cell_height,
                                   header_fill_color=(32, 32, 32),         # Fundo escuro
                                   header_text_color=(242, 211, 119))       # Texto dourado (#F2D377)
                desenhar_linhas_tabela(pdf, table_x, cell_height, cell_width_left, cell_width_right, preco_colunas, prices)
    if not output_file:
        output_file = os.path.join(get_documents_folder(), f"{catalogo}.pdf")
    
    output_dir_for_file = os.path.dirname(output_file)
    os.makedirs(output_dir_for_file, exist_ok=True)
    
    if os.path.exists(output_file):
        if not messagebox.askyesno("Arquivo existente", f"O arquivo {output_file} já existe. Deseja sobrescrevê-lo?"):
            return False
        try:
            os.remove(output_file)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível remover o arquivo existente:\n{e}")
            return False

    pdf.output(output_file)
    if status_text:
        status_text.config(state="normal")
        status_text.insert("end", f"✅ Catálogo {catalogo} gerado com sucesso!\n")
        status_text.config(state="disabled")
        status_text.see("end")
    return True

def gerar_catalogo_personalizado(catalogo, image_folder, output_file, df, codigo_coluna, preco_colunas,
                                  grupos_ordenados, grupos_dict, position="left", style="personalizado", status_text=None):
    """
    Gera o catálogo personalizado.
    Se style == "personalizado", utiliza cabeçalho com fundo das lâminas (#333333) e título em vermelho (#BF2B2B);
    se style == "principal", utiliza outro conjunto (ex.: fundo escuro e título dourado).
    """
    pdf = None
    total_imagens = 0
    image_folder = os.path.normpath(image_folder)
    
    for grupo in grupos_ordenados:
        prefixos = grupos_dict.get(grupo, [])
        imagens = sorted([
            f for f in os.listdir(image_folder)
            if f.lower().endswith((".jpg", ".png")) and any(f.startswith(pref) for pref in prefixos)
        ])
        total_imagens += len(imagens)
    
    if total_imagens == 0:
        messagebox.showwarning("Aviso", f"Nenhuma imagem encontrada em {image_folder} para os grupos selecionados.")
        return False

    if status_text:
        status_text.config(state="normal")
        status_text.insert("end", f"📄 Iniciando geração do catálogo: {catalogo} (total {total_imagens} imagens, organizadas por grupos)\n")
        status_text.config(state="disabled")
        status_text.see("end")

    cont_imagens = 0
    for grupo in grupos_ordenados:
        prefixos = grupos_dict.get(grupo, [])
        imagens = sorted([
            f for f in os.listdir(image_folder)
            if f.lower().endswith((".jpg", ".png")) and any(f.startswith(pref) for pref in prefixos)
        ])
        for image_file in imagens:
            cont_imagens += 1
            image_path = os.path.normpath(os.path.join(image_folder, image_file))
            if os.path.exists(image_path):
                if status_text:
                    status_text.config(state="normal")
                    status_text.insert("end", f"🔄 [{cont_imagens}/{total_imagens}] Processando {image_file} (Grupo: {grupo})\n")
                    status_text.config(state="disabled")
                    status_text.see("end")
                    product_code = os.path.splitext(image_file)[0].split(' ')[0]
                    if "capa" in product_code.lower():
                        prices = {col: "N/A" for col in preco_colunas}
                    else:
                        prices = get_prices_for_code(df, codigo_coluna, preco_colunas, product_code)
                img = processar_imagem(image_path)
                width, height = img.size
                cell_height = 25
                table_x = 0 if position == "left" else width - 280
                table_y = height - ((len(preco_colunas) + 1) * cell_height)
                cell_width_left = 120
                cell_width_right = 80
                total_width = cell_width_left + cell_width_right

                # Adiciona a página com a imagem sem cabeçalho
                pdf = adicionar_pagina_com_imagem_simples(pdf, img)
                
                # Apenas desenha a tabela se houver dados válidos (não todos "N/A")
                if not all(value == "N/A" for value in prices.values()):
                    if style == "principal":
                        header_fill_color = (32, 32, 32)         # Fundo escuro
                        header_text_color = (242, 211, 119)        # Texto dourado (#F2D377)
                        offset_vertical = 0
                        table_y = height - ((len(preco_colunas) + 1) * cell_height) - offset_vertical

                    else:  # style "personalizado" ou outro valor
                        header_fill_color = (77, 79, 89)           # Fundo: cor das lâminas (#333333)
                        header_text_color = (255, 255, 255)          # Texto: vermelho (#BF2B2B)
                        offset_vertical = 40
                        table_y = height - ((len(preco_colunas) + 1) * cell_height) - offset_vertical

                    
                    desenhar_cabecalho(pdf, table_x, table_y, total_width, cell_height,
                                       header_fill_color=header_fill_color,
                                       header_text_color=header_text_color)
                    desenhar_linhas_tabela(pdf, table_x, cell_height, cell_width_left, cell_width_right, preco_colunas, prices)
    if not output_file:
        output_file = os.path.join(get_documents_folder(), f"{catalogo}.pdf")
    
    output_dir_for_file = os.path.dirname(output_file)
    os.makedirs(output_dir_for_file, exist_ok=True)
    
    if os.path.exists(output_file):
        if not messagebox.askyesno("Arquivo existente", f"O arquivo {output_file} já existe. Deseja sobrescrevê-lo?"):
            return False
        try:
            os.remove(output_file)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível remover o arquivo existente:\n{e}")
            return False

    pdf.output(output_file)
    if status_text:
        status_text.config(state="normal")
        status_text.insert("end", f"✅ Catálogo {catalogo} gerado com sucesso!\n")
        status_text.config(state="disabled")
        status_text.see("end")
    return True
