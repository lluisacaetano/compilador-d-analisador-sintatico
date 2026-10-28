# ---------------------------------------------------
# Tradutor para a linguagem D
# ---------------------------------------------------
from lexico import TOKEN, Lexico


class Sintatico:

    def __init__(self, lexico):
        self.lexico = lexico
        self.tokenSeguinte = None   # usado so no for, para olhar um token a frente

    def traduz(self):
        self.tokenLido = self.lexico.getToken()
        try:
            self.prog()
            self.consome(TOKEN.eof)
            print("Programa sintaticamente correto.")
        except:
            pass

    def proximoToken(self):
        if self.tokenSeguinte is not None:
            token = self.tokenSeguinte
            self.tokenSeguinte = None
            return token
        return self.lexico.getToken()

    def olhaSeguinte(self):
        # token que vem depois do tokenLido, sem consumir
        if self.tokenSeguinte is None:
            self.tokenSeguinte = self.lexico.getToken()
        return self.tokenSeguinte[0]

    def consome(self, tokenAtual):
        (token, lexema, linha, coluna) = self.tokenLido
        if tokenAtual == token:
            self.tokenLido = self.proximoToken()
        else:
            msgTokenAtual = TOKEN.msg(tokenAtual)
            self.erro(msgTokenAtual)

    def erro(self, esperado):
        (token, lexema, linha, coluna) = self.tokenLido
        msgTokenLido = TOKEN.msg(token)
        print(f"Erro na linha {linha}, coluna {coluna}")
        if token == TOKEN.erro:
            print(f'Erro lexico: token invalido "{lexema}"')
        else:
            print(f"Era esperado {esperado} mas veio {msgTokenLido}")
        raise Exception

    def testaLexico(self):
        self.tokenLido = self.lexico.getToken()
        (token, lexema, linha, coluna) = self.tokenLido
        while token != TOKEN.eof:
            self.lexico.imprimeToken(self.tokenLido)
            self.tokenLido = self.lexico.getToken()
            (token, lexema, linha, coluna) = self.tokenLido

    # --------------------------------- gramática -------------------------------------
    def prog(self):
        # Prog -> Func RestoProg
        self.func()
        self.restoProg()

    def restoProg(self):
        # RestoProg -> LAMBDA | Func RestoProg
        if self.tokenLido[0] in [TOKEN.VOID, TOKEN.INT, TOKEN.FLOAT, TOKEN.STRING]:
            self.func()
            self.restoProg()
        else:
            pass

    def func(self):
        # Func -> TipoFunc ident ( ListaArgs ) Corpo
        self.tipoFunc()
        self.consome(TOKEN.ident)
        self.consome(TOKEN.abrePar)
        self.listaArgs()
        self.consome(TOKEN.fechaPar)
        self.corpo()

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

    def tipoFunc(self):
        # TipoFunc -> void | TipoPrim
        if self.tokenLido[0] == TOKEN.VOID:
            self.consome(TOKEN.VOID)
        elif self.tokenLido[0] in [TOKEN.INT, TOKEN.FLOAT, TOKEN.STRING]:
            self.tipoPrim()
        else:
            self.erro("void, int, float ou string")

    def listaArgs(self):
        # ListaArgs -> LAMBDA | Arg RestoListaArgs
        if self.tokenLido[0] in [TOKEN.INT, TOKEN.FLOAT, TOKEN.STRING]:
            self.arg()
            self.restoListaArgs()
        else:
            pass

    def restoListaArgs(self):
        # RestoListaArgs -> , Arg RestoListaArgs | LAMBDA
        if self.tokenLido[0] == TOKEN.virgula:
            self.consome(TOKEN.virgula)
            self.arg()
            self.restoListaArgs()
        else:
            pass

    def arg(self):
        # Arg -> TipoPrim OpcRef ident OpcColchete
        self.tipoPrim()
        self.opcRef()
        self.consome(TOKEN.ident)
        self.opcColchete()

    def opcRef(self):
        # OpcRef -> LAMBDA | &
        if self.tokenLido[0] == TOKEN.endereco:
            self.consome(TOKEN.endereco)
        else:
            pass

    def opcColchete(self):
        # OpcColchete -> LAMBDA | [ ]
        if self.tokenLido[0] == TOKEN.abreCol:
            self.consome(TOKEN.abreCol)
            self.consome(TOKEN.fechaCol)
        else:
            pass

    def corpo(self):
        # Corpo -> { ListaDeclar ListaCom }
        self.consome(TOKEN.abreChave)
        self.listaDeclar()
        self.listaCom()
        self.consome(TOKEN.fechaChave)

    def listaDeclar(self):
        # ListaDeclar -> LAMBDA | Declar ListaDeclar
        if self.tokenLido[0] in [TOKEN.INT, TOKEN.FLOAT, TOKEN.STRING]:
            self.declar()
            self.listaDeclar()
        else:
            pass

    def declar(self):
        # Declar -> TipoPrim ident OpcColchete OpcInicializa Listaident ;
        self.tipoPrim()
        self.consome(TOKEN.ident)
        self.opcColchete()
        self.opcInicializa()
        self.listaIdent()
        self.consome(TOKEN.ptoVirg)

    def listaIdent(self):
        # Listaident -> LAMBDA | , ident OpcColchete Listaident
        if self.tokenLido[0] == TOKEN.virgula:
            self.consome(TOKEN.virgula)
            self.consome(TOKEN.ident)
            self.opcColchete()
            self.listaIdent()
        else:
            pass

    def opcInicializa(self):
        # OpcInicializa -> LAMBDA | = Exp
        if self.tokenLido[0] == TOKEN.atribuicao:
            self.consome(TOKEN.atribuicao)
            self.exp()
        else:
            pass

    def listaCom(self):
        # ListaCom -> LAMBDA | Com ListaCom
        if self.tokenLido[0] in [TOKEN.LOOP, TOKEN.WHILE, TOKEN.FOR, TOKEN.IF,
                                 TOKEN.READ, TOKEN.WRITE, TOKEN.BREAK,
                                 TOKEN.CONTINUE, TOKEN.RETURN, TOKEN.abreChave,
                                 TOKEN.increm, TOKEN.decrem, TOKEN.NOT,
                                 TOKEN.mais, TOKEN.menos, TOKEN.valorInt,
                                 TOKEN.valorFloat, TOKEN.valorString,
                                 TOKEN.abrePar, TOKEN.ident, TOKEN.abreCol]:
            self.com()
            self.listaCom()
        else:
            pass

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
            self.exp()
            self.consome(TOKEN.ptoVirg)

    def bloco(self):
        # Bloco -> Corpo
        self.corpo()

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

    def comDecisao(self):
        # ComDecisao -> if ( Exp ) Bloco ListaElif ElseOpc
        self.consome(TOKEN.IF)
        self.consome(TOKEN.abrePar)
        self.exp()
        self.consome(TOKEN.fechaPar)
        self.bloco()
        self.listaElif()
        self.elseOpc()

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

    def elseOpc(self):
        # ElseOpc -> LAMBDA | else Bloco
        if self.tokenLido[0] == TOKEN.ELSE:
            self.consome(TOKEN.ELSE)
            self.bloco()
        else:
            pass

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

    def listaExp(self):
        # ListaExp -> Exp RestoListaExp
        self.exp()
        self.restoListaExp()

    def restoListaExp(self):
        # RestoListaExp -> , Exp RestoListaExp | LAMBDA
        if self.tokenLido[0] == TOKEN.virgula:
            self.consome(TOKEN.virgula)
            self.exp()
            self.restoListaExp()
        else:
            pass

    def opcExp(self):
        # OpcExp -> LAMBDA | Exp
        if self.tokenLido[0] in [TOKEN.increm, TOKEN.decrem, TOKEN.NOT,
                                 TOKEN.mais, TOKEN.menos, TOKEN.valorInt,
                                 TOKEN.valorFloat, TOKEN.valorString,
                                 TOKEN.abrePar, TOKEN.ident, TOKEN.abreCol]:
            self.exp()
        else:
            pass

    def exp(self):
        # Exp -> Zero RestoExp
        self.zero()
        self.restoExp()

    def restoExp(self):
        # RestoExp -> = Zero RestoExp | LAMBDA
        if self.tokenLido[0] == TOKEN.atribuicao:
            self.consome(TOKEN.atribuicao)
            self.zero()
            self.restoExp()
        else:
            pass

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

    def um(self):
        # Um -> Dois RestoUm
        self.dois()
        self.restoUm()

    def restoUm(self):
        # RestoUm -> LAMBDA | OR Dois RestoUm
        if self.tokenLido[0] == TOKEN.OR:
            self.consome(TOKEN.OR)
            self.dois()
            self.restoUm()
        else:
            pass

    def dois(self):
        # Dois -> Tres RestoDois
        self.tres()
        self.restoDois()

    def restoDois(self):
        # RestoDois -> LAMBDA | AND Tres RestoDois
        if self.tokenLido[0] == TOKEN.AND:
            self.consome(TOKEN.AND)
            self.tres()
            self.restoDois()
        else:
            pass

    def tres(self):
        # Tres -> NOT Tres | Quatro
        if self.tokenLido[0] == TOKEN.NOT:
            self.consome(TOKEN.NOT)
            self.tres()
        else:
            self.quatro()

    def quatro(self):
        # Quatro -> Cinco Resto4
        self.cinco()
        self.resto4()

    def resto4(self):
        # Resto4 -> > Cinco | >= Cinco | < Cinco | <= Cinco
        # Resto4 -> == Cinco | != Cinco | LAMBDA
        # os seis operadores chegam do lexico como oprel; o lexema diz qual e
        if self.tokenLido[0] == TOKEN.oprel:
            self.consome(TOKEN.oprel)
            self.cinco()
        else:
            pass

    def cinco(self):
        # Cinco -> Seis RestoCinco
        self.seis()
        self.restoCinco()

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

    def seis(self):
        # Seis -> Sete RestoSeis
        self.sete()
        self.restoSeis()

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

    def folha(self):
        # Folha -> valorInt | valorFloat | valorString | ValorLista
        # Folha -> ( Zero )
        # Folha -> ident RestoFolha
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
        else:
            self.erro("uma expressao")

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

    def listaParam(self):
        # ListaParam -> LAMBDA | Param RestoListaParam
        if self.tokenLido[0] in [TOKEN.increm, TOKEN.decrem, TOKEN.NOT,
                                 TOKEN.mais, TOKEN.menos, TOKEN.valorInt,
                                 TOKEN.valorFloat, TOKEN.valorString,
                                 TOKEN.abrePar, TOKEN.ident, TOKEN.abreCol]:
            self.param()
            self.restoListaParam()
        else:
            pass

    def restoListaParam(self):
        # RestoListaParam -> , Param RestoListaParam | LAMBDA
        if self.tokenLido[0] == TOKEN.virgula:
            self.consome(TOKEN.virgula)
            self.param()
            self.restoListaParam()
        else:
            pass

    def param(self):
        # Param -> Zero
        self.zero()

    def valorLista(self):
        # ValorLista -> [ ListaParam ]
        self.consome(TOKEN.abreCol)
        self.listaParam()
        self.consome(TOKEN.fechaCol)


# inicia a traducao
if __name__ == "__main__":
    print("Para testar, chame o Tradutor")
