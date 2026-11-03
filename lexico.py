# ---------------------------------------------------
# Analisador lexico da linguagem D
# Automato de reconhecimento: le o fonte caractere por caractere
# e agrupa os caracteres em tokens
# ---------------------------------------------------
from ttoken import TOKEN


class Lexico:

    # construtor: carrega o fonte inteiro na memoria e zera a posicao de leitura
    def __init__(self, arqFonte):
        self.arqFonte = arqFonte           # objeto file
        self.fonte = self.arqFonte.read()  # conteudo do arquivo
        self.tamFonte = len(self.fonte)    # quantidade de caracteres do fonte
        self.indiceFonte = 0               # posicao do proximo caractere a ler
        self.tokenLido = None              # (token, lexema, linha, coluna)
        self.linha = 1                     # linha atual no fonte
        self.coluna = 0                    # coluna atual no fonte

    # ---------------- leitura do fonte ----------------

    # fimDoArquivo: diz se todos os caracteres ja foram lidos
    def fimDoArquivo(self):
        return self.indiceFonte >= self.tamFonte

    # getchar: devolve o proximo caractere, avanca a posicao e atualiza
    # linha e coluna; no fim do arquivo devolve o marcador '\0'
    def getchar(self):
        if self.fimDoArquivo():
            return '\0'
        car = self.fonte[self.indiceFonte]
        self.indiceFonte += 1
        if car == '\n':
            # quebra de linha: passa para a linha seguinte, coluna recomeca
            self.linha += 1
            self.coluna = 0
        else:
            self.coluna += 1
        return car

    # ungetchar: devolve um caractere lido a mais, para ser lido de novo.
    # necessario porque o fim de um token so e percebido ao ler o caractere
    # seguinte (em "abc;" o ident termina ao ler o ;)
    def ungetchar(self, simbolo):
        # '\0' e apenas o marcador de fim de arquivo, nao veio do fonte;
        # devolve-lo faria o ultimo caractere ser lido duas vezes
        if simbolo == '\0':
            return

        # desfaz a mudanca de linha feita pelo getchar
        if simbolo == '\n':
            self.linha -= 1

        # volta uma posicao na leitura
        if self.indiceFonte > 0:
            self.indiceFonte -= 1

        self.coluna -= 1

    # ---------------- classes de caracteres ----------------

    # eLetra: so a-z e A-Z; letras acentuadas nao fazem parte da linguagem
    def eLetra(self, simbolo):
        return ('a' <= simbolo <= 'z') or ('A' <= simbolo <= 'Z')

    # eDigito: so 0-9
    def eDigito(self, simbolo):
        return '0' <= simbolo <= '9'

    # eLetraDigitoSublinha: caracteres permitidos depois do inicio de um ident
    def eLetraDigitoSublinha(self, simbolo):
        return self.eLetra(simbolo) or self.eDigito(simbolo) or simbolo == '_'

    # ---------------- saida ----------------

    # imprimeToken: mostra um token no formato (tk=... lex="..." lin=... col=...)
    def imprimeToken(self, tokenCorrente):
        (token, lexema, linha, coluna) = tokenCorrente
        msg = TOKEN.msg(token)
        print(f'(tk={msg} lex="{lexema}" lin={linha} col={coluna})')

    # ---------------- automato ----------------

    # getToken: funcao principal do lexico. A cada chamada, reconhece UM token
    # e devolve a tupla (token, lexema, linha, coluna)
    def getToken(self):
        estado = 1                # o automato sempre comeca no estado 1
        lexema = ''               # texto do token que esta sendo montado
        simbolo = self.getchar()  # caractere atual

        # descarta brancos e comentarios (que iniciam com // ate o fim da linha)
        while True:
            # pula espaco, tabulacao e quebras de linha
            while simbolo in [' ', '\t', '\n', '\r']:
                simbolo = self.getchar()
            if simbolo == '/':
                # uma / pode ser divisao ou comentario: precisa olhar a seguinte
                prox = self.getchar()
                if prox == '/':
                    # e comentario: ignora tudo ate o fim da linha
                    while simbolo not in ['\n', '\0']:
                        simbolo = self.getchar()
                    continue          # volta a descartar brancos/comentarios
                self.ungetchar(prox)  # era uma divisao, nao um comentario
            break

        # inicio do token
        lin = self.linha   # onde inicia o token, para msgs
        col = self.coluna  # onde inicia o token, para msgs

        # cada volta do laco processa um caractere no estado atual
        while (True):
            if estado == 1:
                # inicio do automato: o primeiro caractere decide o caminho
                if self.eLetra(simbolo):
                    estado = 2    # idents, pal.reservadas, func.primitivas
                elif self.eDigito(simbolo):
                    estado = 3    # valorInt, valorFloat
                elif simbolo == '"':
                    estado = 4    # valorString
                # simbolos de um caractere so: o token ja esta completo
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
                # simbolos que podem ter 2 caracteres: precisam olhar o seguinte
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
                    # acabou o arquivo
                    return (TOKEN.eof, '<eof>', lin, col)
                else:
                    # caractere que nao pertence a linguagem (ex.: @)
                    lexema += simbolo
                    return (TOKEN.erro, lexema, lin, col)

            elif estado == 2:
                # identificadores, palavras reservadas e funcoes primitivas
                if self.eLetraDigitoSublinha(simbolo):
                    estado = 2    # a palavra continua
                else:
                    # a palavra acabou: devolve o caractere extra e classifica
                    self.ungetchar(simbolo)
                    token = TOKEN.reservada(lexema)
                    return (token, lexema, lin, col)

            elif estado == 3:
                # parte inteira do numero
                if self.eDigito(simbolo):
                    estado = 3    # o numero continua
                elif simbolo == '.':
                    estado = 31   # vai ser float
                elif self.eLetra(simbolo) or simbolo == '_':
                    estado = 33   # erro: numero seguido de letra (12abc)
                else:
                    # o numero acabou: e inteiro
                    self.ungetchar(simbolo)
                    return (TOKEN.valorInt, lexema, lin, col)

            elif estado == 31:
                # tem que vir pelo menos um digito depois do ponto
                if self.eDigito(simbolo):
                    estado = 32
                else:
                    # ponto sem digito depois (10.) e erro
                    self.ungetchar(simbolo)
                    return (TOKEN.erro, lexema, lin, col)

            elif estado == 32:
                # parte fracionaria do numero
                if self.eDigito(simbolo):
                    estado = 32   # a parte fracionaria continua
                elif self.eLetra(simbolo) or simbolo == '_':
                    estado = 33   # erro: numero seguido de letra (1.5x)
                else:
                    # o numero acabou: e float
                    self.ungetchar(simbolo)
                    return (TOKEN.valorFloat, lexema, lin, col)

            elif estado == 33:
                # numero seguido de letra: o erro vai ate o fim da palavra
                if self.eLetraDigitoSublinha(simbolo):
                    estado = 33
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.erro, lexema, lin, col)

            elif estado == 4:
                # strings, com escapes do tipo \" e \\
                while True:
                    if simbolo == '"':
                        # aspas de fechamento: a string terminou
                        lexema += simbolo
                        return (TOKEN.valorString, lexema, lin, col)
                    if simbolo in ['\n', '\0']:
                        # string nao fechada na mesma linha
                        self.ungetchar(simbolo)
                        return (TOKEN.erro, lexema, lin, col)
                    if simbolo == '\\':
                        # barra: guarda e le o proximo sem interpreta-lo,
                        # por isso \" nao fecha a string
                        lexema += simbolo
                        simbolo = self.getchar()
                        if simbolo in ['\n', '\0']:
                            self.ungetchar(simbolo)
                            return (TOKEN.erro, lexema, lin, col)

                    # caractere comum: entra na string
                    lexema = lexema + simbolo
                    simbolo = self.getchar()

            elif estado == 5:
                # ja leu <
                if simbolo == '=':
                    lexema = lexema + simbolo
                    return (TOKEN.oprel, lexema, lin, col)   # <=
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.oprel, lexema, lin, col)   # <

            elif estado == 6:
                # ja leu >
                if simbolo == '=':
                    lexema = lexema + simbolo
                    return (TOKEN.oprel, lexema, lin, col)   # >=
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.oprel, lexema, lin, col)   # >

            elif estado == 7:
                # ja leu =
                if simbolo == '=':
                    lexema = lexema + simbolo
                    return (TOKEN.oprel, lexema, lin, col)   # ==
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.atribuicao, lexema, lin, col)   # =

            elif estado == 8:
                # ja leu !
                if simbolo == '=':
                    lexema = lexema + simbolo
                    return (TOKEN.oprel, lexema, lin, col)   # !=
                else:
                    # '!' sozinho nao existe; a negacao e NOT
                    self.ungetchar(simbolo)
                    return (TOKEN.erro, lexema, lin, col)

            elif estado == 9:
                # ja leu +
                if simbolo == '+':
                    lexema = lexema + simbolo
                    return (TOKEN.increm, lexema, lin, col)   # ++
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.mais, lexema, lin, col)     # +

            elif estado == 10:
                # ja leu -
                if simbolo == '-':
                    lexema = lexema + simbolo
                    return (TOKEN.decrem, lexema, lin, col)   # --
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.menos, lexema, lin, col)    # -

            else:
                # estado inexistente: so aconteceria por erro no codigo
                print('BUG!!!')

            # o token continua: guarda o caractere atual e le o proximo
            lexema = lexema + simbolo
            simbolo = self.getchar()


# rodando este arquivo direto, so mostra como usar
if __name__ == '__main__':
    print("Para testar, chame o analisador lexico no main.py")
