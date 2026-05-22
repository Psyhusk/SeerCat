# 🐱 SeerCat v3.0 - Professional Cyber Audit Suite

<p align="center">
  <img src="images.webp" alt="SeerCat Companion" width="200"/>
</p>

O **SeerCat** é um orquestrador avançado de auditoria de segurança Wi-Fi, concebido para automatizar fluxos de trabalho forenses e testes de penetração. Com a transição para a **v3.0**, o SeerCat apresenta-se agora com uma interface gráfica (GUI) híbrida e moderna, mantendo a potência de orquestração via linha de comandos, mas com um *Companion* visual dinâmico que monitoriza o seu ambiente.

> **Powered by Psyhusk**

## 🚀 O que há de novo na v3.0?

* **Interface Híbrida (GUI + CLI):** Interface gráfica moderna construída com `customtkinter`, oferecendo um ambiente organizado sem perder a visibilidade dos processos.
* **Companion Dinâmico:** Integração visual de renderização via `pygame`, proporcionando uma experiência imersiva durante as auditorias.
* **Dashboard Forense:** Console de logs em tempo real com estilo "Noir", focado na clareza de dados técnicos.
* **Gestão de Dependências:** Instalação automática de ferramentas de auditoria (Aircrack-ng, Hashcat, etc.) para ambientes Debian/Kali.
* **Relatórios Automatizados:** Geração integrada de relatórios em PDF para documentação profissional de auditorias.

## 🛠️ Tecnologias Utilizadas

- **Interface:** `customtkinter`
- **Companion Engine:** `pygame`
- **Relatórios:** `fpdf`
- **Orquestração:** `subprocess` (Linux native)

## 📋 Pré-requisitos

O SeerCat foi desenhado para Linux. Certifique-se de que tem o Python 3 instalado.
## 📔 instalando e usando a seer cat 
* **git clone [https://github.com/o_teu_usuario/seercat.git](https://github.com/o_teu_usuario/seercat.git)
cd seercat**
* **💻 executando a seer cat
  sudo python3 SeerCat.py**
  
```bash
# Dependências do sistema (Debian/Kali)
sudo apt update && sudo apt install -y aircrack-ng hashcat macchanger

# Dependências Python
pip install customtkinter pygame fpdf
