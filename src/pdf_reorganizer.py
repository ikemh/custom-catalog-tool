import sys
import os
import fitz  # PyMuPDF
from PyQt5 import QtWidgets, QtGui, QtCore
from PIL import Image
from io import BytesIO
from PyPDF2 import PdfFileReader, PdfFileWriter
from utils import get_base_path  # Função para obter o caminho base

# Define a pasta base do projeto
if getattr(sys, 'frozen', False):
    project_folder = get_base_path()
else:
    project_folder = os.path.abspath(os.path.dirname(__file__))

def pil2pixmap(im):
    """Converte uma imagem PIL para QPixmap."""
    im = im.convert("RGBA")
    data = im.tobytes("raw", "RGBA")
    qimage = QtGui.QImage(data, im.size[0], im.size[1], QtGui.QImage.Format_RGBA8888)
    return QtGui.QPixmap.fromImage(qimage)

class PDFPageWidget(QtWidgets.QWidget):
    """
    Widget que exibe a miniatura de uma página com seu índice e um botão para removê-la.
    """
    def __init__(self, pixmap, index, parent=None):
        super().__init__(parent)
        self.initUI(pixmap, index)

    def initUI(self, pixmap, index):
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        self.index_label = QtWidgets.QLabel(f"{index + 1}.")
        layout.addWidget(self.index_label)
        self.thumbnail_label = QtWidgets.QLabel(self)
        self.thumbnail_label.setPixmap(pixmap)
        layout.addWidget(self.thumbnail_label)
        self.remove_button = QtWidgets.QPushButton("Remover", self)
        self.remove_button.setObjectName("removeButton")
        layout.addWidget(self.remove_button)

