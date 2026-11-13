#include "GrafoSaude.hpp"
#include <iostream>
#include <fstream>
#include <sstream>
#include <chrono>

using namespace std;
using namespace std::chrono;

int main() {
    GrafoSaude grafo;
    
    // Abre Dataset CSV bruto do DATASUS
    ifstream arquivo("data/grafo_sus_mg.csv");
    if (!arquivo.is_open()) {
        cerr << "[ERRO Critico] Nao foi possivel abrir o arquivo CSV em data/grafo_sus_mg.csv!" << endl;
        return 1;
    }

    string linha, origem, destino, peso_str;
    getline(arquivo, linha); // Descarta a linha de cabeçalho do CSV

    // medição de performance computacional
    auto inicio_tempo = high_resolution_clock::now();

    // Leitura linha a linha e construção dinâmica do grafo em memória
    while (getline(arquivo, linha)) {
        stringstream ss(linha);
        getline(ss, origem, ',');
        getline(ss, destino, ',');
        getline(ss, peso_str, ',');
        
        if (!origem.empty() && !destino.empty() && !peso_str.empty()) {
            grafo.adicionarAresta(origem, destino, stoi(peso_str));
        }
    }

    // Fim da medição de performance
    auto fim_tempo = high_resolution_clock::now();
    auto duracao_ms = duration_cast<milliseconds>(fim_tempo - inicio_tempo).count();

    cout << "Grafo estruturado na memoria em " << duracao_ms << " ms!" << endl;

    // Executa a análise estatística dos Top N Polos e Desertos de Saúde
    grafo.analisarInjustica(10);
    
    // Executa a BFS exigida pela especificação acadêmica (Polo Referência: Belo Horizonte - IBGE 310620)
    grafo.bfsBaciaAtendimento("310620"); 

    return 0;
}