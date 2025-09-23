from labirinto import Labirinto
from robo import Robo

class Simulacao:
    """
    Classe que gerencia a simulação do robô no labirinto.
    
    Atributos:
        - lab (Labirinto): O labirinto onde o robô irá operar.
        - robo (Robo): O robô que irá explorar o labirinto.
    """
    def __init__(self, mapa_str, nome_arquivo):
        """
        Inicializa a simulação com o mapa e o nome do arquivo de log.

        Args:
            mapa_str (str): Representação em string do labirinto.
            nome_arquivo (str): Nome do arquivo para salvar o log.

        Returns:
            - None

        Raises:
            - None
        """

        self.lab = Labirinto(mapa_str)
        log_file = nome_arquivo.replace(".txt",".csv")
        self.robo = Robo(self.lab, log_file)

    def executar(self):
        """
        Executa a simulação do robô no labirinto.

        Returns:
            - None

        Raises:
            - None
        """

        self.robo.explorar()
        self.robo.retornar()
        self.robo.salvar_log()