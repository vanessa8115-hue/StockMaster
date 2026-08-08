# StockMaster

Sistema de controle de estoque em Python com interface gráfica.

## Descrição

StockMaster é um aplicativo para gerenciamento de produtos, entradas, saídas e relatórios. Ele foi desenvolvido com `CustomTkinter` para interface moderna e usa um banco de dados local para armazenar informações de estoque.

## Funcionalidades

- Cadastro, edição e exclusão de produtos
- Busca de produtos por código, nome ou categoria
- Controle de quantidades no estoque e níveis de estoque mínimo
- Registro de entradas e saídas de produtos
- Visualização de relatórios de estoque
- Interface gráfica com navegação entre telas

## Tecnologias

- Python 3
- CustomTkinter
- Tkinter
- SQLite (ou outro banco local, conforme implementado em `banco.py`)

## Como usar

1. Instale o Python 3
2. Instale as dependências:

```bash
pip install customtkinter
```

3. Execute o aplicativo:

```bash
python main.py
```

## Estrutura do projeto

- `main.py` - ponto de entrada do aplicativo
- `banco.py` - lógica de banco de dados
- `telas/` - telas da interface gráfica
- `config.py` - configurações gerais do projeto

## Contato

- GitHub: https://github.com/vanessa8115-hue/StockMaster

## Observações

Se você usar um ambiente virtual, recomenda-se ativá-lo antes de instalar dependências.
