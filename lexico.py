# ---------------------------------------------------
# Analisador lexico da linguagem D
# Automato de reconhecimento
# ---------------------------------------------------
from ttoken import TOKEN


class Lexico:

    def __init__(self, arqFonte):
        self.arqFonte = arqFonte           # objeto file
        self.fonte = self.arqFonte.read()  # conteudo do arquivo
        self.tamFonte = len(self.fonte)
        self.indiceFonte = 0
        self.tokenLido = None              # (token, lexema, linha, coluna)
        self.linha = 1                     # linha atual no fonte
        self.coluna = 0                    # coluna atual no fonte

    # ---------------- leitura do fonte ----------------

    def fimDoArquivo(self):
        return self.indiceFonte >= self.tamFonte

    def getchar(self):
        if self.fimDoArquivo():
            return '\0'
        car = self.fonte[self.indiceFonte]
        self.indiceFonte += 1
        if car == '\n':
            self.linha += 1
            self.coluna = 0
        else:
            self.coluna += 1
        return car

    def ungetchar(self, simbolo):
        # '\0' e apenas o marcador de fim de arquivo, nao veio do fonte;
        # devolve-lo faria o ultimo caractere ser lido duas vezes
        if simbolo == '\0':
            return

        if simbolo == '\n':
            self.linha -= 1

        if self.indiceFonte > 0:
            self.indiceFonte -= 1

        self.coluna -= 1

    # ---------------- classes de caracteres ----------------

    def eLetra(self, simbolo):
        return ('a' <= simbolo <= 'z') or ('A' <= simbolo <= 'Z')

    def eDigito(self, simbolo):
        return '0' <= simbolo <= '9'

    def eLetraDigitoSublinha(self, simbolo):
        return self.eLetra(simbolo) or self.eDigito(simbolo) or simbolo == '_'

    # ---------------- saida ----------------

    def imprimeToken(self, tokenCorrente):
        (token, lexema, linha, coluna) = tokenCorrente
        msg = TOKEN.msg(token)
        print(f'(tk={msg} lex="{lexema}" lin={linha} col={coluna})')

    # ---------------- automato ----------------

    def getToken(self):
        estado = 1
        lexema = ''
        simbolo = self.getchar()

        # descarta brancos e comentarios (que iniciam com // ate o fim da linha)
        while True:
            while simbolo in [' ', '\t', '\n', '\r']:
                simbolo = self.getchar()
            if simbolo == '/':
                prox = self.getchar()
                if prox == '/':
                    while simbolo not in ['\n', '\0']:
                        simbolo = self.getchar()
                    continue          # volta a descartar brancos/comentarios
                self.ungetchar(prox)  # era uma divisao, nao um comentario
            break

        # inicio do token
        lin = self.linha   # onde inicia o token, para msgs
        col = self.coluna  # onde inicia o token, para msgs

        while (True):
            if estado == 1:
                # inicio do automato
                if self.eLetra(simbolo):
                    estado = 2    # idents, pal.reservadas, func.primitivas
                elif self.eDigito(simbolo):
                    estado = 3    # valorInt, valorFloat
                elif simbolo == '"':
                    estado = 4    # valorString
                elif simbolo == "(":
                    return (TOKEN.abrePar, "(", lin, col)
                elif simbolo == ")":
                    return (TOKEN.fechaPar, ")", lin, col)
                elif simbolo == "[":
                    return (TOKEN.abreCol, "[", lin, col)
                elif simbolo == "]":
                    return (TOKEN.fechaCol, "]", lin, col)
                elif simbolo == "{":
                    return (TOKEN.abreChave, "{", lin, col)
                elif simbolo == "}":
                    return (TOKEN.fechaChave, "}", lin, col)
                elif simbolo == ",":
                    return (TOKEN.virgula, ",", lin, col)
                elif simbolo == ";":
                    return (TOKEN.ptoVirg, ";", lin, col)
                elif simbolo == "&":
                    return (TOKEN.endereco, "&", lin, col)
                elif simbolo == "*":
                    return (TOKEN.multiplica, "*", lin, col)
                elif simbolo == "/":
                    # comentario ja foi descartado antes; aqui e divisao
                    return (TOKEN.divide, "/", lin, col)
                elif simbolo == "+":
                    estado = 9    # + ou ++
                elif simbolo == "-":
                    estado = 10   # - ou --
                elif simbolo == "<":
                    estado = 5    # < ou <=
                elif simbolo == ">":
                    estado = 6    # > ou >=
                elif simbolo == "=":
                    estado = 7    # = ou ==
                elif simbolo == "!":
                    estado = 8    # so existe !=
                elif simbolo == '\0':
                    return (TOKEN.eof, '<eof>', lin, col)
                else:
                    lexema += simbolo
                    return (TOKEN.erro, lexema, lin, col)

            elif estado == 2:
                # identificadores, palavras reservadas e funcoes primitivas
                if self.eLetraDigitoSublinha(simbolo):
                    estado = 2
                else:
                    self.ungetchar(simbolo)
                    token = TOKEN.reservada(lexema)
                    return (token, lexema, lin, col)

            elif estado == 3:
                # parte inteira do numero
                if self.eDigito(simbolo):
                    estado = 3
                elif simbolo == '.':
                    estado = 31
                elif self.eLetra(simbolo) or simbolo == '_':
                    lexema += simbolo
                    return (TOKEN.erro, lexema, lin, col)
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.valorInt, lexema, lin, col)

            elif estado == 31:
                # tem que vir pelo menos um digito depois do ponto
                if self.eDigito(simbolo):
                    estado = 32
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.erro, lexema, lin, col)

            elif estado == 32:
                # parte fracionaria do numero
                if self.eDigito(simbolo):
                    estado = 32
                elif self.eLetra(simbolo) or simbolo == '_':
                    lexema += simbolo
                    return (TOKEN.erro, lexema, lin, col)
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.valorFloat, lexema, lin, col)

            elif estado == 4:
                # strings, com escapes do tipo \" e \\
                while True:
                    if simbolo == '"':
                        lexema += simbolo
                        return (TOKEN.valorString, lexema, lin, col)
                    if simbolo in ['\n', '\0']:
                        # string nao fechada na mesma linha
                        self.ungetchar(simbolo)
                        return (TOKEN.erro, lexema, lin, col)
                    if simbolo == '\\':
                        lexema += simbolo
                        simbolo = self.getchar()
                        if simbolo in ['\n', '\0']:
                            self.ungetchar(simbolo)
                            return (TOKEN.erro, lexema, lin, col)

                    lexema = lexema + simbolo
                    simbolo = self.getchar()

            elif estado == 5:
                if simbolo == '=':
                    lexema = lexema + simbolo
                    return (TOKEN.oprel, lexema, lin, col)   # <=
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.oprel, lexema, lin, col)   # <

            elif estado == 6:
                if simbolo == '=':
                    lexema = lexema + simbolo
                    return (TOKEN.oprel, lexema, lin, col)   # >=
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.oprel, lexema, lin, col)   # >

            elif estado == 7:
                if simbolo == '=':
                    lexema = lexema + simbolo
                    return (TOKEN.oprel, lexema, lin, col)   # ==
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.atribuicao, lexema, lin, col)

            elif estado == 8:
                if simbolo == '=':
                    lexema = lexema + simbolo
                    return (TOKEN.oprel, lexema, lin, col)   # !=
                else:
                    # '!' sozinho nao existe; a negacao e NOT
                    self.ungetchar(simbolo)
                    return (TOKEN.erro, lexema, lin, col)

            elif estado == 9:
                if simbolo == '+':
                    lexema = lexema + simbolo
                    return (TOKEN.increm, lexema, lin, col)
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.mais, lexema, lin, col)

            elif estado == 10:
                if simbolo == '-':
                    lexema = lexema + simbolo
                    return (TOKEN.decrem, lexema, lin, col)
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.menos, lexema, lin, col)

            else:
                print('BUG!!!')

            lexema = lexema + simbolo
            simbolo = self.getchar()


if __name__ == '__main__':
    print("Para testar, chame o analisador lexico no main.py")
