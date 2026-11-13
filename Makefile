# Compilador e flags de otimizacao
CXX = g++
CXXFLAGS = -O3 -Wall

# Nomes dos arquivos e pastas
SRC_DIR = src
SCRIPT_DIR = scripts
TARGET = analise_sus
SRCS = $(SRC_DIR)/analise_sus.cpp $(SRC_DIR)/GrafoSaude.cpp
SCRIPT = $(SCRIPT_DIR)/traduzir_ibge.py

# Regra padrao: compila o executavel
all: $(TARGET)

$(TARGET): $(SRCS)
	$(CXX) $(CXXFLAGS) $(SRCS) -o $(TARGET)

# Regra para rodar o programa e salvar o relatorio automaticamente
run: $(TARGET)
	mkdir -p results
	./$(TARGET) | python3 $(SCRIPT) | tee results/relatorio_bfs.txt

# Regra para rodar apenas o binario bruto (sem traducao)
run-bruto: $(TARGET)
	./$(TARGET)

# Regra para limpar os binarios gerados
clean:
	rm -f $(TARGET)