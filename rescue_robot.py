import os
import time
import platform
import csv

DIRS = [(-1,0),(0,1),(1,0),(0,-1)]  # N, L, S, O
SIM_DELAY = 0.1  # tempo entre passos

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


class Robo:
    def __init__(self, labirinto: Labirinto, log_file):
        self.lab = labirinto
        self.pos = labirinto.entrada
        self.humano_coletado = False
        self.orientacao = 0  # 0=N, 1=L, 2=S, 3=O
        self.caminho_ate_humano = []
        self.log = []
        self.log_file = log_file
        self.log_comando("LIGAR")

    def sensores(self):
        # calcula as direções relativas
        frente_dir = DIRS[self.orientacao]
        esquerda_dir = DIRS[(self.orientacao - 1) % 4]
        direita_dir = DIRS[(self.orientacao + 1) % 4]

        sensores = []
        for dx, dy in [frente_dir, esquerda_dir, direita_dir]:
            nx, ny = self.pos[0] + dx, self.pos[1] + dy
            cel = self.lab.get_celula((nx, ny))
            if cel == 'X':
                sensores.append("PAREDE")
            elif cel == '@':
                sensores.append("HUMANO")
            else:
                sensores.append("VAZIO")
        return sensores

    def log_comando(self, cmd):
        sensores = self.sensores()
        carga = "COM HUMANO" if self.humano_coletado else "SEM CARGA"
        self.log.append([cmd]+sensores+[carga])

    def explorar(self):
        visitados = set()
        caminho = []
        orientacao = 0  # começa virado para "Norte" (DIRS[0])

        def mover_para(nova_pos, nova_orientacao):
            # calcular diferença de orientação
            giros = (nova_orientacao - self.orientacao) % 4
            for _ in range(giros):
                self.log_comando("G")  # cada giro registrado
            self.orientacao = nova_orientacao

            # andar
            self.pos = nova_pos
            self.lab.print(self.pos, humano_presente=not self.humano_coletado)
            self.log_comando("A")

        def dfs(pos):
            if pos in visitados:
                return False
            visitados.add(pos)

            if self.lab.get_celula(pos) == '@':
                self.pegar_humano()
                return True

            for nd, (dx, dy) in enumerate(DIRS):
                nx, ny = pos[0] + dx, pos[1] + dy
                if self.lab.get_celula((nx, ny)) in ['.', '@'] and (nx, ny) not in visitados:
                    caminho.append((nx, ny))
                    mover_para((nx, ny), nd)
                    if dfs((nx, ny)):
                        return True
                    # --- BACKTRACK REAL ---
                    mover_para(pos, (nd + 2) % 4)  # virar para trás e andar
                    caminho.pop()

            return False

        dfs(self.pos)
        self.caminho_ate_humano = [self.lab.entrada] + caminho



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
            writer.writerow(["Comando","Frente","Esquerda","Direita","Carga"])
            writer.writerows(self.log)


class Simulacao:
    def __init__(self, mapa_str, nome_arquivo):
        self.lab = Labirinto(mapa_str)
        log_file = nome_arquivo.replace(".txt",".csv")
        self.robo = Robo(self.lab, log_file)

    def executar(self):
        self.robo.explorar()
        self.robo.retornar()
        self.robo.salvar_log()


# -------- MAIN --------
def carregar_mapa(caminho_arquivo):
    with open(caminho_arquivo, "r") as f:
        return f.read()

if __name__ == "__main__":
    arquivos = ["lab4.txt"]  # coloque seus labirintos aqui
    for arq in arquivos:
        if os.path.exists(arq):
            mapa = carregar_mapa(arq)
            sim = Simulacao(mapa, arq)
            sim.executar()
            print(f"Teste {arq} concluído. Log salvo em {arq.replace('.txt','.csv')}")