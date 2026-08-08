import customtkinter as ctk

import config
from banco import criar_banco, criar_backup_automatico_diario, obter_configuracao
from telas.login import Login


def iniciar_app():
    criar_banco()
    criar_backup_automatico_diario()

    modo_visual = obter_configuracao("modo_visual", config.MODO)

    ctk.set_appearance_mode(modo_visual)
    ctk.set_default_color_theme(config.TEMA)

    janela = ctk.CTk()
    janela.title(config.TITULO)
    janela.geometry(f"{config.LARGURA}x{config.ALTURA}")
    janela.resizable(False, False)

    Login(janela)
    janela.mainloop()


if __name__ == "__main__":
    iniciar_app()
