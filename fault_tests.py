import pytest
from rescue_robot import Labirinto, Robo, DIRS

# Função auxiliar para criar rapidamente o robo
def criar_robo(mapa_str):
    lab = Labirinto(mapa_str)
    return Robo(lab, "log.csv")


# --------------------------
# 1. Alarme de colisão com parede
# --------------------------
def test_alarme_colisao_parede():
    mapa = """
EX
..
"""
    robo = criar_robo(mapa)
    destino = (robo.pos[0], robo.pos[1] - 1)  # fora do mapa => 'X'

    with pytest.raises(Exception, match="colisão com parede"):
        if robo.lab.get_celula(destino) == 'X':
            raise Exception("⚠️ ALARME: Tentativa de colisão com parede!")


# --------------------------
# 2. Alarme de atropelamento de humano
# --------------------------
def test_alarme_atropelamento_humano():
    mapa = """
E.
@.
"""
    robo = criar_robo(mapa)
    robo.humano_coletado = True
    destino = (robo.pos[0] + 1, robo.pos[1])  # célula com '@'

    with pytest.raises(Exception, match="atropelamento de humano"):
        if robo.lab.get_celula(destino) == '@' and robo.humano_coletado:
            raise Exception("⚠️ ALARME: Tentativa de atropelamento de humano!")


# --------------------------
# 3. Alarme de beco sem saída após coleta de humano
# --------------------------
def test_alarme_beco_sem_saida():
    mapa = """
XXXXX
XEXXX
XXXXX
XXX@X
XXXXX
"""
    robo = criar_robo(mapa)
    # posiciona o robo onde está o humano '@' no mapa (linha 3, coluna 3, zero-based)
    robo.pos = (3, 3)
    with pytest.raises(Exception, match="Beco sem saída"):
        robo.pegar_humano()


# --------------------------
# 4. Alarme de ejeção sem humano
# --------------------------
def test_alarme_ejecao_sem_humano():
    mapa = """
E.
..
"""
    robo = criar_robo(mapa)
    robo.humano_coletado = False
    with pytest.raises(Exception, match="ejeção sem humano"):
        robo.ejetar()


# --------------------------
# 5. Alarme de tentativa de coleta sem humano
# --------------------------
def test_alarme_coleta_sem_humano():
    mapa = """
E.
..
"""
    robo = criar_robo(mapa)
    with pytest.raises(Exception, match="coleta sem humano"):
        robo.pegar_humano()
