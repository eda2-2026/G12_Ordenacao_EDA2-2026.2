#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "auxiliares.h"

// Calcula a média ponderada do candidato com base nos pesos do curso
void calcular_nota_ponderada(Candidato *candidato, const Curso *curso) {
    float soma_pesos = curso->peso_cn + curso->peso_ch + curso->peso_lc + curso->peso_mt + curso->peso_red;
    
    if (soma_pesos == 0) {
        candidato->nota_final = 0.0f;
        return;
    }
    float soma_ponderada = (candidato->nota_cn * curso->peso_cn) +
                           (candidato->nota_ch * curso->peso_ch) +
                           (candidato->nota_lc * curso->peso_lc) +
                           (candidato->nota_mt * curso->peso_mt) +
                           (candidato->nota_red * curso->peso_red);
    candidato->nota_final = soma_ponderada / soma_pesos;
}

// Filtra candidatos pelo ID do curso pretendido, alocando um novo vetor dinâmico
Candidato* filtrar_por_curso(const Candidato *todos, int total, int id_curso_alvo, int *total_filtrados) {
    int count = 0;
    for (int i = 0; i < total; i++) {
        if (todos[i].id_curso_pretendido == id_curso_alvo) {
            count++;
        }
    }

    if (count == 0) {
        *total_filtrados = 0;
        return NULL;
    }

    Candidato *filtrados = (Candidato *)malloc(count * sizeof(Candidato));
    if (!filtrados) {
        *total_filtrados = 0;
        return NULL;
    }

    int pos = 0;
    for (int i = 0; i < total; i++) {
        if (todos[i].id_curso_pretendido == id_curso_alvo) {
            filtrados[pos++] = todos[i];
        }
    }

    *total_filtrados = count;
    return filtrados;
}

// Lê o arquivo CSV completo de candidatos
int carregar_candidatos(const char *caminho, Candidato *arr) {
    FILE *f = fopen(caminho, "r");
    if (!f) {
        return -1;
    }

    char buffer[512];
    if (!fgets(buffer, sizeof(buffer), f)) {
        fclose(f);
        return 0;
    }

    int count = 0;
    while (fgets(buffer, sizeof(buffer), f) && count < MAX_CANDIDATOS) {
        char *token = strtok(buffer, ",");
        if (!token) continue;
        arr[count].inscricao = atoll(token);

        token = strtok(NULL, ",");
        if (!token) continue;
        strncpy(arr[count].nome, token, sizeof(arr[count].nome) - 1);
        arr[count].nome[sizeof(arr[count].nome) - 1] = '\0';

        token = strtok(NULL, ",");
        if (!token) continue;
        arr[count].id_curso_pretendido = atoi(token);

        token = strtok(NULL, ",");
        if (!token) continue;
        arr[count].nota_cn = atof(token);

        token = strtok(NULL, ",");
        if (!token) continue;
        arr[count].nota_ch = atof(token);

        token = strtok(NULL, ",");
        if (!token) continue;
        arr[count].nota_lc = atof(token);

        token = strtok(NULL, ",");
        if (!token) continue;
        arr[count].nota_mt = atof(token);

        token = strtok(NULL, ",\r\n");
        if (!token) continue;
        arr[count].nota_red = atof(token);

        arr[count].nota_final = 0.0f;
        count++;
    }

    fclose(f);
    return count;
}

// Salva a lista de nomes ordenados em um arquivo .txt
int salvar_nomes_txt(const char *caminho_saida, const Candidato *arr, int total) {
    FILE *f = fopen(caminho_saida, "w");
    if (!f) {
        fprintf(stderr, "Erro ao criar arquivo de saida: %s\n", caminho_saida);
        return 0;
    }

    fprintf(f, "=====================================================\n");
    fprintf(f, " RELATORIO DE CANDIDATOS ORDENADOS POR NOME (SISU)   \n");
    fprintf(f, " Total de candidatos listados: %d                   \n", total);
    fprintf(f, "=====================================================\n\n");

    for (int i = 0; i < total; i++) {
        fprintf(f, "%d. %s (Inscricao: %lld | Curso ID: %d)\n", 
                i + 1, arr[i].nome, arr[i].inscricao, arr[i].id_curso_pretendido);
    }

    fclose(f);
    return 1;
}
