# SeerCat v2.0 — Orquestrador Automatizado de Auditoria Wi-Fi

```
  ___  ___  ___  ___  ___  __  _  _
 / __|| __|| __|| _ \/ __|\  || |_|
 \__ \| _| | _| |   / (__  \_/|  _|
 |___/|___||___||_|_\\___|   |_||_|
```

## ⚠️ AVISO LEGAL

Esta ferramenta destina-se **EXCLUSIVAMENTE** a:
- Testes de segurança em redes **de sua propriedade**
- Auditorias com **autorização escrita** do proprietário
- Fins educacionais em **ambientes controlados**

O uso não autorizado é crime no Brasil (Lei 12.737/2012 — pena de 3 meses a 2 anos + multa).

---

## 🚀 Instalação e Uso

```bash
# Clonar / baixar o script
chmod +x seercat.py

# Executar como root (obrigatório)
sudo python3 seercat.py
```

O SeerCat instala automaticamente as dependências Python e de sistema.

---

## 📦 Dependências

### Python (auto-instaladas)
- `rich` — Interface TUI neobank
- `pyfiglet` — Banner ASCII

### Sistema (auto-instaladas via apt/pacman/dnf/zypper)
| Ferramenta       | Função                                  |
|------------------|-----------------------------------------|
| aircrack-ng      | Monitor, deauth, captura de IVs         |
| reaver           | Ataque WPS Pixie-Dust                   |
| bully            | Ataque WPS PIN bruteforce               |
| hashcat          | Quebra de senha (GPU/CPU)               |
| hcxdumptool      | Captura PMKID                           |
| hcxtools         | Conversão de hashes                     |
| john             | Quebra de senha alternativa             |
| iw / iwconfig    | Gerenciamento de interfaces             |

---

## 🔧 Funcionalidades

### 1. Modo Monitor Automatizado
- Detecta interfaces wireless disponíveis
- Mata processos interferentes (NetworkManager, wpa_supplicant)
- Ativa modo monitor via `airmon-ng` ou `iw` manual

### 2. Varredura Passiva (Channel Hopping)
- Salta entre canais automaticamente
- Detecta SSIDs, BSSIDs, canais, criptografia e WPS
- Identifica clientes conectados a cada AP

### 3. Ataques Suportados
- **WPA/WPA2 Handshake**: Deautenticação + captura do 4-way handshake
- **PMKID**: Captura sem necessidade de clientes conectados
- **WPS Pixie-Dust**: via Reaver com flag `-K 1`
- **WPS PIN Bruteforce**: via Bully
- **WEP**: Reinjeção ARP para coleta de IVs + quebra

### 4. Quebra de Senhas
- Hashcat (modo 22000 para PMKID/HCCAPX)
- John the Ripper como alternativa
- Suporte a qualquer wordlist personalizada

### 5. Gestão de Sessão
- Organiza capturas em `~/SeerCat_Sessoes/sessao_YYYYMMDD_HHMMSS/`
- Log em tempo real (buffer circular de 200 entradas)
- Relatório JSON completo ao encerrar
- Restaura interface ao modo managed automaticamente

---

## 🖥️ Interface TUI

Design inspirado em neobanks (C6 Bank, Nubank):
- Paleta escura com acentos ciano/roxo/rosa
- Animações de spinner e progress bar
- Tabelas formatadas com indicadores coloridos
- Painel de log em tempo real para especialistas
- Banner ASCII animado com gradiente

---

## 📁 Estrutura de Arquivos de Saída

```
~/SeerCat_Sessoes/
└── sessao_20260502_143000/
    ├── scan_temp-01.csv          # Dados brutos da varredura
    ├── handshake_AA-BB-CC-*.cap  # Capturas de handshake
    ├── pmkid_AA-BB-CC-*.hash     # Hashes PMKID
    ├── wps_AA-BB-CC-*.txt        # Resultados WPS
    ├── senhas_encontradas.txt    # Senhas quebradas
    └── relatorio.json            # Relatório completo JSON
```

---

## 🔑 Compatibilidade

Testado em:
- Kali Linux 2024+
- Parrot OS 6+
- Ubuntu 22.04+ (com adaptador wireless compatível)
- Arch Linux (via pacman)
- Fedora 38+ (via dnf)
- OpenSUSE (via zypper)

Requisito de hardware: adaptador wireless com suporte a **modo monitor e injeção de pacotes**.
