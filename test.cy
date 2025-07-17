# Programa exemplo na linguagem Cython (mix C + Python)
# Lê 10 inteiros e os imprime em ordem crescente

# detalhes da linguagem:
# ----> todas as listas iniciam em 1
# ----> declaracoes só podem aparecer no inicio das funcoes, nao no meio
# ----> parametros de funcoes sempre sao passados por valor (nunca por referencia)

[int] sort([int] lista) {
   int i, j, chave;
   int tam = 0;

   foreach elemento = lista : {
       tam = tam + 1;
   }

   for (i = 2; i <= tam; i = i + 1) {
      chave = lista[i];
      j = i - 1;
      while (j >= 1 and lista[j] > chave) {
         lista[j+1] = lista[j];
         j = j - 1;
      }
      lista[j+1] = chave;
   }
   return lista;
}

void main() {
   [int] ordenada;

   [int] lista = [ ];
   int i, aux;
   for (i = 1; i <= 10; i = i + 1) {
      write("Forneça o ", i, "º inteiro: ");
      read(aux);
      lista = lista + [aux];
   }

   ordenada = sort(lista);

   write("\nLista ordenada:\n");
   for (i = 1; i <= 10; i = i + 1) {
      write(i, "º: ", ordenada[i], "\n");
   }

   return;
}
