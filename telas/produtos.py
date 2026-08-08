import customtkinter as ctk
from tkinter import messagebox, ttk

from banco import (
    buscar_produtos,
    cadastrar_produto,
    editar_produto,
    excluir_produto,
    listar_produtos,
)


class Produtos:
    def __init__(self, janela):
        self.janela = janela

        for widget in self.janela.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.janela,
            text="📦 Produtos",
            font=("Segoe UI", 32, "bold")
        ).pack(pady=20)

        topo = ctk.CTkFrame(self.janela)
        topo.pack(pady=10)

        self.pesquisa = ctk.CTkEntry(
            topo,
            placeholder_text="Pesquisar por nome, código ou categoria",
            width=300
        )
        self.pesquisa.grid(row=0, column=0, padx=10)
        self.pesquisa.bind("<Return>", lambda _evento: self.buscar())

        ctk.CTkButton(topo, text="🔎 Buscar", command=self.buscar).grid(
            row=0,
            column=1,
            padx=10
        )
        ctk.CTkButton(topo, text="← Voltar ao Dashboard", command=self.voltar_dashboard).grid(
            row=0,
            column=2,
            padx=10
        )

        tabela_frame = ctk.CTkFrame(self.janela)
        tabela_frame.pack(pady=20, padx=20, expand=True, fill="both")

        colunas = ("id", "codigo", "nome", "categoria", "quantidade", "estoque_minimo", "preco")
        self.tabela = ttk.Treeview(tabela_frame, columns=colunas, show="headings")

        cabecalhos = [
            ("id", "ID", 60),
            ("codigo", "Código", 110),
            ("nome", "Produto", 220),
            ("categoria", "Categoria", 150),
            ("quantidade", "Estoque", 90),
            ("estoque_minimo", "Estoque mín.", 110),
            ("preco", "Preço", 100),
        ]

        for coluna, texto, largura in cabecalhos:
            self.tabela.heading(coluna, text=texto)
            self.tabela.column(coluna, width=largura, anchor="center")

        self.tabela.pack(side="left", expand=True, fill="both")

        barra_rolagem = ttk.Scrollbar(
            tabela_frame,
            orient="vertical",
            command=self.tabela.yview
        )
        barra_rolagem.pack(side="right", fill="y")
        self.tabela.configure(yscrollcommand=barra_rolagem.set)

        botoes = ctk.CTkFrame(self.janela)
        botoes.pack(pady=10)

        ctk.CTkButton(botoes, text="🔄 Atualizar", command=self.carregar).grid(row=0, column=0, padx=10)
        ctk.CTkButton(botoes, text="🗑 Excluir", command=self.excluir).grid(row=0, column=1, padx=10)
        ctk.CTkButton(botoes, text="✏ Editar", command=self.editar).grid(row=0, column=2, padx=10)
        ctk.CTkButton(botoes, text="➕ Novo Produto", command=self.novo_produto).grid(row=0, column=3, padx=10)

        self.carregar()

    def carregar(self):
        self._preencher_tabela(listar_produtos())

    def buscar(self):
        termo = self.pesquisa.get().strip()
        self._preencher_tabela(buscar_produtos(termo))

    def _preencher_tabela(self, produtos):
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        for produto in produtos:
            id_produto, codigo, nome, categoria, quantidade, estoque_minimo, preco = produto
            self.tabela.insert(
                "",
                "end",
                values=(
                    id_produto,
                    codigo,
                    nome,
                    categoria,
                    quantidade,
                    estoque_minimo,
                    f"R$ {preco:.2f}",
                )
            )

    def excluir(self):
        dados = self._obter_produto_selecionado()

        if dados is None:
            messagebox.showwarning("Atenção", "Selecione um produto para excluir.")
            return

        confirmar = messagebox.askyesno(
            "Confirmar exclusão",
            f"Tem certeza que deseja excluir o produto?\n\n"
            f"Código: {dados[1]}\n"
            f"Produto: {dados[2]}"
        )

        if not confirmar:
            return

        try:
            excluir_produto(dados[0])
            self.carregar()
            messagebox.showinfo("Sucesso", "Produto excluído com sucesso!")
        except Exception as erro:
            messagebox.showerror("Erro", f"Não foi possível excluir o produto.\n\n{erro}")

    def novo_produto(self):
        self._abrir_formulario("Novo Produto")

    def editar(self):
        dados = self._obter_produto_selecionado()

        if dados is None:
            messagebox.showwarning("Atenção", "Selecione um produto para editar.")
            return

        self._abrir_formulario("Editar Produto", dados)

    def _abrir_formulario(self, titulo, dados=None):
        janela = ctk.CTkToplevel(self.janela)
        janela.title(titulo)
        janela.geometry("420x520")
        janela.resizable(False, False)
        janela.transient(self.janela)
        janela.grab_set()

        if dados:
            ctk.CTkLabel(
                janela,
                text=f"Código: {dados[1]}",
                font=("Segoe UI", 16, "bold")
            ).pack(pady=15)
        else:
            ctk.CTkLabel(
                janela,
                text="Código gerado automaticamente",
                font=("Segoe UI", 16, "bold")
            ).pack(pady=15)

        campos = {}
        nomes = ["Nome", "Categoria", "Quantidade", "Estoque mínimo", "Preço"]
        valores = ["", "", "0", "5", "0.00"] if dados is None else dados[2:]

        for nome, valor in zip(nomes, valores):
            entrada = ctk.CTkEntry(janela, placeholder_text=nome, width=300)
            entrada.insert(0, str(valor).replace("R$ ", ""))
            entrada.pack(pady=8)
            campos[nome] = entrada

        def salvar():
            valores_validados = self._validar_campos(campos)

            if valores_validados is None:
                return

            nome, categoria, quantidade, estoque_minimo, preco = valores_validados

            try:
                if dados is None:
                    codigo = cadastrar_produto(nome, categoria, quantidade, estoque_minimo, preco)
                    mensagem = f"Produto cadastrado com sucesso!\n\nCódigo gerado: {codigo}"
                else:
                    editar_produto(dados[0], nome, categoria, quantidade, estoque_minimo, preco)
                    mensagem = "Produto atualizado com sucesso!"

                janela.destroy()
                self.carregar()
                messagebox.showinfo("Sucesso", mensagem)

            except Exception as erro:
                messagebox.showerror("Erro", f"Não foi possível salvar o produto.\n\n{erro}")

        ctk.CTkButton(janela, text="Salvar", command=salvar, width=200).pack(pady=20)

    def _validar_campos(self, campos):
        nome = campos["Nome"].get().strip()
        categoria = campos["Categoria"].get().strip()
        quantidade_texto = campos["Quantidade"].get().strip()
        estoque_minimo_texto = campos["Estoque mínimo"].get().strip()
        preco_texto = campos["Preço"].get().strip()

        if not nome:
            messagebox.showwarning("Atenção", "Informe o nome do produto.")
            return None

        if not categoria:
            messagebox.showwarning("Atenção", "Informe a categoria do produto.")
            return None

        try:
            quantidade = int(quantidade_texto)
            estoque_minimo = int(estoque_minimo_texto)
            preco = float(preco_texto.replace(",", "."))
        except ValueError:
            messagebox.showerror(
                "Erro",
                "Quantidade e estoque mínimo devem ser inteiros. Preço deve ser um número válido."
            )
            return None

        if quantidade < 0 or estoque_minimo < 0 or preco < 0:
            messagebox.showerror("Erro", "Os valores numéricos não podem ser negativos.")
            return None

        return nome, categoria, quantidade, estoque_minimo, preco

    def _obter_produto_selecionado(self):
        selecionado = self.tabela.selection()

        if not selecionado:
            return None

        dados = list(self.tabela.item(selecionado[0])["values"])
        dados[6] = float(str(dados[6]).replace("R$", "").replace(",", ".").strip())

        return dados

    def voltar_dashboard(self):
        from telas.dashboard import Dashboard

        Dashboard(self.janela)
