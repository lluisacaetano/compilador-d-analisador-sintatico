# ---------------------------------------------------
# Analisador lexico da linguagem D
# Tabela de tokens
# ---------------------------------------------------

from enum import IntEnum


class TOKEN(IntEnum):
    # controle
    erro = 1
    eof = 2

    # identificadores e literais
    ident = 3
    valorInt = 4
    valorFloat = 5
    valorString = 6

    # delimitadores e separadores
    virgula = 7
    ptoVirg = 8
    abrePar = 9
    fechaPar = 10
    abreCol = 11
    fechaCol = 12
    abreChave = 13
    fechaChave = 14
    endereco = 15

    # operadores
    increm = 16
    decrem = 17
    oprel = 18          # >  >=  <  <=  ==  !=  (o lexema identifica qual)
    mais = 19
    menos = 20
    multiplica = 21
    divide = 22
    atribuicao = 23

    # palavras reservadas
    INT = 24
    FLOAT = 25
    STRING = 26
    VOID = 27
    BREAK = 28
    CONTINUE = 29
    LOOP = 30
    WHILE = 31
    FOR = 32
    IN = 33
    IF = 34
    ELIF = 35
    ELSE = 36
    READ = 37
    WRITE = 38
    OR = 39
    AND = 40
    NOT = 41
    DIV = 42
    MOD = 43
    RETURN = 44

    # funcoes primitivas
    funcPrim = 45       # str2int, str2float, int2str, float2string

    @classmethod
    def msg(cls, token):
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

    # comparacao exata: a linguagem e case sensitive, entao 'While' e
    # 'or' permanecem identificadores
    @classmethod
    def reservada(cls, lexema):
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
        primitivas = ['str2int', 'str2float', 'int2str', 'float2string']

        if lexema in reservadas:
            return reservadas[lexema]
        elif lexema in primitivas:
            return TOKEN.funcPrim
        else:
            return TOKEN.ident
