# Analisa data/motivos_agregado.csv: que tipo de internacao sai dos municipios?
# Entrada: data/motivos_agregado.csv e data/nodes.csv
# Saida: tabelas na tela e em results/motivos_*.csv
# Rodar na raiz do projeto: python3 scripts/analise_motivos.py
import os
import pandas as pd

d = pd.read_csv("data/motivos_agregado.csv", dtype=str)
d["n"] = d["n"].astype(int)
d["fora"] = d["fora"].astype(int)
nos = pd.read_csv("data/nodes.csv")
os.makedirs("results", exist_ok=True)

total = d["n"].sum()
print("Total:", total, " fora:", d[d.fora == 1]["n"].sum())

# nomes (conferir no dicionario do SIH se aparecer algum codigo diferente)
nome_comp = {"01": "atencao basica", "02": "media", "03": "alta", "00": "nao se aplica"}
nome_espec = {"01": "cirurgia", "02": "obstetricia", "03": "clinica medica",
              "04": "cuidados prolongados", "05": "psiquiatria", "06": "tisiologia",
              "07": "pediatria", "08": "reabilitacao", "09": "psiquiatria hospital-dia"}


def tabela(col, nomes=None):
    # para cada valor de 'col': total, fora e percentual fora
    t = d.pivot_table(index=col, columns="fora", values="n", aggfunc="sum", fill_value=0)
    t.columns = ["local", "fora"]
    t["total"] = t["local"] + t["fora"]
    t["pct_fora"] = (t["fora"] / t["total"] * 100).round(1)
    t["pct_do_que_sai"] = (t["fora"] / t["fora"].sum() * 100).round(1)
    if nomes:
        t.insert(0, "nome", [nomes.get(i, "?") for i in t.index])
    return t.sort_values("fora", ascending=False)


# 1. complexidade
t1 = tabela("COMPLEX", nome_comp)
print("\n=== 1. COMPLEXIDADE (pct_fora = quanto desse tipo acontece fora) ===")
print(t1.to_string())
t1.to_csv("results/motivos_complexidade.csv")

# 2. especialidade
t2 = tabela("ESPEC", nome_espec)
print("\n=== 2. ESPECIALIDADE ===")
print(t2.to_string())
t2.to_csv("results/motivos_especialidade.csv")

# 3. capitulo do CID
t3 = tabela("CAP_CID")
print("\n=== 3. CAPITULO DO CID-10 (10 que mais saem) ===")
print(t3.head(10).to_string())
t3.to_csv("results/motivos_capitulo_cid.csv")

# 4. carater da internacao: eletivo (01) ou urgencia/outros
d["tipo_car"] = d["CAR_INT"].apply(lambda x: "eletivo" if x == "01" else "urgencia/outros")
t4 = d.pivot_table(index="tipo_car", columns="fora", values="n", aggfunc="sum", fill_value=0)
t4.columns = ["local", "fora"]
t4["pct_fora"] = (t4["fora"] / (t4["local"] + t4["fora"]) * 100).round(1)
print("\n=== 4. CARATER (eletivo x urgencia/outros) ===")
print(t4.to_string())
t4.to_csv("results/motivos_carater.csv")

# 5. complexidade do que sai, por porte do municipio de residencia
porte = nos.set_index("Id")["total_res"]
d["total_res"] = d["MUNIC_RES"].astype(int).map(porte)
faixas = [0, 500, 1000, 2000, 5000, 20000, 10**9]
rotulos = ["<500", "500-1k", "1k-2k", "2k-5k", "5k-20k", ">=20k"]
d["faixa"] = pd.cut(d["total_res"], faixas, labels=rotulos, right=False)
sai = d[d.fora == 1].pivot_table(index="faixa", columns="COMPLEX", values="n",
                                 aggfunc="sum", fill_value=0, observed=False)
sai_pct = (sai.div(sai.sum(axis=1), axis=0) * 100).round(1)
sai_pct.columns = [f"{c} {nome_comp.get(c, '?')} (%)" for c in sai_pct.columns]
print("\n=== 5. COMPLEXIDADE DO QUE SAI, POR PORTE DO MUNICIPIO ===")
print(sai_pct.to_string())
sai_pct.to_csv("results/motivos_complexidade_por_porte.csv")

# 6. especialidade do que sai, por porte
sai_e = d[d.fora == 1].pivot_table(index="faixa", columns="ESPEC", values="n",
                                   aggfunc="sum", fill_value=0, observed=False)
sai_e_pct = (sai_e.div(sai_e.sum(axis=1), axis=0) * 100).round(1)
sai_e_pct.columns = [f"{c} {nome_espec.get(c, '?')} (%)" for c in sai_e_pct.columns]
print("\n=== 6. ESPECIALIDADE DO QUE SAI, POR PORTE ===")
print(sai_e_pct.to_string())
sai_e_pct.to_csv("results/motivos_especialidade_por_porte.csv")
