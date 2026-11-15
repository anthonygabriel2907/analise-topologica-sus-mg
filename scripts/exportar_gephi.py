import pandas as pd
import requests

# --- arestas (aceita qualquer cabeçalho: origem,destino,internacoes ou Source,Target,Weight) ---
g = pd.read_csv('data/grafo_sus_mg.csv', dtype=str)
g = g.iloc[:, :3]
g.columns = ['origem', 'destino', 'internacoes']
g['internacoes'] = g['internacoes'].astype(int)

edges = g.rename(columns={'origem': 'Source', 'destino': 'Target', 'internacoes': 'Weight'})
edges['Type'] = 'Directed'

# --- nomes dos municipios (IBGE, 6 digitos como no DATASUS) ---
print("Baixando nomes dos municipios do IBGE...")
url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados/MG/municipios"
nomes = {str(c['id'])[:6]: c['nome'] for c in requests.get(url).json()}

# --- resumo por municipio (total de internacoes de residentes e % fora) ---
resumo = pd.read_csv('data/resumo_municipios.csv', dtype=str)
resumo = resumo.set_index(resumo.columns[0])
resumo['total'] = pd.to_numeric(resumo['total'])
resumo['pct_fora'] = pd.to_numeric(resumo['pct_fora'])

# --- atributos dos nos ---
recebidos = g.groupby('destino')['internacoes'].sum()   # grau de entrada ponderado
enviados = g.groupby('origem')['internacoes'].sum()     # grau de saida ponderado

ids = pd.concat([g['origem'], g['destino']]).unique()
nodes = pd.DataFrame({'Id': ids})
nodes['Label'] = nodes['Id'].map(nomes).fillna(nodes['Id'])
nodes['recebidos'] = nodes['Id'].map(recebidos).fillna(0).astype(int)
nodes['enviados'] = nodes['Id'].map(enviados).fillna(0).astype(int)
nodes['total_res'] = nodes['Id'].map(resumo['total']).fillna(0).astype(int)
nodes['pct_fora'] = nodes['Id'].map(resumo['pct_fora']).fillna(0).round(1)
nodes['saldo'] = nodes['recebidos'] - nodes['enviados']   # >0 polo, <0 deserto

# --- versao filtrada: so os 3 destinos principais de cada municipio ---
top3 = (edges.sort_values('Weight', ascending=False)
             .groupby('Source').head(3))

nodes.to_csv('data/nodes.csv', index=False)
edges.to_csv('data/edges.csv', index=False)
top3.to_csv('data/edges_top3.csv', index=False)

print(len(nodes), "nos |", len(edges), "arestas |", len(top3), "arestas top3")
print("Arquivos gerados em data/: nodes.csv, edges.csv, edges_top3.csv")
