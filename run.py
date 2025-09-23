import os
from simulacao import Simulacao
from config import LABIRINTOS

def carregar_mapa(caminho_arquivo):
    with open(caminho_arquivo, "r") as f:
        return f.read()

if __name__ == "__main__":
    
    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)

    labirintos_dir = "labirintos"
    os.makedirs(labirintos_dir, exist_ok=True)

    arquivos = [os.path.join(labirintos_dir, nome) for nome in LABIRINTOS]  # nomes vêm de config.labirintos
    for arq in arquivos:
        if os.path.exists(arq):
            mapa = carregar_mapa(arq)
            sim = Simulacao(mapa, arq)
            sim.executar()

            src_log = arq.replace(".txt", ".csv")
            dest_log = os.path.join(logs_dir, os.path.basename(src_log))

            if os.path.exists(src_log):
                os.replace(src_log, dest_log)  # move/replace de forma atômica
                print(f"Teste {arq} concluído. Log salvo em {dest_log}")
            else:
                print(f"Teste {arq} concluído. Log não encontrado em {src_log}")