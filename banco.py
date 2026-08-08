import os
import sqlite3
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_BANCO = os.path.join(BASE_DIR, "banco")
PASTA_BACKUP = os.path.join(BASE_DIR, "backups")
CAMINHO_BANCO = os.path.join(PASTA_BANCO, "stockmaster.db")
TIPO_SAIDA = "Saída"
TIPO_SAIDA_LEGADO = "Sa" + chr(195) + chr(173) + "da"


def conectar():
    os.makedirs(PASTA_BANCO, exist_ok=True)

    conexao = sqlite3.connect(CAMINHO_BANCO, timeout=10)
    conexao.execute("PRAGMA busy_timeout = 10000")
    conexao.execute("PRAGMA journal_mode = WAL")
    conexao.execute("PRAGMA foreign_keys = ON")

    return conexao


def criar_banco():
    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                usuario TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE,
                nome TEXT NOT NULL,
                categoria TEXT,
                quantidade INTEGER DEFAULT 0,
                estoque_minimo INTEGER DEFAULT 5,
                preco REAL DEFAULT 0
            )
        """)

        cursor.execute("PRAGMA table_info(produtos)")
        nomes_colunas = [coluna[1] for coluna in cursor.fetchall()]

        if "estoque_minimo" not in nomes_colunas:
            cursor.execute("""
                ALTER TABLE produtos
                ADD COLUMN estoque_minimo INTEGER DEFAULT 5
            """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movimentacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id INTEGER NOT NULL,
                tipo TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                data DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (produto_id) REFERENCES produtos(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS configuracoes (
                chave TEXT PRIMARY KEY,
                valor TEXT NOT NULL
            )
        """)

        cursor.execute("""
            UPDATE movimentacoes
            SET tipo = ?
            WHERE tipo IN (?, ?)
        """, (TIPO_SAIDA, TIPO_SAIDA_LEGADO, "Saida"))

        cursor.execute("""
            INSERT OR IGNORE INTO usuarios (nome, usuario, senha)
            VALUES (?, ?, ?)
        """, ("Administrador", "admin", "123"))

        cursor.execute("""
            INSERT OR IGNORE INTO configuracoes (chave, valor)
            VALUES (?, ?)
        """, ("modo_visual", "Light"))

        conexao.commit()

    except sqlite3.Error:
        conexao.rollback()
        raise

    finally:
        conexao.close()


def obter_configuracao(chave, padrao=None):
    conexao = conectar()

    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT valor FROM configuracoes WHERE chave = ?", (chave,))
        resultado = cursor.fetchone()

        return resultado[0] if resultado else padrao

    finally:
        conexao.close()


def salvar_configuracao(chave, valor):
    conexao = conectar()

    try:
        cursor = conexao.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO configuracoes (chave, valor)
            VALUES (?, ?)
        """, (chave, valor))
        conexao.commit()

    except sqlite3.Error:
        conexao.rollback()
        raise

    finally:
        conexao.close()


def gerar_codigo_produto(cursor):
    cursor.execute("""
        SELECT codigo
        FROM produtos
        WHERE codigo LIKE 'PROD-%'
        ORDER BY id DESC
        LIMIT 1
    """)

    resultado = cursor.fetchone()

    if resultado is None:
        return "PROD-0001"

    try:
        numero = int(resultado[0].replace("PROD-", ""))
    except (ValueError, AttributeError):
        numero = 0

    return f"PROD-{numero + 1:04d}"


def validar_login(usuario, senha):
    conexao = conectar()

    try:
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT id, nome, usuario
            FROM usuarios
            WHERE usuario = ? AND senha = ?
        """, (usuario, senha))

        return cursor.fetchone()

    finally:
        conexao.close()


