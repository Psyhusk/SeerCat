#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SeerCat v5.0 — Script de Build (PyInstaller)
============================================
Compila o instalador imersivo em executável único.
Execute este script no mesmo diretório que 'seercat_v5_installer.py'.

Pré-requisitos:
  pip install pyinstaller PySide6 pygame reportlab

Uso:
  python build_seercat.py

Resultado:
  dist/seercat_v5_installer   (Linux/macOS)
  dist/seercat_v5_installer.exe  (Windows)
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

# ─── Configuração do build ────────────────────────────────
NOME_APP    = "SeerCat_v5_Installer"
SCRIPT_MAIN = "seercat_v5_installer.py"
ICONE_PNG   = "26050.jpg"   # ícone fornecido pelo usuário

# Arquivos extras a incluir no bundle (opcional)
# Coloque 'bad_apple.mp3' no mesmo diretório para áudio
DATAS_EXTRAS = []
if os.path.exists("bad_apple.mp3"):
    DATAS_EXTRAS.append(("bad_apple.mp3", "."))

def verificar_pyinstaller():
    """Verifica se PyInstaller está instalado."""
    try:
        import PyInstaller
        print(f"[+] PyInstaller {PyInstaller.__version__} disponível.")
        return True
    except ImportError:
        print("[!] PyInstaller não encontrado. Instalando...")
        ret = subprocess.run(
            [sys.executable, "-m", "pip", "install", "pyinstaller"],
            capture_output=True, text=True
        )
        if ret.returncode == 0:
            print("[+] PyInstaller instalado com sucesso.")
            return True
        else:
            print(f"[-] Falha ao instalar PyInstaller: {ret.stderr}")
            return False

def converter_icone():
    """Converte o ícone JPG para ICO/PNG conforme a plataforma."""
    import platform
    so = platform.system()

    # Tenta converter com Pillow
    try:
        from PIL import Image
        img = Image.open(ICONE_PNG)
        img = img.resize((256, 256), Image.LANCZOS)

        if so == "Windows":
            ico_path = "seercat_icon.ico"
            img.save(ico_path, format="ICO", sizes=[(256,256),(128,128),(64,64),(32,32)])
        else:
            ico_path = "seercat_icon.png"
            img.save(ico_path, format="PNG")

        print(f"[+] Ícone convertido: {ico_path}")
        return ico_path
    except ImportError:
        print("[!] Pillow não encontrado — build sem ícone customizado.")
        print("    Instale com: pip install Pillow")
        return None
    except Exception as e:
        print(f"[!] Erro ao converter ícone: {e}")
        return None

def build():
    """Executa o build do PyInstaller."""
    if not verificar_pyinstaller():
        sys.exit(1)

    if not os.path.exists(SCRIPT_MAIN):
        print(f"[-] Script não encontrado: {SCRIPT_MAIN}")
        print("    Certifique-se de que 'seercat_v5_installer.py' está no diretório atual.")
        sys.exit(1)

    # Ícone
    icone_path = None
    if os.path.exists(ICONE_PNG):
        icone_path = converter_icone()

    # Monta comando PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                     # executável único
        "--windowed",                    # sem janela de console no Windows
        "--name", NOME_APP,
        "--clean",                       # limpa cache antes
        "--noconfirm",                   # não pede confirmação
    ]

    # Ícone (se disponível)
    if icone_path and os.path.exists(icone_path):
        cmd += ["--icon", icone_path]

    # Dados extras (áudio, etc.)
    for src, dst in DATAS_EXTRAS:
        cmd += ["--add-data", f"{src}{os.pathsep}{dst}"]

    # Hidden imports necessários para PySide6/pygame/reportlab
    hidden_imports = [
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "pygame",
        "pygame.mixer",
        "reportlab",
        "reportlab.platypus",
        "reportlab.lib.pagesizes",
        "reportlab.lib.styles",
        "reportlab.lib.units",
        "reportlab.lib.colors",
        "reportlab.lib.enums",
        "scapy",
        "nmap",
        "netifaces",
        "psutil",
        "cryptography",
        "paramiko",
    ]
    for hi in hidden_imports:
        cmd += ["--hidden-import", hi]

    # Coleta de submódulos inteiros
    for collect in ["PySide6", "pygame", "reportlab", "scapy"]:
        cmd += ["--collect-submodules", collect]

    # Script principal
    cmd.append(SCRIPT_MAIN)

    print("\n[>] Iniciando build PyInstaller...")
    print(f"    Comando: {' '.join(cmd[:8])}... [{SCRIPT_MAIN}]")
    print()

    resultado = subprocess.run(cmd, text=True)

    if resultado.returncode == 0:
        print("\n" + "=" * 60)
        print(f"  BUILD CONCLUÍDO COM SUCESSO!")
        print("=" * 60)

        import platform
        ext = ".exe" if platform.system() == "Windows" else ""
        binario = Path("dist") / f"{NOME_APP}{ext}"
        if binario.exists():
            tamanho = binario.stat().st_size / (1024 * 1024)
            print(f"  Executável: {binario}")
            print(f"  Tamanho:    {tamanho:.1f} MB")
        print()
        print("  Para distribuir, copie apenas o arquivo em dist/")
    else:
        print("\n[-] Build falhou. Verifique os erros acima.")
        sys.exit(1)

if __name__ == "__main__":
    build()
