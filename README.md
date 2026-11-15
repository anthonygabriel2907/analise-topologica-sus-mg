# Análise topológica da rede de internações do SUS em Minas Gerais (2025)

Trabalho final da disciplina Algoritmo e Estrutura de Dados II.

Modelamos as internações do SUS em Minas Gerais em 2025 como um grafo direcionado e ponderado: cada vértice é um município e cada aresta liga o município onde o paciente mora ao município onde fica o hospital. Com a lista de adjacência, os graus ponderados e uma busca em largura (BFS) medimos quais municípios concentram as internações vindas de fora e quanto cada município depende de outros para internar seus moradores.

## Sumário

1. [Objetivo](#1-objetivo)
2. [Dados e fontes](#2-dados-e-fontes)
3. [Modelagem do grafo](#3-modelagem-do-grafo)
4. [Estruturas de dados e algoritmos](#4-estruturas-de-dados-e-algoritmos)
5. [Arquitetura do código](#5-arquitetura-do-código)
6. [Como compilar e executar](#6-como-compilar-e-executar)
7. [Resultados](#7-resultados)
8. [Limitações e leitura dos resultados](#8-limitações-e-leitura-dos-resultados)
9. [Reprodutibilidade e dataset](#9-reprodutibilidade-e-dataset)
10. [Autoria](#10-autoria)

## 1. Objetivo

**Pergunta do trabalho:** como as internações do SUS em Minas Gerais se distribuem entre os 853 municípios, e quanto dos moradores se interna fora do município onde mora?

Para responder, o programa:

- constrói o grafo de fluxos entre municípios a partir dos dados do DATASUS;
- identifica os **polos**, que são os municípios que mais recebem internações de moradores de outros municípios (grau de entrada ponderado);
- identifica os municípios de **maior saída**, de onde mais moradores se internam fora (grau de saída ponderado);
- usa uma **BFS na rede invertida** para mapear quais municípios alimentam um polo, direta e indiretamente (o polo analisado é Belo Horizonte);
- calcula, por município, a proporção de internações feitas fora do município de residência (`pct_fora`, em `data/nodes.csv`).

O trabalho descreve o fluxo de internações. Ele não avalia a qualidade nem a suficiência da oferta de saúde.

## 2. Dados e fontes

| Fonte | O que foi usado | Arquivos |
|---|---|---|
| DATASUS, SIH/SUS, arquivo RD (AIH Reduzida), Minas Gerais, competências 01 a 12/2025 | colunas `MUNIC_RES` (município de residência) e `MUNIC_MOV` (município do hospital), ambas com código IBGE de 6 dígitos | `RDMG2501.dbc` a `RDMG2512.dbc`, baixados da página de transferência de arquivos do DATASUS (https://datasus.saude.gov.br/transferencia-de-arquivos/) |
| IBGE, API de localidades (municípios de MG) | código e nome de cada município, usados só para traduzir os códigos na saída | `data/municipios.json` |

Cada registro do arquivo RD corresponde a uma internação (AIH), e não a uma pessoa.

### Tratamento dos dados

O tratamento tem duas etapas, as duas em Python.

**Etapa 1: `scripts/gerar_grafo_saude.py`** (usa `pyreaddbc`, `dbfread` e `pandas`)

1. converter cada `.dbc` (formato comprimido do DATASUS) para `.dbf` e ler apenas `MUNIC_RES` e `MUNIC_MOV`;
2. manter só os moradores de Minas Gerais (código IBGE começando com `31`);
3. descartar registros com município ignorado (código terminado em `0000`);
4. internações no próprio município não viram aresta (não há laços); elas só entram no total de internações do município (`total_res`);
5. agrupar por (município de residência, município do hospital) e somar o número de internações, que vira o peso da aresta.

Saídas: `data/grafo_sus_mg.csv` (arestas) e `data/resumo_municipios.csv` (por município: `total`, `fora` e `pct_fora`).

**Etapa 2: `scripts/exportar_gephi.py`** (usa `pandas` e `requests`)

Lê as duas saídas da etapa 1, baixa os nomes dos municípios da API do IBGE e gera `data/edges.csv`, `data/nodes.csv` e `data/edges_top3.csv`.

### Arquivos em `data/`

| Arquivo | Conteúdo |
|---|---|
| `grafo_sus_mg.csv` | arestas direcionadas, 10.915 linhas (etapa 1). **É a entrada do programa em C++.** O script da etapa 1 grava o cabeçalho `origem,destino,internacoes`; neste repositório o cabeçalho é `Source,Target,Weight`. O programa em C++ ignora a primeira linha, então os dois funcionam. |
| `resumo_municipios.csv` | por município de residência: `total` (internações de moradores, inclusive as feitas no próprio município), `fora` e `pct_fora` (etapa 1). É lido pela etapa 2. |
| `edges.csv` | as mesmas arestas, com a coluna extra `Type` (sempre `Directed`). Formato de arestas compatível com importação no Gephi (etapa 2). |
| `edges_top3.csv` | para cada município de origem, as 3 arestas de maior peso (2.553 linhas, pois alguns municípios têm menos de 3 destinos). Em caso de empate de peso, a escolha entre as arestas empatadas pode variar (etapa 2). |
| `nodes.csv` | uma linha por município (853): `Id`, `Label` (nome), `recebidos`, `enviados`, `total_res`, `pct_fora`, `saldo`, `tamanho_visual` (etapa 2 gera as 7 primeiras). |
| `municipios.json` | lista de municípios de MG retornada pela API do IBGE (id de 7 dígitos). É a cópia local usada por `traduzir_ibge.py`; o `exportar_gephi.py` baixa a lista da API quando roda. |

Colunas de `nodes.csv`:

- `recebidos`: soma dos pesos das arestas que chegam ao município (internações de moradores de outros municípios);
- `enviados`: soma dos pesos das arestas que saem do município (internações de seus moradores em outros municípios);
- `total_res`: todas as internações de moradores do município, inclusive as feitas no próprio município;
- `pct_fora`: `enviados / total_res * 100`;
- `saldo`: `recebidos - enviados`;
- `tamanho_visual`: valor usado para dimensionar o vértice na visualização (não é gerado pelo `exportar_gephi.py`).

## 3. Modelagem do grafo

- **Vértice:** um município, identificado pelo código IBGE de 6 dígitos (como no DATASUS). São 853 vértices, todos os municípios de MG.
- **Aresta `u -> v`:** existe quando moradores de `u` foram internados em hospitais de `v`.
- **Peso:** número de internações de moradores de `u` em hospitais de `v` em 2025.
- **Tipo:** grafo direcionado e ponderado, sem laços. São 10.915 arestas.
- **Grau de entrada ponderado** de `v`: total de internações que `v` recebe de outros municípios (`pacientes_recebidos` no código).
- **Grau de saída ponderado** de `u`: total de internações de moradores de `u` feitas fora (`pacientes_enviados` no código).
- **Grafo invertido:** a BFS percorre as arestas no sentido contrário. Partindo de um polo, ela encontra os municípios que mandam internações para ele (nível 1) e os que mandam para esses (nível 2 em diante).

## 4. Estruturas de dados e algoritmos

| Estrutura | Onde | Para que serve |
|---|---|---|
| `unordered_map<string, vector<Aresta>> adj` | `GrafoSaude` | lista de adjacência do grafo (sentido origem -> destino) |
| `unordered_map<string, vector<Aresta>> adj_reversa` | `GrafoSaude` | lista de adjacência do grafo invertido (destino -> origem), usada pela BFS |
| `unordered_map<string, int> pacientes_recebidos` e `pacientes_enviados` | `GrafoSaude` | graus de entrada e de saída ponderados |
| `queue<string>` | BFS | fila da busca em largura |
| `unordered_map<string, int> nivel` | BFS | marca os municípios já visitados e guarda a distância (em saltos) até o polo |

| Operação | Custo |
|---|---|
| Construção do grafo (leitura do CSV e inserção das arestas) | O(E), em média, por usar tabelas hash |
| Rankings de polos e de maior saída | O(V log V), pela ordenação dos graus |
| BFS na rede invertida | O(V + E) |

## 5. Arquitetura do código

```
.
├── Makefile                   compilar, executar e limpar
├── data/                      dados já tratados (seção 2)
├── scripts/
│   ├── gerar_grafo_saude.py   etapa 1: arquivos .dbc do DATASUS -> grafo e resumo
│   ├── exportar_gephi.py      etapa 2: nós e arestas em formato para visualização
│   └── traduzir_ibge.py       troca códigos IBGE por nomes na saída do programa
├── src/
│   ├── GrafoSaude.hpp         struct Aresta e declaração da classe GrafoSaude
│   ├── GrafoSaude.cpp         construção do grafo, rankings e BFS
│   └── analise_sus.cpp        main: lê o CSV, mede o tempo e chama as análises
└── results/
    └── relatorio_bfs.txt      saída do programa, já com os nomes dos municípios
```

Fluxo de execução:

```
RDMG25xx.dbc (DATASUS)
      |  scripts/gerar_grafo_saude.py
      v
data/grafo_sus_mg.csv + data/resumo_municipios.csv
      |                               |
      |                               |  scripts/exportar_gephi.py
      |                               v
      |                    data/nodes.csv, edges.csv, edges_top3.csv
      |
      |  src/analise_sus.cpp + src/GrafoSaude.cpp
      v
saída com códigos IBGE
      |  scripts/traduzir_ibge.py  (usa data/municipios.json)
      v
results/relatorio_bfs.txt
```

Componentes principais:

- **`GrafoSaude::adicionarAresta`**: insere a aresta nas duas listas de adjacência e acumula os graus de entrada e de saída.
- **`GrafoSaude::analisarInjustica`**: ordena os graus e imprime os 10 maiores de cada lista. O nome do método é um nome simplificado; ele só gera rankings (seção 8).
- **`GrafoSaude::bfsBaciaAtendimento`**: BFS na rede invertida a partir do polo informado. Conta os municípios que mandam internações direto para o polo (nível 1) e os que chegam só de forma indireta (nível 2 em diante).
- **`analise_sus.cpp`**: abre `data/grafo_sus_mg.csv`, constrói o grafo, mede o tempo de construção e roda a análise com Belo Horizonte (código `310620`) como polo.
- **`traduzir_ibge.py`**: lê a saída do programa pela entrada padrão e troca os códigos de 6 dígitos que começam com `31` pelo nome do município.
- **`gerar_grafo_saude.py`**: lê os 12 arquivos `.dbc`, aplica os filtros da seção 2 e grava `grafo_sus_mg.csv` e `resumo_municipios.csv`.
- **`exportar_gephi.py`**: monta `nodes.csv` (com graus ponderados e `pct_fora`), `edges.csv` e `edges_top3.csv` a partir das saídas da etapa 1.

## 6. Como compilar e executar

Requisitos (Ubuntu 24.04): `g++`, `make` e `python3`. O programa em C++ e o script de tradução usam só a biblioteca padrão, sem pacotes externos.

```bash
sudo apt update && sudo apt install -y g++ make python3 git
git clone https://github.com/anthonygabriel2907/analise-topologica-sus-mg.git
cd analise-topologica-sus-mg
make run
```

Rode sempre a partir da raiz do projeto, porque o programa abre `data/grafo_sus_mg.csv` por caminho relativo.

| Comando | O que faz |
|---|---|
| `make` | compila o executável `analise_sus` |
| `make run` | compila, executa, traduz os códigos e grava `results/relatorio_bfs.txt` |
| `make clean` | apaga o executável |

## 7. Resultados

Os números abaixo vêm de `data/grafo_sus_mg.csv`, `data/nodes.csv` e `results/relatorio_bfs.txt`.

### Panorama

| Medida | Valor |
|---|---|
| Municípios (vértices) | 853 |
| Arestas | 10.915 |
| Internações de moradores de MG | 1.589.022 |
| Internações feitas fora do município de residência | 581.742 (36,6%) |
| Municípios que receberam internações de fora | 332 |
| Municípios com 100% das internações dos moradores feitas fora | 485 (56,9%) |
| Municípios com 50% ou mais das internações feitas fora | 634 (74,3%) |
| Mediana de `pct_fora` | 100% |

### Municípios que mais recebem internações de fora (grau de entrada ponderado)

| # | Município | Internações recebidas |
|---|---|---|
| 1 | Belo Horizonte | 129.563 |
| 2 | Montes Claros | 24.774 |
| 3 | Juiz de Fora | 15.651 |
| 4 | Muriaé | 13.758 |
| 5 | Ipatinga | 13.722 |
| 6 | Pouso Alegre | 11.944 |
| 7 | Uberaba | 10.723 |
| 8 | Teófilo Otoni | 10.458 |
| 9 | Divinópolis | 10.159 |
| 10 | Alfenas | 9.416 |

### Municípios de onde mais moradores se internam fora (grau de saída ponderado)

| # | Município | Internações de moradores feitas fora |
|---|---|---|
| 1 | Ribeirão das Neves | 15.423 |
| 2 | Contagem | 14.753 |
| 3 | Santa Luzia | 11.354 |
| 4 | Vespasiano | 8.530 |
| 5 | Ibirité | 7.288 |
| 6 | Betim | 7.073 |
| 7 | Sabará | 6.303 |
| 8 | Divinópolis | 4.159 |
| 9 | Esmeraldas | 4.074 |
| 10 | Belo Horizonte | 3.074 |

### BFS na rede invertida a partir de Belo Horizonte

- Municípios que mandam internações direto para Belo Horizonte: **785**.
- Municípios que chegam a Belo Horizonte só de forma indireta: **67**.
- Juntos, os 852 são todos os outros municípios do estado.
- Belo Horizonte recebe 129.563 internações de fora, cerca de 22% de todas as internações feitas fora do município de residência (581.742).

## 8. Limitações e leitura dos resultados

- **Só internações do SUS.** O arquivo RD é do SIH/SUS e não inclui atendimento particular nem ambulatorial.
- **Internação não é pessoa.** Cada registro é uma internação; a mesma pessoa pode aparecer mais de uma vez. O programa imprime "pacientes" por simplicidade, mas a unidade é a internação.
- **Valores absolutos acompanham o tamanho do município.** Oito dos dez municípios de maior saída (Ribeirão das Neves, Contagem, Santa Luzia, Vespasiano, Ibirité, Betim, Sabará e Esmeraldas) são vizinhos de Belo Horizonte na região metropolitana, e a própria capital aparece na lista pelo volume. Para comparar municípios de tamanhos diferentes, o `pct_fora` do `nodes.csv` é mais adequado. A normalização por população **não foi feita**.
- **O dado não explica o motivo.** Ele mostra onde o morador mora e onde o hospital fica, mas não diz se a internação fora do município foi por falta de serviço, por encaminhamento previsto na organização regional do SUS ou por escolha do paciente. Por isso o trabalho descreve fluxos e não conclui que há falha de atendimento.
- **Nomes simplificados no código.** No código e na saída do programa aparecem termos como "pacientes", "desertos" e "expulsou". Aqui usamos "internações" e "municípios de maior saída", que descrevem o que é medido.
- **Recorte.** Um estado (MG) e um ano (2025). Moradores de outros estados e registros com município ignorado foram removidos.

## 9. Reprodutibilidade e dataset

- **Código:** este repositório.
- **Dataset tratado (Zenodo):** `https://doi.org/10.5281/zenodo.24203942`
- **Fontes originais:** arquivos `RDMG2501.dbc` a `RDMG2512.dbc` do DATASUS e a API de localidades do IBGE (`https://servicodados.ibge.gov.br/api/v1/localidades/estados/MG/municipios`).

Para refazer o tratamento a partir dos arquivos originais:

```bash
pip install pandas dbfread pyreaddbc requests
# coloque os 12 arquivos RDMG25xx.dbc em data/ (ou em data/datasus_mg/)
python3 scripts/gerar_grafo_saude.py
python3 scripts/exportar_gephi.py   # precisa de internet (nomes dos municípios, API do IBGE)
make run
```

Rode todos os comandos a partir da raiz do projeto, porque os scripts usam caminhos relativos a `data/`.

## 10. Autoria

- Autores: `Anthony Gabriel Sotto Mayor Silva, Henrique Parreira Cavalcante de Souza`
- Instituição e curso: `UFCI - MG | Engenharia da Computação`
- Disciplina: Algoritmos e Estruturas de Dados II
