# ---------------------------------------------------
# COMO RODAR: copie cada linha sem o # do inicio
#   cd ~/DEV/Compiladores/compilador-d/analisador-sintatico
#   python3 main.py testes/exemplo.d
#   python3 -c "from lexico import Lexico; from sintatico import Sintatico; Sintatico(Lexico(open('testes/exemplo.d', encoding='utf-8'))).testaLexico()"
#   python3 -c "from lexico import Lexico; from sintatico import Sintatico; Sintatico(Lexico(open('testes/erros.d', encoding='utf-8'))).testaLexico()"
# ---------------------------------------------------

# ---------------------------------------------------
# Analisador lexico da linguagem D
# Tabela de tokens: lista todos os tipos de token que existem na linguagem
# ---------------------------------------------------

# IntEnum: cada nome (ex.: TOKEN.ident) vira uma constante com um numero inteiro
from enum import IntEnum


class TOKEN(IntEnum):
    # controle
    erro = 1            # sequencia invalida (ex.: @ ou 12abc)
    eof = 2             # fim do arquivo

    # identificadores e literais
    ident = 3           # nome de variavel ou funcao: contador, Total_1
    valorInt = 4        # numero inteiro: 42
    valorFloat = 5      # numero com ponto: 3.14
    valorString = 6     # texto entre aspas: "ola"

    # delimitadores e separadores
    virgula = 7         # ,
    ptoVirg = 8         # ;
    abrePar = 9         # (
    fechaPar = 10       # )
    abreCol = 11        # [
    fechaCol = 12       # ]
    abreChave = 13      # {
    fechaChave = 14     # }
    endereco = 15       # &  (parametro por referencia: int &a)

    # operadores
    increm = 16         # ++
    decrem = 17         # --
    oprel = 18          # >  >=  <  <=  ==  !=  (o lexema identifica qual)
    mais = 19           # +
    menos = 20          # -
    multiplica = 21     # *
    divide = 22         # /
    atribuicao = 23     # =

    # palavras reservadas: em maiusculas para nao colidir com palavras do Python
    INT = 24            # tipo inteiro
    FLOAT = 25          # tipo real
    STRING = 26         # tipo texto
    VOID = 27           # funcao sem retorno
    BREAK = 28          # sai da repeticao
    CONTINUE = 29       # vai para a proxima volta da repeticao
    LOOP = 30           # repeticao sem condicao
    WHILE = 31          # repeticao com condicao
    FOR = 32            # repeticao for
    IN = 33             # usado no for (i in lista)
    IF = 34             # decisao
    ELIF = 35           # senao-se
    ELSE = 36           # senao
    READ = 37           # entrada
    WRITE = 38          # saida
    OR = 39             # ou logico
    AND = 40            # e logico
    NOT = 41            # negacao logica
    DIV = 42            # divisao inteira
    MOD = 43            # resto da divisao
    RETURN = 44         # retorno de funcao

    # funcoes primitivas
    funcPrim = 45       # str2int, str2float, int2str, float2string

    # msg: recebe um token e devolve o nome legivel, usado nas impressoes e
    # nas mensagens de erro (ex.: TOKEN.ptoVirg -> ';')
    @classmethod
    def msg(cls, token):
        # dicionario numero do token -> texto mostrado ao usuario
        nomes = {
            1: 'erro',
            2: '<eof>',
            3: 'ident',
            4: 'valorInt',
            5: 'valorFloat',
            6: 'valorString',
            7: ',',
            8: ';',
            9: '(',
            10: ')',
            11: '[',
            12: ']',
            13: '{',
            14: '}',
            15: '&',
            16: '++',
            17: '--',
            18: 'oprel',
            19: '+',
            20: '-',
            21: '*',
            22: '/',
            23: '=',
            24: 'int',
            25: 'float',
            26: 'string',
            27: 'void',
            28: 'break',
            29: 'continue',
            30: 'loop',
            31: 'while',
            32: 'for',
            33: 'in',
            34: 'if',
            35: 'elif',
            36: 'else',
            37: 'read',
            38: 'write',
            39: 'OR',
            40: 'AND',
            41: 'NOT',
            42: 'div',
            43: 'mod',
            44: 'return',
            45: 'funcPrim'
        }
        return nomes[token]

    # reservada: recebe uma palavra lida do fonte e decide o que ela e:
    # palavra reservada, funcao primitiva ou identificador.
    # comparacao exata: a linguagem e case sensitive, entao 'While' e
    # 'or' permanecem identificadores
    @classmethod
    def reservada(cls, lexema):
        # dicionario palavra -> token
        reservadas = {
            'int': TOKEN.INT,
            'float': TOKEN.FLOAT,
            'string': TOKEN.STRING,
            'void': TOKEN.VOID,
            'break': TOKEN.BREAK,
            'continue': TOKEN.CONTINUE,
            'loop': TOKEN.LOOP,
            'while': TOKEN.WHILE,
            'for': TOKEN.FOR,
            'in': TOKEN.IN,
            'if': TOKEN.IF,
            'elif': TOKEN.ELIF,
            'else': TOKEN.ELSE,
            'read': TOKEN.READ,
            'write': TOKEN.WRITE,
            'OR': TOKEN.OR,
            'AND': TOKEN.AND,
            'NOT': TOKEN.NOT,
            'div': TOKEN.DIV,
            'mod': TOKEN.MOD,
            'return': TOKEN.RETURN
        }
        # as 4 funcoes primitivas compartilham um unico token
        primitivas = ['str2int', 'str2float', 'int2str', 'float2string']

        if lexema in reservadas:
            return reservadas[lexema]
        elif lexema in primitivas:
            return TOKEN.funcPrim
        else:
            # nao e reservada nem primitiva: e um nome criado pelo programador
            return TOKEN.ident
