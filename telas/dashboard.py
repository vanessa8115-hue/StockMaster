import customtkinter as ctk

from banco import TIPO_SAIDA, contar_produtos, estoque_baixo, total_movimentos, valor_estoque
from telas.entradas import Entradas
from telas.produtos import Produtos
from telas.relatorios import Relatorios
from telas.saidas import Saidas
from telas.usuarios import Usuarios


class Dashboard:
    def __init__(self, janela):
        self.janela = janela

        for widget in self.janela.winfo_children():
            widget.destroy()

        self.menu = ctk.CTkFrame(self.janela, width=240, corner_radius=0)
        self.menu.pack(side="left", fill="y")
        self.menu.pack_propagate(False)

        self.conteudo = ctk.CTkFrame(self.janela, corner_radius=0)
        self.conteudo.pack(side="right", expand=True, fill="both")

        self.criar_menu()
        self.criar_dashboard()

    def criar_menu(self):
        ctk.CTkLabel(
            self.menu,
            text="StockMaster",
            font=("Segoe UI", 28, "bold")
        ).pack(pady=(35, 5))

        ctk.CTkLabel(
            self.menu,
            text="Sistema inteligente\nde gestão de estoque",
            font=("Segoe UI", 14)
        ).pack(pady=(0, 25))

        botoes = [
            ("🏠 Dashboard", self.recarregar),
            ("📦 Produtos", lambda: Produtos(self.janela)),
            ("📥 Entradas", lambda: Entradas(self.janela)),
            ("📤 Saídas", lambda: Saidas(self.janela)),
            ("📊 Relatórios", lambda: Relatorios(self.janela)),
            ("👤 Usuários", lambda: Usuarios(self.janela)),
            ("⚙ Configurações", self.abrir_configuracoes),
            ("🚪 Sair", self.sair),
        ]

        for texto, comando in botoes:
            ctk.CTkButton(
                self.menu,
                text=texto,
                width=190,
                height=36,
                command=comando
            ).pack(pady=6)

    def criar_dashboard(self):
        ctk.CTkLabel(
            self.conteudo,
            text="Bem-vinda ao StockMaster",
            font=("Segoe UI", 32, "bold")
        ).pack(pady=(35, 5))

        ctk.CTkLabel(
            self.conteudo,
            text="Controle simples, rápido e confiável do seu estoque",
            font=("Segoe UI", 16)
        ).pack()

        ctk.CTkLabel(
            self.conteudo,
            text="Resumo geral",
            font=("Segoe UI", 22, "bold")
        ).pack(pady=(40, 10))

        area_cards = ctk.CTkFrame(self.conteudo, fg_color="transparent")
        area_cards.pack()

        dados = [
            ("📦 Produtos", contar_produtos()),
            ("⚠ Estoque baixo", estoque_baixo()),
            ("💰 Valor estoque", f"R$ {valor_estoque():,.2f}"),
            ("📥 Entradas", total_movimentos("Entrada")),
            ("📤 Saídas", total_movimentos(TIPO_SAIDA)),
        ]

        for titulo_card, valor in dados:
            self.criar_card(area_cards, titulo_card, valor)

        ctk.CTkLabel(
            self.conteudo,
            text="Dica: faça backup antes de grandes alterações no estoque.",
            font=("Segoe UI", 14)
        ).pack(pady=45)

    def criar_card(self, pai, titulo, valor):
        card = ctk.CTkFrame(pai, width=190, height=130, corner_radius=20)
        card.pack(side="left", padx=10)
        card.pack_propagate(False)

        ctk.CTkLabel(
            card,
            text=titulo,
            font=("Segoe UI", 17, "bold")
        ).pack(pady=(25, 10))

        ctk.CTkLabel(
            card,
            text=str(valor),
            font=("Segoe UI", 27)
        ).pack()

    def abrir_configuracoes(self):
        from telas.configuracoes import Configuracoes

        Configuracoes(self.janela)

    def recarregar(self):
        Dashboard(self.janela)

    def sair(self):
        from telas.login import Login

        for widget in self.janela.winfo_children():
            widget.destroy()

        Login(self.janela)
