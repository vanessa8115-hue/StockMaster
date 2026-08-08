from datetime import datetime
from tkinter import messagebox, ttk

import customtkinter as ctk

from banco import (
    TIPO_SAIDA,
    contar_produtos,
    estoque_baixo,
    listar_estoque_baixo,
    listar_movimentacoes,
    total_movimentos,
    valor_estoque,
)
from exportadores import escolher_arquivo, exportar_excel, exportar_pdf


class Relatorios:
    def __init__(self, janela):
        self.janela = janela
        self.movimentacoes = []

        for widget in self.janela.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.janela,
            text="📊 Relatórios",
            font=("Segoe UI", 32, "bold")
        ).pack(pady=(20, 8))

        topo = ctk.CTkFrame(self.janela, fg_color="transparent")
        topo.pack(pady=(0, 12))

        ctk.CTkButton(
            topo,
            text="← Voltar ao Dashboard",
            command=self.voltar_dashboard,
            width=180
        ).grid(row=0, column=0, padx=8)

        self.data_inicio = ctk.CTkEntry(topo, placeholder_text="Data inicial: AAAA-MM-DD", width=190)
        self.data_inicio.grid(row=0, column=1, padx=8)

        self.data_fim = ctk.CTkEntry(topo, placeholder_text="Data final: AAAA-MM-DD", width=190)
        self.data_fim.grid(row=0, column=2, padx=8)

        ctk.CTkButton(topo, text="Filtrar", command=self.aplicar_filtro, width=110).grid(row=0, column=3, padx=8)
        ctk.CTkButton(topo, text="Limpar filtro", command=self.limpar_filtro, width=120).grid(row=0, column=4, padx=8)

        botoes_exportacao = ctk.CTkFrame(self.janela, fg_color="transparent")
        botoes_exportacao.pack(pady=(0, 8))

        ctk.CTkButton(
            botoes_exportacao,
            text="Exportar Excel",
            command=self.exportar_excel,
            width=160
        ).grid(row=0, column=0, padx=8)

        ctk.CTkButton(
            botoes_exportacao,
            text="Exportar PDF",
            command=self.exportar_pdf,
            width=160
        ).grid(row=0, column=1, padx=8)

        self.criar_resumo()
        self.criar_tabelas()
        self.aplicar_filtro()

    def criar_resumo(self):
        area = ctk.CTkFrame(self.janela, fg_color="transparent")
        area.pack(pady=8)

        dados = [
            ("📦 Produtos", contar_produtos()),
            ("⚠ Estoque baixo", estoque_baixo()),
            ("💰 Valor estoque", f"R$ {valor_estoque():,.2f}"),
            ("📥 Entradas", total_movimentos("Entrada")),
            ("📤 Saídas", total_movimentos(TIPO_SAIDA)),
        ]

        for coluna, (titulo_card, valor) in enumerate(dados):
            card = ctk.CTkFrame(area, width=205, height=100, corner_radius=18)
            card.grid(row=0, column=coluna, padx=8)
            card.pack_propagate(False)

            ctk.CTkLabel(
                card,
                text=titulo_card,
                font=("Segoe UI", 16, "bold")
            ).pack(pady=(18, 4))

            ctk.CTkLabel(card, text=str(valor), font=("Segoe UI", 22)).pack()

    def criar_tabelas(self):
        area = ctk.CTkFrame(self.janela)
        area.pack(padx=20, pady=10, expand=True, fill="both")

        estoque_frame = ctk.CTkFrame(area)
        estoque_frame.pack(side="left", padx=10, pady=10, expand=True, fill="both")

        movimentacoes_frame = ctk.CTkFrame(area)
        movimentacoes_frame.pack(side="right", padx=10, pady=10, expand=True, fill="both")

        ctk.CTkLabel(
            estoque_frame,
            text="Produtos com estoque baixo",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=10)

        self._criar_tabela_estoque(estoque_frame)

        ctk.CTkLabel(
            movimentacoes_frame,
            text="Movimentações",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=10)

        self._criar_tabela_movimentacoes(movimentacoes_frame)

    def _criar_tabela_estoque(self, pai):
        frame = ctk.CTkFrame(pai)
        frame.pack(padx=10, pady=(0, 10), expand=True, fill="both")

        colunas = ("codigo", "nome", "qtd", "min")
        self.tabela_estoque = ttk.Treeview(frame, columns=colunas, show="headings", height=10)

        for coluna, texto, largura in [
            ("codigo", "Código", 90),
            ("nome", "Produto", 180),
            ("qtd", "Qtd", 70),
            ("min", "Mín.", 70),
        ]:
            self.tabela_estoque.heading(coluna, text=texto)
            self.tabela_estoque.column(coluna, width=largura, anchor="center")

        for produto in listar_estoque_baixo():
            self.tabela_estoque.insert("", "end", values=(produto[1], produto[2], produto[4], produto[5]))

        self.tabela_estoque.pack(side="left", expand=True, fill="both")
        barra = ttk.Scrollbar(frame, orient="vertical", command=self.tabela_estoque.yview)
        barra.pack(side="right", fill="y")
        self.tabela_estoque.configure(yscrollcommand=barra.set)

    def _criar_tabela_movimentacoes(self, pai):
        frame = ctk.CTkFrame(pai)
        frame.pack(padx=10, pady=(0, 10), expand=True, fill="both")

        colunas = ("codigo", "nome", "tipo", "qtd", "data")
        self.tabela_movimentacoes = ttk.Treeview(frame, columns=colunas, show="headings", height=10)

        for coluna, texto, largura in [
            ("codigo", "Código", 80),
            ("nome", "Produto", 160),
            ("tipo", "Tipo", 80),
            ("qtd", "Qtd", 60),
            ("data", "Data", 130),
        ]:
            self.tabela_movimentacoes.heading(coluna, text=texto)
            self.tabela_movimentacoes.column(coluna, width=largura, anchor="center")

        self.tabela_movimentacoes.pack(side="left", expand=True, fill="both")
        barra = ttk.Scrollbar(frame, orient="vertical", command=self.tabela_movimentacoes.yview)
        barra.pack(side="right", fill="y")
        self.tabela_movimentacoes.configure(yscrollcommand=barra.set)

    def aplicar_filtro(self):
        data_inicio = self.data_inicio.get().strip()
        data_fim = self.data_fim.get().strip()

        if not self._validar_data(data_inicio) or not self._validar_data(data_fim):
            return

        self.movimentacoes = listar_movimentacoes(data_inicio or None, data_fim or None)
        self._preencher_movimentacoes()

    def limpar_filtro(self):
        self.data_inicio.delete(0, "end")
        self.data_fim.delete(0, "end")
        self.aplicar_filtro()

    def _validar_data(self, valor):
        if not valor:
            return True

        try:
            datetime.strptime(valor, "%Y-%m-%d")
            return True
        except ValueError:
            messagebox.showwarning("Atenção", "Use o formato de data AAAA-MM-DD. Exemplo: 2026-08-08.")
            return False

    def _preencher_movimentacoes(self):
        for item in self.tabela_movimentacoes.get_children():
            self.tabela_movimentacoes.delete(item)

        for movimentacao in self.movimentacoes[:200]:
            self.tabela_movimentacoes.insert(
                "",
                "end",
                values=(movimentacao[1], movimentacao[2], movimentacao[3], movimentacao[4], movimentacao[5])
            )

    def exportar_excel(self):
        caminho = escolher_arquivo("xlsx", "Salvar relatório em Excel")

        if not caminho:
            return

        try:
            exportar_excel(caminho, *self._dados_exportacao())
            messagebox.showinfo("Exportação concluída", f"Relatório Excel salvo em:\n\n{caminho}")
        except Exception as erro:
            messagebox.showerror("Erro", f"Não foi possível exportar o Excel.\n\n{erro}")

    def exportar_pdf(self):
        caminho = escolher_arquivo("pdf", "Salvar relatório em PDF")

        if not caminho:
            return

        try:
            exportar_pdf(caminho, *self._dados_exportacao())
            messagebox.showinfo("Exportação concluída", f"Relatório PDF salvo em:\n\n{caminho}")
        except Exception as erro:
            messagebox.showerror("Erro", f"Não foi possível exportar o PDF.\n\n{erro}")

    def _dados_exportacao(self):
        titulo = "Relatório de movimentações - StockMaster"
        cabecalhos = ["Código", "Produto", "Tipo", "Quantidade", "Data"]
        linhas = [(m[1], m[2], m[3], m[4], m[5]) for m in self.movimentacoes]

        return titulo, cabecalhos, linhas

    def voltar_dashboard(self):
        from telas.dashboard import Dashboard

        Dashboard(self.janela)
