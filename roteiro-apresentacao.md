# Roteiro da apresentação: analisador léxico e sintático da linguagem D

Ordem: visão geral → léxico → sintático → demonstração → perguntas.
Tudo é apresentado pela pasta `analisador-sintatico`, que já contém o léxico (`lexico.py` e `ttoken.py`).
As falas estão entre aspas. O que está em **Mostrar** é o que abrir na tela.

---

## 1. Visão geral

> "Nosso compilador para a linguagem D está dividido em fases. Até aqui fizemos duas: o
> léxico, que transforma o texto do programa em tokens, e o sintático, que confere se esses
> tokens seguem a gramática da linguagem."

> "Um exemplo: em `a = 1;`, o léxico enxerga quatro tokens: `ident`, `=`, `valorInt` e `;`.
> O sintático verifica se essa sequência forma um comando válido."

---

## 2. Trabalho 1: analisador léxico

### `ttoken.py`
**Mostrar:** a classe `TOKEN`.

> "Aqui está a lista de todos os tokens da linguagem, cada um com um número."

> "`msg` traduz o token para um nome legível, usado nas mensagens."

> "`reservada` recebe uma palavra e decide se ela é palavra reservada, função primitiva ou
> identificador. A comparação é exata porque a linguagem é case sensitive: `while` é reservada
> e `While` é identificador."

### `lexico.py`
**Mostrar:** `getchar` e `ungetchar`.

> "`getchar` lê um caractere e atualiza a linha e a coluna, que usamos nas mensagens de erro.
> `ungetchar` devolve um caractere lido a mais. Ele é necessário porque só sabemos que um
> token acabou ao ler o caractere seguinte: em `abc;`, o identificador termina quando lemos
> o `;`, e esse `;` precisa ser lido de novo."

> "O fim de arquivo é representado por `\0`, que não veio do fonte. Por isso `ungetchar` não
> o devolve. Se devolvesse, o último caractere seria lido duas vezes."

**Mostrar:** `getToken`.

> "`getToken` é a função principal. Cada chamada devolve um token, na forma de uma tupla com o
> tipo, o lexema, a linha e a coluna."

> "Ela começa descartando espaços e comentários. Uma `/` pode ser divisão ou comentário, então
> olhamos o próximo caractere para decidir."

> "Depois vem o autômato. O estado 1 olha o primeiro caractere e escolhe o caminho."

| Estado | O que reconhece |
|---|---|
| 1 | início; símbolos de um caractere já retornam aqui |
| 2 | identificador, palavra reservada ou função primitiva |
| 3 | parte inteira do número |
| 31 | exige um dígito depois do ponto |
| 32 | parte fracionária do número |
| 33 | erro: número seguido de letra, como `12abc` |
| 4 | string, incluindo `\"` |
| 5, 6, 7, 8 | `<` `<=`, `>` `>=`, `=` `==`, `!=` |
| 9, 10 | `+` `++`, `-` `--` |

> "Quando encontra um erro léxico, o programa imprime o token de erro, com linha e coluna, e
> para. O sintático faz o mesmo: para no primeiro erro."

### Vendo os tokens
**Mostrar:** `testaLexico`, em `sintatico.py`.

> "Para ver só o trabalho do léxico, usamos o `testaLexico`, que pede um token por vez e imprime
> cada um, até o `<eof>` ou o primeiro erro, sem analisar a gramática."

---

## 3. Trabalho 2: analisador sintático

### A ideia
> "É um parser descendente recursivo: cada não-terminal da gramática virou um método, com a
> produção escrita no comentário logo acima. Quando a produção cita outro não-terminal, o
> método o chama; quando cita um terminal, chama `consome`."

**Mostrar:** `func` (a produção está no comentário).

> "`Func -> TipoFunc ident ( ListaArgs ) Corpo` vira exatamente essa sequência de chamadas."

### As peças centrais
**Mostrar:** `traduz`, `consome` e `erro`.

> "`traduz` lê o primeiro token, analisa o programa e exige `eof` no final, para garantir que
> não sobrou nada depois da última função."

