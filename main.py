# ---------------------------------------------------
# COMO RODAR: copie cada linha sem o # do inicio
#   cd ~/DEV/Compiladores/compilador-d/analisador-sintatico
#   python3 main.py testes/exemplo.d
#   python3 -c "from lexico import Lexico; from sintatico import Sintatico; Sintatico(Lexico(open('testes/exemplo.d', encoding='utf-8'))).testaLexico()"
#   python3 -c "from lexico import Lexico; from sintatico import Sintatico; Sintatico(Lexico(open('testes/erros.d', encoding='utf-8'))).testaLexico()"
# ---------------------------------------------------

# ---------------------------------------------------
# Analisador sintatico da linguagem D
# Programa principal: liga o arquivo fonte, o lexico e o sintatico
#
# uso: python3 main.py testes/exemplo.d
# ---------------------------------------------------
import sys       # da acesso aos argumentos da linha de comando

from lexico import Lexico
from sintatico import Sintatico

# so executa quando este arquivo e rodado diretamente
if __name__ == '__main__':
    # sys.argv[0] e o main.py; sys.argv[1] e o arquivo informado, se houver
    if len(sys.argv) > 1:
        caminho = sys.argv[1]
    else:
        caminho = 'testes/exemplo.d'   # sem argumento, usa o programa de exemplo

    # o lexico le o fonte inteiro no construtor, entao o arquivo pode ser fechado
    arqfonte = open(caminho, 'r', encoding='utf-8')
    lexico = Lexico(arqfonte)
    arqfonte.close()

    # o sintatico pede os tokens ao lexico e confere a gramatica
    sintatico = Sintatico(lexico)
    sintatico.traduz()
