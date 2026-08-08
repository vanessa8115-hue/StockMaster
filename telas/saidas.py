import customtkinter as ctk

from banco import listar_produtos, registrar_saida


class Saidas:
    def __init__(self, janela):
        self.janela = janela

        for widget in self.janela.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.janela,
            text="📤 Saídas de Estoque",
            font=("Segoe UI", 32, "bold")
        ).pack(pady=(30, 15))

        ctk.CTkButton(
            self.janela,
            text="← Voltar ao Dashboard",
            command=self.voltar_dashboard,
            width=200
        ).pack(pady=(0, 25))

        self.produtos = []
        self.opcoes_produtos = {}

        self.combo = ctk.CTkComboBox(self.janela, width=380, values=[])
        self.combo.pack(pady=15)

        self.estoque_label = ctk.CTkLabel(self.janela, text="", font=("Segoe UI", 14))
        self.estoque_label.pack()

        self.quantidade = ctk.CTkEntry(
            self.janela,
            placeholder_text="Quantidade",
            width=300
        )
        self.quantidade.pack(pady=15)
        self.quantidade.bind("<Return>", lambda _evento: self.salvar())

        ctk.CTkButton(
            self.janela,
            text="Registrar Saída",
            command=self.salvar,
            width=200
        ).pack(pady=20)

        self.mensagem = ctk.CTkLabel(self.janela, text="", font=("Segoe UI", 14))
        self.mensagem.pack(pady=10)

        self.carregar_produtos()
        self.combo.configure(command=lambda _valor: self.atualizar_estoque_label())

    def carregar_produtos(self):
        self.produtos = listar_produtos()
        self.opcoes_produtos = {
            f"{produto[1]} - {produto[2]}": produto
            for produto in self.produtos
        }

        opcoes = list(self.opcoes_produtos.keys())
        self.combo.configure(values=opcoes)

        if opcoes:
            self.combo.set(opcoes[0])
        else:
            self.combo.set("")
            self.mensagem.configure(
                text="Cadastre um produto antes de registrar saídas.",
                text_color="orange"
            )

        self.atualizar_estoque_label()

    def atualizar_estoque_label(self):
        produto = self.opcoes_produtos.get(self.combo.get().strip())

        if produto is None:
            self.estoque_label.configure(text="")
            return

        self.estoque_label.configure(text=f"Estoque disponível: {produto[4]}")

    def salvar(self):
        produto = self.opcoes_produtos.get(self.combo.get().strip())

        if produto is None:
            self.mensagem.configure(text="⚠ Selecione um produto válido.", text_color="red")
            return

        quantidade = self._obter_quantidade()

        if quantidade is None:
            return

        estoque_atual = produto[4]

        if quantidade > estoque_atual:
            self.mensagem.configure(
                text=f"⚠ Estoque insuficiente. Disponível: {estoque_atual}",
                text_color="red"
            )
            return

        sucesso = registrar_saida(produto[0], quantidade)

        if not sucesso:
            self.mensagem.configure(text="⚠ Não foi possível registrar a saída.", text_color="red")
            return

        self.quantidade.delete(0, "end")
        self.carregar_produtos()
        self.mensagem.configure(
            text=f"✓ Saída de {quantidade} unidade(s) registrada com sucesso!",
            text_color="green"
        )

    def _obter_quantidade(self):
        texto = self.quantidade.get().strip()

        if not texto:
            self.mensagem.configure(text="⚠ Informe a quantidade.", text_color="red")
            return None

        try:
            quantidade = int(texto)
        except ValueError:
            self.mensagem.configure(text="⚠ A quantidade deve ser um número inteiro.", text_color="red")
            return None

        if quantidade <= 0:
            self.mensagem.configure(text="⚠ A quantidade deve ser maior que zero.", text_color="red")
            return None

        return quantidade

    def voltar_dashboard(self):
        from telas.dashboard import Dashboard

        Dashboard(self.janela)