class PDFManager(QtWidgets.QMainWindow):
    """
    Janela principal para gerenciamento do PDF.
    Permite:
      - Carregar PDF e exibir suas páginas
      - Reordenar (via drag & drop)
      - Remover páginas
      - Adicionar páginas a partir de imagens e PDFs
      - Salvar o PDF reorganizado utilizando PyPDF2 para mesclagem
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerenciador de PDF")
        self.resize(900, 600)
        self.doc = None                   # Documento PDF original (para visualização)
        self.original_pdf_path = None     # Caminho do PDF original carregado
        self.pages = []                   # Lista de páginas (cada página é um dicionário com dados)
        self.setupUI()

    def setupUI(self):
        central = QtWidgets.QWidget(self)
        self.setCentralWidget(central)
        vlayout = QtWidgets.QVBoxLayout(central)
        
        # Botões superiores
        hlayout = QtWidgets.QHBoxLayout()
        load_btn = QtWidgets.QPushButton("Carregar PDF")
        load_btn.clicked.connect(self.load_pdf)
        hlayout.addWidget(load_btn)
        add_page_btn = QtWidgets.QPushButton("Adicionar Imagem")
        add_page_btn.clicked.connect(self.add_page)
        hlayout.addWidget(add_page_btn)
        add_pdf_btn = QtWidgets.QPushButton("Adicionar PDF")
        add_pdf_btn.clicked.connect(self.add_pdf)
        hlayout.addWidget(add_pdf_btn)
        save_btn = QtWidgets.QPushButton("Salvar PDF")
        save_btn.clicked.connect(self.save_pdf)
        hlayout.addWidget(save_btn)
        vlayout.addLayout(hlayout)
        
        # Lista com suporte a drag & drop para reordenação
        self.listWidget = QtWidgets.QListWidget()
        self.listWidget.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        vlayout.addWidget(self.listWidget)

    def load_pdf(self):
        options = QtWidgets.QFileDialog.Options()
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Selecione o PDF", "", "PDF Files (*.pdf)", options=options)
        if fileName:
            fileName = os.path.normpath(fileName)
            self.doc = fitz.open(fileName)
            self.original_pdf_path = fileName
            self.pages = [{"source": "original", "page": i} for i in range(len(self.doc))]
            self.populate_list()

    def populate_list(self):
        """Cria os itens do QListWidget com base em self.pages, atualizando a numeração."""
        self.listWidget.clear()
        for i, page in enumerate(self.pages):
            item = QtWidgets.QListWidgetItem()
            item.setData(QtCore.Qt.UserRole, page)
            widget = self.create_item_widget(page, i)
            item.setSizeHint(widget.sizeHint())
            self.listWidget.addItem(item)
            self.listWidget.setItemWidget(item, widget)

    def create_item_widget(self, page, index):
        """
        Cria o widget que representa uma página.
        Renderiza uma miniatura baseada na fonte:
          - "original": página do PDF carregado
          - "image": imagem adicionada
          - "pdf": página de um PDF externo
        """
        if page["source"] == "original":
            page_obj = self.doc[page["page"]]
            mat = fitz.Matrix(0.2, 0.2)
            pix = page_obj.get_pixmap(matrix=mat)
            mode = "RGB" if pix.alpha == 0 else "RGBA"
            img = Image.frombytes(mode, (pix.width, pix.height), pix.samples)
            qpixmap = pil2pixmap(img)
        elif page["source"] == "image":
            image_path = os.path.normpath(page["image_path"])
            img = Image.open(image_path)
            img.thumbnail((100, 150))
            qpixmap = pil2pixmap(img)
        elif page["source"] == "pdf":
            ext_pdf = fitz.open(page["pdf_path"])
            page_obj = ext_pdf[page["page"]]
            mat = fitz.Matrix(0.2, 0.2)
            pix = page_obj.get_pixmap(matrix=mat)
            mode = "RGB" if pix.alpha == 0 else "RGBA"
            img = Image.frombytes(mode, (pix.width, pix.height), pix.samples)
            qpixmap = pil2pixmap(img)
        widget = PDFPageWidget(qpixmap, index)
        widget.remove_button.clicked.connect(lambda _, w=widget: self.remove_item(w))
        return widget

    def remove_item(self, widget):
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            if self.listWidget.itemWidget(item) == widget:
                self.listWidget.takeItem(i)
                self.update_pages_order()
                self.populate_list()
                break

    def update_pages_order(self):
        new_order = []
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            new_order.append(item.data(QtCore.Qt.UserRole))
        self.pages = new_order

    def add_page(self):
        """Adiciona uma página a partir de uma imagem."""
        options = QtWidgets.QFileDialog.Options()
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Selecione a Imagem", "", "Image Files (*.png *.jpg *.jpeg *.bmp)", options=options)
        if fileName:
            fileName = os.path.normpath(fileName)
            pos, ok = QtWidgets.QInputDialog.getInt(self, "Inserir Página", "Digite a posição para inserir a nova página:", value=len(self.pages) + 1, min=1, max=len(self.pages) + 1)
            if ok:
                new_page = {"source": "image", "page": None, "image_path": fileName}
                self.pages.insert(pos - 1, new_page)
                self.populate_list()

    def add_pdf(self):
        """Adiciona páginas a partir de um arquivo PDF externo."""
        options = QtWidgets.QFileDialog.Options()
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Selecione o PDF", "", "PDF Files (*.pdf)", options=options)
        if fileName:
            fileName = os.path.normpath(fileName)
            novo_pdf = fitz.open(fileName)
            pos, ok = QtWidgets.QInputDialog.getInt(self, "Inserir PDF", "Digite a posição para inserir as páginas do PDF:", value=len(self.pages) + 1, min=1, max=len(self.pages) + 1)
            if ok:
                for i in range(len(novo_pdf)):
                    nova_pagina = {"source": "pdf", "page": i, "pdf_path": fileName}
                    self.pages.insert(pos - 1, nova_pagina)
                    pos += 1
                self.populate_list()

    def save_pdf(self):
        """Salva o PDF reorganizado utilizando PyPDF2 para mesclagem de páginas."""
        if not self.pages:
            QtWidgets.QMessageBox.critical(self, "Erro", "Nenhuma página para salvar.")
            return
        options = QtWidgets.QFileDialog.Options()
        output, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Salvar PDF", os.path.join(os.getcwd(), "output.pdf"), "PDF Files (*.pdf)", options=options)
        if output:
            output = os.path.normpath(output)
            pdf_writer = PdfFileWriter()
            # Itera sobre cada página adicionada
            for page in self.pages:
                if page["source"] == "original":
                    pdf_reader = PdfFileReader(self.original_pdf_path)
                    pdf_writer.addPage(pdf_reader.getPage(page["page"]))
                elif page["source"] == "pdf":
                    pdf_reader = PdfFileReader(page["pdf_path"])
                    pdf_writer.addPage(pdf_reader.getPage(page["page"]))
                elif page["source"] == "image":
                    try:
                        image = Image.open(page["image_path"])
                    except Exception as e:
                        QtWidgets.QMessageBox.critical(self, "Erro", f"Erro ao abrir a imagem: {e}")
                        return
                    if image.mode in ("RGBA", "LA"):
                        image = image.convert("RGB")
                    buffer = BytesIO()
                    image.save(buffer, format="PDF")
                    buffer.seek(0)
                    pdf_image_reader = PdfFileReader(buffer)
                    pdf_writer.addPage(pdf_image_reader.getPage(0))
            with open(output, 'wb') as out_file:
                pdf_writer.write(out_file)
            QtWidgets.QMessageBox.information(self, "Sucesso", "PDF salvo com sucesso!")
            self.close()

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    dark_palette = QtGui.QPalette()
    dark_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
    dark_palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    dark_palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
    dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
    dark_palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    app.setPalette(dark_palette)
    app.setStyleSheet("""
        QPushButton {
            background-color: #333333;
            color: white;
            border: 1px solid #555555;
            border-radius: 5px;
            padding: 5px;
        }
        QPushButton:hover {
            background-color: #444444;
        }
        QPushButton#removeButton {
            min-width: 50px;
            background-color: #AA3333;
            border: 1px solid #BB4444;
            padding: 3px 5px;
        }
        QPushButton#removeButton:hover {
            background-color: #BB4444;
        }
    """)
    
    window = PDFManager()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
