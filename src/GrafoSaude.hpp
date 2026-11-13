#ifndef GRAFO_SAUDE_HPP
#define GRAFO_SAUDE_HPP

#include <string>
#include <vector>
#include <unordered_map>

/**
 * @brief Estrutura que representa uma aresta ponderada no grafo de saúde.
 */
struct Aresta {
    std::string destino; // Código IBGE do município de destino
    int peso;            // Volume de internações/transferências
};

/**
 * @brief Classe principal para modelagem e análise topológica da malha do SUS.
 */
class GrafoSaude {
public:
    // Listas de adjacência para o grafo original e reverso
    std::unordered_map<std::string, std::vector<Aresta>> adj;
    std::unordered_map<std::string, std::vector<Aresta>> adj_reversa; // Destino -> Origem (para BFS reversa)

    // Estruturas para contabilização de graus
    std::unordered_map<std::string, int> pacientes_recebidos; // Grau de Entrada (Polos)
    std::unordered_map<std::string, int> pacientes_enviados;  // Grau de Saída (Desertos)

    /**
     * @brief Adiciona uma aresta direcionada e atualiza os contadores de fluxo.
     */
    void adicionarAresta(std::string origem, std::string destino, int peso);

    /**
     * @brief Processa e exibe os rankings de polos de saúde e desertos (ambulancioterapia).
     */
    void analisarInjustica(int top_n);

    /**
     * @brief Executa BFS na rede reversa para mapear a area de atendimento.
     * @param polo_ibge Código IBGE da cidade polo 
     */
    void bfsBaciaAtendimento(std::string polo_ibge);
};

#endif