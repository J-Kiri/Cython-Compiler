void main() {
    [int] lista = [1, 2, 3, 4, 5];
    int i, j;
    int a, b, c, d, e;

    i = 1;
    j = 4;

    a = lista[i];         # lista[1] → 2
    b = lista[i + 1];     # lista[2] → 3

    [int] fatia1 = lista[i:j];    # lista[1:4] → [2, 3, 4]
    [int] fatia2 = lista[:j];     # lista[:4] → [1, 2, 3, 4]
    [int] fatia3 = lista[i:];     # lista[1:] → [2, 3, 4, 5]
    [int] fatia4 = lista[:];      # lista[:] → [1, 2, 3, 4, 5]

    write("a = ", a);
    write("b = ", b);
    write("fatia1 = ", fatia1);
    write("fatia2 = ", fatia2);
    write("fatia3 = ", fatia3);
    write("fatia4 = ", fatia4);

    return;
}