def listar_usuarios():
    conexao = conectar()

    try:
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT id, nome, usuario
            FROM usuarios
            ORDER BY nome
        """)
        return cursor.fetchall()

    finally:
        conexao.close()


def cadastrar_usuario(nome, usuario, senha):
    conexao = conectar()

    try:
        cursor = conexao.cursor()
        cursor.execute("""
            INSERT INTO usuarios (nome, usuario, senha)
            VALUES (?, ?, ?)
        """, (nome, usuario, senha))
        conexao.commit()

    except sqlite3.Error:
        conexao.rollback()
        raise

    finally:
        conexao.close()


def editar_usuario(id_usuario, nome, usuario, senha=None):
    conexao = conectar()

    try:
        cursor = conexao.cursor()

        if senha:
            cursor.execute("""
                UPDATE usuarios
                SET nome = ?, usuario = ?, senha = ?
                WHERE id = ?
            """, (nome, usuario, senha, id_usuario))
        else:
            cursor.execute("""
                UPDATE usuarios
                SET nome = ?, usuario = ?
                WHERE id = ?
            """, (nome, usuario, id_usuario))

        conexao.commit()

    except sqlite3.Error:
        conexao.rollback()
        raise

    finally:
        conexao.close()


def excluir_usuario(id_usuario):
    conexao = conectar()

    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios")

        if cursor.fetchone()[0] <= 1:
            return False

        cursor.execute("DELETE FROM usuarios WHERE id = ?", (id_usuario,))
        conexao.commit()
        return cursor.rowcount > 0

    except sqlite3.Error:
        conexao.rollback()
        raise

    finally:
        conexao.close()


def cadastrar_produto(nome, categoria, quantidade, estoque_minimo, preco):
    conexao = conectar()

    try:
        cursor = conexao.cursor()
        codigo = gerar_codigo_produto(cursor)

        cursor.execute("""
            INSERT INTO produtos (
                codigo,
                nome,
                categoria,
                quantidade,
                estoque_minimo,
                preco
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (codigo, nome, categoria, quantidade, estoque_minimo, preco))

        conexao.commit()
        return codigo

    except sqlite3.Error:
        conexao.rollback()
        raise

    finally:
        conexao.close()


def listar_produtos():
    conexao = conectar()

    try:
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT id, codigo, nome, categoria, quantidade, estoque_minimo, preco
            FROM produtos
            ORDER BY id DESC
        """)

        return cursor.fetchall()

    finally:
        conexao.close()


def buscar_produtos(termo):
    conexao = conectar()

    try:
        cursor = conexao.cursor()
        like = f"%{termo}%"

        cursor.execute("""
            SELECT id, codigo, nome, categoria, quantidade, estoque_minimo, preco
            FROM produtos
            WHERE nome LIKE ?
               OR codigo LIKE ?
               OR categoria LIKE ?
            ORDER BY nome
        """, (like, like, like))

        return cursor.fetchall()

    finally:
        conexao.close()


def editar_produto(id_produto, nome, categoria, quantidade, estoque_minimo, preco):
    conexao = conectar()

    try:
        cursor = conexao.cursor()
        cursor.execute("""
            UPDATE produtos
            SET nome = ?,
                categoria = ?,
                quantidade = ?,
                estoque_minimo = ?,
                preco = ?
            WHERE id = ?
        """, (nome, categoria, quantidade, estoque_minimo, preco, id_produto))

        conexao.commit()

    except sqlite3.Error:
        conexao.rollback()
        raise

    finally:
        conexao.close()


def excluir_produto(id_produto):
    conexao = conectar()

    try:
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM movimentacoes WHERE produto_id = ?", (id_produto,))
        cursor.execute("DELETE FROM produtos WHERE id = ?", (id_produto,))
        conexao.commit()

    except sqlite3.Error:
        conexao.rollback()
        raise

    finally:
        conexao.close()


def contar_produtos():
    conexao = conectar()

    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT COUNT(*) FROM produtos")
        return cursor.fetchone()[0]

    finally:
        conexao.close()


def valor_estoque():
    conexao = conectar()

    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT SUM(quantidade * preco) FROM produtos")
        return cursor.fetchone()[0] or 0

    finally:
        conexao.close()


def estoque_baixo():
    conexao = conectar()

    try:
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT COUNT(*)
            FROM produtos
            WHERE quantidade <= estoque_minimo
        """)
        return cursor.fetchone()[0]

    finally:
        conexao.close()


