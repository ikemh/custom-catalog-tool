
# Projeto Catálogo para Corte a Laser

## Descrição

Este sistema foi desenvolvido sob demanda para um cliente do segmento B2B especializado em corte a laser para cuteleiros. A aplicação visa automatizar a geração de catálogos de produtos com base em planilhas e imagens, permitindo a criação de PDFs organizados e visualmente padronizados com informações como preços, grupos e modelos.

A interface gráfica foi construída com `Tkinter` e `ttkbootstrap`, com funcionalidades voltadas para:

- Gerenciamento e reordenação de grupos e modelos.
- Geração de catálogos em PDF a partir de dados tabulares.
- Reorganização visual de páginas PDF para finalização e revisão.

> **IMPORTANTE:** Apesar do uso de bibliotecas open-source, este código é de uso exclusivo do cliente contratante e está protegido contratualmente contra redistribuição, cópia ou modificação sem autorização formal.

## Funcionalidades

- Geração de catálogos PDF com layout customizado.
- Interface para manipulação de grupos de produtos.
- Ferramenta auxiliar de reorganização de páginas PDF.
- Scripts de instalação e empacotamento (.nsi, PyInstaller).

## Estrutura do Projeto

```
projeto_catalogo/
├── catalog_groups.py
├── catalogo.py
├── gui_components.py
├── gui_logic.py
├── main.py
├── pdf_utils.py
├── pdf_reorganizer.py
├── utils.py
├── requirements.txt
├── icone.ico
├── *.nsi (scripts de instalação)
├── *.spec (configuração PyInstaller)
├── src/
├── *.dist/, *.build/ (diretórios de build)
└── arquivos sensíveis (omitidos do repositório)
```

## Requisitos

- Python 3.10+
- Dependências listadas em `requirements.txt`, incluindo:
  - `pandas`, `fpdf`, `Pillow`
  - `PyMuPDF`, `PyPDF2`
  - `ttkbootstrap`, `PyQt5`

## Execução

### Ambiente de Desenvolvimento

1. Clone o repositório:
```bash
git clone git@github.com:seuusuario/projeto_catalogo.git
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute a aplicação principal:
```bash
python main.py
```

### Geração de Executável

Para empacotar a aplicação com PyInstaller:
```bash
pyinstaller --onefile --noconsole main.py
```

O executável será gerado no diretório `dist/`.

## Segurança e Política de Uso

- **Distribuição:** Proibida sem autorização formal, mesmo que partes do código usem licenças open-source.
- **Dados Sensíveis:** Planilhas e arquivos de clientes devem ser mantidos fora do repositório.
- **Execução:** Recomendado uso apenas em ambiente interno controlado (ex: rede corporativa).

## Manutenção

Este projeto é mantido sob contrato e uso exclusivo do cliente. Alterações devem seguir validação técnica e formalização adequada.

---

*Todos os direitos reservados. Uso e redistribuição restritos conforme acordado contratualmente.*
