void main() {
    [int] lista = [1, 2, 3, 4, 5];
    int i = 1;  # Inicializado com valor
    int j = 4;  # Inicializado com valor

    # Acessos normais
    int a = lista[i];
    int b = lista[i + 1];

    # Slicing
    [int] fatia1 = lista[i:j];
    [int] fatia2 = lista[:j];
    [int] fatia3 = lista[i:];
    [int] fatia4 = lista[:];

    # ... resto do código
}