# ---------------------------------------------------
# Analisador sintatico da linguagem D
#
# uso: python3 main.py testes/exemplo.d
# ---------------------------------------------------
import sys

from lexico import Lexico
from sintatico import Sintatico

if __name__ == '__main__':
    if len(sys.argv) > 1:
        caminho = sys.argv[1]
    else:
        caminho = 'testes/exemplo.d'

    arqfonte = open(caminho, 'r')
    lexico = Lexico(arqfonte)
    arqfonte.close()

    sintatico = Sintatico(lexico)
    sintatico.traduz()
