import os
import zipfile
from datetime import datetime
from tkinter import filedialog
from xml.sax.saxutils import escape


def escolher_arquivo(extensao, titulo):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_padrao = f"stockmaster_relatorio_{timestamp}.{extensao}"

    return filedialog.asksaveasfilename(
        title=titulo,
        defaultextension=f".{extensao}",
        initialfile=nome_padrao,
        filetypes=[(extensao.upper(), f"*.{extensao}")]
    )


def exportar_excel(caminho, titulo, cabecalhos, linhas):
    pasta = os.path.dirname(caminho)

    if pasta:
        os.makedirs(pasta, exist_ok=True)

    worksheet = _montar_planilha_xml(titulo, cabecalhos, linhas)

    arquivos = {
        "[Content_Types].xml": """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
</Types>""",
        "_rels/.rels": """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>""",
        "xl/workbook.xml": """<?xml version="1.0" encoding="UTF-8"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
          xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
    <sheet name="Relatório" sheetId="1" r:id="rId1"/>
  </sheets>
</workbook>""",
        "xl/_rels/workbook.xml.rels": """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>""",
        "xl/styles.xml": """<?xml version="1.0" encoding="UTF-8"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font></fonts>
  <fills count="1"><fill><patternFill patternType="none"/></fill></fills>
  <borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs count="2"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/><xf numFmtId="0" fontId="1" fillId="0" borderId="0"/></cellXfs>
</styleSheet>""",
        "xl/worksheets/sheet1.xml": worksheet,
    }

    with zipfile.ZipFile(caminho, "w", zipfile.ZIP_DEFLATED) as arquivo:
        for nome, conteudo in arquivos.items():
            arquivo.writestr(nome, conteudo)


def _montar_planilha_xml(titulo, cabecalhos, linhas):
    linhas_xml = []
    linhas_xml.append(_montar_linha(1, [titulo], estilo=1))
    linhas_xml.append(_montar_linha(3, cabecalhos, estilo=1))

    for indice, linha in enumerate(linhas, start=4):
        linhas_xml.append(_montar_linha(indice, linha))

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheetData>
    {''.join(linhas_xml)}
  </sheetData>
</worksheet>"""


def _montar_linha(numero, valores, estilo=0):
    celulas = []

    for indice, valor in enumerate(valores, start=1):
        referencia = f"{_coluna_excel(indice)}{numero}"
        texto = escape(str(valor))
        atributo_estilo = f' s="{estilo}"' if estilo else ""
        celulas.append(f'<c r="{referencia}" t="inlineStr"{atributo_estilo}><is><t>{texto}</t></is></c>')

    return f'<row r="{numero}">{"".join(celulas)}</row>'


def _coluna_excel(numero):
    nome = ""

    while numero:
        numero, resto = divmod(numero - 1, 26)
        nome = chr(65 + resto) + nome

    return nome


def exportar_pdf(caminho, titulo, cabecalhos, linhas):
    pasta = os.path.dirname(caminho)

    if pasta:
        os.makedirs(pasta, exist_ok=True)

    linhas_texto = [
        titulo,
        f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        "",
        " | ".join(str(cabecalho) for cabecalho in cabecalhos),
        "-" * 110,
    ]

    for linha in linhas:
        linhas_texto.append(" | ".join(str(valor) for valor in linha))

    paginas = [
        linhas_texto[indice:indice + 38]
        for indice in range(0, len(linhas_texto), 38)
    ] or [["Sem dados para exibir."]]

    objetos = []
    paginas_refs = []

    objetos.append("<< /Type /Catalog /Pages 2 0 R >>")
    objetos.append("<< /Type /Pages /Kids [] /Count 0 >>")
    objetos.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    for pagina in paginas:
        conteudo = _montar_conteudo_pdf(pagina)
        conteudo_numero = len(objetos) + 1
        pagina_numero = len(objetos) + 2

        objetos.append(f"<< /Length {len(conteudo.encode('latin-1', errors='replace'))} >>\nstream\n{conteudo}\nendstream")
        objetos.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 842 595] "
            f"/Resources << /Font << /F1 3 0 R >> >> /Contents {conteudo_numero} 0 R >>"
        )
        paginas_refs.append(f"{pagina_numero} 0 R")

    objetos[1] = f"<< /Type /Pages /Kids [{' '.join(paginas_refs)}] /Count {len(paginas_refs)} >>"

    _gravar_pdf(caminho, objetos)


def _montar_conteudo_pdf(linhas):
    comandos = ["BT", "/F1 10 Tf", "40 555 Td", "12 TL"]

    for linha in linhas:
        texto = _escapar_pdf(linha[:150])
        comandos.append(f"({texto}) Tj")
        comandos.append("T*")

    comandos.append("ET")

    return "\n".join(comandos)


def _escapar_pdf(texto):
    return (
        str(texto)
        .encode("latin-1", errors="replace")
        .decode("latin-1")
        .replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
    )


def _gravar_pdf(caminho, objetos):
    partes = ["%PDF-1.4\n"]
    offsets = [0]

    for indice, objeto in enumerate(objetos, start=1):
        offsets.append(sum(len(parte.encode("latin-1", errors="replace")) for parte in partes))
        partes.append(f"{indice} 0 obj\n{objeto}\nendobj\n")

    inicio_xref = sum(len(parte.encode("latin-1", errors="replace")) for parte in partes)
    partes.append(f"xref\n0 {len(objetos) + 1}\n")
    partes.append("0000000000 65535 f \n")

    for offset in offsets[1:]:
        partes.append(f"{offset:010d} 00000 n \n")

    partes.append(
        f"trailer\n<< /Size {len(objetos) + 1} /Root 1 0 R >>\n"
        f"startxref\n{inicio_xref}\n%%EOF"
    )

    with open(caminho, "wb") as arquivo:
        arquivo.write("".join(partes).encode("latin-1", errors="replace"))
