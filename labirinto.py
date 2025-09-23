import os
import time
import platform
from config import SIM_DELAY

class Labirinto:
    """
    Classe que representa o labirinto.

    Atributos:
        - mapa: Lista de listas representando o mapa do labirinto.
        - linhas: Número de linhas do labirinto.
        - colunas: Número de colunas do labirinto.
        - entrada: Tupla (x, y) representando a posição da entrada 'E'.
        - humano: Tupla (x, y) representando a posição do humano '@'.
    """

    def __init__(self, mapa_str):
        """
        Inicializa o labirinto a partir de uma string.

        Args:
            - mapa_str: String representando o mapa do labirinto.

        Returns:
            - None

        Raises:
            - None
        """
        self.mapa = [list(l) for l in mapa_str.strip().splitlines()]
        self.linhas = len(self.mapa)
        self.colunas = len(self.mapa[0])
        self.entrada = self._find_char('E')
        self.humano = self._find_char('@')

    def _find_char(self, c):
        """
        Encontra a posição de um caractere no mapa.

        Args:
            - c: Caractere a ser encontrado.

        Returns:
            - Tupla (x, y) representando a posição do caractere ou None se não encontrado.

        Raises:
            - None
        """

        for i,row in enumerate(self.mapa):
            for j,val in enumerate(row):
                if val==c: return (i,j)
        return None

    def get_celula(self,pos):
        """
        Obtém o valor de uma célula no mapa.

        Args:
            - pos: Tupla (x, y) representando a posição da célula.

        Returns:
            - O valor da célula ou 'X' se fora do mapa.

        Raises:
            - None
        """

        x,y = pos
        if 0<=x<self.linhas and 0<=y<self.colunas:
            return self.mapa[x][y]
        return 'X' 

    def set_celula(self,pos,val):
        """
        Define o valor de uma célula no mapa.

        Args:
            - pos: Tupla (x, y) representando a posição da célula.
            - val: Novo valor para a célula.

        Returns:
            - None

        Raises:
            - None
        """

        x,y = pos
        self.mapa[x][y] = val

    def print(self, robo_pos, humano_presente=True):
        """
        Imprime o estado atual do labirinto, incluindo a posição do robô e do humano.
        
        Args:
            - robo_pos: Tupla (x, y) representando a posição do robô.
            - humano_presente: Booleano indicando se o humano deve ser mostrado no mapa.

        Returns:
            - None

        Raises:
            - None
        """

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