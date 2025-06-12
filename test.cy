# Programa exemplo na nossa linguagem Cython (mix C + Python)
# leia 10 inteiros e os imprima em ordem crescente

[int] sort([int] lista) {
   [int] ordenada = [];
   int tam = 0;
   int x, i;
   int aux;
   foreach x = lista : {
      ordenada = [x] + ordenada;
      tam = tam + 1;
      i = 0;
      while (i < tam-1) {
          if (ordenada[i] > ordenada[i+1]) {
             aux = ordenada[i+1];
             ordenada[i+1] = ordenada[i];
             ordenada[i] = aux;
             i = i + 1;
          } else break;
      }
   }
   return ordenada;
}

void main() {
   [int] lista = [ ];
   [int] ordenada = [];
   int i, aux;
   for (i=1; i<=10; i=i+1) {
      write("Forneca o ", i, "o inteiro: ");
      read(aux);
      lista = lista + [aux];
   }
   ordenada = sort(lista);
   write("\n Lista ordenada:\n");
   for (i=0; i<10; i=i+1)
      write(i+1, "o: ", ordenada[i], "\n");
   return;
}