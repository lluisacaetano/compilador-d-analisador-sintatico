# ---------------------------------------------------
# COMO RODAR: copie cada linha sem o # do inicio
#   cd ~/DEV/Compiladores/compilador-d/analisador-sintatico
#   python3 main.py testes/exemplo.d
#   python3 -c "from lexico import Lexico; from sintatico import Sintatico; Sintatico(Lexico(open('testes/exemplo.d', encoding='utf-8'))).testaLexico()"
#   python3 -c "from lexico import Lexico; from sintatico import Sintatico; Sintatico(Lexico(open('testes/erros.d', encoding='utf-8'))).testaLexico()"
# ---------------------------------------------------

# ---------------------------------------------------
# Tradutor para a linguagem D
# Analisador sintatico descendente recursivo: cada nao-terminal da gramatica
# vira um metodo, e o metodo chama os outros na ordem da producao
# ---------------------------------------------------
from lexico import TOKEN, Lexico


class Sintatico:

    # construtor: recebe o lexico, de onde vem os tokens
    def __init__(self, lexico):
        self.lexico = lexico
        self.tokenSeguinte = None   # usado so no for, para olhar um token a frente

    # traduz: ponto de partida. Le o primeiro token, analisa o programa inteiro
    # e confere se nao sobrou nada depois dele
    def traduz(self):
        self.tokenLido = self.lexico.getToken()
        try:
            self.prog()
            self.consome(TOKEN.eof)
            print("Programa sintaticamente correto.")
        except Exception as e:
            # erro sintatico ja foi impresso e vem sem mensagem;
            # qualquer outro erro (ex.: recursao) precisa aparecer
            if e.args:
                print(f"Execucao interrompida: {e}")

    # proximoToken: se o for ja olhou um token a frente, usa esse;
    # senao, pede um novo ao lexico
    def proximoToken(self):
        if self.tokenSeguinte is not None:
            token = self.tokenSeguinte
            self.tokenSeguinte = None
            return token
        return self.lexico.getToken()

    # olhaSeguinte: espia o token depois do atual, sem consumir nada
    def olhaSeguinte(self):
        # token que vem depois do tokenLido, sem consumir
        if self.tokenSeguinte is None:
            self.tokenSeguinte = self.lexico.getToken()
        return self.tokenSeguinte[0]

    # consome: o token atual tem que ser o esperado. Se for, avanca para o
    # proximo; se nao for, e erro sintatico
    def consome(self, tokenAtual):
        (token, lexema, linha, coluna) = self.tokenLido
        if tokenAtual == token:
            self.tokenLido = self.proximoToken()
        else:
            msgTokenAtual = TOKEN.msg(tokenAtual)
            self.erro(msgTokenAtual)

    # erro: mostra a posicao e o problema e para a analise com uma excecao,
    # que e capturada em traduz()
    def erro(self, esperado):
        (token, lexema, linha, coluna) = self.tokenLido
        msgTokenLido = TOKEN.msg(token)
        print(f"Erro na linha {linha}, coluna {coluna}")
        if token == TOKEN.erro:
            # o lexico nao reconheceu o trecho: erro lexico, nao sintatico
            print(f'Erro lexico: token invalido "{lexema}"')
        else:
            print(f"Era esperado {esperado} mas veio {msgTokenLido}")
        raise Exception

    # testaLexico: imprime os tokens, sem analisar a gramatica; para no primeiro
    # erro ou no fim do arquivo
    def testaLexico(self):
        self.tokenLido = self.lexico.getToken()
        (token, lexema, linha, coluna) = self.tokenLido
        while token not in [TOKEN.eof, TOKEN.erro]:
            self.lexico.imprimeToken(self.tokenLido)
            self.tokenLido = self.lexico.getToken()
            (token, lexema, linha, coluna) = self.tokenLido
        # imprime tambem o token que parou a leitura: o erro ou o <eof>
        self.lexico.imprimeToken(self.tokenLido)

    # --------------------------------- gramática -------------------------------------

    # ---------------- programa e funcoes ----------------

    # prog: um programa tem pelo menos uma funcao
    def prog(self):
        # Prog -> Func RestoProg
        self.func()
        self.restoProg()

    # restoProg: se vier um tipo, comeca outra funcao; senao, acabaram as funcoes
    def restoProg(self):
        # RestoProg -> LAMBDA | Func RestoProg
        if self.tokenLido[0] in [TOKEN.VOID, TOKEN.INT, TOKEN.FLOAT, TOKEN.STRING]:
            self.func()
            self.restoProg()
        else:
            pass

    # func: uma funcao completa. Ex.: int soma(int a) { ... }
    def func(self):
        # Func -> TipoFunc ident ( ListaArgs ) Corpo
        self.tipoFunc()
        self.consome(TOKEN.ident)
        self.consome(TOKEN.abrePar)
        self.listaArgs()
        self.consome(TOKEN.fechaPar)
        self.corpo()

    # tipoPrim: tipo de variavel ou parametro
    def tipoPrim(self):
        # TipoPrim -> int | float | string
        if self.tokenLido[0] == TOKEN.INT:
            self.consome(TOKEN.INT)
        elif self.tokenLido[0] == TOKEN.FLOAT:
            self.consome(TOKEN.FLOAT)
        elif self.tokenLido[0] == TOKEN.STRING:
            self.consome(TOKEN.STRING)
        else:
            self.erro("int, float ou string")

    # tipoFunc: tipo de retorno de funcao; alem dos primitivos, aceita void
    def tipoFunc(self):
        # TipoFunc -> void | TipoPrim
        if self.tokenLido[0] == TOKEN.VOID:
            self.consome(TOKEN.VOID)
        elif self.tokenLido[0] in [TOKEN.INT, TOKEN.FLOAT, TOKEN.STRING]:
            self.tipoPrim()
        else:
            self.erro("void, int, float ou string")

    # ---------------- parametros da funcao ----------------

    # listaArgs: a lista pode ser vazia; so comeca se vier um tipo
    def listaArgs(self):
        # ListaArgs -> LAMBDA | Arg RestoListaArgs
        if self.tokenLido[0] in [TOKEN.INT, TOKEN.FLOAT, TOKEN.STRING]:
            self.arg()
            self.restoListaArgs()
        else:
            pass

    # restoListaArgs: cada virgula traz mais um parametro
    def restoListaArgs(self):
        # RestoListaArgs -> , Arg RestoListaArgs | LAMBDA
        if self.tokenLido[0] == TOKEN.virgula:
            self.consome(TOKEN.virgula)
            self.arg()
            self.restoListaArgs()
        else:
            pass

    # arg: um parametro. Ex.: int a | int &a | float b[]
    def arg(self):
        # Arg -> TipoPrim OpcRef ident OpcColchete
        self.tipoPrim()
        self.opcRef()
        self.consome(TOKEN.ident)
        self.opcColchete()

    # opcRef: & opcional, passagem por referencia
    def opcRef(self):
        # OpcRef -> LAMBDA | &
        if self.tokenLido[0] == TOKEN.endereco:
            self.consome(TOKEN.endereco)
        else:
            pass

    # opcColchete: [] opcional, indica lista
    def opcColchete(self):
        # OpcColchete -> LAMBDA | [ ]
        if self.tokenLido[0] == TOKEN.abreCol:
            self.consome(TOKEN.abreCol)
            self.consome(TOKEN.fechaCol)
        else:
            pass

    # ---------------- corpo e declaracoes ----------------

    # corpo: entre chaves, primeiro todas as declaracoes, depois os comandos
    def corpo(self):
        # Corpo -> { ListaDeclar ListaCom }
        self.consome(TOKEN.abreChave)
        self.listaDeclar()
        self.listaCom()
        self.consome(TOKEN.fechaChave)

    # listaDeclar: enquanto vier um tipo, ha mais uma declaracao
    def listaDeclar(self):
        # ListaDeclar -> LAMBDA | Declar ListaDeclar
        if self.tokenLido[0] in [TOKEN.INT, TOKEN.FLOAT, TOKEN.STRING]:
            self.declar()
            self.listaDeclar()
        else:
            pass

    # declar: uma declaracao. Ex.: int x = 3, y, z[];
    def declar(self):
        # Declar -> TipoPrim ident OpcColchete OpcInicializa Listaident ;
        self.tipoPrim()
        self.consome(TOKEN.ident)
        self.opcColchete()
        self.opcInicializa()
        self.listaIdent()
        self.consome(TOKEN.ptoVirg)

    # listaIdent: demais variaveis da declaracao; estas nao aceitam inicializacao
    def listaIdent(self):
        # Listaident -> LAMBDA | , ident OpcColchete Listaident
        if self.tokenLido[0] == TOKEN.virgula:
            self.consome(TOKEN.virgula)
            self.consome(TOKEN.ident)
            self.opcColchete()
            self.listaIdent()
        else:
            pass

    # opcInicializa: = valor opcional, so na primeira variavel da declaracao
    def opcInicializa(self):
        # OpcInicializa -> LAMBDA | = Exp
        if self.tokenLido[0] == TOKEN.atribuicao:
            self.consome(TOKEN.atribuicao)
            self.exp()
        else:
            pass

    # ---------------- comandos ----------------

    # listaCom: a lista contem todos os tokens que podem iniciar um comando;
    # se o token nao esta nela, os comandos acabaram
    def listaCom(self):
        # ListaCom -> LAMBDA | Com ListaCom
        if self.tokenLido[0] in [TOKEN.LOOP, TOKEN.WHILE, TOKEN.FOR, TOKEN.IF,
                                 TOKEN.READ, TOKEN.WRITE, TOKEN.BREAK,
                                 TOKEN.CONTINUE, TOKEN.RETURN, TOKEN.abreChave,
                                 TOKEN.increm, TOKEN.decrem, TOKEN.NOT,
                                 TOKEN.mais, TOKEN.menos, TOKEN.valorInt,
                                 TOKEN.valorFloat, TOKEN.valorString,
                                 TOKEN.abrePar, TOKEN.ident, TOKEN.abreCol,
                                 TOKEN.funcPrim]:
            self.com()
            self.listaCom()
        else:
            pass

    # com: o token atual decide qual comando e
    def com(self):
        # Com -> ComRepete | ComDecisao | ComIO | Exp ;
        # Com -> break ; | continue ; | return OpcExp ;
        # Com -> Bloco
        if self.tokenLido[0] in [TOKEN.LOOP, TOKEN.WHILE, TOKEN.FOR]:
            self.comRepete()
        elif self.tokenLido[0] == TOKEN.IF:
            self.comDecisao()
        elif self.tokenLido[0] in [TOKEN.READ, TOKEN.WRITE]:
            self.comIO()
        elif self.tokenLido[0] == TOKEN.BREAK:
            self.consome(TOKEN.BREAK)
            self.consome(TOKEN.ptoVirg)
        elif self.tokenLido[0] == TOKEN.CONTINUE:
            self.consome(TOKEN.CONTINUE)
            self.consome(TOKEN.ptoVirg)
        elif self.tokenLido[0] == TOKEN.RETURN:
            self.consome(TOKEN.RETURN)
            self.opcExp()
            self.consome(TOKEN.ptoVirg)
        elif self.tokenLido[0] == TOKEN.abreChave:
            self.bloco()
        else:
            # nenhuma palavra-chave: e uma expressao. Ex.: a = 1;
            self.exp()
            self.consome(TOKEN.ptoVirg)

    # bloco: { ... } com suas proprias declaracoes e comandos
    def bloco(self):
        # Bloco -> Corpo
        self.corpo()

    # comRepete: as tres formas de repeticao
    def comRepete(self):
        # ComRepete -> loop Bloco
        # ComRepete -> while ( Exp ) Bloco
        # ComRepete -> for ( RestoComRepete
        if self.tokenLido[0] == TOKEN.LOOP:
            self.consome(TOKEN.LOOP)
            self.bloco()
        elif self.tokenLido[0] == TOKEN.WHILE:
            self.consome(TOKEN.WHILE)
            self.consome(TOKEN.abrePar)
            self.exp()
            self.consome(TOKEN.fechaPar)
            self.bloco()
        else:
            self.consome(TOKEN.FOR)
            self.consome(TOKEN.abrePar)
            self.restoComRepete()

    # restoComRepete: for (i in lista) ou for (inicio; condicao; passo)
    def restoComRepete(self):
        # RestoComRepete -> ident in ident ) Bloco
        # RestoComRepete -> OpcExp ; OpcExp ; OpcExp ) Bloco
        # as duas alternativas podem comecar com ident: decide pelo 'in' depois dele
        if self.tokenLido[0] == TOKEN.ident and self.olhaSeguinte() == TOKEN.IN:
            self.consome(TOKEN.ident)
            self.consome(TOKEN.IN)
            self.consome(TOKEN.ident)
            self.consome(TOKEN.fechaPar)
            self.bloco()
        else:
            self.opcExp()
            self.consome(TOKEN.ptoVirg)
            self.opcExp()
            self.consome(TOKEN.ptoVirg)
            self.opcExp()
            self.consome(TOKEN.fechaPar)
            self.bloco()

    # comDecisao: if, seguido de zero ou mais elif e de um else opcional
    def comDecisao(self):
        # ComDecisao -> if ( Exp ) Bloco ListaElif ElseOpc
        self.consome(TOKEN.IF)
        self.consome(TOKEN.abrePar)
        self.exp()
        self.consome(TOKEN.fechaPar)
        self.bloco()
        self.listaElif()
        self.elseOpc()

    # listaElif: repete enquanto vier elif
    def listaElif(self):
        # ListaElif -> LAMBDA | elif ( Exp ) Bloco ListaElif
        if self.tokenLido[0] == TOKEN.ELIF:
            self.consome(TOKEN.ELIF)
            self.consome(TOKEN.abrePar)
            self.exp()
            self.consome(TOKEN.fechaPar)
            self.bloco()
            self.listaElif()
        else:
            pass

    # elseOpc: else opcional
    def elseOpc(self):
        # ElseOpc -> LAMBDA | else Bloco
        if self.tokenLido[0] == TOKEN.ELSE:
            self.consome(TOKEN.ELSE)
            self.bloco()
        else:
            pass

    # comIO: entrada e saida
    def comIO(self):
        # ComIO -> read ( ident ) ; | write ( ListaExp ) ;
        if self.tokenLido[0] == TOKEN.READ:
            self.consome(TOKEN.READ)
            self.consome(TOKEN.abrePar)
            self.consome(TOKEN.ident)
            self.consome(TOKEN.fechaPar)
            self.consome(TOKEN.ptoVirg)
        else:
            self.consome(TOKEN.WRITE)
            self.consome(TOKEN.abrePar)
            self.listaExp()
            self.consome(TOKEN.fechaPar)
            self.consome(TOKEN.ptoVirg)

    # listaExp: uma ou mais expressoes separadas por virgula, usada no write
    def listaExp(self):
        # ListaExp -> Exp RestoListaExp
        self.exp()
        self.restoListaExp()

    # restoListaExp: cada virgula traz mais uma expressao
    def restoListaExp(self):
        # RestoListaExp -> , Exp RestoListaExp | LAMBDA
        if self.tokenLido[0] == TOKEN.virgula:
            self.consome(TOKEN.virgula)
            self.exp()
            self.restoListaExp()
        else:
            pass

    # opcExp: expressao opcional, usada no return e nas partes do for;
    # a lista contem os tokens que podem iniciar uma expressao
    def opcExp(self):
        # OpcExp -> LAMBDA | Exp
        if self.tokenLido[0] in [TOKEN.increm, TOKEN.decrem, TOKEN.NOT,
                                 TOKEN.mais, TOKEN.menos, TOKEN.valorInt,
                                 TOKEN.valorFloat, TOKEN.valorString,
                                 TOKEN.abrePar, TOKEN.ident, TOKEN.abreCol,
                                 TOKEN.funcPrim]:
            self.exp()
        else:
            pass

    # ---------------- expressoes ----------------
    # a precedencia vem da ordem das chamadas: quanto mais fundo o metodo,
    # mais forte o operador
    # = -> ++ -- -> OR -> AND -> NOT -> relacionais -> + - -> * / div mod
    #   -> + - unarios -> folha

    # exp: nivel mais externo; trata a atribuicao
    def exp(self):
        # Exp -> Zero RestoExp
        self.zero()
        self.restoExp()

    # restoExp: cada = traz mais um valor. Ex.: a = b = 2
    def restoExp(self):
        # RestoExp -> = Zero RestoExp | LAMBDA
        if self.tokenLido[0] == TOKEN.atribuicao:
            self.consome(TOKEN.atribuicao)
            self.zero()
            self.restoExp()
        else:
            pass

    # zero: ++ ou -- prefixado, opcional. Ex.: ++i
    def zero(self):
        # Zero -> ++ Um | -- Um | Um
        if self.tokenLido[0] == TOKEN.increm:
            self.consome(TOKEN.increm)
            self.um()
        elif self.tokenLido[0] == TOKEN.decrem:
            self.consome(TOKEN.decrem)
            self.um()
        else:
            self.um()

    # um: expressao com OR
    def um(self):
        # Um -> Dois RestoUm
        self.dois()
        self.restoUm()

    # restoUm: cada OR traz mais um operando
    def restoUm(self):
        # RestoUm -> LAMBDA | OR Dois RestoUm
        if self.tokenLido[0] == TOKEN.OR:
            self.consome(TOKEN.OR)
            self.dois()
            self.restoUm()
        else:
            pass

    # dois: expressao com AND
    def dois(self):
        # Dois -> Tres RestoDois
        self.tres()
        self.restoDois()

    # restoDois: cada AND traz mais um operando
    def restoDois(self):
        # RestoDois -> LAMBDA | AND Tres RestoDois
        if self.tokenLido[0] == TOKEN.AND:
            self.consome(TOKEN.AND)
            self.tres()
            self.restoDois()
        else:
            pass

    # tres: NOT, que pode se repetir. Ex.: NOT NOT a
    def tres(self):
        # Tres -> NOT Tres | Quatro
        if self.tokenLido[0] == TOKEN.NOT:
            self.consome(TOKEN.NOT)
            self.tres()
        else:
            self.quatro()

    # quatro: comparacao entre dois valores
    def quatro(self):
        # Quatro -> Cinco Resto4
        self.cinco()
        self.resto4()

    # resto4: no maximo um operador relacional, sem repeticao (a < b < c e erro)
    def resto4(self):
        # Resto4 -> > Cinco | >= Cinco | < Cinco | <= Cinco
        # Resto4 -> == Cinco | != Cinco | LAMBDA
        # os seis operadores chegam do lexico como oprel; o lexema diz qual e
        if self.tokenLido[0] == TOKEN.oprel:
            self.consome(TOKEN.oprel)
            self.cinco()
        else:
            pass

    # cinco: soma e subtracao
    def cinco(self):
        # Cinco -> Seis RestoCinco
        self.seis()
        self.restoCinco()

    # restoCinco: cada + ou - traz mais um operando
    def restoCinco(self):
        # RestoCinco -> LAMBDA | + Seis RestoCinco | - Seis RestoCinco
        if self.tokenLido[0] == TOKEN.mais:
            self.consome(TOKEN.mais)
            self.seis()
            self.restoCinco()
        elif self.tokenLido[0] == TOKEN.menos:
            self.consome(TOKEN.menos)
            self.seis()
            self.restoCinco()
        else:
            pass

    # seis: multiplicacao e divisao
    def seis(self):
        # Seis -> Sete RestoSeis
        self.sete()
        self.restoSeis()

    # restoSeis: cada * / div mod traz mais um operando
    def restoSeis(self):
        # RestoSeis -> LAMBDA | * Sete RestoSeis | / Sete RestoSeis
        # RestoSeis -> div Sete RestoSeis | mod Sete RestoSeis
        if self.tokenLido[0] == TOKEN.multiplica:
            self.consome(TOKEN.multiplica)
            self.sete()
            self.restoSeis()
        elif self.tokenLido[0] == TOKEN.divide:
            self.consome(TOKEN.divide)
            self.sete()
            self.restoSeis()
        elif self.tokenLido[0] == TOKEN.DIV:
            self.consome(TOKEN.DIV)
            self.sete()
            self.restoSeis()
        elif self.tokenLido[0] == TOKEN.MOD:
            self.consome(TOKEN.MOD)
            self.sete()
            self.restoSeis()
        else:
            pass

    # sete: sinal na frente do valor. Ex.: -x
    def sete(self):
        # Sete -> + Sete | - Sete | Folha
        if self.tokenLido[0] == TOKEN.mais:
            self.consome(TOKEN.mais)
            self.sete()
        elif self.tokenLido[0] == TOKEN.menos:
            self.consome(TOKEN.menos)
            self.sete()
        else:
            self.folha()

    # folha: nivel mais fundo; o valor em si
    def folha(self):
        # Folha -> valorInt | valorFloat | valorString | ValorLista
        # Folha -> ( Zero )
        # Folha -> ident RestoFolha
        # Folha -> funcPrim ( ListaParam )
        if self.tokenLido[0] == TOKEN.valorInt:
            self.consome(TOKEN.valorInt)
        elif self.tokenLido[0] == TOKEN.valorFloat:
            self.consome(TOKEN.valorFloat)
        elif self.tokenLido[0] == TOKEN.valorString:
            self.consome(TOKEN.valorString)
        elif self.tokenLido[0] == TOKEN.abreCol:
            self.valorLista()
        elif self.tokenLido[0] == TOKEN.abrePar:
            self.consome(TOKEN.abrePar)
            self.zero()
            self.consome(TOKEN.fechaPar)
        elif self.tokenLido[0] == TOKEN.ident:
            self.consome(TOKEN.ident)
            self.restoFolha()
        elif self.tokenLido[0] == TOKEN.funcPrim:
            self.consome(TOKEN.funcPrim)
            self.consome(TOKEN.abrePar)
            self.listaParam()
            self.consome(TOKEN.fechaPar)
        else:
            self.erro("uma expressao")

    # restoFolha: o que vem depois de um ident: nada (a), posicao (a[0]) ou
    # chamada de funcao (a(1, 2))
    def restoFolha(self):
        # RestoFolha -> LAMBDA | [ Zero ] | ( ListaParam )
        if self.tokenLido[0] == TOKEN.abreCol:
            self.consome(TOKEN.abreCol)
            self.zero()
            self.consome(TOKEN.fechaCol)
        elif self.tokenLido[0] == TOKEN.abrePar:
            self.consome(TOKEN.abrePar)
            self.listaParam()
            self.consome(TOKEN.fechaPar)
        else:
            pass

    # listaParam: valores de uma chamada ou de uma lista; pode ser vazia;
    # a lista contem os tokens que podem iniciar um parametro
    def listaParam(self):
        # ListaParam -> LAMBDA | Param RestoListaParam
        if self.tokenLido[0] in [TOKEN.increm, TOKEN.decrem, TOKEN.NOT,
                                 TOKEN.mais, TOKEN.menos, TOKEN.valorInt,
                                 TOKEN.valorFloat, TOKEN.valorString,
                                 TOKEN.abrePar, TOKEN.ident, TOKEN.abreCol,
                                 TOKEN.funcPrim]:
            self.param()
            self.restoListaParam()
        else:
            pass

    # restoListaParam: cada virgula traz mais um parametro
    def restoListaParam(self):
        # RestoListaParam -> , Param RestoListaParam | LAMBDA
        if self.tokenLido[0] == TOKEN.virgula:
            self.consome(TOKEN.virgula)
            self.param()
            self.restoListaParam()
        else:
            pass

    # param: um valor passado; sem = (atribuicao nao vale aqui)
    def param(self):
        # Param -> Zero
        self.zero()

    # valorLista: lista literal. Ex.: [1, 2, 3] ou []
    def valorLista(self):
        # ValorLista -> [ ListaParam ]
        self.consome(TOKEN.abreCol)
        self.listaParam()
        self.consome(TOKEN.fechaCol)


# rodando este arquivo direto, so mostra como usar
# inicia a traducao
if __name__ == "__main__":
    print("Para testar, chame o Tradutor")