> "`consome` compara o token atual com o esperado. Se forem iguais, avança. Se não, chama
> `erro`, que mostra linha, coluna, o que era esperado e o que veio, e para na primeira falha."

### Decidindo o caminho
**Mostrar:** `listaCom` e `com`.

> "Para escolher a produção, olhamos só o token atual. A lista em `listaCom` tem os tokens que
> podem iniciar um comando. Se o token não está nela, os comandos acabaram: é a produção
> LAMBDA."

### Precedência
**Mostrar:** de `exp` até `folha`.

> "A precedência vem da ordem das chamadas: quanto mais fundo o método, mais forte o operador.
> Por isso `a + b * c` multiplica antes de somar."

| Método | Operadores |
|---|---|
| `exp` / `restoExp` | `=` |
| `zero` | `++` `--` prefixados |
| `um` / `restoUm` | `OR` |
| `dois` / `restoDois` | `AND` |
| `tres` | `NOT` |
| `quatro` / `resto4` | `>` `>=` `<` `<=` `==` `!=` |
| `cinco` / `restoCinco` | `+` `-` |
| `seis` / `restoSeis` | `*` `/` `div` `mod` |
| `sete` | `+` `-` de sinal |
| `folha` | valores, parênteses, identificadores, chamadas |

### Problemas que encontramos na gramática
> "O enunciado avisou para esperar problemas, e encontramos alguns. Estes foram os que
> precisamos tratar:"

| Problema | O que fizemos |
|---|---|
| `RestoExp -> = Zero RestoExp \| Zero` não tem LAMBDA: `a = 1;` seria inválido e `a b;` válido | `RestoExp -> = Zero RestoExp \| LAMBDA` |
| `OpcExp -> LAMBDA \| Zero` não aceita `=`, o que invalida `for (i = 0; ...)` | `OpcExp -> LAMBDA \| Exp` |
| No `for`, as duas alternativas podem começar com `ident` | `olhaSeguinte` espia o próximo token: se for `in`, é o `for-in` |
| `write ( ListaExp );` trata `);` como um só terminal | `)` e `;` são consumidos separados |
| `OpcPos` não é usado por nenhuma regra | não foi implementado |
| Funções primitivas não aparecem na gramática | `Folha -> funcPrim ( ListaParam )`, regra acrescentada por nós |

---

## 4. Perguntas prováveis

**Os dois `for` passam?**
"Sim. O `for-in` e o `for` de três partes passam. As duas formas podem começar com `ident`, então
`olhaSeguinte` espia o token seguinte: se for `in`, é o `for-in`; se não, é o de três partes."

**O `for` funciona sem o `i = 0`?**
"Sim. As três expressões são opcionais, então `for (; i > 5; ++i)` e `for (;;)` são válidos. Os
dois `;` é que são obrigatórios."

**O analisador para ou continua depois de um erro?**
"Para no primeiro erro, tanto no léxico quanto no sintático."

**Por que `oprel` é um token só?**
"Os seis operadores levam ao mesmo próximo passo, `Cinco`. O lexema guarda qual deles é."

**O que é LAMBDA no código?**
"É a produção vazia: o `else: pass`, que não consome nada."

**Por que `eLetra` em vez de `isalpha()`?**
"`isalpha()` aceita letras acentuadas, que não fazem parte da linguagem."

**`1 = 2;` passa?**
"Passa, porque a gramática não restringe o lado esquerdo do `=`. Verificar se ele é atribuível
é trabalho da análise semântica."

**`int x, y = 2;` passa?**
"Não. Pela gramática, só a primeira variável da declaração pode ser inicializada."

**`a < b < c` passa?**
"Não. `Resto4` aceita só um operador relacional e não é recursivo."

**`i++` passa?**
"Não. A gramática só tem `++` e `--` prefixados, então o certo é `++i`."

**Por que declarar depois de um comando dá erro?**
"`Corpo` exige `ListaDeclar` antes de `ListaCom`. Dentro de um bloco novo, pode declarar de novo."

