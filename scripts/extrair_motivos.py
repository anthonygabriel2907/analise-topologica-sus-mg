# Etapa 3 (nova): le de novo os arquivos RD do SIH e guarda, para cada internacao de morador de MG,
# alem da residencia e do hospital, o tipo de internacao: ESPEC (especialidade), COMPLEX (complexidade),
# DIAG_PRINC (capitulo do CID-10) e CAR_INT (carater: eletivo ou urgencia).
# Os filtros sao os mesmos do gerar_grafo_saude.py, entao os totais tem que bater:
# 1.589.022 internacoes e 581.742 fora do municipio.
# Saida: data/motivos_agregado.csv (uma linha por combinacao, com a contagem)
# Rodar na raiz do projeto: python3 scripts/extrair_motivos.py
import os
from collections import Counter
import pyreaddbc
from dbfread import DBF


def capitulo_cid(diag):
    # recebe o CID principal (ex: "O800", "C509") e devolve o numero do capitulo do CID-10
    d = (diag or "").strip().upper()
    if len(d) < 3:
        return "sem CID"
    letra = d[0]
    try:
        num = int(d[1:3])
    except ValueError:
        return "sem CID"
    if letra in "AB":
        return "I"
    if letra == "C":
        return "II"
    if letra == "D":
        return "II" if num <= 48 else "III"
    if letra == "E":
        return "IV"
    if letra == "F":
        return "V"
    if letra == "G":
        return "VI"
    if letra == "H":
        return "VII" if num <= 59 else "VIII"
    capitulos = {"I": "IX", "J": "X", "K": "XI", "L": "XII", "M": "XIII", "N": "XIV",
                 "O": "XV", "P": "XVI", "Q": "XVII", "R": "XVIII", "S": "XIX", "T": "XIX",
                 "V": "XX", "W": "XX", "X": "XX", "Y": "XX", "Z": "XXI", "U": "XXII"}
    return capitulos.get(letra, "sem CID")


def contar(registro, cont):
    # aplica os mesmos filtros do gerar_grafo_saude.py e soma 1 na combinacao do registro
    res = str(registro["MUNIC_RES"])
    mov = str(registro["MUNIC_MOV"])
    if not res.startswith("31"):
        return
    if res.endswith("0000") or mov.endswith("0000"):
        return
    fora = 0 if res == mov else 1
    espec = str(registro["ESPEC"]).strip()
    complexidade = str(registro["COMPLEX"]).strip()
    cap = capitulo_cid(registro["DIAG_PRINC"])
    carater = str(registro["CAR_INT"]).strip()
    cont[(res, fora, espec, complexidade, cap, carater)] += 1


if __name__ == "__main__":
    pasta_dados = "data/datasus_mg/"
    if not os.path.exists(pasta_dados):
        pasta_dados = "data/"

    arquivos = sorted(f for f in os.listdir(pasta_dados)
                      if f.upper().startswith("RDMG") and f.upper().endswith(".DBC"))
    if not arquivos:
        print("Erro: nenhum arquivo RDMG .dbc encontrado em", pasta_dados)
        raise SystemExit

    print("Arquivos RD encontrados:", len(arquivos))
    cont = Counter()
    for arq in arquivos:
        caminho = os.path.join(pasta_dados, arq)
        caminho_dbf = caminho.replace(".dbc", ".dbf").replace(".DBC", ".dbf")
        pyreaddbc.dbc2dbf(caminho, caminho_dbf)
        tabela = DBF(caminho_dbf, load=False, encoding="latin1")
        n = 0
        for registro in tabela:
            contar(registro, cont)
            n += 1
        os.remove(caminho_dbf)
        print(f"[{arq}] {n} registros lidos")

    with open("data/motivos_agregado.csv", "w", encoding="utf-8") as f:
        f.write("MUNIC_RES,fora,ESPEC,COMPLEX,CAP_CID,CAR_INT,n\n")
        for (res, fora, espec, comp, cap, car), n in sorted(cont.items()):
            f.write(f"{res},{fora},{espec},{comp},{cap},{car},{n}\n")

    total = sum(cont.values())
    total_fora = sum(n for k, n in cont.items() if k[1] == 1)
    print("\n=== CONFERENCIA (tem que bater com o grafo) ===")
    print("Internacoes de moradores de MG:", total, "(esperado 1589022)")
    print("Internacoes fora do municipio:", total_fora, "(esperado 581742)")
    print("Linhas no arquivo agregado:", len(cont))
