
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
## Geração de Executáveis

O projeto pode ser empacotado de duas formas distintas, a depender do objetivo de distribuição:

### PyInstaller (empacotamento prático)

#### `main.py`

```bash
pyinstaller --clean --windowed --icon=icone.ico --paths=src ^
  --add-data "src\\logo.png;." --distpath dist src\\main.py
```

Gera um executável leve em dist\
Oculta o console (--windowed)
Inclui o ícone e o arquivo logo.png
Utiliza a pasta src como base para localizar os módulos auxiliares

#### pdf_reorganizer.py
```
pyinstaller --windowed --icon=icone.ico --paths=src ^
  --distpath dist\\main --name pdf_reorganizer src\\pdf_reorganizer.py
```

Gera o utilitário auxiliar pdf_reorganizer.exe
Organizado dentro do diretório dist\main\


### Nuitka (compilação otimizada e proteção de código)

#### main.py

```
nuitka --standalone --msvc=latest --windows-console-mode=disable ^
  --windows-icon-from-ico=icone.ico ^
  --include-data-file=src/logo.png=logo.png ^
  --enable-plugin=tk-inter --verbose src/main.py
```

Compila o código Python em C para otimização de performance
Ideal para distribuições finais com maior proteção contra engenharia reversa
Produz uma pasta standalone com todas as dependências incluídas

Requisitos:

Nuitka instalado (pip install nuitka)

Visual Studio Build Tools com MSVC habilitado

tkinter instalado e funcional no ambiente Python

Estrutura de saída esperada
dist\main.exe (via PyInstaller)

dist\main\pdf_reorganizer.exe (via PyInstaller)

main.build\ ou main.dist\ (se gerado via Nuitka)

## Segurança e Política de Uso

- **Distribuição:** Proibida sem autorização formal, mesmo que partes do código usem licenças open-source.
- **Dados Sensíveis:** Planilhas e arquivos de clientes devem ser mantidos fora do repositório.
- **Execução:** Recomendado uso apenas em ambiente interno controlado (ex: rede corporativa).

## Manutenção

Este projeto é mantido sob contrato e uso exclusivo do cliente. Alterações devem seguir validação técnica e formalização adequada.

---

*Todos os direitos reservados. Uso e redistribuição restritos conforme acordado contratualmente.*
