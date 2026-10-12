#include <stdio.h>
#include <stdlib.h>
#include "radix.h"

//Encontra a maior nota (e converte em inteiro) para determinar a quantidade de digitos
static int get_max_nota(Candidato *arr, int n) {
    int max = (int)(arr[0].nota_final * 100.0f + 0.5f);
    for (int i = 1; i < n; i++) {
        int val = (int)(arr[i].nota_final * 100.0f + 0.5f);
        if (val > max) {
            max = val;
        }
    }
    return max;
}

//counting Sort estavel por digito em ordem decrescente
static void counting_sort_digito(Candidato *arr, int n, int exp) {
    Candidato *output = (Candidato *)malloc(n * sizeof(Candidato));
    if (!output) {
        fprintf(stderr, "Erro ao alocar memoria para o Radix Sort.\n");
        return;
    }

    int count[10] = {0};

    //contagem da frequencia dos digitos
    for (int i = 0; i < n; i++) {
        int val = (int)(arr[i].nota_final * 100.0f + 0.5f);
        int digito = (val / exp) % 10;
        count[9 - digito]++;
    }

    for (int i = 1; i < 10; i++) {
        count[i] += count[i - 1];
    }

    //array ordenado de tras para frente para manter estabilidade
    for (int i = n - 1; i >= 0; i--) {
        int val = (int)(arr[i].nota_final * 100.0f + 0.5f);
        int digito = (val / exp) % 10;
        output[count[9 - digito] - 1] = arr[i];
        count[9 - digito]--;
    }

    //copia de volta para o array original
    for (int i = 0; i < n; i++) {
        arr[i] = output[i];
    }

    free(output);
}

//função principal do Radix
void radix_sort_notas(Candidato *arr, int n) {
    if (n <= 1) return;

    int max = get_max_nota(arr, n);

    for (int exp = 1; max / exp > 0; exp *= 10) {
        counting_sort_digito(arr, n, exp);
    }
}
