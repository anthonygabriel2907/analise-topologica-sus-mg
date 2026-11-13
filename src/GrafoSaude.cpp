#include "GrafoSaude.hpp"
#include <iostream>
#include <algorithm>
#include <queue>

using namespace std;

// Adiciona aresta e computa o peso acumulado de entrada e saída por município
void GrafoSaude::adicionarAresta(string origem, string destino, int peso) {
    adj[origem].push_back({destino, peso});
    adj_reversa[destino].push_back({origem, peso}); // Essencial para rastrear quem alimenta o polo
    
    pacientes_recebidos[destino] += peso; // Acumula sobrecarga no destino
    pacientes_enviados[origem] += peso;   // Acumula evasão na origem
}

// Ordena e exibe os maiores receptores (polos) e maiores emissores (desertos)
void GrafoSaude::analisarInjustica(int top_n) {
    // Converte mapas para vetores permitindo ordenação por lambda
    vector<pair<string, int>> polos(pacientes_recebidos.begin(), pacientes_recebidos.end());
    vector<pair<string, int>> desertos(pacientes_enviados.begin(), pacientes_enviados.end());

    // Ordenação decrescente, maior volume de pacientes primeiro
    sort(polos.begin(), polos.end(), [](auto& a, auto& b) { return a.second > b.second; });
    sort(desertos.begin(), desertos.end(), [](auto& a, auto& b) { return a.second > b.second; });

    cout << "\n=== TOP " << top_n << " POLOS DE SAUDE ===" << endl;
    cout << "Cidades que mais recebem pacientes de fora:" << endl;
    for (int i = 0; i < min(top_n, (int)polos.size()); i++) {
        cout << i + 1 << ". " << polos[i].first << ": Recebeu " << polos[i].second << " pacientes" << endl;
    }

    cout << "\n=== TOP " << top_n << " DESERTOS DE SAUDE (Ambulancioterapia) ===" << endl;
    cout << "Cidades que mais expulsam seus moradores para se tratar fora:" << endl;
    for (int i = 0; i < min(top_n, (int)desertos.size()); i++) {
        cout << i + 1 << ". " << desertos[i].first << ": Expulsou " << desertos[i].second << " pacientes" << endl;
    }
}

// Algoritmo BFS em O(V + E) sobre a rede invertida para calcular o alcance da bacia de saúde
void GrafoSaude::bfsBaciaAtendimento(string polo_ibge) {
    unordered_map<string, int> nivel; // Controla nós visitados e distância em saltos 
    queue<string> fila;

    // Inicialização da Fila com o polo central
    fila.push(polo_ibge);
    nivel[polo_ibge] = 0;

    int diretos = 0;
    int indiretos = 0;

    while (!fila.empty()) {
        string atual = fila.front();
        fila.pop();

        // Explora os municípios que enviam pacientes diretamente para o nó atual via grafo reverso
        for (auto& vizinho : adj_reversa[atual]) {
            // Se o município ainda não foi visitado na travessia
            if (nivel.find(vizinho.destino) == nivel.end()) {
                nivel[vizinho.destino] = nivel[atual] + 1;
                fila.push(vizinho.destino);

                // Classificação topológica do alcance
                if (nivel[vizinho.destino] == 1) {
                    diretos++;   // Conecta diretamente ao polo
                } else {
                    indiretos++; // Dependência indireta
                }
            }
        }
    }

    cout << "\n=== BUSCA EM LARGURA O(V+E) ===" << endl;
    cout << "Polo " << polo_ibge << ":" << endl;
    cout << "Municipios que mandam pacientes direto para o polo: " << diretos << endl;
    cout << "Internacoes recebidas direto: " << pacientes_recebidos[polo_ibge] << endl;
    cout << "Municipios alcancados so de forma indireta (pela rede): " << indiretos << endl;
}