def listar_estoque_baixo():
    conexao = conectar()

    try:
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT id, codigo, nome, categoria, quantidade, estoque_minimo, preco
            FROM produtos
            WHERE quantidade <= estoque_minimo
            ORDER BY quantidade ASC, nome ASC
        """)
        return cursor.fetchall()

    finally:
        conexao.close()


def registrar_entrada(produto_id, quantidade):
    return registrar_movimentacao(produto_id, quantidade, "Entrada")


def registrar_saida(produto_id, quantidade):
    conexao = conectar()

    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT quantidade FROM produtos WHERE id = ?", (produto_id,))
        resultado = cursor.fetchone()

        if resultado is None or quantidade <= 0:
            return False

        estoque_atual = resultado[0]

        if quantidade > estoque_atual:
            return False

        cursor.execute("""
            UPDATE produtos
            SET quantidade = quantidade - ?
            WHERE id = ?
        """, (quantidade, produto_id))

        cursor.execute("""
            INSERT INTO movimentacoes (produto_id, tipo, quantidade)
            VALUES (?, ?, ?)
        """, (produto_id, TIPO_SAIDA, quantidade))

        conexao.commit()
        return True

    except sqlite3.Error:
        conexao.rollback()
        raise

    finally:
        conexao.close()


def registrar_movimentacao(produto_id, quantidade, tipo):
    if quantidade <= 0:
        return False

    conexao = conectar()

    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT id FROM produtos WHERE id = ?", (produto_id,))

        if cursor.fetchone() is None:
            return False

        cursor.execute("""
            UPDATE produtos
            SET quantidade = quantidade + ?
            WHERE id = ?
        """, (quantidade, produto_id))

        cursor.execute("""
            INSERT INTO movimentacoes (produto_id, tipo, quantidade)
            VALUES (?, ?, ?)
        """, (produto_id, tipo, quantidade))

        conexao.commit()
        return True

    except sqlite3.Error:
        conexao.rollback()
        raise

    finally:
        conexao.close()


def total_movimentos(tipo):
    tipos = [tipo]

    if tipo == TIPO_SAIDA:
        tipos.extend([TIPO_SAIDA_LEGADO, "Saida"])

    conexao = conectar()

    try:
        cursor = conexao.cursor()
        placeholders = ",".join("?" for _ in tipos)

        cursor.execute(f"""
            SELECT SUM(quantidade)
            FROM movimentacoes
            WHERE tipo IN ({placeholders})
        """, tipos)

        return cursor.fetchone()[0] or 0

    finally:
        conexao.close()


def listar_movimentacoes(data_inicio=None, data_fim=None):
    conexao = conectar()

    try:
        cursor = conexao.cursor()
        filtros = []
        parametros = []

        if data_inicio:
            filtros.append("date(movimentacoes.data) >= date(?)")
            parametros.append(data_inicio)

        if data_fim:
            filtros.append("date(movimentacoes.data) <= date(?)")
            parametros.append(data_fim)

        where = ""

        if filtros:
            where = "WHERE " + " AND ".join(filtros)

        cursor.execute(f"""
            SELECT
                movimentacoes.id,
                produtos.codigo,
                produtos.nome,
                movimentacoes.tipo,
                movimentacoes.quantidade,
                strftime('%d/%m/%Y %H:%M', movimentacoes.data)
            FROM movimentacoes
            INNER JOIN produtos ON produtos.id = movimentacoes.produto_id
            {where}
            ORDER BY movimentacoes.id DESC
        """, parametros)

        return cursor.fetchall()

    finally:
        conexao.close()


def criar_backup_banco():
    if not os.path.exists(CAMINHO_BANCO):
        criar_banco()

    os.makedirs(PASTA_BACKUP, exist_ok=True)

    data = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = os.path.join(PASTA_BACKUP, f"stockmaster_backup_{data}.db")

    origem = conectar()
    backup = sqlite3.connect(destino)

    try:
        origem.backup(backup)
    finally:
        backup.close()
        origem.close()

    return destino


def criar_backup_automatico_diario():
    hoje = datetime.now().strftime("%Y-%m-%d")
    ultimo_backup = obter_configuracao("ultimo_backup_automatico", "")

    if ultimo_backup == hoje:
        return None

    caminho = criar_backup_banco()
    salvar_configuracao("ultimo_backup_automatico", hoje)

    return caminho
