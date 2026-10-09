import psutil
import csv
import time
import argparse
import os
from datetime import datetime
from abc import ABC, abstractmethod

# 1. e 2. Classe Base (Superclasse) definindo a estrutura e atributos
class Metrica(ABC):
    def __init__(self, nome, unidade):
        self.nome = nome
        self.unidade = unidade
        self.valor = 0.0

    @abstractmethod
    def coletar(self):
        """Método que será sobrescrito (polimorfismo) pelas classes filhas"""
        pass

# 3. Subclasses (Herança)
# 4. CPU Métrica
class CpuMetrica(Metrica):
    def __init__(self):
        super().__init__("CPU", "%")

    def coletar(self):
        # interval=0.5 garante que ele fará uma leitura mais rápida
        self.valor = psutil.cpu_percent(interval=0.5)

# 5. Memória Métrica
class MemoriaMetrica(Metrica):
    def __init__(self):
        super().__init__("Memoria", "MB")

    def coletar(self):
        memoria = psutil.virtual_memory()
        # Convertendo bytes para Megabytes (MB)
        self.valor = round(memoria.used / (1024 * 1024), 2)

# 6. Disco Métrica
class DiscoMetrica(Metrica):
    def __init__(self):
        super().__init__("Disco", "MB")

    def coletar(self):
        disco = psutil.disk_usage('/')
        # Convertendo bytes para Megabytes (MB)
        self.valor = round(disco.free / (1024 * 1024), 2)

# 7. Função para salvar no CSV
def salvar_csv(arquivo_saida, metricas):
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Verifica se o arquivo já existe para adicionar ou não o cabeçalho
    arquivo_existe = os.path.isfile(arquivo_saida)
    
    with open(arquivo_saida, mode="a", newline="") as arquivo:
        escritor = csv.writer(arquivo)
        
        if not arquivo_existe:
            escritor.writerow(["datetime", "metrica", "valor", "unidade"])
            
        for metrica in metricas:
            # 8, 9, 10 e 11. Gravando no formato solicitado
            escritor.writerow([agora, metrica.nome, metrica.valor, metrica.unidade])

def main():
    # Desafio Extra (b): Aceitar parâmetros via terminal
    parser = argparse.ArgumentParser(description="Coletor de Métricas de Sistema - DevOps")
    parser.add_argument("-i", "--intervalo", type=int, default=5, help="Intervalo de tempo entre coletas (segundos)")
    parser.add_argument("-n", "--iteracoes", type=int, default=10, help="Número de vezes que as métricas serão coletadas")
    parser.add_argument("-s", "--saida", type=str, default="metricas.csv", help="Nome do arquivo CSV de saída")
    parser.add_argument("-m", "--metricas", nargs="+", choices=['cpu', 'memoria', 'disco', 'todas'], 
                        default=['todas'], help="Escolha quais métricas coletar (ex: cpu memoria)")
    
    args = parser.parse_args()

    # Dicionário mapeando os nomes para as classes (Fábrica de Objetos)
    opcoes_metricas = {
        'cpu': CpuMetrica,
        'memoria': MemoriaMetrica,
        'disco': DiscoMetrica
    }

    # Instanciando apenas as métricas solicitadas pelo usuário
    metricas_ativas = []
    if 'todas' in args.metricas:
        metricas_ativas = [CpuMetrica(), MemoriaMetrica(), DiscoMetrica()]
    else:
        for m in set(args.metricas):
            metricas_ativas.append(opcoes_metricas[m]())

    print(f"Iniciando coleta... Salvando em: '{args.saida}'")
    print(f"Configuração: {args.iteracoes} iterações a cada {args.intervalo} segundos.\n")

    # Desafio Extra (a): Loop periódico
    for i in range(1, args.iteracoes + 1):
        print(f"--- Iteração {i}/{args.iteracoes} ---")
        
        # POLIMORFISMO: O loop não precisa saber qual métrica é, 
        # basta chamar .coletar() e o objeto correto executa a sua versão do método.
        for metrica in metricas_ativas:
            metrica.coletar()
            print(f"{metrica.nome: <8} | {metrica.valor} {metrica.unidade}")
            
        salvar_csv(args.saida, metricas_ativas)
        print("Dados salvos.\n")

        # Pausa antes da próxima iteração (exceto na última)
        if i < args.iteracoes:
            time.sleep(args.intervalo)

    print("Coleta finalizada com sucesso!")

if __name__ == "__main__":
    main()