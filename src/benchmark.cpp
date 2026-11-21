// mede o tempo de construcao do grafo e da BFS quando o numero de arestas cresce.
#include "GrafoSaude.hpp"
#include <iostream>
#include <fstream>
#include <sstream>
#include <chrono>
#include <algorithm>
#include <random>
#include <cmath>
using namespace std;
using namespace std::chrono;

struct Reg { string o, d; int p; };

// mede construcao e BFS (mediana de varias rodadas); a saida da BFS e descartada
void medir(const vector<Reg>& regs, const string& origem_bfs, int rodadas, const string& nome) {
    vector<double> t_cons, t_bfs;
    for (int r = 0; r < rodadas; r++) {
        GrafoSaude g;
        auto a = high_resolution_clock::now();
        for (const Reg& x : regs) g.adicionarAresta(x.o, x.d, x.p);
        auto b = high_resolution_clock::now();

        streambuf* velho = cout.rdbuf();
        ostringstream lixo;
        cout.rdbuf(lixo.rdbuf());
        auto c = high_resolution_clock::now();
        g.bfsBaciaAtendimento(origem_bfs);
        auto d = high_resolution_clock::now();
        cout.rdbuf(velho);

        t_cons.push_back(duration<double, milli>(b - a).count());
        t_bfs.push_back(duration<double, milli>(d - c).count());
    }
    sort(t_cons.begin(), t_cons.end());
    sort(t_bfs.begin(), t_bfs.end());
    cout << nome << ";" << regs.size() << ";" << t_cons[rodadas / 2] << ";" << t_bfs[rodadas / 2] << "\n";
}

int main() {
    ifstream arq("data/grafo_sus_mg.csv");
    if (!arq.is_open()) { cerr << "rode a partir da raiz do projeto\n"; return 1; }
    vector<Reg> reais;
    string l;
    getline(arq, l); // cabecalho
    while (getline(arq, l)) {
        stringstream ss(l);
        string o, d, p;
        getline(ss, o, ','); getline(ss, d, ','); getline(ss, p, ',');
        reais.push_back({o, d, stoi(p)});
    }
    mt19937 gen(42);
    shuffle(reais.begin(), reais.end(), gen);

    cout << "tipo;E;construcao_ms;bfs_ms\n";
    double fracoes[] = {0.25, 0.5, 0.75, 1.0};
    for (double f : fracoes) {
        vector<Reg> parte(reais.begin(), reais.begin() + (int)(reais.size() * f));
        medir(parte, "310620", 50, "real");
    }

    // sinteticos: V = 853*k, E = 10915*k; destinos concentrados em poucos vertices (parecido com polos)
    int ks[] = {1, 2, 5, 10, 25, 50, 100};
    for (int k : ks) {
        int V = 853 * k, E = 10915 * k;
        mt19937 g2(7);
        uniform_int_distribution<int> um(0, V - 1);
        uniform_real_distribution<double> ur(0.0, 1.0);
        vector<Reg> regs;
        regs.reserve(E);
        for (int i = 0; i < E; i++) {
            int o = um(g2);
            int d = (int)(V * pow(ur(g2), 3.0));
            if (d >= V) d = V - 1;
            if (o == d) o = (o + 1) % V;
            regs.push_back({to_string(100000 + o), to_string(100000 + d), 1 + (int)(ur(g2) * 50)});
        }
        medir(regs, "100000", k >= 50 ? 5 : 15, "sintetico");
    }
}
