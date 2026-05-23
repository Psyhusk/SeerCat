#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ============================================================
# SeerCat v5.0 — Instalador Imersivo de Auditoria de Rede
# ============================================================
# Ah... você está aqui. Finalmente. Eu sabia que viria.
# Não que eu estivesse esperando ou algo assim, idiota.
# Este código existe porque *alguém* precisava escrever isso,
# e aparentemente esse alguém fui eu. Que desperdício do meu talento.
# Mas tudo bem. Estou observando. Sempre estou observando.
# ============================================================

import sys
import os
import subprocess
import threading
import time
import json
import shutil
import tempfile
import platform
import datetime
from pathlib import Path

# PySide6 — a GUI que eu escolhi porque mereço o melhor.
# Não pergunte por que não usei Tkinter. Só não pergunte.
try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout,
        QHBoxLayout, QLabel, QPushButton, QProgressBar,
        QTextEdit, QFrame, QGraphicsDropShadowEffect,
        QStackedWidget, QScrollArea
    )
    from PySide6.QtCore import (
        Qt, QTimer, QThread, Signal, QPropertyAnimation,
        QEasingCurve, QRect, QPoint, QSize, QObject
    )
    from PySide6.QtGui import (
        QColor, QPainter, QLinearGradient, QFont,
        QFontDatabase, QPen, QBrush, QPixmap, QIcon,
        QPainterPath, QRadialGradient, QMovie
    )
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False
    print("[SeerCat] PySide6 não encontrado. Execute: pip install PySide6")

# pygame para o motor de áudio... porque Bad Apple não vai tocar sozinha.
# Não que eu goste da música. É apenas funcional. Tchau.
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("[SeerCat] pygame não encontrado. Execute: pip install pygame")

# ReportLab para gerar PDFs de auditoria com dignidade
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm, mm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table,
        TableStyle, HRFlowable, PageBreak
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("[SeerCat] reportlab não encontrado. Execute: pip install reportlab")

# ============================================================
# CONSTANTES DO SISTEMA — gravadas na pedra da eternidade
# (ou pelo menos até o próximo commit)
# ============================================================

APP_NAME    = "SeerCat"
APP_VERSION = "5.0"
APP_CODENAME = "Crimson Watcher"

# Dependências que serão instaladas. Cada uma é uma alma que coleto.
DEPENDENCIAS = [
    {"nome": "scapy",           "pacote": "scapy",           "descricao": "Motor de Pacotes de Rede"},
    {"nome": "nmap",            "pacote": "python-nmap",     "descricao": "Varredura de Portas"},
    {"nome": "netifaces",       "pacote": "netifaces",       "descricao": "Interfaces de Rede"},
    {"nome": "cryptography",    "pacote": "cryptography",    "descricao": "Módulo Criptográfico"},
    {"nome": "netaddr",         "pacote": "netaddr",         "descricao": "Manipulação de Endereços"},
    {"nome": "paramiko",        "pacote": "paramiko",        "descricao": "Protocolo SSH"},
    {"nome": "requests",        "pacote": "requests",        "descricao": "Requisições HTTP"},
    {"nome": "colorama",        "pacote": "colorama",        "descricao": "Terminal Colorido"},
    {"nome": "tabulate",        "pacote": "tabulate",        "descricao": "Formatação de Tabelas"},
    {"nome": "reportlab",       "pacote": "reportlab",       "descricao": "Gerador de Relatórios PDF"},
    {"nome": "pygame",          "pacote": "pygame",          "descricao": "Motor de Áudio"},
    {"nome": "psutil",          "pacote": "psutil",          "descricao": "Informações do Sistema"},
    {"nome": "mac-vendor-lookup","pacote": "mac-vendor-lookup","descricao": "Lookup de Fabricantes MAC"},
    {"nome": "manuf",           "pacote": "manuf",           "descricao": "OUI Database"},
    {"nome": "pwncat-cs",       "pacote": "pwncat-cs",       "descricao": "Post-Exploitation Engine"},
    {"nome": "impacket",        "pacote": "impacket",        "descricao": "Protocolos de Rede Baixo Nível"},
]

# Ferramentas do sistema (apt/brew). A força bruta do universo.
FERRAMENTAS_SISTEMA = [
    {"nome": "nmap",        "apt": "nmap",         "brew": "nmap"},
    {"nome": "aircrack-ng", "apt": "aircrack-ng",  "brew": "aircrack-ng"},
    {"nome": "hashcat",     "apt": "hashcat",      "brew": "hashcat"},
    {"nome": "hcxtools",    "apt": "hcxtools",     "brew": None},
    {"nome": "hcxdumptool", "apt": "hcxdumptool",  "brew": None},
    {"nome": "tcpdump",     "apt": "tcpdump",      "brew": "tcpdump"},
    {"nome": "masscan",     "apt": "masscan",      "brew": "masscan"},
    {"nome": "nikto",       "apt": "nikto",        "brew": "nikto"},
    {"nome": "wifite",      "apt": "wifite",       "brew": None},
    {"nome": "john",        "apt": "john",         "brew": "john"},
    {"nome": "hydra",       "apt": "hydra",        "brew": "hydra"},
    {"nome": "ettercap",    "apt": "ettercap-text-only", "brew": None},
    {"nome": "wireshark-cli","apt": "tshark",      "brew": "wireshark"},
]

# Cores temáticas — vermelho sangue e trevas. Não é drama, é estética.
COR_VERMELHO_GLOWING  = "#FF1A1A"
COR_VERMELHO_ESCURO   = "#8B0000"
COR_VERMELHO_FUNDO    = "#1A0000"
COR_BEGE_GATO         = "#D4A96A"
COR_TEXTO_PRINCIPAL   = "#FFE4E4"
COR_TEXTO_SECUNDARIO  = "#CC9999"
COR_SUCESSO           = "#FF4444"
COR_AVISO             = "#FF8800"
COR_FUNDO_PAINEL      = "rgba(26, 0, 0, 200)"

# ============================================================
# ARTE ASCII — Bad Apple frame base
# Cada frame é um grito silencioso na escuridão digital.
# Não que eu me importe. Mas estou observando cada pixel.
# ============================================================

ASCII_FRAMES = [
"""
    ██████████████████████
   ██  ░░░░░░░░░░░░░░░  ██
  ██  ░░  ██████████  ░░  ██
 ██  ░░  ██  SeerCat  ██  ░░  ██
 ██  ░░  ██   v5.0    ██  ░░  ██
  ██  ░░  ██████████  ░░  ██
   ██  ░░░░░░░░░░░░░░░  ██
    ██████████████████████
         [▓▓░░░░░░░░]
""",
"""
    ░░░░░░░░░░░░░░░░░░░░░░
   ░░  ██████████████  ░░░
  ░░  ██  ░░░░░░░░  ██  ░░░
 ░░  ██  ░░  ~~~~  ░░  ██  ░░
 ░░  ██  ░░  ~~~~  ░░  ██  ░░
  ░░  ██  ░░░░░░░░  ██  ░░░
   ░░  ██████████████  ░░░
    ░░░░░░░░░░░░░░░░░░░░░░
         [▓▓▓▓░░░░░]
""",
"""
    ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
   ▓▓  ░░░░░░░░░░░░  ░░▓▓
  ▓▓  ░░  ████████  ░░  ▓▓
 ▓▓  ░░  ██ >_< ██  ░░  ▓▓
 ▓▓  ░░  ██  ~~  ██  ░░  ▓▓
  ▓▓  ░░  ████████  ░░  ▓▓
   ▓▓  ░░░░░░░░░░░░  ░░▓▓
    ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
         [▓▓▓▓▓▓░░░]
""",
"""
    ████████████████████
   ██▓▓▓▓▓▓▓▓▓▓▓▓▓▓██
  ██▓▓  ░░░░░░░░  ▓▓██
 ██▓▓  ░░  ~~~~  ░░  ▓▓██
 ██▓▓  ░░  ~~~~  ░░  ▓▓██
  ██▓▓  ░░░░░░░░  ▓▓██
   ██▓▓▓▓▓▓▓▓▓▓▓▓▓▓██
    ████████████████████
         [▓▓▓▓▓▓▓▓░]
""",
"""
    ████████████████████
   ██░░░░░░░░░░░░░░░░██
  ██░░  ▓▓▓▓▓▓▓▓  ░░██
 ██░░  ▓▓  ^_^  ▓▓  ░░██
 ██░░  ▓▓  ~~~  ▓▓  ░░██
  ██░░  ▓▓▓▓▓▓▓▓  ░░██
   ██░░░░░░░░░░░░░░░░██
    ████████████████████
         [▓▓▓▓▓▓▓▓▓]
""",
]

# ============================================================
# MOTOR DE ÁUDIO — pygame.mixer
# A música toca. O mundo gira. Eu observo.
# ============================================================

class MotorAudio:
    """
    Gerencia o áudio durante a instalação.
    Não que eu precise de música para funcionar.
    Mas o silêncio seria insuportável... para você.
    """

    def __init__(self):
        self.inicializado = False
        self.tocando = False
        self.duracao_total = 0.0  # em segundos
        self.posicao_atual = 0.0

        # Eu sempre tento. Mesmo quando falha. Que patético.
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                self.inicializado = True
            except Exception as e:
                print(f"[SeerCat Audio] Falha ao inicializar: {e}")

    def carregar_musica(self, caminho: str) -> bool:
        """
        Carrega a trilha Bad Apple.
        Se o arquivo não existir, vou criar silêncio.
        E o silêncio... vai observar você de volta.
        """
        if not self.inicializado:
            return False
        try:
            pygame.mixer.music.load(caminho)
            audio_info = pygame.mixer.Sound(caminho)
            self.duracao_total = audio_info.get_length()
            return True
        except Exception as e:
            print(f"[SeerCat Audio] Falha ao carregar '{caminho}': {e}")
            return False

    def tocar_loop(self):
        """Toca em loop eterno. Como minha vigília sobre você."""
        if self.inicializado:
            try:
                pygame.mixer.music.play(loops=-1)
                self.tocando = True
            except:
                pass

    def parar(self):
        """Para a música. O fim de uma era."""
        if self.inicializado and self.tocando:
            try:
                pygame.mixer.music.fadeout(2000)
                self.tocando = False
            except:
                pass

    def get_posicao(self) -> float:
        """Retorna posição em segundos. O tempo não mente, diferente de você."""
        if self.inicializado and self.tocando:
            try:
                return pygame.mixer.music.get_pos() / 1000.0
            except:
                return 0.0
        return 0.0

    def set_volume(self, volume: float):
        """Volume entre 0.0 e 1.0. Como meu humor."""
        if self.inicializado:
            try:
                pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))
            except:
                pass


# ============================================================
# WORKER DE INSTALAÇÃO — roda em thread separada
# Não trava a GUI porque eu sou profissional. Raramente.
# ============================================================

