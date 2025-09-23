import csv
from labirinto import Labirinto
from config import DIRS

class Robo:
    """
    Classe que representa o robô de resgate.

    Atributos:
        - lab: Instância de Labirinto representando o ambiente.
        - pos: Tupla (x, y) representando a posição atual do robô.
        - humano_coletado: Booleano indicando se o robô está carregando um humano.
        - orientacao: Inteiro representando a direção atual (0=N, 1=L, 2=S, 3=O).
        - caminho_ate_humano: Lista de posições do caminho até o humano.
        - log: Lista de listas representando o log de comandos e sensores.
        - log_file: Nome do arquivo CSV onde o log será salvo.
    """
    def __init__(self, labirinto: Labirinto, log_file):
        """
        Inicializa o robô na posição de entrada do labirinto.

        Args:
        - labirinto: Instância de Labirinto.
        - log_file: Nome do arquivo CSV para salvar o log.

        Returns:
        - None

        Raises:
        - None
        """
        self.lab = labirinto
        self.pos = labirinto.entrada
        self.humano_coletado = False
        self.orientacao = 0
        self.caminho_ate_humano = []
        self.log = []
        self.log_file = log_file
        self.log_comando("LIGAR")

    def sensores(self):
        """
        Retorna o estado dos sensores do robô.

        Args:
            - None

        Returns:
            - lista de strings representando o estado dos sensores [frente, esquerda, direita]

        Raises:
            - None
        """
        frente_dir = DIRS[self.orientacao]
        esquerda_dir = DIRS[(self.orientacao - 1) % 4]
        direita_dir = DIRS[(self.orientacao + 1) % 4]

        sensores = []
        for i, (dx, dy) in enumerate([frente_dir, esquerda_dir, direita_dir]):
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
        """
        Registra um comando e o estado dos sensores no log.

        Args:
            - cmd: String representando o comando executado.

        Returns:
            - None

        Raises:
            - None
        """
        sensores = self.sensores()
        carga = "COM HUMANO" if self.humano_coletado else "SEM CARGA"
        self.log.append([cmd]+sensores+[carga])

    def mover_para(self, nova_pos, nova_orientacao):
        """
        Move o robô para uma nova posição e orientação.

        Args:
            - nova_pos: Tupla (x, y) representando a nova posição.
            - nova_orientacao: Inteiro representando a nova orientação (0=N, 1=L, 2=S, 3=O).
        
        Returns:
            - None

        Raises:
            - Exception: Se houver tentativa de colisão com parede ou atropelamento de humano.
        """

        if self.lab.get_celula(nova_pos) == 'X':
            raise Exception("⚠️ ALARME: Tentativa de colisão com parede!")

        if self.lab.get_celula(nova_pos) == '@' and self.humano_coletado:
            raise Exception("⚠️ ALARME: Tentativa de atropelamento de humano!")

        giros = (nova_orientacao - self.orientacao) % 4
        for _ in range(giros):

            self.orientacao = (self.orientacao + 1) % 4
            self.log_comando("G")

        self.pos = nova_pos
        self.lab.print(self.pos, humano_presente=not self.humano_coletado)
        self.log_comando("A")

    def explorar(self):
        """
        Explora o labirinto em busca do humano usando DFS com prioridade para sensores.

        Args:
            - None

        Returns:
            - None
        
        Raises:
            - Exception: Se o robô ficar em beco sem saída após coletar o humano.
        """

        visitados = set()
        caminho = []

        def dfs(pos):
            """
            Realiza a busca em profundidade (DFS) a partir da posição atual.

            Args:
                - pos: Tupla (x, y) representando a posição atual.

            Returns:
                - True se o humano foi encontrado e coletado, False caso contrário.

            Raises:
                - None
            """

            if pos in visitados:
                return False
            visitados.add(pos)

            sensores = self.sensores()
            if "HUMANO" in sensores:
                idx = sensores.index("HUMANO")
                if idx == 0:
                    nd = self.orientacao
                elif idx == 1:
                    nd = (self.orientacao - 1) % 4
                else:
                    nd = (self.orientacao + 1) % 4
                dx, dy = DIRS[nd]
                nx, ny = pos[0] + dx, pos[1] + dy
                if self.lab.get_celula((nx, ny)) == '@':
                    self._girar_para(nd)
                    self.pegar_humano_frente((nx, ny))
                    return True

            if self.lab.get_celula(pos) == '@':
                self.pegar_humano()
                return True

            for nd, (dx, dy) in enumerate(DIRS):
                nx, ny = pos[0] + dx, pos[1] + dy
                cel_vizinha = self.lab.get_celula((nx, ny))

                if cel_vizinha == '@' and (nx, ny) not in visitados:
                    self._girar_para(nd)
                    self.pegar_humano_frente((nx, ny))
                    return True

                if cel_vizinha in ['.', 'E'] and (nx, ny) not in visitados:
                    caminho.append((nx, ny))
                    self.mover_para((nx, ny), nd)
                    if dfs((nx, ny)):
                        return True

                    self.mover_para(pos, (nd + 2) % 4)
                    caminho.pop()

            return False

        dfs(self.pos)
        self.caminho_ate_humano = [self.lab.entrada] + caminho

    def _girar_para(self, nova_orientacao):
        """
        Gira o robô para a nova orientação.

        Args:
            - nova_orientacao: Inteiro representando a nova orientação (0=N, 1=L, 2=S, 3=O).    

        Returns:
            - None

        Raises:
            - None
        """

        giros = (nova_orientacao - self.orientacao) % 4
        for _ in range(giros):
            self.orientacao = (self.orientacao + 1) % 4
            self.log_comando("G")

    def _tem_caminho_para_entrada(self, start_pos):
        """
        Verifica se há um caminho da posição start_pos até a entrada do labirinto.
        
        Args:
            - start_pos: Tupla (x, y) representando a posição inicial.

        Returns:
            - True se há um caminho, False caso contrário.

        Raises:
            - None
        """

        from collections import deque
        q = deque([start_pos])
        visitados = {start_pos}
        while q:
            x, y = q.popleft()
            if (x, y) == self.lab.entrada:
                return True
            for dx, dy in DIRS:
                nx, ny = x + dx, y + dy
                if (nx, ny) in visitados:
                    continue
                cel = self.lab.get_celula((nx, ny))
                if cel in ('.', 'E', '@'):
                    visitados.add((nx, ny))
                    q.append((nx, ny))
        return False

    def pegar_humano_frente(self, pos_humano):
        """
        Caso o robô esteja de frente para a célula do humano (não entra na célula).
        Args:
            - pos_humano: Tupla (x, y) representando a posição do humano.

        Returns:
            - None

        Raises:
            - Exception: Se não houver humano na célula à frente.
        """

        if self.lab.get_celula(pos_humano) != '@':
            raise Exception("⚠️ ALARME: Tentativa de coleta frontal sem humano!")

        self.humano_coletado = True
        self.lab.set_celula(pos_humano, '.')

        self.log_comando("P")
        self.lab.print(self.pos, humano_presente=False)

    def pegar_humano(self):
        """
        Coleta o humano na célula atual do robô.

        Args:
            - None

        Returns:
            - None

        Raises:
            - None
        """

        if self.lab.get_celula(self.pos) != '@':
            raise Exception("⚠️ ALARME: tentativa de coleta sem humano")

        if not self._tem_caminho_para_entrada(self.pos):
            raise Exception("⚠️ ALARME: Beco sem saída")

        self.humano_coletado = True
        self.lab.set_celula(self.pos, '.')
        self.log_comando("P")
        self.lab.print(self.pos, humano_presente=False)

    def retornar(self):
        """
        Retorna à entrada do labirinto após coletar o humano.

        Args:
            - None
        
        Returns:
            - None

        Raises:
            - Exception: Se houver tentativa de ejeção sem humano ou se o robô não estiver em posição válida para ejeção.
        """

        caminho_volta = list(reversed(self.caminho_ate_humano[:-1]))
        for prox in caminho_volta:

            if prox == self.lab.entrada:
                break
            dx = prox[0] - self.pos[0]
            dy = prox[1] - self.pos[1]
            nd = DIRS.index((dx, dy))
            self.mover_para(prox, nd)

        ex, ey = self.lab.entrada
        rx, ry = self.pos
        dx = ex - rx
        dy = ey - ry
        if (dx, dy) not in DIRS:

            raise Exception("⚠️ ALARME: Não está em posição válida para ejeção (não adjacente à entrada)!")
        nd_entrada = DIRS.index((dx, dy))

        self._girar_para(nd_entrada)

        self.ejetar()

    def ejetar(self):
        """
        Ejetar o humano na célula de entrada.

        Args:
            - None
        
        Returns:
            - None

        Raises:
            - Exception: Se houver tentativa de ejeção sem humano ou se o robô não estiver de frente para a entrada.
        """

        if not self.humano_coletado:
            raise Exception("⚠️ ALARME: Tentativa de ejeção sem humano!")

        frente = (self.pos[0] + DIRS[self.orientacao][0],
                  self.pos[1] + DIRS[self.orientacao][1])
        if frente != self.lab.entrada:
            raise Exception("⚠️ ALARME: Tentativa de ejeção somente é permitida quando o robô estiver de frente para a saída!")

        self.lab.set_celula(self.lab.entrada, '@')
        self.humano_coletado = False
        self.log_comando("E")

    def salvar_log(self):
        with open(self.log_file,"w",newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Comando","Frente","Esquerda","Direita","Carga"])
            writer.writerows(self.log)