import customtkinter as ctk

from banco import validar_login
from telas.dashboard import Dashboard


class Login:
    def __init__(self, janela):
        self.janela = janela

        self.frame = ctk.CTkFrame(
            self.janela,
            width=400,
            height=450,
            corner_radius=20
        )
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        self.frame.pack_propagate(False)

        ctk.CTkLabel(
            self.frame,
            text="StockMaster",
            font=("Segoe UI", 32, "bold")
        ).pack(pady=(45, 10))

        ctk.CTkLabel(
            self.frame,
            text="Sistema de Gestão de Estoque"
        ).pack(pady=10)

        self.usuario = ctk.CTkEntry(
            self.frame,
            placeholder_text="Usuário",
            width=280
        )
        self.usuario.pack(pady=15)
        self.usuario.focus()

        self.senha = ctk.CTkEntry(
            self.frame,
            placeholder_text="Senha",
            show="*",
            width=280
        )
        self.senha.pack(pady=15)
        self.senha.bind("<Return>", lambda _evento: self.entrar())

        ctk.CTkButton(
            self.frame,
            text="Entrar",
            width=280,
            command=self.entrar
        ).pack(pady=25)

        self.mensagem = ctk.CTkLabel(self.frame, text="")
        self.mensagem.pack()

        ctk.CTkLabel(
            self.frame,
            text="Acesso padrão: admin / 123",
            font=("Segoe UI", 12)
        ).pack(pady=(20, 0))

    def entrar(self):
        usuario = self.usuario.get().strip()
        senha = self.senha.get().strip()

        if not usuario or not senha:
            self.mensagem.configure(
                text="Informe usuário e senha.",
                text_color="orange"
            )
            return

        resultado = validar_login(usuario, senha)

        if resultado:
            self.frame.destroy()
            Dashboard(self.janela)
        else:
            self.mensagem.configure(
                text="Usuário ou senha incorretos.",
                text_color="red"
            )
