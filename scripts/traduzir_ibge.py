import sys
import json
import re
import os

# Caminho para o arquivo dos codigos do IBGE
caminho_json = os.path.join(os.path.dirname(__file__), '..', 'data', 'municipios.json')

try:
    # Abre o arquivo
    with open(caminho_json, 'r', encoding='utf-8') as f:
        dados = json.load(f)
        # cria o dicionário pegando os 6 primeiros dígitos do código
        nomes = {str(c['id'])[:6]: c['nome'] for c in dados}
except Exception as e:
    sys.stderr.write(f"\n[ERRO] Não foi possível ler data/municipios.json: {e}\n\n")
    nomes = {}

# Lê o relatório do C++, traduz e limpa
for linha in sys.stdin:
    # Troca o código pela cidade
    linha = re.sub(r'\b31\d{4}\b', lambda m: nomes.get(m.group(0), m.group(0)), linha)
    # Remove o texto sujo
    linha = linha.replace("Cod IBGE ", "")
    sys.stdout.write(linha)
