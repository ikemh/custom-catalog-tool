import os
from PIL import Image
from io import BytesIO
from fpdf import FPDF
from utils import get_base_path  # Função para obter o caminho base

def processar_imagem(image_path, max_size=(1024, 1024)):
    """
    Processa e retorna uma cópia da imagem redimensionada para o tamanho máximo especificado.
    """
    # Normaliza o caminho para garantir compatibilidade no Windows
    image_path = os.path.normpath(image_path)
    # Se o arquivo não existir, tenta procurar na pasta base (ex: em ambiente empacotado)
    if not os.path.exists(image_path):
        base_path = get_base_path()
        image_path = os.path.join(base_path, image_path)
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        img.thumbnail(max_size)
        return img.copy()

def adicionar_pagina_com_imagem_simples(pdf, img):
    """
    Adiciona uma nova página ao PDF com a imagem fornecida.
    Essa função não desenha cabeçalho nem tabela, apenas insere a imagem.
    """
    width, height = img.size
    if pdf is None:
        pdf = FPDF(unit="pt", format=(width, height))
        pdf.set_auto_page_break(auto=False, margin=0)
        pdf.set_margins(0, 0, 0)
    pdf.add_page(format=(width, height))
    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    buffer.seek(0)
    pdf.image(buffer, 0, 0, width, height)
    buffer.close()
    return pdf
