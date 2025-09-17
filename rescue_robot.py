##########################################
# IMPORTAÇÕES
##########################################

import os
import time
import platform
import csv

###########################################
# CONSTANTES GLOBAIS
###########################################

DIRS = [(-1,0),(0,1),(1,0),(0,-1)]  # N, L, S, O
SIM_DELAY = 0.1  # tempo entre passos (ajuste se quiser mais lento/rápido)


##########################################
# CLASSE QUE REPRESENTA O LABIRINTO
##########################################
class Labirinto:
    def __init__(self, mapa_str):
        self.mapa = [list(l) for l in mapa_str.strip().splitlines()]
        self.linhas = len(self.mapa)
        self.colunas = len(self.mapa[0])
        self.entrada = self._find_char('E')
        self.humano = self._find_char('@')

    def _find_char(self, c):
        for i,row in enumerate(self.mapa):
            for j,val in enumerate(row):
                if val==c: return (i,j)
        return None

    def get_celula(self,pos):
        x,y = pos
        if 0<=x<self.linhas and 0<=y<self.colunas:
            return self.mapa[x][y]
        return 'X'  # fora do mapa = parede

    def set_celula(self,pos,val):
        x,y = pos
        self.mapa[x][y] = val

    def print(self, robo_pos, humano_presente=True):
        sistema = platform.system()
        if sistema == 'Windows':
            os.system('cls')
        else:
            os.system('clear')

        for i, row in enumerate(self.mapa):
            linha = ""
            for j, c in enumerate(row):
                if (i, j) == robo_pos:
                    linha += "R"
                elif c == '@' and humano_presente:
                    linha += '@'
                else:
                    linha += c
            print(linha)
        time.sleep(SIM_DELAY)




##########################################
# CLASSE QUE REPRESENTA O ROBÔ
##########################################
class Robo:
    def __init__(self, labirinto: Labirinto, log_file):
        self.lab = labirinto
        self.pos = labirinto.entrada
        self.humano_coletado = False
        self.caminho_ate_humano = []
        self.log = []
        self.log_file = log_file
        self.log_comando("LIGAR")

    def sensores(self):
        resultados=[]
        for d in [-1,0,1]:  # esquerda, frente, direita
            nd = (0+d)%4  # não usamos direção real aqui
            dx,dy = DIRS[d+1] if d!=-1 else DIRS[-1]
            nx,ny = self.pos[0]+dx, self.pos[1]+dy
            cel = self.lab.get_celula((nx,ny))
            if cel=='X':
                resultados.append("PAREDE")
            elif cel=='@':
                resultados.append("HUMANO")
            else:
                resultados.append("VAZIO")
        return resultados

    def log_comando(self, cmd):
        sensores = self.sensores()
        carga = "COM HUMANO" if self.humano_coletado else "SEM CARGA"
        self.log.append([cmd]+sensores+[carga])

    def explorar_ate_humano(self):
        stack = [(self.pos,[self.pos])]
        visited = set([self.pos])
        while stack:
            current, path = stack.pop()
            if self.lab.get_celula(current)=='@':
                self.caminho_ate_humano = path
                return
            for dx,dy in DIRS:
                nx,ny = current[0]+dx, current[1]+dy
                if 0<=nx<self.lab.linhas and 0<=ny<self.lab.colunas:
                    if self.lab.get_celula((nx,ny)) in ['.','@'] and (nx,ny) not in visited:
                        visited.add((nx,ny))
                        stack.append(((nx,ny), path + [(nx,ny)]))

    def andar_ate_humano(self):
        for pos in self.caminho_ate_humano[1:]:
            self.pos = pos
            self.lab.print(self.pos, humano_presente=True)
            self.log_comando("A")
        self.pegar_humano()

    def pegar_humano(self):
        if self.lab.get_celula(self.pos)=='@':
            self.humano_coletado = True
            self.lab.set_celula(self.pos,'.')
            self.log_comando("P")
            self.lab.print(self.pos, humano_presente=False)

    def retornar(self):
        caminho_volta = list(reversed(self.caminho_ate_humano[:-1]))
        for pos in caminho_volta:
            self.pos = pos
            self.lab.print(self.pos, humano_presente=False)
            self.log_comando("A")
        self.ejetar()

    def ejetar(self):
        if self.pos == self.lab.entrada and self.humano_coletado:
            self.humano_coletado = False
            self.log_comando("E")

    def salvar_log(self):
        with open(self.log_file,"w",newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Comando","Sensor Esq","Sensor Frente","Sensor Dir","Carga"])
            writer.writerows(self.log)



##########################################
# CLASSE DA SIMULAÇÃO
##########################################
class Simulacao:
    def __init__(self, mapa_str, nome_arquivo):
        self.lab = Labirinto(mapa_str)
        log_file = nome_arquivo.replace(".txt",".csv")
        self.robo = Robo(self.lab, log_file)

    def executar(self):
        self.robo.explorar_ate_humano()
        self.robo.andar_ate_humano()
        self.robo.retornar()
        self.robo.salvar_log()

###########################################
## EXECUÇÃO PRINCIPAL
###########################################

def carregar_mapa(caminho_arquivo):
    with open(caminho_arquivo, "r") as f:
        return f.read()


if __name__ == "__main__":
    arquivos = ["lab1.txt","lab2.txt","lab3.txt"]  # coloque seus labirintos aqui
    for arq in arquivos:
        if os.path.exists(arq):
            mapa = carregar_mapa(arq)
            sim = Simulacao(mapa, arq)
            sim.executar()
            print(f"Teste {arq} concluído. Log salvo em {arq.replace('.txt','.csv')}")
