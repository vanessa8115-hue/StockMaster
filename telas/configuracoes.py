import customtkinter as ctk
from tkinter import messagebox

import config
from banco import criar_backup_banco, obter_configuracao, salvar_configuracao


class Configuracoes:
    def __init__(self, janela):
        self.janela = janela

        for widget in self.janela.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.janela,
            text="⚙ Configurações",
            font=("Segoe UI", 32, "bold")
        ).pack(pady=(35, 15))

        ctk.CTkButton(
            self.janela,
            text="← Voltar ao Dashboard",
            command=self.voltar_dashboard,
            width=200
        ).pack(pady=(0, 25))

        card = ctk.CTkFrame(self.janela, width=580, height=430, corner_radius=20)
        card.pack()
        card.pack_propagate(False)

        ctk.CTkLabel(
            card,
            text="Preferências do sistema",
            font=("Segoe UI", 22, "bold")
        ).pack(pady=(28, 18))

        modo_atual = obter_configuracao("modo_visual", config.MODO)

        ctk.CTkLabel(
            card,
            text="Tema visual",
            font=("Segoe UI", 15, "bold")
        ).pack(pady=(5, 5))

        self.modo_visual = ctk.CTkComboBox(
            card,
            values=["Light", "Dark", "System"],
            width=220
        )
        self.modo_visual.pack(pady=5)
        self.modo_visual.set(modo_atual)

        ctk.CTkButton(
            card,
            text="Aplicar tema",
            command=self.aplicar_tema,
            width=220
        ).pack(pady=(8, 20))

        ctk.CTkLabel(
            card,
            text="Backup do banco de dados",
            font=("Segoe UI", 15, "bold")
        ).pack(pady=(5, 5))

        ctk.CTkButton(
            card,
            text="Criar backup agora",
            command=self.criar_backup,
            width=220
        ).pack(pady=8)

        ctk.CTkLabel(
            card,
            text=f"Versão: {config.VERSAO}\nJanela: {config.LARGURA}x{config.ALTURA}\nLogin padrão inicial: admin / 123",
            font=("Segoe UI", 14)
        ).pack(pady=20)

        self.mensagem = ctk.CTkLabel(self.janela, text="", font=("Segoe UI", 13))
        self.mensagem.pack(pady=18)

    def aplicar_tema(self):
        modo = self.modo_visual.get().strip()

        salvar_configuracao("modo_visual", modo)
        ctk.set_appearance_mode(modo)

        self.mensagem.configure(
            text=f"Tema '{modo}' aplicado e salvo.",
            text_color="green"
        )

    def criar_backup(self):
        try:
            caminho = criar_backup_banco()
            self.mensagem.configure(
                text=f"Backup criado em: {caminho}",
                text_color="green"
            )
            messagebox.showinfo("Backup criado", f"Backup salvo com sucesso em:\n\n{caminho}")
        except Exception as erro:
            messagebox.showerror("Erro", f"Não foi possível criar o backup.\n\n{erro}")

    def voltar_dashboard(self):
        from telas.dashboard import Dashboard

        Dashboard(self.janela)
