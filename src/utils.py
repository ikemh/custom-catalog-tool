# src/utils.py
import os
import sys

def get_base_path():
    if getattr(sys, 'frozen', False):
        # Rodando dentro de um executável PyInstaller
        return sys._MEIPASS
    else:
        # Rodando em modo normal (fora do PyInstaller)
        return os.path.dirname(__file__)
