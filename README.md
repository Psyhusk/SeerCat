💜 Apoie o Desenvolvimento
O SeerCat é um projeto de código aberto, arquitetado e desenvolvido 100% em ambiente mobile.
Meu objetivo é criar ferramentas de alta performance que facilitem o fluxo de trabalho de profissionais da área, mesmo com as limitações técnicas do meu setup atual.
Se esta ferramenta foi útil para você, considere apoiar o projeto:
👉 patreon.com/cw/Psyhusk/membership
Seu apoio é fundamental para que eu possa continuar dedicando tempo integral ao desenvolvimento, à correção de bugs e à implementação de novas funcionalidades.
Todo apoio é muito bem-vindo e me ajuda a manter este ecossistema vivo e em constante evolução. 🙏

---

# 🐱‍💻 SeerCat v5.0 — Crimson Watcher

### *Instalador Imersivo de Auditoria de Rede*

> *"Ah... você está aqui. Finalmente. Eu sabia que viria."*

O **SeerCat v5.0** é mais do que uma ferramenta de auditoria de rede; é uma experiência técnica imersiva. Projetado para automatizar varreduras de rede, análise de vulnerabilidades e geração de relatórios profissionais, ele combina performance bruta com uma estética *Crimson* única.

---

## ✨ Funcionalidades Principais

* **Auditoria Automatizada:** Motor de escaneamento de rede baseado em `scapy` e `nmap`, equivalente a fluxos de trabalho do *Wifite*.
* **Varredura Inteligente:** Detecção de hosts via ARP scan, análise profunda de portas abertas e serviços, e identificação de sistema operacional.
* **Relatórios Profissionais:** Geração automática de auditorias detalhadas em formato **PDF** (`ReportLab`), prontos para entrega técnica.
* **Instalador Imersivo:** Interface gráfica moderna (`PySide6`) com motor de áudio integrado (suporte para *Bad Apple* em loop) e tema visual *Crimson* customizado.
* **Multi-ferramentas:** Automatiza a instalação e configuração de dependências de rede essenciais (Nmap, Aircrack-ng, Hashcat, Tcpdump, entre outras).

---

## 🛠 Pré-requisitos de Instalação

Para garantir o funcionamento pleno da interface e do motor de auditoria, o sistema irá validar e instalar automaticamente:

* **Python:** 3.8+
* **Bibliotecas Python:** `PySide6`, `scapy`, `nmap`, `pygame`, `reportlab`, `psutil`, `cryptography`, `paramiko`, entre outras.
* **Ferramentas de Sistema:** A instalação automática tentará configurar via `apt` (Linux) ou `brew` (macOS) pacotes como:
* `nmap`, `aircrack-ng`, `hashcat`, `tcpdump`, `wireshark-cli`, `hydra`, `john`, etc.



---

## 🚀 Como Usar

### Execução do Instalador

Para iniciar a jornada de instalação e configurar o ambiente:

```bash
python3 seercat_v5_installer.py

```

### Build do Executável (Standalone)

Se você deseja compilar o SeerCat em um executável único (`dist/`), utilize o script de build fornecido:

```bash
# Certifique-se de ter o pyinstaller instalado:
pip install pyinstaller PySide6 pygame reportlab

# Execute o script de build:
python3 build_seercat.py

```

---

## 🏗 Estrutura do Projeto

* `seercat_v5_installer.py`: O instalador gráfico com interface *Crimson Watcher*.
* `build_seercat.py`: Script de compilação automática via `PyInstaller`.
* `seercat_core.py` (Gerado após instalação): O núcleo de auditoria de rede que executa as varreduras e gera os relatórios.

---

## ⚠️ Aviso de Uso

> **Operações de rede exigem permissões de administrador.**
> Utilize esta ferramenta estritamente em **ambientes autorizados** e para fins de auditoria ética. O uso indevido contra redes não autorizadas é de total responsabilidade do usuário.

---

```
 ____  _____ _____ ____   ____    _  _____
/ ___|| ____| ____|  _ \\ / ___|  / \\|_   _|
\\___ \\|  _| |  _| | |_) | |     / _ \\ | |
 ___) | |___| |___| _ < | |___ / ___ \\| |
|____/|_____|_____|_| \\_\\\\____/_/   \\_\\_|

          v5.0 — Crimson Watcher

```

*Consertando o que mentes mortais quebraram.*
