import os
import pandas as pd
import pyreaddbc
from dbfread import DBF

# onde estao os arquivos .dbc
pasta_dados = 'data/datasus_mg/'
if not os.path.exists(pasta_dados):
    pasta_dados = 'data/'

# so os arquivos RD de MG (internacoes), ex: RDMG2501.dbc
arquivos = [f for f in os.listdir(pasta_dados) if f.upper().startswith('RDMG') and f.upper().endswith('.DBC')]
arquivos = sorted(arquivos)

if not arquivos:
    print(f"Erro: Nenhum arquivo RDMG .dbc encontrado na pasta {pasta_dados}")
    exit()

print("Arquivos RD encontrados:", len(arquivos))
dfs = []

for arq in arquivos:
    caminho = os.path.join(pasta_dados, arq)
    caminho_dbf = caminho.replace('.dbc', '.dbf').replace('.DBC', '.dbf')

    try:
        # 1. descompacta o .dbc para .dbf
        pyreaddbc.dbc2dbf(caminho, caminho_dbf)

        # 2. le so as duas colunas que preciso, registro por registro
        tabela = DBF(caminho_dbf, load=False, encoding='latin1')
        linhas = []
        for registro in tabela:
            linhas.append((registro['MUNIC_RES'], registro['MUNIC_MOV']))
        dfs.append(pd.DataFrame(linhas, columns=['MUNIC_RES', 'MUNIC_MOV']))
        print(f"[{arq}] {len(linhas)} internacoes")

        # 3. apaga o .dbf temporario
        if os.path.exists(caminho_dbf):
            os.remove(caminho_dbf)

    except Exception as e:
        print(f"Erro ao ler {arq}: {e}")

if not dfs:
    print("Nenhum dado valido encontrado.")
    exit()

df = pd.concat(dfs, ignore_index=True)
df['MUNIC_RES'] = df['MUNIC_RES'].astype(str)
df['MUNIC_MOV'] = df['MUNIC_MOV'].astype(str)
print("Internacoes lidas:", len(df))

# tirar quem mora fora de MG (codigo IBGE de MG comeca com 31)
total_antes = len(df)
df = df[df['MUNIC_RES'].str.startswith('31')]
print("Removidas (moram fora de MG):", total_antes - len(df))

# tirar municipio ignorado (codigo terminado em 0000)
total_antes = len(df)
df = df[~df['MUNIC_RES'].str.endswith('0000')]
df = df[~df['MUNIC_MOV'].str.endswith('0000')]
print("Removidas (municipio ignorado):", total_antes - len(df))

# internacoes no proprio municipio e em outro municipio
df['mesmo'] = df['MUNIC_RES'] == df['MUNIC_MOV']
fora = df[~df['mesmo']]
print("\nInternacoes no proprio municipio:", df['mesmo'].sum())
print("Internacoes em outro municipio:", len(fora))
print("Percentual fora do municipio de residencia:", round(len(fora) / len(df) * 100, 1), "%")

# arestas do grafo (so entre municipios diferentes)
grafo = fora.groupby(['MUNIC_RES', 'MUNIC_MOV']).size().reset_index(name='internacoes')
grafo.columns = ['origem', 'destino', 'internacoes']

# resumo por municipio de residencia (precisa das internacoes locais tambem)
total_res = df.groupby('MUNIC_RES').size()
fora_res = fora.groupby('MUNIC_RES').size()
resumo = pd.DataFrame({'total': total_res, 'fora': fora_res}).fillna(0)
resumo['pct_fora'] = resumo['fora'] / resumo['total'] * 100

os.makedirs('data', exist_ok=True)
grafo.to_csv('data/grafo_sus_mg.csv', index=False)
resumo.to_csv('data/resumo_municipios.csv')

print("\n=== GRAFO GERADO ===")
print("Municipios no grafo:", len(pd.concat([grafo['origem'], grafo['destino']]).unique()))
print("Arestas:", len(grafo))
print("Internacoes fora do municipio de residencia:", grafo['internacoes'].sum())
