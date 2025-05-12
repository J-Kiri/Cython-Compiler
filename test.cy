# Programa exemplo na nossa linguagem Cython (mix C + Python)
# leia 10 inteiros e os imprima em ordem crescente

void main() {
   [int] lista = [ ];
   int i, aux;
   for (i=1; i<=10; i=i+1) {
      write("Forneca o ", i, "o inteiro: ");
      read(aux);
      lista = lista + [aux];
   }
   ordenada = sort(lista);
   write("\n Lista ordenada:\n");
   for (i=1; i<=10; i=i+1)
      write(i, "o: ", lista[i], "\n");
   return;
}

[int] sort([int] lista) {
   [int] ordenada = [];
   int tam = 0;
   int x, i;
   foreach x = lista : {
      ordenada = [x] + ordenada;
      tam = tam + 1;
      i = 1;
      while (i < tam) {
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