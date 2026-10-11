#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "merge.h"

void merge_nomes(Candidato *arr, Candidato *aux, int inicio, int meio, int fim) {
    int i = inicio;
    int j = meio + 1;
    int k = inicio;

    while (i <= meio && j <= fim) {
        if (strcmp(arr[i].nome, arr[j].nome) <= 0) {
            aux[k++] = arr[i++];
        } else {
            aux[k++] = arr[j++];
        }
    }

    while (i <= meio) {
        aux[k++] = arr[i++];
    }

    while (j <= fim) {
        aux[k++] = arr[j++];
    }

    for (i = inicio; i <= fim; i++) {
        arr[i] = aux[i];
    }
}

void merge_sort_nomes_recursivo(Candidato *arr, Candidato *aux, int inicio, int fim) {
    if (inicio < fim) {
        int meio = inicio + (fim - inicio) / 2;

        merge_sort_nomes_recursivo(arr, aux, inicio, meio);
        merge_sort_nomes_recursivo(arr, aux, meio + 1, fim);

        merge_nomes(arr, aux, inicio, meio, fim);
    }
}

void merge_sort_nomes(Candidato *arr, int n) {
    if (n <= 1) return;

    Candidato *aux = (Candidato *)malloc(n * sizeof(Candidato));
    if (aux == NULL) {
        fprintf(stderr, "Erro ao alocar memoria auxiliar para o Merge Sort.\n");
        return;
    }

    merge_sort_nomes_recursivo(arr, aux, 0, n - 1);

    free(aux);
}
