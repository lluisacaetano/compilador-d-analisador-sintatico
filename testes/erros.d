// fonte com erros lexicos propositais, para testar as mensagens de erro
int f() {
    a = 12abc;      // digito seguido de letra
    b = 10.;        // float sem parte fracionaria
    c = 1.5x;       // float seguido de letra
    d = !e;         // ! sozinho (a negacao e NOT)
    g = "sem fechar aspas
    h = @;          // caractere que nao pertence a linguagem
    i = _nome;      // identificador nao pode comecar com sublinha
}
