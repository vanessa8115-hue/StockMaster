# StockMaster

Sistema de controle de estoque em Python com interface gráfica.

## Descrição

StockMaster é um aplicativo para gerenciamento de produtos, entradas, saídas e relatórios. Ele foi desenvolvido com `CustomTkinter` para interface moderna e utiliza um banco de dados local para armazenar e consultar informações de estoque.

## Funcionalidades

- Cadastro, edição e exclusão de produtos
- Busca por código, nome ou categoria
- Controle de quantidades no estoque e níveis de estoque mínimo
- Registro de entradas e saídas de produtos
- Visualização de relatórios de movimentos e estoque
- Interface gráfica com navegação entre telas

## Tecnologias

- Python 3
- CustomTkinter
- Tkinter
- SQLite

## Requisitos

- Python 3.8 ou superior
- `pip`

## Instalação

1. Clone o repositório ou copie o projeto para sua máquina.

```bash
git clone https://github.com/vanessa8115-hue/StockMaster.git
cd StockMaster
```

2. Crie e ative um ambiente virtual (recomendado):

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

## Uso

Para iniciar o aplicativo, execute:

```bash
python main.py
```

## Estrutura do projeto

- `main.py` - ponto de entrada do aplicativo
- `banco.py` - lógica de banco de dados e CRUD
- `config.py` - configurações do aplicativo
- `exportadores.py` - funções para exportação de dados
- `telas/` - telas da interface gráfica do sistema

## Observações

- Use um ambiente virtual para manter as dependências isoladas.
- O banco de dados local é criado automaticamente ao iniciar o aplicativo.

## Contato

- GitHub: https://github.com/vanessa8115-hue/StockMaster
