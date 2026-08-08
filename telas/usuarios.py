import sqlite3
import customtkinter as ctk
from tkinter import messagebox, ttk

from banco import cadastrar_usuario, editar_usuario, excluir_usuario, listar_usuarios


class Usuarios:
    def __init__(self, janela):
        self.janela = janela

        for widget in self.janela.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.janela,
            text="👤 Usuários",
            font=("Segoe UI", 32, "bold")
        ).pack(pady=25)

        ctk.CTkButton(
            self.janela,
            text="← Voltar ao Dashboard",
            command=self.voltar_dashboard,
            width=200
        ).pack(pady=(0, 20))

        tabela_frame = ctk.CTkFrame(self.janela)
        tabela_frame.pack(padx=25, pady=10, expand=True, fill="both")

        colunas = ("id", "nome", "usuario")
        self.tabela = ttk.Treeview(tabela_frame, columns=colunas, show="headings")

        cabecalhos = [
            ("id", "ID", 80),
            ("nome", "Nome", 260),
            ("usuario", "Usuário", 180),
        ]

        for coluna, texto, largura in cabecalhos:
            self.tabela.heading(coluna, text=texto)
            self.tabela.column(coluna, width=largura, anchor="center")

        self.tabela.pack(side="left", expand=True, fill="both")

        barra_rolagem = ttk.Scrollbar(tabela_frame, orient="vertical", command=self.tabela.yview)
        barra_rolagem.pack(side="right", fill="y")
        self.tabela.configure(yscrollcommand=barra_rolagem.set)

        botoes = ctk.CTkFrame(self.janela)
        botoes.pack(pady=15)

        ctk.CTkButton(botoes, text="➕ Novo usuário", command=self.novo_usuario).grid(row=0, column=0, padx=10)
        ctk.CTkButton(botoes, text="✏ Editar", command=self.editar).grid(row=0, column=1, padx=10)
        ctk.CTkButton(botoes, text="🗑 Excluir", command=self.excluir).grid(row=0, column=2, padx=10)
        ctk.CTkButton(botoes, text="🔄 Atualizar", command=self.carregar).grid(row=0, column=3, padx=10)

        self.carregar()

    def carregar(self):
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        for usuario in listar_usuarios():
            self.tabela.insert("", "end", values=usuario)

    def novo_usuario(self):
        self._abrir_formulario("Novo usuário")

    def editar(self):
        dados = self._obter_usuario_selecionado()

        if dados is None:
            messagebox.showwarning("Atenção", "Selecione um usuário para editar.")
            return

        self._abrir_formulario("Editar usuário", dados)

    def excluir(self):
        dados = self._obter_usuario_selecionado()

        if dados is None:
            messagebox.showwarning("Atenção", "Selecione um usuário para excluir.")
            return

        confirmar = messagebox.askyesno(
            "Confirmar exclusão",
            f"Tem certeza que deseja excluir o usuário '{dados[2]}'?"
        )

        if not confirmar:
            return

        try:
            sucesso = excluir_usuario(dados[0])

            if not sucesso:
                messagebox.showwarning("Atenção", "Não é permitido excluir o último usuário do sistema.")
                return

            self.carregar()
            messagebox.showinfo("Sucesso", "Usuário excluído com sucesso!")

        except Exception as erro:
            messagebox.showerror("Erro", f"Não foi possível excluir o usuário.\n\n{erro}")

    def _abrir_formulario(self, titulo, dados=None):
        janela = ctk.CTkToplevel(self.janela)
        janela.title(titulo)
        janela.geometry("400x420")
        janela.resizable(False, False)
        janela.transient(self.janela)
        janela.grab_set()

        ctk.CTkLabel(
            janela,
            text=titulo,
            font=("Segoe UI", 24, "bold")
        ).pack(pady=25)

        nome = ctk.CTkEntry(janela, placeholder_text="Nome", width=300)
        nome.pack(pady=10)

        usuario = ctk.CTkEntry(janela, placeholder_text="Usuário", width=300)
        usuario.pack(pady=10)

        senha = ctk.CTkEntry(
            janela,
            placeholder_text="Senha" if dados is None else "Nova senha (opcional)",
            show="*",
            width=300
        )
        senha.pack(pady=10)

        confirmar_senha = ctk.CTkEntry(
            janela,
            placeholder_text="Confirmar senha",
            show="*",
            width=300
        )
        confirmar_senha.pack(pady=10)

        if dados:
            nome.insert(0, dados[1])
            usuario.insert(0, dados[2])

        def salvar():
            nome_texto = nome.get().strip()
            usuario_texto = usuario.get().strip()
            senha_texto = senha.get().strip()
            confirmar_senha_texto = confirmar_senha.get().strip()

            if not nome_texto or not usuario_texto:
                messagebox.showwarning("Atenção", "Informe nome e usuário.")
                return

            if dados is None and not senha_texto:
                messagebox.showwarning("Atenção", "Informe a senha.")
                return

            if senha_texto != confirmar_senha_texto:
                messagebox.showwarning("Atenção", "As senhas não conferem.")
                return

            try:
                if dados is None:
                    cadastrar_usuario(nome_texto, usuario_texto, senha_texto)
                    mensagem = "Usuário cadastrado com sucesso!"
                else:
                    editar_usuario(dados[0], nome_texto, usuario_texto, senha_texto or None)
                    mensagem = "Usuário atualizado com sucesso!"

                janela.destroy()
                self.carregar()
                messagebox.showinfo("Sucesso", mensagem)

            except sqlite3.IntegrityError:
                messagebox.showerror("Erro", "Já existe um usuário com esse login.")
            except Exception as erro:
                messagebox.showerror("Erro", f"Não foi possível salvar o usuário.\n\n{erro}")

        ctk.CTkButton(janela, text="Salvar", command=salvar, width=200).pack(pady=25)

    def _obter_usuario_selecionado(self):
        selecionado = self.tabela.selection()

        if not selecionado:
            return None

        return list(self.tabela.item(selecionado[0])["values"])

    def voltar_dashboard(self):
        from telas.dashboard import Dashboard

        Dashboard(self.janela)
