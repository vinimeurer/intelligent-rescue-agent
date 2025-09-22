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
        frente_dir = DIRS[self.orientacao]
        esquerda_dir = DIRS[(self.orientacao - 1) % 4]
        direita_dir = DIRS[(self.orientacao + 1) % 4]

        sensores = []
        for i, (dx, dy) in enumerate([frente_dir, esquerda_dir, direita_dir]):
            nx, ny = self.pos[0] + dx, self.pos[1] + dy
            cel = self.lab.get_celula((nx, ny))

            if cel == 'X':
                sensores.append("PAREDE")
            elif cel == '@' and i == 0:
                # só mostrar HUMANO se estiver exatamente à frente
                sensores.append("HUMANO")
            else:
                sensores.append("VAZIO")
        return sensores

    def log_comando(self, cmd):
        sensores = self.sensores()
        carga = "COM HUMANO" if self.humano_coletado else "SEM CARGA"
        self.log.append([cmd]+sensores+[carga])

    def mover_para(self, nova_pos, nova_orientacao):
        # --- Alarme 1: colisão com parede ---
        if self.lab.get_celula(nova_pos) == 'X':
            raise Exception("⚠️ ALARME: Tentativa de colisão com parede!")

        # --- Alarme 2: atropelamento de humano ---
        if self.lab.get_celula(nova_pos) == '@' and self.humano_coletado:
            raise Exception("⚠️ ALARME: Tentativa de atropelamento de humano!")

        # Giro de orientação (registra G para cada giro à direita)
        giros = (nova_orientacao - self.orientacao) % 4
        for _ in range(giros):
            # atualizar orientacao antes de logar para que sensores reflitam o novo rumo
            self.orientacao = (self.orientacao + 1) % 4
            self.log_comando("G")

        # Movimento
        self.pos = nova_pos
        self.lab.print(self.pos, humano_presente=not self.humano_coletado)
        self.log_comando("A")

    def explorar(self):
        visitados = set()
        caminho = []

        def dfs(pos):
            if pos in visitados:
                return False
            visitados.add(pos)

            # se estiver sobre o humano, pegar (caso raro)
            if self.lab.get_celula(pos) == '@':
                self.pegar_humano()
                return True

            for nd, (dx, dy) in enumerate(DIRS):
                nx, ny = pos[0] + dx, pos[1] + dy
                cel_vizinha = self.lab.get_celula((nx, ny))

                # Se houver humano na célula à frente: girar e pegar sem entrar
                if cel_vizinha == '@' and (nx, ny) not in visitados:
                    self._girar_para(nd)
                    self.pegar_humano_frente((nx, ny))
                    return True

                # mover normalmente por células livres ('.' ou 'E')
                if cel_vizinha in ['.', 'E'] and (nx, ny) not in visitados:
                    caminho.append((nx, ny))
                    self.mover_para((nx, ny), nd)
                    if dfs((nx, ny)):
                        return True
                    # backtrack: voltar para pos
                    self.mover_para(pos, (nd + 2) % 4)
                    caminho.pop()

            return False

        dfs(self.pos)
        self.caminho_ate_humano = [self.lab.entrada] + caminho

    def _girar_para(self, nova_orientacao):
        # girar passo a passo: atualizar orientacao primeiro e então logar "G"
        giros = (nova_orientacao - self.orientacao) % 4
        for _ in range(giros):
            self.orientacao = (self.orientacao + 1) % 4
            self.log_comando("G")

    def pegar_humano_frente(self, pos_humano):
        # pos_humano é a célula da frente que deve conter '@'
        if self.lab.get_celula(pos_humano) != '@':
            raise Exception("⚠️ ALARME: Tentativa de coleta frontal sem humano!")
        # marcar humano como coletado (não entra na célula)
        self.humano_coletado = True
        self.lab.set_celula(pos_humano, '.')
        # registrar P e atualizar visual (humano não é mais mostrado)
        self.log_comando("P")
        self.lab.print(self.pos, humano_presente=False)

    def pegar_humano(self):
        # caso o robô esteja sobre a célula do humano (entra na célula)
        if self.lab.get_celula(self.pos) != '@':
            return
        self.humano_coletado = True
        self.lab.set_celula(self.pos, '.')
        self.log_comando("P")
        self.lab.print(self.pos, humano_presente=False)

    def retornar(self):
        caminho_volta = list(reversed(self.caminho_ate_humano[:-1]))
        for prox in caminho_volta:
            # se o próximo passo é a entrada, parar antes de entrar
            if prox == self.lab.entrada:
                break
            dx = prox[0] - self.pos[0]
            dy = prox[1] - self.pos[1]
            nd = DIRS.index((dx, dy))
            self.mover_para(prox, nd)

        # agora o robô deve estar adjacente à entrada; girar para encará-la
        ex, ey = self.lab.entrada
        rx, ry = self.pos
        dx = ex - rx
        dy = ey - ry
        if (dx, dy) not in DIRS:
            # caso o caminho calculado tenha colocado o robô exatamente na entrada
            # ou em posição inválida para ejeção, sinalizar erro
            raise Exception("⚠️ ALARME: Não está em posição válida para ejeção (não adjacente à entrada)!")
        nd_entrada = DIRS.index((dx, dy))
        # girar sem mover para ficar de frente à entrada
        self._girar_para(nd_entrada)

        self.ejetar()

    def ejetar(self):
        if not self.humano_coletado:
            raise Exception("⚠️ ALARME: Tentativa de ejeção sem humano!")

        # verificar que o robô está de frente para a entrada (célula à frente é a entrada)
        frente = (self.pos[0] + DIRS[self.orientacao][0],
                  self.pos[1] + DIRS[self.orientacao][1])
        if frente != self.lab.entrada:
            raise Exception("⚠️ ALARME: Tentativa de ejeção somente é permitida quando o robô estiver de frente para a saída!")

        # colocar humano na célula da entrada antes de logar para que sensores mostrem HUMANO na frente
        self.lab.set_celula(self.lab.entrada, '@')
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
    arquivos = ["lab3.txt"]  # coloque seus labirintos aqui
    for arq in arquivos:
        if os.path.exists(arq):
            mapa = carregar_mapa(arq)
            sim = Simulacao(mapa, arq)
            sim.executar()
            print(f"Teste {arq} concluído. Log salvo em {arq.replace('.txt','.csv')}")