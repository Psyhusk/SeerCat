#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SeerCat v3.0 - Professional Cyber Audit Suite
Dashboard de Auditoria com Companion Dinâmico
Powered by Psyhusk
"""

import customtkinter as ctk
import pygame
import threading
import os
import sys
import subprocess
from fpdf import FPDF
from pathlib import Path

# --- Configurações ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COMPANION_IMG = os.path.join(BASE_DIR, "images.webp")
REPORT_DIR = os.path.join(BASE_DIR, "auditorias")
os.makedirs(REPORT_DIR, exist_ok=True)

class SeerCatCompanion(threading.Thread):
    def __init__(self, frame_id, width, height):
        super().__init__()
        self.frame_id = frame_id
        self.width = width
        self.height = height
        self.running = True

    def run(self):
        os.environ['SDL_WINDOWID'] = str(self.frame_id)
        pygame.display.init()
        screen = pygame.display.set_mode((self.width, self.height))
        
        try:
            image = pygame.image.load(COMPANION_IMG)
            image = pygame.transform.smoothscale(image, (220, 260))
        except:
            image = None
            
        clock = pygame.time.Clock()
        while self.running:
            screen.fill((15, 15, 15)) # Noir Dark
            if image:
                screen.blit(image, (40, 20))
            pygame.display.update()
            clock.tick(30)
        pygame.display.quit()

class SeerCatGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SeerCat v3.0 - Auditoria Forense")
        self.geometry("1200x800")
        ctk.set_appearance_mode("dark")

        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Barra Lateral
        self.sidebar = ctk.CTkFrame(self, width=250)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(self.sidebar, text="SEERCAT v3.0", font=("Consolas", 24, "bold")).pack(pady=20)
        
        # Botões
        buttons = [("Ativar Monitor", self.run_monitor), 
                   ("Scan Passivo", self.run_scan), 
                   ("Gerar PDF", self.gen_pdf)]
        for text, cmd in buttons:
            ctk.CTkButton(self.sidebar, text=text, command=cmd).pack(pady=10, padx=10)

        # Companion
        self.companion_frame = ctk.CTkFrame(self.sidebar, width=250, height=300, fg_color="black")
        self.companion_frame.pack(pady=30, padx=10)

        # Dashboard / Console
        self.console = ctk.CTkTextbox(self, fg_color="#050505", text_color="#00FF00")
        self.console.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.footer = ctk.CTkLabel(self, text="Powered by Psyhusk | Auditoria Profissional", font=("Consolas", 10))
        self.footer.grid(row=1, column=1, sticky="e", padx=20)
        
        self.after(500, self.start_companion)
        self.log("Sistema v3.0 pronto. Aguardando comandos.")

    def log(self, msg):
        self.console.insert("end", f"[SeerCat] {msg}\n")
        self.console.see("end")

    def run_monitor(self): self.log("Modo monitor ativado em wlan0.")
    def run_scan(self): self.log("Iniciando varredura passiva de canais...")
    def gen_pdf(self): 
        self.log("Relatório gerado em /auditorias.")
        # FPDF logic placeholder
    
    def start_companion(self):
        self.comp = SeerCatCompanion(self.companion_frame.winfo_id(), 300, 300)
        self.comp.start()

    def on_closing(self):
        if hasattr(self, 'comp'): self.comp.running = False
        self.destroy()

if __name__ == "__main__":
    app = SeerCatGUI()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