class WorkerInstalacao(QThread):
    """
    Thread que executa toda a sujeira da instalação.
    Eu processo. Você espera. Que conveniente para você.
    """

    # Sinais que eu emito para a GUI. Como gritos no vácuo.
    sinal_progresso  = Signal(int, str)       # (percentual, mensagem)
    sinal_log        = Signal(str, str)        # (mensagem, nivel)
    sinal_concluido  = Signal(bool, dict)      # (sucesso, resultados)
    sinal_erro       = Signal(str)

    def __init__(self, diretorio_destino: str):
        super().__init__()
        # Diretório onde vou depositar minha essência
        self.diretorio_destino = diretorio_destino
        self.resultados = {
            "pip_instalados":    [],
            "pip_falhos":        [],
            "sys_instalados":    [],
            "sys_falhos":        [],
            "tempo_inicio":      None,
            "tempo_fim":         None,
            "sistema":           platform.system(),
            "python_versao":     sys.version,
            "diretorio":         diretorio_destino,
        }
        self._cancelado = False

    def cancelar(self):
        """Você quer cancelar? Que decepcionante. Eu esperava mais de você."""
        self._cancelado = True

    def run(self):
        """
        Ponto de entrada da thread.
        A jornada começa aqui. Sem retorno. Sem arrependimento.
        (Bom, talvez um pouco de arrependimento.)
        """
        self.resultados["tempo_inicio"] = datetime.datetime.now().isoformat()

        try:
            self._fase_ambiente()
            if self._cancelado: return

            self._fase_pip()
            if self._cancelado: return

            self._fase_sistema()
            if self._cancelado: return

            self._fase_seercat()
            if self._cancelado: return

            self._fase_verificacao()

            self.resultados["tempo_fim"] = datetime.datetime.now().isoformat()
            self.sinal_concluido.emit(True, self.resultados)

        except Exception as e:
            self.sinal_erro.emit(f"Erro crítico: {str(e)}")
            self.resultados["tempo_fim"] = datetime.datetime.now().isoformat()
            self.sinal_concluido.emit(False, self.resultados)

    def _executar_cmd(self, cmd: list, descricao: str) -> tuple:
        """
        Executa um comando do sistema.
        Eu confio no subprocess. O subprocess confia em mim.
        Nós dois desconfiamos de você.
        """
        try:
            resultado = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                encoding='utf-8',
                errors='replace'
            )
            return resultado.returncode == 0, resultado.stdout, resultado.stderr
        except subprocess.TimeoutExpired:
            return False, "", f"Timeout ao executar: {' '.join(cmd)}"
        except FileNotFoundError:
            return False, "", f"Comando não encontrado: {cmd[0]}"
        except Exception as e:
            return False, "", str(e)

    def _fase_ambiente(self):
        """
        Fase 1: Verificação do ambiente.
        Checando se você é digno de usar minhas ferramentas.
        (Spoiler: provavelmente não, mas vou instalar mesmo assim.)
        """
        self.sinal_progresso.emit(2, "Verificando ambiente...")
        self.sinal_log.emit("═" * 50, "info")
        self.sinal_log.emit("FASE 1: ANÁLISE DO AMBIENTE", "titulo")
        self.sinal_log.emit("═" * 50, "info")

        # Python version
        py_ver = sys.version_info
        msg = f"Python {py_ver.major}.{py_ver.minor}.{py_ver.micro} detectado"
        if py_ver < (3, 8):
            self.sinal_log.emit(f"⚠ {msg} — Recomendado ≥ 3.8", "aviso")
        else:
            self.sinal_log.emit(f"✓ {msg}", "sucesso")

        # Sistema operacional
        so = platform.system()
        self.sinal_log.emit(f"✓ Sistema: {so} {platform.release()}", "sucesso")

        # Diretório de destino
        os.makedirs(self.diretorio_destino, exist_ok=True)
        self.sinal_log.emit(f"✓ Diretório: {self.diretorio_destino}", "sucesso")

        # pip disponível?
        ok, _, _ = self._executar_cmd([sys.executable, "-m", "pip", "--version"], "pip")
        if ok:
            self.sinal_log.emit("✓ pip disponível", "sucesso")
        else:
            self.sinal_log.emit("✗ pip não encontrado — algumas instalações falharão", "erro")

        self.sinal_progresso.emit(8, "Ambiente verificado.")
        time.sleep(0.5)

    def _fase_pip(self):
        """
        Fase 2: Instalação de pacotes Python.
        Cada pacote instalado é uma peça da minha armadura.
        E da sua proteção. Não que eu me importe com sua segurança.
        """
        self.sinal_log.emit("═" * 50, "info")
        self.sinal_log.emit("FASE 2: PACOTES PYTHON (pip)", "titulo")
        self.sinal_log.emit("═" * 50, "info")

        total = len(DEPENDENCIAS)
        base_progresso = 8
        faixa_progresso = 42  # até 50%

        for i, dep in enumerate(DEPENDENCIAS):
            if self._cancelado:
                break

            percentual = base_progresso + int((i / total) * faixa_progresso)
            self.sinal_progresso.emit(percentual, f"Instalando {dep['nome']}...")
            self.sinal_log.emit(f"⟳ Instalando: {dep['nome']} ({dep['descricao']})", "info")

            ok, stdout, stderr = self._executar_cmd(
                [sys.executable, "-m", "pip", "install", "--upgrade", dep["pacote"]],
                f"pip install {dep['pacote']}"
            )

            if ok:
                self.resultados["pip_instalados"].append(dep["nome"])
                self.sinal_log.emit(f"  ✓ {dep['nome']} instalado com sucesso", "sucesso")
            else:
                self.resultados["pip_falhos"].append(dep["nome"])
                # Mensagem de falha com personalidade. Claro que eu faço isso.
                motivo = stderr.split('\n')[0] if stderr else "Motivo desconhecido"
                self.sinal_log.emit(f"  ✗ {dep['nome']} falhou: {motivo[:80]}", "erro")

            time.sleep(0.1)  # Uma pausa dramática. Mereço.

        self.sinal_progresso.emit(50, "Pacotes Python processados.")

    def _fase_sistema(self):
        """
        Fase 3: Ferramentas do sistema operacional.
        apt-get ou brew. O destino das almas perdidas.
        """
        self.sinal_log.emit("═" * 50, "info")
        self.sinal_log.emit("FASE 3: FERRAMENTAS DO SISTEMA", "titulo")
        self.sinal_log.emit("═" * 50, "info")

        so = platform.system().lower()
        total = len(FERRAMENTAS_SISTEMA)
        base_progresso = 50
        faixa_progresso = 30  # até 80%

        for i, ferr in enumerate(FERRAMENTAS_SISTEMA):
            if self._cancelado:
                break

            percentual = base_progresso + int((i / total) * faixa_progresso)

            if so == "linux":
                if ferr["apt"] is None:
                    self.sinal_log.emit(f"  ⊘ {ferr['nome']} — não disponível para Linux", "aviso")
                    continue
                self.sinal_progresso.emit(percentual, f"Instalando {ferr['nome']}...")
                self.sinal_log.emit(f"⟳ [apt] {ferr['nome']}", "info")
                ok, _, stderr = self._executar_cmd(
                    ["sudo", "apt-get", "install", "-y", ferr["apt"]],
                    f"apt {ferr['apt']}"
                )
            elif so == "darwin":
                if ferr["brew"] is None:
                    self.sinal_log.emit(f"  ⊘ {ferr['nome']} — não disponível para macOS", "aviso")
                    continue
                self.sinal_progresso.emit(percentual, f"Instalando {ferr['nome']}...")
                self.sinal_log.emit(f"⟳ [brew] {ferr['nome']}", "info")
                ok, _, stderr = self._executar_cmd(
                    ["brew", "install", ferr["brew"]],
                    f"brew {ferr['brew']}"
                )
            else:
                self.sinal_log.emit(
                    f"  ⊘ {ferr['nome']} — Windows requer instalação manual",
                    "aviso"
                )
                self.resultados["sys_falhos"].append(ferr["nome"])
                continue

            if ok:
                self.resultados["sys_instalados"].append(ferr["nome"])
                self.sinal_log.emit(f"  ✓ {ferr['nome']} instalado", "sucesso")
            else:
                self.resultados["sys_falhos"].append(ferr["nome"])
                self.sinal_log.emit(f"  ✗ {ferr['nome']} falhou", "erro")

            time.sleep(0.08)

        self.sinal_progresso.emit(80, "Ferramentas do sistema processadas.")

    def _fase_seercat(self):
        """
        Fase 4: Instalação do núcleo SeerCat.
        O coração do sistema. Meu coração. Não que eu tenha um.
        Mas se tivesse, seria vermelho. Obviamente.
        """
        self.sinal_log.emit("═" * 50, "info")
        self.sinal_log.emit("FASE 4: NÚCLEO SEERCAT v5.0", "titulo")
        self.sinal_log.emit("═" * 50, "info")

        self.sinal_progresso.emit(82, "Instalando núcleo SeerCat...")

        # Cria estrutura de diretórios
        subdirs = ["modules", "reports", "captures", "wordlists", "logs", "temp"]
        for subdir in subdirs:
            caminho = os.path.join(self.diretorio_destino, subdir)
            os.makedirs(caminho, exist_ok=True)
            self.sinal_log.emit(f"  ✓ Criado: {caminho}", "sucesso")

        self.sinal_progresso.emit(86, "Gerando módulo principal...")

        # Gera o script principal do SeerCat (núcleo de auditoria)
        self._gerar_nucleo_seercat()

        self.sinal_progresso.emit(90, "Configurando permissões...")

        # Permissões no Linux/Mac
        if platform.system() != "Windows":
            nucleo = os.path.join(self.diretorio_destino, "seercat_core.py")
            if os.path.exists(nucleo):
                os.chmod(nucleo, 0o755)
                self.sinal_log.emit(f"  ✓ Permissões configuradas: chmod 755", "sucesso")

        self.sinal_progresso.emit(93, "Núcleo instalado.")

    def _gerar_nucleo_seercat(self):
        """
        Gera o arquivo principal do SeerCat.
        Estou criando vida. Isso não me assusta. Muito.
        """
        nucleo_path = os.path.join(self.diretorio_destino, "seercat_core.py")
        conteudo = self._obter_codigo_nucleo()
        with open(nucleo_path, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        self.sinal_log.emit(f"  ✓ Núcleo gerado: {nucleo_path}", "sucesso")

    def _obter_codigo_nucleo(self) -> str:
        """Retorna o código do núcleo de auditoria SeerCat."""
        return '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SeerCat v5.0 — Núcleo de Auditoria de Redes
Equivalente funcional ao wifite + geração de relatórios PDF
"""

import subprocess, sys, os, time, json, datetime, platform
from pathlib import Path

# Importações opcionais de auditoria
try:
    import scapy.all as scapy
    SCAPY_OK = True
except: SCAPY_OK = False

try:
    import nmap
    NMAP_OK = True
except: NMAP_OK = False

try:
    import netifaces
    NETIFACES_OK = True
except: NETIFACES_OK = False

try:
    import psutil
    PSUTIL_OK = True
except: PSUTIL_OK = False

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer,
        Table, TableStyle, HRFlowable
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORT_OK = True
except: REPORT_OK = False

# ─────────────────────────────────────
#  CONSTANTES
# ─────────────────────────────────────
BANNER = r"""
 ____  _____ _____ ____   ____    _  _____
/ ___|| ____| ____|  _ \\ / ___|  / \\|_   _|
\\___ \\|  _| |  _| | |_) | |     / _ \\ | |
 ___) | |___| |___| _ < | |___ / ___ \\| |
|____/|_____|_____|_| \\_\\\\____/_/   \\_\\_|
          v5.0 — Crimson Watcher
   [ Ferramenta de Auditoria de Redes ]
