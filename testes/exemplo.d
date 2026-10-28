// programa valido em D que exercita todas as construcoes da gramatica

int soma(int a, int &b, float c[], string &d[]) {
    int i = 0, total[];
    float media = 0.5;
    string nome;
    int x, y[], z;

    total = [1, 2, 3];
    x = y[0] = z = 10;
    nome = "resultado: \"parcial\"";

    while (i < 3) {
        total[i] = total[i] + a * 2 - b / 2;
        i = i + 1;
        if (i >= 2 AND i != 3) {
            media = media + 1.75;
        } elif (i <= 0 OR NOT i == 0) {
            continue;
        } elif ((i + 1) * 2 > 7) {
            i = -i;
        } else {
            break;
        }
    }

    for (i in total) {
        write(i, " ", nome);
    }

    for (i = 0; i > 5; ++i) {
        --i;
        media = media * 7 div 2 mod 3;
    }

    for (;;) {
        break;
    }

    loop {
        read(nome);
        break;
    }

    {
        int local = soma(a, b, c, d);
        write(local);
    }

    total = [];
    total = [x, y[1], soma(1, 2, [0.5], ["s"]), - + x];
    return a;
}

void main() {
    write("fim");
    return;
}