**O parser tem alguma limitação?**
"Como os `Resto*` e as listas são recursivos, um corpo com cerca de mil comandos ou mais estoura
o limite de recursão do Python. Nesse caso, ele mostra `Execucao interrompida` com o motivo."

**A gramática foi seguida à risca?**
"Fora as correções da tabela acima, sim. Sem elas, programas normais como `a = 1;` seriam
rejeitados."

---

## 5. Como rodar na hora

**Python não precisa ser compilado.** É só executar com o interpretador. Se o professor pedir
para "compilar", explique isso e rode o comando direto.

Abra só a pasta `analisador-sintatico`. Os comandos abaixo também estão no topo de cada `.py`.

### Preparação
```
cd ~/DEV/Compiladores/compilador-d/analisador-sintatico
python3 --version
```

No Windows, use `python` ou `py` no lugar de `python3` em todos os comandos.

### Sintático
```
python3 main.py testes/exemplo.d
```

Resultado esperado:
```
Programa sintaticamente correto.
```

### Léxico: listar os tokens
```
python3 -c "from lexico import Lexico; from sintatico import Sintatico; Sintatico(Lexico(open('testes/exemplo.d', encoding='utf-8'))).testaLexico()"
```

A primeira linha é `(tk=int lex="int" lin=3 col=1)` e a última é
`(tk=<eof> lex="<eof>" lin=61 col=0)`.

### Léxico: parar no primeiro erro
```
python3 -c "from lexico import Lexico; from sintatico import Sintatico; Sintatico(Lexico(open('testes/erros.d', encoding='utf-8'))).testaLexico()"
```

A última linha é `(tk=erro lex="12abc" lin=3 col=9)`. O `erros.d` tem erros de propósito.

Pelo parser, o mesmo arquivo dá:
```
python3 main.py testes/erros.d
```
```
Erro na linha 3, coluna 9
Erro lexico: token invalido "12abc"
```

### Mostrando um erro ao vivo
Faça uma mudança por vez em `testes/exemplo.d`, salve e rode `python3 main.py testes/exemplo.d`.
Depois desfaça com `Cmd+Z`, salve e rode de novo. Se perder o original, restaure o arquivo com
`git restore testes/exemplo.d`.

| Mudança | Resultado |
|---|---|
| Linha 11: apagar o `;` do fim | `Erro na linha 12, coluna 5` / `Era esperado ; mas veio ident` |
| Linha 9: trocar o `=` por `@` | `Erro na linha 9, coluna 11` / `Erro lexico: token invalido "@"` |
| Linha 33: `for (i = 0 i > 5; ++i) {` | `Erro na linha 33, coluna 16` / `Era esperado ; mas veio ident` |

> "O `;` faltou na linha 11, mas o parser só percebe ao ler o próximo token, que está na linha 12."

> "O `@` não pertence à linguagem, então o erro é léxico. No caso do `;`, os tokens são válidos,
> mas a ordem está errada, por isso o erro é sintático."

### Os dois `for`
Estão no `exemplo.d`: `for-in` na linha 29 e o de três partes na linha 33. No código, a decisão
está em `restoComRepete` e `olhaSeguinte`.

A linha 33 original é `for (i = 0; i > 5; ++i) {`. Para testar, altere-a, salve e rode
`python3 main.py testes/exemplo.d`:

| Linha 33 | Resultado |
|---|---|
| `for (; i > 5; ++i) {` | `Programa sintaticamente correto.` |
| `for (i > 5; ++i) {` | `Erro na linha 33, coluna 20` / `Era esperado ; mas veio )` |

> "As três expressões do `for` são opcionais, mas os dois `;` são obrigatórios."

### Se o professor quiser testar um programa dele
```
python3 main.py caminho/do/arquivo.d
```

### Se der errado
| Mensagem | Causa | Solução |
|---|---|---|
| `No such file or directory` | pasta atual ou caminho errado | confira o `cd` e o caminho do arquivo |
| `command not found: python3` | outro nome no sistema | use `python` ou `py` |
| `ModuleNotFoundError` | rodou de outro lugar ou faltam arquivos | rode dentro da pasta, com todos os `.py` juntos |