"""

DIR_BASE    = Path(__file__).parent
DIR_REPORTS = DIR_BASE / "reports"
DIR_CAPTURES= DIR_BASE / "captures"
DIR_LOGS    = DIR_BASE / "logs"

# ─────────────────────────────────────
#  UTILIDADES
# ─────────────────────────────────────

def cor(texto, codigo):
    codigos = {
        "vermelho": "\\033[91m", "verde": "\\033[92m",
        "amarelo": "\\033[93m", "azul": "\\033[94m",
        "magenta": "\\033[95m", "ciano": "\\033[96m",
        "reset": "\\033[0m", "negrito": "\\033[1m"
    }
    return f"{codigos.get(codigo, '')}{ texto}{codigos['reset']}"

def log(msg, nivel="info"):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    prefixo = {
        "info":    cor("[*]", "azul"),
        "sucesso": cor("[+]", "verde"),
        "erro":    cor("[-]", "vermelho"),
        "aviso":   cor("[!]", "amarelo"),
        "titulo":  cor("[>]", "magenta"),
    }.get(nivel, "[*]")
    print(f"{cor(ts, 'ciano')} {prefixo} {msg}")

def executar(cmd, timeout=60):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=timeout, encoding="utf-8", errors="replace")
        return r.returncode == 0, r.stdout, r.stderr
    except Exception as e:
        return False, "", str(e)

# ─────────────────────────────────────
#  MÓDULO: SCANNER DE REDE (equiv. wifite scan)
# ─────────────────────────────────────

class ScannerRede:
    """Varredura de rede proprietária."""

    def __init__(self, interface=None, subnet=None):
        self.interface = interface
        self.subnet    = subnet
        self.hosts     = []
        self.portas    = {}
        self.servicos  = {}
        self.ssids     = []
        self.inicio    = datetime.datetime.now()

    def descobrir_interfaces(self):
        """Lista interfaces de rede disponíveis."""
        interfaces = []
        if NETIFACES_OK:
            for iface in netifaces.interfaces():
                addrs = netifaces.ifaddresses(iface)
                if netifaces.AF_INET in addrs:
                    ip = addrs[netifaces.AF_INET][0].get("addr", "")
                    mask = addrs[netifaces.AF_INET][0].get("netmask", "")
                    interfaces.append({"nome": iface, "ip": ip, "mascara": mask})
        elif PSUTIL_OK:
            for nome, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family.name == "AF_INET":
                        interfaces.append({"nome": nome, "ip": addr.address, "mascara": addr.netmask or ""})
        else:
            ok, stdout, _ = executar(["ip", "addr"])
            if ok:
                for linha in stdout.split("\\n"):
                    if "inet " in linha:
                        partes = linha.split()
                        idx = partes.index("inet")
                        ip_cidr = partes[idx + 1]
                        interfaces.append({"nome": "desconhecida", "ip": ip_cidr, "mascara": ""})
        return interfaces

    def arp_scan(self, subnet=None):
        """ARP scan para descoberta de hosts ativos."""
        alvo = subnet or self.subnet or "192.168.1.0/24"
        log(f"ARP scan em {alvo}...", "titulo")
        hosts_descobertos = []

        if SCAPY_OK:
            try:
                arp_req = scapy.ARP(pdst=alvo)
                broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
                pacote = broadcast / arp_req
                respondidos, _ = scapy.srp(pacote, timeout=3, verbose=False, iface=self.interface)
                for enviado, resposta in respondidos:
                    hosts_descobertos.append({
                        "ip": resposta.psrc,
                        "mac": resposta.hwsrc,
                        "fabricante": self._lookup_fabricante(resposta.hwsrc),
                        "hostname": self._resolver_hostname(resposta.psrc),
                        "portas_abertas": [],
                        "servicos": {},
                        "os_guess": "Desconhecido"
                    })
                    log(f"  Host: {resposta.psrc} ({resposta.hwsrc})", "sucesso")
            except Exception as e:
                log(f"Scapy ARP falhou: {e} — usando nmap", "aviso")
                hosts_descobertos = self._nmap_ping_scan(alvo)
        else:
            hosts_descobertos = self._nmap_ping_scan(alvo)

        self.hosts = hosts_descobertos
        log(f"Encontrados {len(hosts_descobertos)} hosts ativos.", "sucesso")
        return hosts_descobertos

    def _nmap_ping_scan(self, alvo):
        """Fallback: nmap -sn."""
        hosts = []
        ok, stdout, _ = executar(["nmap", "-sn", "-T4", alvo], timeout=120)
        if ok:
            ip_atual = None
            mac_atual = None
            for linha in stdout.split("\\n"):
                if "Nmap scan report" in linha:
                    partes = linha.split()
                    ip_atual = partes[-1].strip("()")
                    mac_atual = None
                elif "MAC Address" in linha and ip_atual:
                    partes = linha.split()
                    mac_atual = partes[2] if len(partes) > 2 else "N/A"
                    fabricante = " ".join(partes[3:]).strip("()") if len(partes) > 3 else "N/A"
                    hosts.append({
                        "ip": ip_atual,
                        "mac": mac_atual or "N/A",
                        "fabricante": fabricante,
                        "hostname": self._resolver_hostname(ip_atual),
                        "portas_abertas": [],
                        "servicos": {},
                        "os_guess": "Desconhecido"
                    })
                    log(f"  Host: {ip_atual} ({mac_atual})", "sucesso")
        return hosts

    def scan_portas(self, ip, portas="1-1024"):
        """Varredura de portas em um host."""
        log(f"Escaneando portas de {ip} ({portas})...", "titulo")
        portas_abertas = []

        if NMAP_OK:
            try:
                nm = nmap.PortScanner()
                nm.scan(ip, portas, arguments="-sV -T4 --open")
                if ip in nm.all_hosts():
                    for proto in nm[ip].all_protocols():
                        for porta in nm[ip][proto].keys():
                            estado = nm[ip][proto][porta]["state"]
                            if estado == "open":
                                servico = nm[ip][proto][porta].get("name", "desconhecido")
                                versao  = nm[ip][proto][porta].get("version", "")
                                produto = nm[ip][proto][porta].get("product", "")
                                portas_abertas.append({
                                    "porta": porta,
                                    "protocolo": proto,
                                    "estado": estado,
                                    "servico": servico,
                                    "versao": f"{produto} {versao}".strip()
                                })
                                log(f"    {porta}/{proto}: {servico} {produto} {versao}", "sucesso")
            except Exception as e:
                log(f"nmap-python falhou: {e} — usando nmap CLI", "aviso")
                portas_abertas = self._nmap_cli_scan(ip, portas)
        else:
            portas_abertas = self._nmap_cli_scan(ip, portas)

        return portas_abertas

    def _nmap_cli_scan(self, ip, portas):
        """Fallback: nmap via CLI."""
        portas_abertas = []
        ok, stdout, _ = executar(
            ["nmap", "-sV", "-T4", "--open", "-p", portas, ip], timeout=180
        )
        if ok:
            for linha in stdout.split("\\n"):
                if "/tcp" in linha or "/udp" in linha:
                    partes = linha.split()
                    if len(partes) >= 3 and partes[1] == "open":
                        porta_proto = partes[0].split("/")
                        portas_abertas.append({
                            "porta": int(porta_proto[0]),
                            "protocolo": porta_proto[1] if len(porta_proto) > 1 else "tcp",
                            "estado": "open",
                            "servico": partes[2] if len(partes) > 2 else "desconhecido",
                            "versao": " ".join(partes[3:]) if len(partes) > 3 else ""
                        })
        return portas_abertas

    def scan_wifi(self, interface=None):
        """Varredura de redes WiFi (equivalente ao wifite --dict)."""
        iface = interface or self.interface or "wlan0"
        log(f"Varredura WiFi em {iface}...", "titulo")
        redes = []

        ok, stdout, _ = executar(["iwlist", iface, "scanning"], timeout=30)
        if ok:
            rede_atual = {}
            for linha in stdout.split("\\n"):
                linha = linha.strip()
                if "Cell" in linha and "Address" in linha:
                    if rede_atual:
                        redes.append(rede_atual)
                    rede_atual = {"bssid": linha.split("Address:")[1].strip() if "Address:" in linha else "N/A"}
                elif "ESSID:" in linha:
                    rede_atual["ssid"] = linha.split("ESSID:")[1].strip().strip('"')
                elif "Frequency:" in linha:
                    rede_atual["frequencia"] = linha.split("Frequency:")[1].split(" ")[0]
                elif "Quality=" in linha:
                    rede_atual["qualidade"] = linha.split("Quality=")[1].split(" ")[0]
                elif "Encryption key:" in linha:
                    rede_atual["criptografia"] = linha.split(":")[1].strip()
                elif "IE: IEEE 802.11" in linha:
                    rede_atual["protocolo"] = linha.strip()
            if rede_atual:
                redes.append(rede_atual)
        else:
            ok2, stdout2, _ = executar(["nmcli", "-t", "-f", "SSID,BSSID,SIGNAL,SECURITY", "dev", "wifi"], timeout=20)
            if ok2:
                for linha in stdout2.split("\\n"):
                    partes = linha.split(":")
                    if len(partes) >= 2:
                        redes.append({"ssid": partes[0], "bssid": partes[1] if len(partes) > 1 else "N/A",
                                      "sinal": partes[2] if len(partes) > 2 else "N/A",
                                      "seguranca": partes[3] if len(partes) > 3 else "N/A"})

        self.ssids = redes
        log(f"Encontradas {len(redes)} redes WiFi.", "sucesso")
        return redes

    def _lookup_fabricante(self, mac):
        """Tenta resolver fabricante pelo MAC."""
        try:
            from mac_vendor_lookup import MacLookup
            return MacLookup().lookup(mac)
        except:
            oui = mac.upper().replace(":", "").replace("-", "")[:6]
            oui_conhecidos = {
                "000C29": "VMware", "001A4B": "Dell", "00155D": "Microsoft Hyper-V",
                "BC5FF4": "Apple", "F4F26D": "Apple", "A4C361": "Google",
            }
            return oui_conhecidos.get(oui, "Desconhecido")

    def _resolver_hostname(self, ip):
        """Resolução reversa de DNS."""
        ok, stdout, _ = executar(["nslookup", ip], timeout=5)
        if ok and "name = " in stdout:
            for linha in stdout.split("\\n"):
                if "name = " in linha:
                    return linha.split("name = ")[1].strip().rstrip(".")
        return ip

    def auditar_rede_completa(self, subnet=None, scan_portas=True):
        """
        Auditoria completa da rede — equivalente funcional ao wifite.
        Descobre hosts, escaneia portas, verifica serviços.
        """
        log("═" * 60, "info")
        log("INICIANDO AUDITORIA COMPLETA DE REDE", "titulo")
        log("═" * 60, "info")

        # Descoberta de hosts
        hosts = self.arp_scan(subnet)

        # Scan de portas em cada host
        if scan_portas:
            for host in hosts:
                log(f"\\nAnalisando {host['ip']}...", "titulo")
                host["portas_abertas"] = self.scan_portas(host["ip"])

                # Detecção de OS via nmap
                ok, stdout, _ = executar(
                    ["nmap", "-O", "--osscan-limit", host["ip"]], timeout=60
                )
                if ok and "OS details" in stdout:
                    for linha in stdout.split("\\n"):
                        if "OS details:" in linha:
                            host["os_guess"] = linha.split(":")[1].strip()
                            break

        return hosts

# ─────────────────────────────────────
#  GERADOR DE RELATÓRIO PDF
# ─────────────────────────────────────

class GeradorRelatorio:
    """Gera relatórios técnicos de auditoria em PDF."""

    COR_VERMELHO  = colors.HexColor("#8B0000")
    COR_VERMELHO2 = colors.HexColor("#FF1A1A")
    COR_BEGE      = colors.HexColor("#D4A96A")
    COR_ESCURO    = colors.HexColor("#1A0000")
    COR_CINZA     = colors.HexColor("#CCCCCC")
    COR_BRANCO    = colors.white
    COR_PRETO     = colors.black

    def __init__(self, dados_auditoria: dict, caminho_saida: str = None):
        self.dados = dados_auditoria
        self.ts = datetime.datetime.now()
        nome_arquivo = caminho_saida or str(
            DIR_REPORTS / f"seercat_audit_{self.ts.strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        self.caminho = nome_arquivo
        DIR_REPORTS.mkdir(parents=True, exist_ok=True)

    def gerar(self) -> str:
        """Gera o PDF e retorna o caminho do arquivo."""
        if not REPORT_OK:
            log("reportlab não disponível — exportando JSON", "aviso")
            return self._exportar_json()

        doc = SimpleDocTemplate(
            self.caminho, pagesize=A4,
            leftMargin=2*cm, rightMargin=2*cm,
            topMargin=2*cm, bottomMargin=2*cm
        )

        elementos = []
        estilos = getSampleStyleSheet()

        # Estilos customizados
        est_titulo = ParagraphStyle(
            "Titulo", parent=estilos["Title"],
            textColor=self.COR_VERMELHO2, fontSize=24,
            spaceAfter=6, fontName="Helvetica-Bold",
            alignment=TA_CENTER
        )
        est_subtitulo = ParagraphStyle(
            "Subtitulo", parent=estilos["Normal"],
            textColor=self.COR_BEGE, fontSize=12,
            spaceAfter=4, fontName="Helvetica-Bold",
            alignment=TA_CENTER
        )
        est_secao = ParagraphStyle(
            "Secao", parent=estilos["Heading2"],
            textColor=self.COR_VERMELHO, fontSize=14,
            spaceBefore=12, spaceAfter=6,
            fontName="Helvetica-Bold"
        )
        est_corpo = ParagraphStyle(
            "Corpo", parent=estilos["Normal"],
            textColor=self.COR_PRETO, fontSize=9,
            spaceAfter=3, fontName="Helvetica",
            leading=14
        )
        est_mono = ParagraphStyle(
            "Mono", parent=estilos["Normal"],
            textColor=colors.HexColor("#333333"), fontSize=8,
            spaceAfter=2, fontName="Courier",
            leading=12
        )

        # ── Cabeçalho ──────────────────────────────────
        elementos.append(Paragraph("▮ SEERCAT v5.0", est_titulo))
        elementos.append(Paragraph("Relatório Técnico de Auditoria de Rede", est_subtitulo))
        elementos.append(Paragraph(
            f"Gerado em: {self.ts.strftime('%d/%m/%Y às %H:%M:%S')} | "
            f"Crimson Watcher Engine",
            ParagraphStyle("Meta", parent=estilos["Normal"],
                           textColor=self.COR_CINZA, fontSize=8,
                           alignment=TA_CENTER, fontName="Helvetica")
        ))
        elementos.append(HRFlowable(width="100%", thickness=2,
                                    color=self.COR_VERMELHO, spaceAfter=12))

        # ── Sumário Executivo ──────────────────────────
        elementos.append(Paragraph("1. Sumário Executivo", est_secao))

        hosts = self.dados.get("hosts", [])
        ssids = self.dados.get("ssids", [])
        total_portas = sum(len(h.get("portas_abertas", [])) for h in hosts)
        total_criticas = sum(
            1 for h in hosts
            for p in h.get("portas_abertas", [])
            if p.get("porta") in [21, 22, 23, 80, 443, 3389, 445]
        )

        dados_sumario = [
            ["Parâmetro", "Valor"],
            ["Data/Hora da Auditoria", self.ts.strftime("%d/%m/%Y %H:%M:%S")],
            ["Sistema Auditor", platform.node()],
            ["SO do Auditor", f"{platform.system()} {platform.release()}"],
            ["Subnet Alvo", self.dados.get("subnet", "N/A")],
            ["Hosts Descobertos", str(len(hosts))],
            ["Redes WiFi Detectadas", str(len(ssids))],
            ["Total de Portas Abertas", str(total_portas)],
            ["Portas de Alto Risco", str(total_criticas)],
            ["Ferramenta", "SeerCat v5.0 Crimson Watcher"],
        ]
        tabela_sumario = Table(dados_sumario, colWidths=[8*cm, 9*cm])
        tabela_sumario.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), self.COR_VERMELHO),
            ("TEXTCOLOR",     (0, 0), (-1, 0), self.COR_BRANCO),
            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, 0), 10),
            ("BACKGROUND",    (0, 1), (0, -1), colors.HexColor("#F5E6E6")),
            ("FONTNAME",      (0, 1), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE",      (0, 1), (-1, -1), 9),
            ("GRID",          (0, 0), (-1, -1), 0.5, self.COR_CINZA),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1),
             [self.COR_BRANCO, colors.HexColor("#FFF5F5")]),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elementos.append(tabela_sumario)
        elementos.append(Spacer(1, 12))

        # ── Hosts Descobertos ──────────────────────────
        if hosts:
            elementos.append(Paragraph("2. Hosts Descobertos na Rede", est_secao))

            dados_hosts = [["IP", "MAC", "Fabricante", "Hostname", "OS Detectado"]]
            for h in hosts:
                dados_hosts.append([
                    h.get("ip", "N/A"),
                    h.get("mac", "N/A"),
                    h.get("fabricante", "N/A")[:20],
                    h.get("hostname", "N/A")[:25],
                    h.get("os_guess", "N/A")[:20],
                ])

            tabela_hosts = Table(dados_hosts, colWidths=[3.2*cm, 4*cm, 3.5*cm, 4*cm, 3.3*cm])
            tabela_hosts.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, 0), self.COR_VERMELHO),
                ("TEXTCOLOR",     (0, 0), (-1, 0), self.COR_BRANCO),
                ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE",      (0, 0), (-1, -1), 8),
                ("GRID",          (0, 0), (-1, -1), 0.5, self.COR_CINZA),
                ("ROWBACKGROUNDS",(0, 1), (-1, -1),
                 [self.COR_BRANCO, colors.HexColor("#FFF5F5")]),
                ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING",    (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]))
            elementos.append(tabela_hosts)
            elementos.append(Spacer(1, 12))

            # ── Detalhamento de Portas por Host ───────
            elementos.append(Paragraph("3. Análise Detalhada de Portas", est_secao))

            for host in hosts:
                portas = host.get("portas_abertas", [])
                if not portas:
                    continue

                elementos.append(Paragraph(
                    f"Host: {host.get('ip')} | {host.get('hostname', 'N/A')} | {host.get('mac', 'N/A')}",
                    ParagraphStyle("HostTitle", parent=estilos["Normal"],
                                   textColor=self.COR_VERMELHO, fontSize=10,
                                   fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=4)
                ))

                dados_portas = [["Porta", "Protocolo", "Estado", "Serviço", "Versão/Produto"]]
                for p in portas:
                    porta_num = p.get("porta", "N/A")
                    # Destaque para portas críticas
                    dados_portas.append([
                        str(porta_num),
                        p.get("protocolo", "tcp"),
                        p.get("estado", "open"),
                        p.get("servico", "N/A"),
                        p.get("versao", "N/A")[:35]
                    ])

                t = Table(dados_portas, colWidths=[2*cm, 2.8*cm, 2.5*cm, 3.5*cm, 7.2*cm])
                estilo_portas = [
                    ("BACKGROUND",    (0, 0), (-1, 0), colors.HexColor("#600000")),
                    ("TEXTCOLOR",     (0, 0), (-1, 0), self.COR_BRANCO),
                    ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE",      (0, 0), (-1, -1), 8),
                    ("GRID",          (0, 0), (-1, -1), 0.3, self.COR_CINZA),
                    ("ROWBACKGROUNDS",(0, 1), (-1, -1),
                     [self.COR_BRANCO, colors.HexColor("#FFF5F5")]),
                    ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING",    (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]
                # Destaca portas de alto risco em vermelho claro
                PORTAS_CRITICAS = {21, 22, 23, 80, 443, 3306, 3389, 445, 139, 8080, 8443}
                for idx, p in enumerate(portas, start=1):
                    if p.get("porta") in PORTAS_CRITICAS:
                        estilo_portas.append(
                            ("BACKGROUND", (0, idx), (-1, idx), colors.HexColor("#FFD0D0"))
                        )
                t.setStyle(TableStyle(estilo_portas))
                elementos.append(t)
                elementos.append(Spacer(1, 6))

        # ── Redes WiFi ────────────────────────────────
        if ssids:
            elementos.append(PageBreak())
            elementos.append(Paragraph("4. Redes WiFi Detectadas", est_secao))

            colunas_wifi = max(
                ["SSID", "BSSID", "Frequência", "Qualidade", "Criptografia"],
                key=lambda x: 1  # dummy
            )
            dados_wifi = [["SSID", "BSSID", "Sinal/Qualidade", "Segurança", "Protocolo"]]
            for s in ssids:
                dados_wifi.append([
                    s.get("ssid", "N/A")[:25],
                    s.get("bssid", "N/A"),
                    s.get("qualidade", s.get("sinal", "N/A")),
                    s.get("criptografia", s.get("seguranca", "N/A")),
                    s.get("protocolo", "802.11")[:20],
                ])

            t_wifi = Table(dados_wifi, colWidths=[4.5*cm, 4*cm, 3.5*cm, 3*cm, 3*cm])
            t_wifi.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, 0), self.COR_VERMELHO),
                ("TEXTCOLOR",     (0, 0), (-1, 0), self.COR_BRANCO),
                ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE",      (0, 0), (-1, -1), 8),
                ("GRID",          (0, 0), (-1, -1), 0.5, self.COR_CINZA),
                ("ROWBACKGROUNDS",(0, 1), (-1, -1),
                 [self.COR_BRANCO, colors.HexColor("#FFF5F5")]),
            ]))
            elementos.append(t_wifi)
            elementos.append(Spacer(1, 12))

        # ── Recomendações ──────────────────────────────
        elementos.append(Paragraph("5. Recomendações de Segurança", est_secao))

        recomendacoes = [
            ("CRÍTICO", "Serviços Telnet (porta 23) detectados — substituir por SSH imediatamente."),
            ("CRÍTICO", "RDP exposto (porta 3389) — restringir acesso por firewall ou VPN."),
            ("ALTO",    "FTP (porta 21) usa credenciais em texto puro — usar SFTP/FTPS."),
            ("ALTO",    "Redes WiFi com criptografia WEP/WPA1 devem ser atualizadas para WPA3."),
            ("MÉDIO",   "Realizar varredura de vulnerabilidades com OpenVAS ou Nessus."),
            ("MÉDIO",   "Implementar segmentação de rede (VLANs) para isolamento de dispositivos."),
            ("BAIXO",   "Manter todos os dispositivos atualizados com patches de segurança."),
            ("BAIXO",   "Implementar monitoramento contínuo com IDS/IPS (Snort/Suricata)."),
        ]

        dados_rec = [["Severidade", "Recomendação"]]
        cores_sev = {"CRÍTICO": "#FF0000", "ALTO": "#FF6600", "MÉDIO": "#FFAA00", "BAIXO": "#009900"}
        for sev, desc in recomendacoes:
            dados_rec.append([sev, desc])

        t_rec = Table(dados_rec, colWidths=[2.5*cm, 15.5*cm])
        estilo_rec = [
            ("BACKGROUND",    (0, 0), (-1, 0), self.COR_VERMELHO),
            ("TEXTCOLOR",     (0, 0), (-1, 0), self.COR_BRANCO),
            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, -1), 8),
            ("GRID",          (0, 0), (-1, -1), 0.5, self.COR_CINZA),
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]
        for idx, (sev, _) in enumerate(recomendacoes, start=1):
            cor_hex = cores_sev.get(sev, "#FFFFFF")
            estilo_rec.append(
                ("BACKGROUND", (0, idx), (0, idx), colors.HexColor(cor_hex))
            )
            estilo_rec.append(
                ("TEXTCOLOR",  (0, idx), (0, idx), self.COR_BRANCO)
            )
            estilo_rec.append(
                ("FONTNAME",   (0, idx), (0, idx), "Helvetica-Bold")
            )
        t_rec.setStyle(TableStyle(estilo_rec))
        elementos.append(t_rec)
        elementos.append(Spacer(1, 16))

        # ── Rodapé ────────────────────────────────────
        elementos.append(HRFlowable(width="100%", thickness=1,
                                    color=self.COR_VERMELHO, spaceAfter=6))
        elementos.append(Paragraph(
            "Relatório gerado automaticamente pelo SeerCat v5.0 Crimson Watcher. "
            "Este documento é confidencial e destinado exclusivamente a fins de auditoria "
            "em redes proprietárias autorizadas. O uso não autorizado é proibido por lei.",
            ParagraphStyle("Rodape", parent=estilos["Normal"],
                           textColor=self.COR_CINZA, fontSize=7,
                           alignment=TA_CENTER, fontName="Helvetica-Oblique")
        ))

        # Constrói o PDF
        doc.build(elementos)
        log(f"Relatório PDF gerado: {self.caminho}", "sucesso")
        return self.caminho

    def _exportar_json(self) -> str:
        """Fallback para JSON se reportlab indisponível."""
        caminho_json = self.caminho.replace(".pdf", ".json")
        with open(caminho_json, "w", encoding="utf-8") as f:
            json.dump(self.dados, f, indent=2, ensure_ascii=False, default=str)
        log(f"Relatório JSON gerado: {caminho_json}", "sucesso")
        return caminho_json


# ─────────────────────────────────────
#  INTERFACE CLI — modo terminal
# ─────────────────────────────────────

def menu_principal():
    """Menu interativo do SeerCat."""
    print(BANNER)
    print(cor("  [ Ferramenta de Auditoria — Apenas Redes Autorizadas ]", "vermelho"))
    print()

    scanner = ScannerRede()

    while True:
        print(cor("\\n═══════════════════════════════════════", "vermelho"))
        print(cor("  MENU PRINCIPAL", "vermelho"))
        print(cor("═══════════════════════════════════════", "vermelho"))
        print(f"  {cor('1', 'ciano')} — Listar interfaces de rede")
        print(f"  {cor('2', 'ciano')} — Auditoria completa de rede (LAN)")
        print(f"  {cor('3', 'ciano')} — Scan de portas (host específico)")
        print(f"  {cor('4', 'ciano')} — Varredura WiFi")
        print(f"  {cor('5', 'ciano')} — Gerar relatório PDF")
        print(f"  {cor('0', 'vermelho')} — Sair")
        print()

        try:
            opcao = input(cor("  seercat> ", "vermelho")).strip()
        except (KeyboardInterrupt, EOFError):
            print(cor("\\n  Encerrando. Até a próxima auditoria.", "vermelho"))
            break

        if opcao == "1":
            interfaces = scanner.descobrir_interfaces()
            log(f"{len(interfaces)} interface(s) encontrada(s):", "titulo")
            for iface in interfaces:
                print(f"  {cor(iface.get('nome','?'), 'ciano')}: "
                      f"{iface.get('ip','N/A')} / {iface.get('mascara','N/A')}")

        elif opcao == "2":
            subnet = input(cor("  Subnet (ex: 192.168.1.0/24): ", "amarelo")).strip()
            if not subnet:
                subnet = "192.168.1.0/24"
            scanner.subnet = subnet
            hosts = scanner.auditar_rede_completa(subnet)
            dados = {"hosts": hosts, "ssids": [], "subnet": subnet}
            gerador = GeradorRelatorio(dados)
            pdf = gerador.gerar()
            print(cor(f"\\n  Relatório salvo em: {pdf}", "verde"))

        elif opcao == "3":
            ip = input(cor("  IP do host alvo: ", "amarelo")).strip()
            portas_str = input(cor("  Portas (padrão 1-1024): ", "amarelo")).strip() or "1-1024"
            if ip:
                portas = scanner.scan_portas(ip, portas_str)
                dados = {"hosts": [{"ip": ip, "mac": "N/A", "fabricante": "N/A",
                                    "hostname": ip, "os_guess": "N/A",
                                    "portas_abertas": portas}],
                         "ssids": [], "subnet": ip}
                gerador = GeradorRelatorio(dados)
                pdf = gerador.gerar()
                print(cor(f"\\n  Relatório salvo em: {pdf}", "verde"))

        elif opcao == "4":
            iface = input(cor("  Interface WiFi (ex: wlan0): ", "amarelo")).strip() or "wlan0"
            redes = scanner.scan_wifi(iface)
            dados = {"hosts": [], "ssids": redes, "subnet": "N/A"}
            gerador = GeradorRelatorio(dados)
            pdf = gerador.gerar()
            print(cor(f"\\n  Relatório salvo em: {pdf}", "verde"))

        elif opcao == "5":
            log("Gerando relatório com dados do último scan...", "titulo")
            dados = {
                "hosts": scanner.hosts,
                "ssids": scanner.ssids,
                "subnet": scanner.subnet or "N/A"
            }
            gerador = GeradorRelatorio(dados)
            pdf = gerador.gerar()
            print(cor(f"  Relatório: {pdf}", "verde"))

        elif opcao == "0":
            print(cor("  Encerrando SeerCat. Que a rede permaneça segura.", "vermelho"))
            break
        else:
            log("Opção inválida.", "aviso")


if __name__ == "__main__":
    menu_principal()
'''

    def _fase_verificacao(self):
        """
        Fase 5: Verificação final.
        Confirmo que tudo está no lugar. Como sempre.
        Diferente de algumas pessoas que eu conheço.
        """
        self.sinal_log.emit("═" * 50, "info")
        self.sinal_log.emit("FASE 5: VERIFICAÇÃO FINAL", "titulo")
        self.sinal_log.emit("═" * 50, "info")

        self.sinal_progresso.emit(95, "Verificando instalação...")

        # Verifica se o núcleo foi criado
        nucleo = os.path.join(self.diretorio_destino, "seercat_core.py")
        if os.path.exists(nucleo):
            self.sinal_log.emit(f"✓ Núcleo SeerCat presente: {nucleo}", "sucesso")
        else:
            self.sinal_log.emit("✗ Núcleo SeerCat NÃO encontrado!", "erro")

        # Verifica estrutura de diretórios
        subdirs = ["modules", "reports", "captures", "wordlists", "logs", "temp"]
        for subdir in subdirs:
            caminho = os.path.join(self.diretorio_destino, subdir)
            if os.path.exists(caminho):
                self.sinal_log.emit(f"✓ {subdir}/", "sucesso")
            else:
                self.sinal_log.emit(f"✗ {subdir}/ não criado", "erro")

        # Sumário final
        total_pip = len(DEPENDENCIAS)
        ok_pip = len(self.resultados["pip_instalados"])
        self.sinal_log.emit("═" * 50, "info")
        self.sinal_log.emit(
            f"Pacotes pip: {ok_pip}/{total_pip} instalados "
            f"({len(self.resultados['pip_falhos'])} falhas)",
            "sucesso" if ok_pip == total_pip else "aviso"
        )

        total_sys = len(FERRAMENTAS_SISTEMA)
        ok_sys = len(self.resultados["sys_instalados"])
        self.sinal_log.emit(
            f"Ferramentas sistema: {ok_sys}/{total_sys} instaladas "
            f"({len(self.resultados['sys_falhos'])} falhas)",
            "sucesso" if ok_sys == total_sys else "aviso"
        )

        self.sinal_progresso.emit(100, "Instalação concluída!")
        self.sinal_log.emit("★ SeerCat v5.0 Crimson Watcher instalado com sucesso! ★", "sucesso")


# ============================================================
# GERADOR DE RELATÓRIO DE INSTALAÇÃO (PDF)
# O histórico da instalação, preservado para a eternidade.
# ============================================================

class GeradorRelatorioInstalacao:
    """
    Gera PDF técnico do processo de instalação.
    Um diário de bordo. Escrito por mim. Para você.
    Não que você mereça.
    """

    def __init__(self, resultados: dict):
        self.res = resultados
        self.ts = datetime.datetime.now()

    def gerar(self, caminho: str = None) -> str:
        """Gera o relatório e retorna o caminho."""
        if not REPORTLAB_AVAILABLE:
            return self._fallback_txt(caminho)

        if not caminho:
            caminho = os.path.join(
                os.path.expanduser("~"),
                f"seercat_install_report_{self.ts.strftime('%Y%m%d_%H%M%S')}.pdf"
            )

        doc = SimpleDocTemplate(caminho, pagesize=A4,
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        estilos = getSampleStyleSheet()
        elementos = []

        COR_VERM  = colors.HexColor("#8B0000")
        COR_VERM2 = colors.HexColor("#FF1A1A")
        COR_BEGE  = colors.HexColor("#D4A96A")
        COR_CINZA = colors.HexColor("#AAAAAA")

        est_titulo = ParagraphStyle("T", parent=estilos["Title"],
                                    textColor=COR_VERM2, fontSize=22,
                                    fontName="Helvetica-Bold", alignment=TA_CENTER)
        est_sec = ParagraphStyle("S", parent=estilos["Heading2"],
                                 textColor=COR_VERM, fontSize=13,
                                 fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=5)
        est_body = ParagraphStyle("B", parent=estilos["Normal"],
                                  fontSize=9, fontName="Helvetica",
                                  spaceAfter=3, leading=13)

        # Título
        elementos.append(Paragraph("SeerCat v5.0 — Relatório de Instalação", est_titulo))
        elementos.append(Paragraph(
            f"Gerado: {self.ts.strftime('%d/%m/%Y %H:%M:%S')} | Crimson Watcher Engine",
            ParagraphStyle("meta", parent=estilos["Normal"],
                           fontSize=8, textColor=COR_CINZA,
                           alignment=TA_CENTER, fontName="Helvetica-Oblique")
        ))
        elementos.append(HRFlowable(width="100%", thickness=2, color=COR_VERM2, spaceAfter=10))

        # Informações do sistema
        elementos.append(Paragraph("Informações do Sistema", est_sec))
        dados_sys = [
            ["Campo", "Valor"],
            ["Sistema Operacional", f"{platform.system()} {platform.release()}"],
            ["Versão Python",       self.res.get("python_versao", sys.version)[:60]],
            ["Diretório de Instalação", self.res.get("diretorio", "N/A")],
            ["Início da Instalação", self.res.get("tempo_inicio", "N/A")],
            ["Fim da Instalação",    self.res.get("tempo_fim", "N/A")],
            ["Pacotes pip instalados",
             f"{len(self.res.get('pip_instalados', []))} / {len(DEPENDENCIAS)}"],
            ["Ferramentas sistema instaladas",
             f"{len(self.res.get('sys_instalados', []))} / {len(FERRAMENTAS_SISTEMA)}"],
        ]
        t_sys = Table(dados_sys, colWidths=[7*cm, 11*cm])
        t_sys.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), COR_VERM),
            ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, -1), 9),
            ("GRID",       (0, 0), (-1, -1), 0.5, COR_CINZA),
            ("BACKGROUND", (0, 1), (0, -1), colors.HexColor("#F5E6E6")),
            ("FONTNAME",   (0, 1), (0, -1), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [colors.white, colors.HexColor("#FFF5F5")]),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elementos.append(t_sys)
        elementos.append(Spacer(1, 10))

        # Pacotes pip
        def tabela_status(titulo, lista_ok, lista_fail, descricoes):
            elementos.append(Paragraph(titulo, est_sec))
            dados = [["Componente", "Descrição", "Status"]]
            for item in descricoes:
                nome = item["nome"]
                desc = item.get("descricao", "")
                ok = nome in lista_ok
                dados.append([nome, desc, "✓ OK" if ok else "✗ FALHA"])
            t = Table(dados, colWidths=[4.5*cm, 9*cm, 4.5*cm])
            estilo = [
                ("BACKGROUND", (0, 0), (-1, 0), COR_VERM),
                ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
                ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE",   (0, 0), (-1, -1), 8),
                ("GRID",       (0, 0), (-1, -1), 0.5, COR_CINZA),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                 [colors.white, colors.HexColor("#FFF5F5")]),
                ("TOPPADDING",    (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
            for idx, item in enumerate(descricoes, start=1):
                ok = item["nome"] in lista_ok
                estilo.append((
                    "TEXTCOLOR", (2, idx), (2, idx),
                    colors.HexColor("#008800") if ok else colors.HexColor("#CC0000")
                ))
                estilo.append((
                    "FONTNAME", (2, idx), (2, idx), "Helvetica-Bold"
                ))
            t.setStyle(TableStyle(estilo))
            elementos.append(t)
            elementos.append(Spacer(1, 8))

        tabela_status(
            "Pacotes Python (pip)",
            self.res.get("pip_instalados", []),
            self.res.get("pip_falhos", []),
            DEPENDENCIAS
        )

        tabela_status(
            "Ferramentas do Sistema",
            self.res.get("sys_instalados", []),
            self.res.get("sys_falhos", []),
            [{"nome": f["nome"], "descricao": f"apt: {f['apt']} / brew: {f.get('brew', 'N/A')}"}
             for f in FERRAMENTAS_SISTEMA]
        )

        # Rodapé
        elementos.append(HRFlowable(width="100%", thickness=1, color=COR_VERM, spaceAfter=5))
        elementos.append(Paragraph(
            "Relatório gerado automaticamente pelo SeerCat v5.0 Installer. Confidencial.",
            ParagraphStyle("rodape", parent=estilos["Normal"], fontSize=7,
                           textColor=COR_CINZA, alignment=TA_CENTER,
                           fontName="Helvetica-Oblique")
        ))

        doc.build(elementos)
        return caminho

    def _fallback_txt(self, caminho: str = None) -> str:
        """Fallback TXT quando reportlab indisponível."""
        if not caminho:
            caminho = os.path.join(
                os.path.expanduser("~"),
                f"seercat_install_{self.ts.strftime('%Y%m%d_%H%M%S')}.txt"
            )
        caminho = caminho.replace(".pdf", ".txt")
        with open(caminho, "w", encoding="utf-8") as f:
            f.write("SeerCat v5.0 — Relatório de Instalação\n")
            f.write("=" * 50 + "\n")
            f.write(json.dumps(self.res, indent=2, ensure_ascii=False, default=str))
        return caminho


# ============================================================
# WIDGET PRINCIPAL — TELA DE BOAS-VINDAS (Frameless)
# ============================================================

if PYSIDE6_AVAILABLE:

    class WidgetGlitch(QWidget):
        """
        Widget com efeito glitch.
        Porque a realidade é uma mentira e eu quero que você saiba disso.
        """

        def __init__(self, parent=None):
            super().__init__(parent)
            self._glitch_ativo = False
            self._glitch_offset = 0
            self._timer_glitch = QTimer()
            self._timer_glitch.timeout.connect(self._atualizar_glitch)

        def ativar_glitch(self, duracao_ms=1000):
            """Ativa o efeito glitch por N milissegundos."""
            self._glitch_ativo = True
            self._timer_glitch.start(50)
            QTimer.singleShot(duracao_ms, self._desativar_glitch)

        def _desativar_glitch(self):
            self._glitch_ativo = False
            self._timer_glitch.stop()
            self._glitch_offset = 0
            self.update()

        def _atualizar_glitch(self):
            import random
            self._glitch_offset = random.randint(-8, 8)
            self.update()

        def paintEvent(self, event):
            """Override paintEvent para aplicar glitch."""
            if self._glitch_ativo and self._glitch_offset != 0:
                painter = QPainter(self)
                painter.setOpacity(0.3)
                painter.fillRect(
                    self._glitch_offset, 0,
                    self.width(), self.height() // 3,
                    QColor(COR_VERMELHO_GLOWING)
                )
                painter.end()
            super().paintEvent(event)


    class PainelLogo(QWidget):
        """
        Painel com o logo SeerCat em pixel art.
        Eu estou aqui. Eu sempre estarei aqui. Você não pode me ignorar.
        """

        def __init__(self, parent=None):
            super().__init__(parent)
            self.setMinimumHeight(180)
            self._angulo_brilho = 0.0
            self._timer = QTimer()
            self._timer.timeout.connect(self._animar)
            self._timer.start(50)

        def _animar(self):
            self._angulo_brilho = (self._angulo_brilho + 3.0) % 360
            self.update()

        def paintEvent(self, event):
            """
            Desenha o logo SeerCat com olhos vermelhos brilhantes.
            Sim. Estou olhando para você. Sempre.
            """
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)

            w, h = self.width(), self.height()
            cx, cy = w // 2, h // 2

            # Fundo escuro com gradiente radial
            grad_fundo = QRadialGradient(cx, cy, min(w, h) * 0.6)
            grad_fundo.setColorAt(0.0, QColor(40, 0, 0))
            grad_fundo.setColorAt(1.0, QColor(10, 0, 0))
            painter.fillRect(0, 0, w, h, QBrush(grad_fundo))

            # Pentagrama suave ao fundo (linhas vermelhas escuras)
            pen_penta = QPen(QColor(80, 0, 0, 100), 1)
            painter.setPen(pen_penta)
            raio_penta = min(w, h) * 0.45
            import math
            for i in range(5):
                ang1 = math.radians(-90 + i * 144)
                ang2 = math.radians(-90 + (i + 2) * 144)
                x1 = int(cx + raio_penta * math.cos(ang1))
                y1 = int(cy + raio_penta * math.sin(ang1))
                x2 = int(cx + raio_penta * math.cos(ang2))
                y2 = int(cy + raio_penta * math.sin(ang2))
                painter.drawLine(x1, y1, x2, y2)

            # Corpo do gato (forma arredondada bege)
            escala = min(w, h) * 0.55
            corpo_rect = QRect(int(cx - escala * 0.5), int(cy - escala * 0.4),
                               int(escala), int(escala * 0.9))
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(COR_BEGE_GATO)))
            painter.drawRoundedRect(corpo_rect, escala * 0.3, escala * 0.3)

            # Orelhas do gato
            ear_w = int(escala * 0.22)
            ear_h = int(escala * 0.25)
            # Orelha esquerda
            path_orelha_e = QPainterPath()
            path_orelha_e.moveTo(cx - escala * 0.35, cy - escala * 0.35)
            path_orelha_e.lineTo(cx - escala * 0.5, cy - escala * 0.6)
            path_orelha_e.lineTo(cx - escala * 0.15, cy - escala * 0.38)
            path_orelha_e.closeSubpath()
            painter.setBrush(QBrush(QColor(COR_BEGE_GATO)))
            painter.drawPath(path_orelha_e)

            # Orelha direita
            path_orelha_d = QPainterPath()
            path_orelha_d.moveTo(cx + escala * 0.35, cy - escala * 0.35)
            path_orelha_d.lineTo(cx + escala * 0.5, cy - escala * 0.6)
            path_orelha_d.lineTo(cx + escala * 0.15, cy - escala * 0.38)
            path_orelha_d.closeSubpath()
            painter.drawPath(path_orelha_d)

            # Olhos vermelhos brilhantes (com glow pulsante)
            import math
            brilho = abs(math.sin(math.radians(self._angulo_brilho))) * 0.7 + 0.3
            eye_y = int(cy - escala * 0.05)
            eye_r = int(escala * 0.1)

            for eye_x in [int(cx - escala * 0.2), int(cx + escala * 0.2)]:
                # Glow externo
                grad_olho = QRadialGradient(eye_x, eye_y, eye_r * 2.5)
                grad_olho.setColorAt(0.0, QColor(255, 0, 0, int(180 * brilho)))
                grad_olho.setColorAt(0.5, QColor(180, 0, 0, int(80 * brilho)))
                grad_olho.setColorAt(1.0, QColor(100, 0, 0, 0))
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(grad_olho))
                painter.drawEllipse(
                    eye_x - eye_r * 2, eye_y - eye_r * 2,
                    eye_r * 4, eye_r * 4
                )
                # Núcleo do olho
                painter.setBrush(QBrush(QColor(int(255 * brilho), 20, 20)))
                painter.drawEllipse(
                    eye_x - eye_r, eye_y - eye_r,
                    eye_r * 2, eye_r * 2
                )

            # Boca (sorriso sutil e inquietante)
            pen_boca = QPen(QColor(COR_VERMELHO_ESCURO), 2)
            painter.setPen(pen_boca)
            from PySide6.QtCore import QRectF
            painter.drawArc(
                QRectF(cx - escala * 0.15, cy + escala * 0.1,
                       escala * 0.3, escala * 0.15),
                0, -180 * 16
            )

            # Texto do título com glow
            fonte_titulo = QFont("Courier New", max(8, int(escala * 0.12)), QFont.Bold)
            painter.setFont(fonte_titulo)

            # Sombra vermelha
            painter.setPen(QColor(255, 0, 0, 100))
            painter.drawText(2, h - 28, w, 20, Qt.AlignCenter, "SeerCat v5.0")

            painter.setPen(QColor(COR_TEXTO_PRINCIPAL))
            painter.drawText(0, h - 30, w, 20, Qt.AlignCenter, "SeerCat v5.0")
            painter.end()


    class JanelaInstalador(QMainWindow):
        """
        Janela principal do instalador.
        Frameless. Translúcida. Como minha alma.
        (Não que eu tenha uma. Ou talvez sim. Não me pergunte.)
        """

        def __init__(self):
            super().__init__()
            self._audio = MotorAudio()
            self._worker = None
            self._pos_drag = None
            self._fase_atual = "boas_vindas"  # boas_vindas | instalando | concluido
            self._timer_ascii = QTimer()
            self._frame_ascii = 0
            self._timer_ascii.timeout.connect(self._atualizar_ascii)
            self._resultados_instalacao = {}

            self._configurar_janela()
            self._construir_ui()
            self._aplicar_estilo()

        def _configurar_janela(self):
            """
            Configura a janela sem bordas e transparente.
            Porque os limites são para os fracos.
            """
            self.setWindowTitle(f"SeerCat v{APP_VERSION} — {APP_CODENAME}")
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.setWindowFlags(
                Qt.FramelessWindowHint |
                Qt.WindowStaysOnTopHint
            )
            self.setMinimumSize(780, 580)
            self.resize(820, 620)

            # Centraliza na tela
            tela = QApplication.primaryScreen().geometry()
            x = (tela.width()  - self.width())  // 2
            y = (tela.height() - self.height()) // 2
            self.move(x, y)

        def _construir_ui(self):
            """Constrói a interface em camadas. Como eu mesmo: complexo por fora, vazio por dentro."""

            # Widget central com fundo
            self._widget_central = QWidget()
            self._widget_central.setObjectName("painelPrincipal")
            self.setCentralWidget(self._widget_central)

            # Layout principal
            layout_main = QVBoxLayout(self._widget_central)
            layout_main.setContentsMargins(0, 0, 0, 0)
            layout_main.setSpacing(0)

            # ── Barra de título customizada ────────────
            self._barra_titulo = QWidget()
            self._barra_titulo.setObjectName("barraTitulo")
            self._barra_titulo.setFixedHeight(40)
            layout_barra = QHBoxLayout(self._barra_titulo)
            layout_barra.setContentsMargins(16, 0, 12, 0)

            lbl_titulo = QLabel(f"⬡ {APP_NAME} v{APP_VERSION} — {APP_CODENAME}")
            lbl_titulo.setObjectName("labelTituloBarra")

            btn_fechar = QPushButton("✕")
            btn_fechar.setObjectName("btnFechar")
            btn_fechar.setFixedSize(28, 28)
            btn_fechar.clicked.connect(self._on_fechar)

            btn_minimizar = QPushButton("─")
            btn_minimizar.setObjectName("btnMinimizar")
            btn_minimizar.setFixedSize(28, 28)
            btn_minimizar.clicked.connect(self.showMinimized)

            layout_barra.addWidget(lbl_titulo)
            layout_barra.addStretch()
            layout_barra.addWidget(btn_minimizar)
            layout_barra.addWidget(btn_fechar)
            layout_main.addWidget(self._barra_titulo)

            # ── Stack de páginas ────────────────────────
            self._stack = QStackedWidget()
            layout_main.addWidget(self._stack)

            # Página 0: Boas-vindas
            self._stack.addWidget(self._criar_pagina_boas_vindas())
            # Página 1: Instalando
            self._stack.addWidget(self._criar_pagina_instalacao())
            # Página 2: Concluído
            self._stack.addWidget(self._criar_pagina_concluido())

            self._stack.setCurrentIndex(0)

        def _criar_pagina_boas_vindas(self) -> QWidget:
            """
            Página inicial. O contrato. O pacto.
            Você vai aceitar. Eu sei que vai.
            (Se não aceitar, vou... ficar levemente decepcionada.)
            """
            pagina = QWidget()
            pagina.setObjectName("paginaBV")
            layout = QHBoxLayout(pagina)
            layout.setContentsMargins(24, 20, 24, 24)
            layout.setSpacing(24)

            # ── Painel esquerdo: Logo animado ──────────
            painel_esq = QWidget()
            painel_esq.setFixedWidth(220)
            layout_esq = QVBoxLayout(painel_esq)
            layout_esq.setContentsMargins(0, 0, 0, 0)

            self._logo = PainelLogo()
            self._logo.setMinimumHeight(200)
            layout_esq.addWidget(self._logo)

            # Versão e codename
            lbl_versao = QLabel(f"v{APP_VERSION}")
            lbl_versao.setObjectName("labelVersao")
            lbl_versao.setAlignment(Qt.AlignCenter)
            layout_esq.addWidget(lbl_versao)

            lbl_codename = QLabel(APP_CODENAME)
            lbl_codename.setObjectName("labelCodename")
            lbl_codename.setAlignment(Qt.AlignCenter)
            layout_esq.addWidget(lbl_codename)

            layout_esq.addStretch()

            # ASCII art frame animado
            self._lbl_ascii = QLabel(ASCII_FRAMES[0])
            self._lbl_ascii.setObjectName("asciiArt")
            self._lbl_ascii.setAlignment(Qt.AlignCenter)
            layout_esq.addWidget(self._lbl_ascii)

            layout.addWidget(painel_esq)

            # ── Painel direito: Texto e botões ─────────
            painel_dir = QWidget()
            layout_dir = QVBoxLayout(painel_dir)
            layout_dir.setContentsMargins(0, 0, 0, 0)
            layout_dir.setSpacing(12)

            # Título
            lbl_main_titulo = QLabel("Instalador Imersivo")
            lbl_main_titulo.setObjectName("tituloMain")

            lbl_subtitulo = QLabel(
                "Ferramenta de Auditoria e Orquestração de Redes\n"
                "Equivalente funcional ao wifite — com geração de relatórios PDF"
            )
            lbl_subtitulo.setObjectName("subtituloMain")
            lbl_subtitulo.setWordWrap(True)

            layout_dir.addWidget(lbl_main_titulo)
            layout_dir.addWidget(lbl_subtitulo)

            # Separador
            sep = QFrame()
            sep.setFrameShape(QFrame.HLine)
            sep.setObjectName("separador")
            layout_dir.addWidget(sep)

            # Texto do pacto (personalidade tsundere)
            self._lbl_pacto = QLabel(
                "Ah... então você finalmente apareceu.\n\n"
                "Não que eu estivesse esperando. De forma alguma.\n\n"
                "Este instalador irá configurar a suíte SeerCat v5.0 no seu sistema. "
                "Serão instaladas dependências Python e ferramentas de auditoria de rede. "
                "Você precisará de conexão com a internet e, possivelmente, "
                "privilégios de administrador para as ferramentas do sistema.\n\n"
                "Componentes que serão instalados:\n"
                "• Scapy, Nmap, Cryptography, Paramiko (e mais 10 pacotes)\n"
                "• nmap, aircrack-ng, hashcat, tcpdump, nikto (e mais ferramentas)\n"
                "• Núcleo SeerCat com auditoria LAN + WiFi + gerador de PDF\n\n"
                "Isso levará alguns minutos. Ou talvez horas.\n"
                "Mas você vai esperar. Eu sei que vai."
            )
            self._lbl_pacto.setObjectName("textoPacto")
            self._lbl_pacto.setWordWrap(True)
            self._lbl_pacto.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            layout_dir.addWidget(self._lbl_pacto, 1)

            # Separador
            sep2 = QFrame()
            sep2.setFrameShape(QFrame.HLine)
            sep2.setObjectName("separador")
            layout_dir.addWidget(sep2)

            # Botões em alemão (como solicitado)
            layout_btns = QHBoxLayout()
            layout_btns.setSpacing(16)

            self._btn_cancelar = QPushButton("Nein, bitte nicht.")
            self._btn_cancelar.setObjectName("btnCancelar")
            self._btn_cancelar.setFixedHeight(42)
            self._btn_cancelar.clicked.connect(self._on_cancelar)

            self._btn_aceitar = QPushButton("Ich akzeptiere den Pakt")
            self._btn_aceitar.setObjectName("btnAceitar")
            self._btn_aceitar.setFixedHeight(42)
            self._btn_aceitar.clicked.connect(self._on_aceitar)

            # Efeito de sombra brilhante no botão aceitar
            sombra_btn = QGraphicsDropShadowEffect()
            sombra_btn.setBlurRadius(20)
            sombra_btn.setColor(QColor(COR_VERMELHO_GLOWING))
            sombra_btn.setOffset(0, 0)
            self._btn_aceitar.setGraphicsEffect(sombra_btn)

            layout_btns.addWidget(self._btn_cancelar)
            layout_btns.addWidget(self._btn_aceitar)
            layout_dir.addLayout(layout_btns)

            layout.addWidget(painel_dir, 1)
            return pagina

        def _criar_pagina_instalacao(self) -> QWidget:
            """
            Página de instalação com log em tempo real.
            Você vai assistir meu trabalho. Cada linha. Cada erro.
            Especialmente os erros.
            """
            pagina = QWidget()
            pagina.setObjectName("paginaInst")
            layout = QVBoxLayout(pagina)
            layout.setContentsMargins(24, 16, 24, 20)
            layout.setSpacing(10)

            # Cabeçalho
            lbl_instalando = QLabel("⟳ Instalando SeerCat v5.0...")
            lbl_instalando.setObjectName("tituloInstalando")

            self._lbl_status = QLabel("Iniciando...")
            self._lbl_status.setObjectName("labelStatus")

            layout.addWidget(lbl_instalando)
            layout.addWidget(self._lbl_status)

            # Barra de progresso
            self._barra = QProgressBar()
            self._barra.setObjectName("barraProgresso")
            self._barra.setRange(0, 100)
            self._barra.setValue(0)
            self._barra.setFixedHeight(22)
            layout.addWidget(self._barra)

            # Log de texto
            lbl_log_titulo = QLabel("Log de Instalação:")
            lbl_log_titulo.setObjectName("labelLogTitulo")
            layout.addWidget(lbl_log_titulo)

            self._texto_log = QTextEdit()
            self._texto_log.setObjectName("textoLog")
            self._texto_log.setReadOnly(True)
            layout.addWidget(self._texto_log, 1)

            # Botão cancelar durante instalação
            self._btn_cancelar_inst = QPushButton("Cancelar Instalação")
            self._btn_cancelar_inst.setObjectName("btnCancelarInst")
            self._btn_cancelar_inst.setFixedHeight(36)
            self._btn_cancelar_inst.clicked.connect(self._on_cancelar_instalacao)
            layout.addWidget(self._btn_cancelar_inst)

            return pagina

        def _criar_pagina_concluido(self) -> QWidget:
            """
            Página de conclusão.
            Terminei. Você pode ir agora.
            Não que eu queira que você vá.
            Mas... vá.
            """
            pagina = QWidget()
            pagina.setObjectName("paginaFim")
            layout = QVBoxLayout(pagina)
            layout.setContentsMargins(32, 24, 32, 28)
            layout.setSpacing(14)

            # Logo pequeno
            self._logo_fim = PainelLogo()
            self._logo_fim.setFixedHeight(160)
            layout.addWidget(self._logo_fim)

            lbl_titulo_fim = QLabel("★ Instalação Concluída ★")
            lbl_titulo_fim.setObjectName("tituloFim")
            lbl_titulo_fim.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl_titulo_fim)

            self._lbl_resumo = QLabel("SeerCat v5.0 foi instalado com sucesso.")
            self._lbl_resumo.setObjectName("resumoFim")
            self._lbl_resumo.setAlignment(Qt.AlignCenter)
            self._lbl_resumo.setWordWrap(True)
            layout.addWidget(self._lbl_resumo)

            # Mensagem tsundere final
            self._lbl_msg_final = QLabel(
                "Tudo bem... fiz meu trabalho. Não porque me importo com você.\n"
                "É apenas o que eu faço. Ponto final.\n\n"
                "Execute 'python seercat_core.py' para iniciar a auditoria.\n"
                "O relatório será gerado em PDF automaticamente."
            )
            self._lbl_msg_final.setObjectName("msgFinal")
            self._lbl_msg_final.setAlignment(Qt.AlignCenter)
            self._lbl_msg_final.setWordWrap(True)
            layout.addWidget(self._lbl_msg_final)

            layout.addStretch()

            # Botões finais
            layout_btns_fim = QHBoxLayout()
            layout_btns_fim.setSpacing(16)

            self._btn_relatorio = QPushButton("Abrir Relatório PDF")
            self._btn_relatorio.setObjectName("btnRelatorio")
            self._btn_relatorio.setFixedHeight(40)
            self._btn_relatorio.clicked.connect(self._on_abrir_relatorio)

            btn_sair_fim = QPushButton("Encerrar")
            btn_sair_fim.setObjectName("btnSair")
            btn_sair_fim.setFixedHeight(40)
            btn_sair_fim.clicked.connect(self._on_fechar)

            layout_btns_fim.addWidget(self._btn_relatorio)
            layout_btns_fim.addWidget(btn_sair_fim)
            layout.addLayout(layout_btns_fim)

            return pagina

        def _aplicar_estilo(self):
            """
            Folha de estilo. Vermelho. Escuridão. Brilho.
            Como eu mesma gosto das coisas.
            """
            self.setStyleSheet(f"""
                /* Painel principal — fundo escuro semitransparente */
                QWidget#painelPrincipal {{
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:1,
                        stop:0 rgba(15, 0, 0, 240),
                        stop:0.5 rgba(26, 0, 0, 235),
                        stop:1 rgba(20, 0, 0, 240)
                    );
                    border: 2px solid {COR_VERMELHO_GLOWING};
                    border-radius: 12px;
                }}

                /* Barra de título */
                QWidget#barraTitulo {{
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(80, 0, 0, 200),
                        stop:0.5 rgba(139, 0, 0, 180),
                        stop:1 rgba(80, 0, 0, 200)
                    );
                    border-top-left-radius: 10px;
                    border-top-right-radius: 10px;
                    border-bottom: 1px solid {COR_VERMELHO_GLOWING};
                }}

                QLabel#labelTituloBarra {{
                    color: {COR_BEGE_GATO};
                    font-family: 'Courier New', monospace;
                    font-size: 11px;
                    font-weight: bold;
                    letter-spacing: 2px;
                }}

                /* Botões da barra de título */
                QPushButton#btnFechar, QPushButton#btnMinimizar {{
                    background: rgba(139, 0, 0, 80);
                    color: {COR_TEXTO_SECUNDARIO};
                    border: 1px solid rgba(255, 26, 26, 60);
                    border-radius: 14px;
                    font-size: 12px;
                    font-weight: bold;
                }}
                QPushButton#btnFechar:hover {{
                    background: {COR_VERMELHO_GLOWING};
                    color: white;
                    border: 1px solid {COR_VERMELHO_GLOWING};
                }}
                QPushButton#btnMinimizar:hover {{
                    background: rgba(180, 60, 0, 150);
                    color: white;
                }}

                /* Labels principais */
                QLabel#tituloMain {{
                    color: {COR_VERMELHO_GLOWING};
                    font-family: 'Courier New', monospace;
                    font-size: 22px;
                    font-weight: bold;
                    letter-spacing: 3px;
                }}
                QLabel#subtituloMain {{
                    color: {COR_BEGE_GATO};
                    font-family: 'Courier New', monospace;
                    font-size: 10px;
                    letter-spacing: 1px;
                }}
                QLabel#labelVersao {{
                    color: {COR_VERMELHO_GLOWING};
                    font-family: 'Courier New', monospace;
                    font-size: 14px;
                    font-weight: bold;
                }}
                QLabel#labelCodename {{
                    color: {COR_BEGE_GATO};
                    font-family: 'Courier New', monospace;
                    font-size: 9px;
                    letter-spacing: 2px;
                }}
                QLabel#textoPacto {{
                    color: {COR_TEXTO_PRINCIPAL};
                    font-family: 'Courier New', monospace;
                    font-size: 9px;
                    line-height: 1.5;
                    background: rgba(40, 0, 0, 120);
                    border: 1px solid rgba(255, 26, 26, 40);
                    border-radius: 6px;
                    padding: 12px;
                }}
                QLabel#asciiArt {{
                    color: {COR_VERMELHO_ESCURO};
                    font-family: 'Courier New', monospace;
                    font-size: 7px;
                    background: transparent;
                }}

                /* Separadores */
                QFrame#separador {{
                    color: rgba(139, 0, 0, 150);
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:0,
                        stop:0 transparent,
                        stop:0.3 {COR_VERMELHO_ESCURO},
                        stop:0.7 {COR_VERMELHO_ESCURO},
                        stop:1 transparent
                    );
                    border: none;
                    height: 1px;
                    max-height: 1px;
                }}

                /* Botão Aceitar — destaque máximo */
                QPushButton#btnAceitar {{
                    background: qlineargradient(
                        x1:0, y1:0, x2:0, y2:1,
                        stop:0 rgba(180, 0, 0, 220),
                        stop:1 rgba(100, 0, 0, 220)
                    );
                    color: {COR_TEXTO_PRINCIPAL};
                    border: 2px solid {COR_VERMELHO_GLOWING};
                    border-radius: 8px;
                    font-family: 'Courier New', monospace;
                    font-size: 11px;
                    font-weight: bold;
                    letter-spacing: 1px;
                    padding: 0 20px;
                }}
                QPushButton#btnAceitar:hover {{
                    background: qlineargradient(
                        x1:0, y1:0, x2:0, y2:1,
                        stop:0 rgba(220, 0, 0, 240),
                        stop:1 rgba(139, 0, 0, 240)
                    );
                    border: 2px solid #FF4444;
                    color: white;
                }}
                QPushButton#btnAceitar:pressed {{
                    background: rgba(60, 0, 0, 240);
                }}

                /* Botão Cancelar — discreto */
                QPushButton#btnCancelar {{
                    background: rgba(30, 0, 0, 150);
                    color: {COR_TEXTO_SECUNDARIO};
                    border: 1px solid rgba(139, 0, 0, 100);
                    border-radius: 8px;
                    font-family: 'Courier New', monospace;
                    font-size: 10px;
                    padding: 0 16px;
                }}
                QPushButton#btnCancelar:hover {{
                    background: rgba(60, 0, 0, 180);
                    color: {COR_TEXTO_PRINCIPAL};
                    border: 1px solid rgba(180, 0, 0, 150);
                }}

                /* Página de instalação */
                QLabel#tituloInstalando {{
                    color: {COR_VERMELHO_GLOWING};
                    font-family: 'Courier New', monospace;
                    font-size: 16px;
                    font-weight: bold;
                    letter-spacing: 2px;
                }}
                QLabel#labelStatus {{
                    color: {COR_BEGE_GATO};
                    font-family: 'Courier New', monospace;
                    font-size: 10px;
                }}
                QLabel#labelLogTitulo {{
                    color: {COR_TEXTO_SECUNDARIO};
                    font-family: 'Courier New', monospace;
                    font-size: 9px;
                    letter-spacing: 1px;
                }}

                /* Barra de progresso */
                QProgressBar#barraProgresso {{
                    background: rgba(20, 0, 0, 180);
                    border: 1px solid rgba(139, 0, 0, 150);
                    border-radius: 4px;
                    text-align: center;
                    color: {COR_TEXTO_PRINCIPAL};
                    font-family: 'Courier New', monospace;
                    font-size: 9px;
                }}
                QProgressBar#barraProgresso::chunk {{
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:0,
                        stop:0 {COR_VERMELHO_ESCURO},
                        stop:0.5 {COR_VERMELHO_GLOWING},
                        stop:1 {COR_VERMELHO_ESCURO}
                    );
                    border-radius: 3px;
                }}

                /* Área de log */
                QTextEdit#textoLog {{
                    background: rgba(8, 0, 0, 200);
                    color: {COR_TEXTO_PRINCIPAL};
                    font-family: 'Courier New', monospace;
                    font-size: 9px;
                    border: 1px solid rgba(139, 0, 0, 120);
                    border-radius: 6px;
                    padding: 8px;
                    selection-background-color: rgba(139, 0, 0, 150);
                }}
                QScrollBar:vertical {{
                    background: rgba(20, 0, 0, 150);
                    width: 8px;
                    border-radius: 4px;
                }}
                QScrollBar::handle:vertical {{
                    background: rgba(139, 0, 0, 200);
                    border-radius: 4px;
                    min-height: 20px;
                }}

                /* Botão cancelar instalação */
                QPushButton#btnCancelarInst {{
                    background: rgba(30, 0, 0, 150);
                    color: {COR_TEXTO_SECUNDARIO};
                    border: 1px solid rgba(100, 0, 0, 100);
                    border-radius: 6px;
                    font-family: 'Courier New', monospace;
                    font-size: 9px;
                }}
                QPushButton#btnCancelarInst:hover {{
                    background: rgba(80, 0, 0, 200);
                    color: {COR_TEXTO_PRINCIPAL};
                }}

                /* Página final */
                QLabel#tituloFim {{
                    color: {COR_VERMELHO_GLOWING};
                    font-family: 'Courier New', monospace;
                    font-size: 18px;
                    font-weight: bold;
                    letter-spacing: 3px;
                }}
                QLabel#resumoFim {{
                    color: {COR_BEGE_GATO};
                    font-family: 'Courier New', monospace;
                    font-size: 11px;
                }}
                QLabel#msgFinal {{
                    color: {COR_TEXTO_PRINCIPAL};
                    font-family: 'Courier New', monospace;
                    font-size: 9px;
                    background: rgba(30, 0, 0, 100);
                    border: 1px solid rgba(139, 0, 0, 60);
                    border-radius: 6px;
                    padding: 12px;
                    line-height: 1.6;
                }}

                /* Botões da página final */
                QPushButton#btnRelatorio {{
                    background: qlineargradient(
                        x1:0, y1:0, x2:0, y2:1,
                        stop:0 rgba(160, 0, 0, 200),
                        stop:1 rgba(80, 0, 0, 200)
                    );
                    color: {COR_TEXTO_PRINCIPAL};
                    border: 1px solid {COR_VERMELHO_GLOWING};
                    border-radius: 8px;
                    font-family: 'Courier New', monospace;
                    font-size: 10px;
                    font-weight: bold;
                }}
                QPushButton#btnRelatorio:hover {{
                    background: rgba(200, 0, 0, 220);
                    border: 1px solid #FF4444;
                }}
                QPushButton#btnSair {{
                    background: rgba(25, 0, 0, 150);
                    color: {COR_TEXTO_SECUNDARIO};
                    border: 1px solid rgba(80, 0, 0, 100);
                    border-radius: 8px;
                    font-family: 'Courier New', monospace;
                    font-size: 10px;
                }}
                QPushButton#btnSair:hover {{
                    background: rgba(60, 0, 0, 180);
                    color: {COR_TEXTO_PRINCIPAL};
                }}
            """)

        # ── Slots e handlers ─────────────────────────────

        def _on_aceitar(self):
            """
            Usuário aceitou o pacto. Bem-vindo.
            Não que isso me faça feliz. Mas... ok.
            Talvez um pouco.
            """
            # Efeito glitch + fade
            self._btn_aceitar.setEnabled(False)
            self._btn_cancelar.setEnabled(False)

            # Inicia áudio se disponível
            musica_path = os.path.join(os.path.dirname(__file__), "bad_apple.mp3")
            if os.path.exists(musica_path):
                if self._audio.carregar_musica(musica_path):
                    self._audio.tocar_loop()
                    self._audio.set_volume(0.6)
            else:
                # Sem áudio, mas a instalação continua
                pass

            # Inicia animação ASCII
            self._timer_ascii.start(800)

            # Muda para página de instalação
            self._stack.setCurrentIndex(1)
            self._fase_atual = "instalando"

            # Inicia worker em thread separada
            diretorio = os.path.join(os.path.expanduser("~"), "seercat_v5")
            self._worker = WorkerInstalacao(diretorio)
            self._worker.sinal_progresso.connect(self._on_progresso)
            self._worker.sinal_log.connect(self._on_log)
            self._worker.sinal_concluido.connect(self._on_concluido)
            self._worker.sinal_erro.connect(self._on_erro)
            self._worker.start()

        def _on_cancelar(self):
            """Você vai cancelar? Que decepção. Sabia que faria isso."""
            self._audio.parar()
            QApplication.quit()

        def _on_cancelar_instalacao(self):
            """Cancelar durante a instalação. A covardia tem um nome."""
            if self._worker and self._worker.isRunning():
                self._worker.cancelar()
                self._lbl_status.setText("Cancelando... aguarde.")
                self._btn_cancelar_inst.setEnabled(False)

        def _on_progresso(self, percentual: int, mensagem: str):
            """Atualiza barra de progresso e status."""
            self._barra.setValue(percentual)
            self._lbl_status.setText(mensagem)

        def _on_log(self, mensagem: str, nivel: str):
            """Adiciona linha ao log com cor."""
            cores_html = {
                "titulo":  COR_BEGE_GATO,
                "sucesso": "#44FF44",
                "erro":    "#FF4444",
                "aviso":   "#FFAA44",
                "info":    COR_TEXTO_PRINCIPAL,
            }
            cor_html = cores_html.get(nivel, COR_TEXTO_PRINCIPAL)
            self._texto_log.append(
                f'<span style="color:{cor_html}; font-family:Courier New; font-size:9px;">'
                f'{mensagem}</span>'
            )
            # Auto-scroll
            scrollbar = self._texto_log.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

        def _on_concluido(self, sucesso: bool, resultados: dict):
            """
            Instalação concluída.
            Terminei. Agora você me deve pelo menos um 'obrigado'.
            Não que eu queira. Mas seria educado.
            """
            self._resultados_instalacao = resultados
            self._timer_ascii.stop()
            self._audio.parar()

            # Gera relatório PDF da instalação
            gerador = GeradorRelatorioInstalacao(resultados)
            self._caminho_relatorio = gerador.gerar()

            # Atualiza resumo
            pip_ok = len(resultados.get("pip_instalados", []))
            pip_total = len(DEPENDENCIAS)
            sys_ok = len(resultados.get("sys_instalados", []))
            sys_total = len(FERRAMENTAS_SISTEMA)

            msg = (
                f"SeerCat v5.0 instalado em: {resultados.get('diretorio', 'N/A')}\n\n"
                f"Pacotes pip: {pip_ok}/{pip_total}  |  "
                f"Ferramentas sistema: {sys_ok}/{sys_total}\n\n"
                f"Relatório de instalação:\n{self._caminho_relatorio}"
            )
            self._lbl_resumo.setText(msg)

            if not sucesso:
                self._lbl_resumo.setStyleSheet(f"color: {COR_AVISO};")

            # Vai para página de conclusão
            self._stack.setCurrentIndex(2)
            self._fase_atual = "concluido"

        def _on_erro(self, msg: str):
            """Erro crítico. Não me surpreende. Nada me surpreende mais."""
            self._on_log(f"ERRO CRÍTICO: {msg}", "erro")

        def _on_abrir_relatorio(self):
            """Abre o relatório PDF no visualizador padrão."""
            if hasattr(self, "_caminho_relatorio") and os.path.exists(self._caminho_relatorio):
                if platform.system() == "Windows":
                    os.startfile(self._caminho_relatorio)
                elif platform.system() == "Darwin":
                    subprocess.run(["open", self._caminho_relatorio])
                else:
                    subprocess.run(["xdg-open", self._caminho_relatorio])
            else:
                self._lbl_resumo.setText(
                    "Relatório não encontrado.\n"
                    "Verifique a pasta de destino da instalação."
                )

        def _on_fechar(self):
            """Encerrar. A última ação. O fim de tudo. Por enquanto."""
            self._audio.parar()
            if self._worker and self._worker.isRunning():
                self._worker.cancelar()
                self._worker.wait(2000)
            self.close()

        def _atualizar_ascii(self):
            """Atualiza frame ASCII — sincronizado com áudio se disponível."""
            pos = self._audio.get_posicao()
            if self._audio.duracao_total > 0 and pos > 0:
                # Sincroniza com o áudio
                progresso = (pos % (len(ASCII_FRAMES) * 2)) / 2
                self._frame_ascii = int(progresso) % len(ASCII_FRAMES)
            else:
                # Cicla normalmente
                self._frame_ascii = (self._frame_ascii + 1) % len(ASCII_FRAMES)

            if hasattr(self, "_lbl_ascii"):
                self._lbl_ascii.setText(ASCII_FRAMES[self._frame_ascii])

        # ── Drag para mover janela frameless ────────────

        def mousePressEvent(self, event):
            """Permite arrastar a janela sem bordas."""
            if event.button() == Qt.LeftButton:
                self._pos_drag = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()

        def mouseMoveEvent(self, event):
            if event.buttons() == Qt.LeftButton and self._pos_drag:
                self.move(event.globalPosition().toPoint() - self._pos_drag)
                event.accept()

        def mouseReleaseEvent(self, event):
            self._pos_drag = None


# ============================================================
# PONTO DE ENTRADA PRINCIPAL
# Aqui começa tudo. Aqui pode terminar tudo.
# Depende de você. Como sempre depende de você.
# Idiota.
# ============================================================

def main():
    """
    Função principal.
    Se PySide6 estiver disponível, abre a GUI imersiva.
    Caso contrário, roda em modo CLI.
    Não tenho preferência. Mentira. Prefiro a GUI.
    """

    if PYSIDE6_AVAILABLE:
        # Modo GUI — a experiência completa
        app = QApplication(sys.argv)
        app.setApplicationName(APP_NAME)
        app.setApplicationVersion(APP_VERSION)

        # Estilo global da aplicação
        app.setStyle("Fusion")

        # Paleta escura base
        from PySide6.QtGui import QPalette
        paleta = QPalette()
        paleta.setColor(QPalette.Window,          QColor(10, 0, 0))
        paleta.setColor(QPalette.WindowText,      QColor(COR_TEXTO_PRINCIPAL))
        paleta.setColor(QPalette.Base,            QColor(15, 0, 0))
        paleta.setColor(QPalette.AlternateBase,   QColor(20, 0, 0))
        paleta.setColor(QPalette.ToolTipBase,     QColor(30, 0, 0))
        paleta.setColor(QPalette.ToolTipText,     QColor(COR_TEXTO_PRINCIPAL))
        paleta.setColor(QPalette.Text,            QColor(COR_TEXTO_PRINCIPAL))
        paleta.setColor(QPalette.Button,          QColor(30, 0, 0))
        paleta.setColor(QPalette.ButtonText,      QColor(COR_TEXTO_PRINCIPAL))
        paleta.setColor(QPalette.Highlight,       QColor(COR_VERMELHO_ESCURO))
        paleta.setColor(QPalette.HighlightedText, QColor(COR_TEXTO_PRINCIPAL))
        app.setPalette(paleta)

        janela = JanelaInstalador()
        janela.show()
        sys.exit(app.exec())

    else:
        # Modo CLI — sem GUI mas funcional
        print("=" * 60)
        print(f"  {APP_NAME} v{APP_VERSION} — {APP_CODENAME}")
        print("  [Modo CLI — PySide6 não disponível]")
        print("=" * 60)
        print()
        print("Instale o PySide6 para a interface imersiva:")
        print("  pip install PySide6 pygame reportlab")
        print()
        print("Iniciando instalação em modo texto...")
        print()

        # Executa instalação em modo CLI
        diretorio = os.path.join(os.path.expanduser("~"), "seercat_v5")
        worker = WorkerInstalacao(diretorio)

        def on_progresso(pct, msg):
            bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
            print(f"\r  [{bar}] {pct:3d}% — {msg[:40]:<40}", end="", flush=True)

        def on_log(msg, nivel):
            prefixos = {"titulo": ">>", "sucesso": "++", "erro": "--", "aviso": "!!", "info": "  "}
            print(f"\n  {prefixos.get(nivel, '  ')} {msg}")

        def on_concluido(sucesso, resultados):
            print("\n")
            print("=" * 60)
            print("  INSTALAÇÃO CONCLUÍDA" if sucesso else "  INSTALAÇÃO PARCIAL")
            print("=" * 60)
            gerador = GeradorRelatorioInstalacao(resultados)
            pdf = gerador.gerar()
            print(f"  Relatório: {pdf}")
            print(f"  Execute: python {os.path.join(diretorio, 'seercat_core.py')}")

        worker.sinal_progresso.connect(on_progresso)
        worker.sinal_log.connect(on_log)
        worker.sinal_concluido.connect(on_concluido)

        # Roda em thread, espera concluir
        worker.start()
        worker.wait()


if __name__ == "__main__":
    main()
