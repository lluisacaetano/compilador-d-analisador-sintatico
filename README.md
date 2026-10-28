# Analisador sintático da linguagem D

Luisa Caetano Araujo e Eduarda Helena Lamounier

Fase 2 do compilador: lê um arquivo `.d` e diz se ele está sintaticamente correto. No
primeiro erro, informa a linha, a coluna, o que era esperado e o que veio, e para.
Parser descendente recursivo preditivo: um método por não-terminal, com a produção em
comentário.

## Arquivos

- `sintatico.py` — classe `Sintatico`; `traduz()` analisa o programa e imprime
  "Programa sintaticamente correto." ou o primeiro erro.
- `lexico.py`, `ttoken.py` — analisador léxico da fase 1.
- `main.py` — programa principal: abre o arquivo `.d`, cria o léxico e chama o
  analisador sintático.
- `testes/exemplo.d` — programa válido que usa todas as construções da gramática.

## Rodar

```
python3 main.py testes/exemplo.d
python3 main.py                          # sem argumento: usa testes/exemplo.d
python3 main.py <arquivo.d>
```

Saídas possíveis:

```
Programa sintaticamente correto.
```

```
Erro na linha 4, coluna 5
Era esperado ; mas veio ident
```

```
Erro na linha 3, coluna 11
Erro lexico: token invalido "@"
```

## Problemas encontrados na gramática e como foram tratados

1. **`RestoExp → = Zero RestoExp | Zero` não tem `LAMBDA`.** Com isso toda expressão
   exigiria dois `Zero`: `x;` e `a = 1;` seriam inválidos e `a b;` seria válido. Também
   deixa a gramática fora de LL(1): nos conjuntos PREDICT, `RestoFolha → λ` e
   `RestoFolha → ( ListaParam )` têm `(`, e `RestoCinco → λ` tem `+` e `-`, os mesmos de
   `RestoCinco → + …` e `RestoCinco → - …`.
   **Correção:** `RestoExp → = Zero RestoExp | LAMBDA`.
2. **`OpcExp → LAMBDA | Zero`** não aceita `=`, então `for (i = 0; i < 5; i = i + 1)` e
   `return a = 1;` seriam inválidos. **Correção:** `OpcExp → LAMBDA | Exp`.
3. **`for`:** os PREDICT de `RestoComRepete → ident in ident ) Bloco` e de
   `RestoComRepete → OpcExp ; OpcExp ; OpcExp ) Bloco` têm `ident` em comum.
   **Tratamento:** quando o token é `ident`, o parser olha o token seguinte; se for `in`,
   é o `for-in`, senão é o `for` com três expressões.
4. **`write ( ListaExp );`** — `)` e `;` são dois tokens: `write ( ListaExp ) ;`.
5. **`OpcPos → LAMBDA | [ Exp ]`** não é usado por nenhuma regra; não foi implementado.
6. **Funções primitivas** (`str2int`, `str2float`, `int2str`, `float2string`): o léxico
   as reconhece como `funcPrim`, mas a gramática não tem regra para elas. O parser segue
   a gramática, então `a = str2int(s);` dá erro sintático.
7. Nada restringe o lado esquerdo do `=`, então `1 = 2;` passa na análise sintática.
   Verificar se o lado esquerdo é atribuível fica para a análise semântica.
8. Só a **primeira** variável de uma declaração aceita inicialização (`int x = 1, y;` é
   válido; `int x, y = 2;` não é). Mantido como está na gramática.
9. **`Resto4 → > Cinco | >= Cinco | …`**: os seis operadores relacionais chegam do léxico
   como um único token, `oprel`; o lexema diz qual é. Como todos levam a `Cinco`, o
   parser trata os seis numa única alternativa.
10. **Tabela de PREDICT do PDF com `[` e `]` faltando:** as produções 18
    (`OpcColchete → [ ]`), 93 (`Folha → ValorLista`), 97 (`RestoFolha → [ Zero ]`), 104
    (`ValorLista → [ ListaParam ]`), 105 e 106 (`OpcPos`) estão com o PREDICT em branco, e o
    de `OpcInicializa → λ` aparece como `,,` em vez de `,` e `;`. O parser foi feito a
    partir da gramática, com os conjuntos corrigidos (por exemplo, `[` inicia `ValorLista`
    e `RestoFolha → [ Zero ]`).
