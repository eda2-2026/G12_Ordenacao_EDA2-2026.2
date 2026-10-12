#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "main.h"
#include "mergeSort/merge.h"
#include "funcoes auxiliares/auxiliares.h"
#include "radixSort/radix.h"

int main() {

    Candidato *candidatos = (Candidato *)malloc(MAX_CANDIDATOS * sizeof(Candidato));
    if (!candidatos) {
        fprintf(stderr, "Erro ao alocar memoria para os candidatos.\n");
        return 1;
    }
    //carrega a base de dados
    int total_candidatos = carregar_candidatos("candidatos_limpo.csv", candidatos);
    if (total_candidatos <= 0) {
        total_candidatos = carregar_candidatos("back/candidatos_limpo.csv", candidatos);
    }
    //função de teste caso o arquivo não seja encontrado
    if (total_candidatos <= 0) {
        printf("[Aviso] 'candidatos_limpo.csv' nao encontrado. Usando dados ficticios.\n");
        total_candidatos = 5;
        candidatos[0] = (Candidato){1001, "Ana Silva", 1, 600.0, 650.0, 700.0, 680.0, 800.0, 0.0};
        candidatos[1] = (Candidato){1002, "Bruno Costa", 1, 750.0, 800.0, 720.0, 850.0, 900.0, 0.0};
        candidatos[2] = (Candidato){1003, "Carla Souza", 1, 700.0, 710.0, 690.0, 740.0, 750.0, 0.0};
        candidatos[3] = (Candidato){1004, "Diego Lima", 1, 800.0, 820.0, 810.0, 890.0, 920.0, 0.0};
        candidatos[4] = (Candidato){1005, "Elena Martins", 1, 650.0, 620.0, 640.0, 600.0, 700.0, 0.0};
    }
    //ex. de curso para calcular a nota ponderada
    Curso curso_teste = {1, "Engenharia de Software", 2, 1, 2, 4, 3};
    for (int i = 0; i < total_candidatos; i++) {
        calcular_nota_ponderada(&candidatos[i], &curso_teste);
    }
    
    clock_t inicio = clock();
    radix_sort_notas(candidatos, total_candidatos);
    clock_t fim = clock();
    double tempo_total = (double)(fim - inicio) / CLOCKS_PER_SEC;
    //primeiros colocados
    int qtd = (total_candidatos < 5) ? total_candidatos : 5;
    printf("\n--- Top %d Classificados (Radix Sort) ---\n", qtd);
    for (int i = 0; i < qtd; i++) {
        printf("%dº | Nota: %.2f | Nome: %s\n", i + 1, candidatos[i].nota_final, candidatos[i].nome);
    }
    //tempo no console
    printf("\nTempo total de processamento (Radix Sort): %f segundos\n", tempo_total);
    free(candidatos);
    return 0;
}