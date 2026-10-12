#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "main.h"
#include "mergeSort/merge.h"
#include "funcoes auxiliares/auxiliares.h"
#include "radixSort/radix.h"

int main(int argc, char *argv[]) {
    // Listagem de Cursos
    if (argc > 1 && strcmp(argv[1], "--cursos") == 0) {
        listar_cursos();
        return 0;
    }

    // Simulação do SISU com Radix Sort
    if (argc >= 3 && strcmp(argv[1], "--simular") == 0) {
        int id_curso_desejado = atoi(argv[2]);
        int vagas = (argc >= 4) ? atoi(argv[3]) : 40;
        if (vagas <= 0) vagas = 40;

        Curso curso;
        if (!carregar_curso_por_id(id_curso_desejado, &curso)) {
            fprintf(stderr, "Erro ao carregar dados do curso ID %d\n", id_curso_desejado);
            return 1;
        }

        Candidato *candidatos = (Candidato *)malloc(MAX_CANDIDATOS * sizeof(Candidato));
        if (!candidatos) {
            fprintf(stderr, "Erro de memoria.\n");
            return 1;
        }

        const char *caminhos[] = {"candidatos_limpo.csv", "../candidatos_limpo.csv", "back/candidatos_limpo.csv"};
        int total_candidatos = -1;
        for (int i = 0; i < 3; i++) {
            total_candidatos = carregar_candidatos(caminhos[i], candidatos);
            if (total_candidatos > 0) break;
        }

        if (total_candidatos <= 0) {
            fprintf(stderr, "Erro ao carregar candidatos_limpo.csv\n");
            free(candidatos);
            return 1;
        }

        int total_filtrados = 0;
        Candidato *candidatos_curso = filtrar_por_curso(candidatos, total_candidatos, id_curso_desejado, &total_filtrados);
        free(candidatos);

        if (!candidatos_curso || total_filtrados == 0) {
            fprintf(stderr, "Nenhum candidato para o curso %d\n", id_curso_desejado);
            return 1;
        }

        for (int i = 0; i < total_filtrados; i++) {
            calcular_nota_ponderada(&candidatos_curso[i], &curso);
        }

        // Radix Sort decrescente pelas notas
        clock_t inicio = clock();
        radix_sort_notas(candidatos_curso, total_filtrados);
        clock_t fim = clock();
        double tempo_total = (double)(fim - inicio) / CLOCKS_PER_SEC;

        int qtd_vagas = (vagas < total_filtrados) ? vagas : total_filtrados;
        float nota_corte = (qtd_vagas > 0) ? candidatos_curso[qtd_vagas - 1].nota_final : 0.0f;

        printf("STATUS:SUCESSO\n");
        printf("CURSO:%s\n", curso.nome_curso);
        printf("TOTAL_INSCRITOS:%d\n", total_filtrados);
        printf("VAGAS:%d\n", vagas);
        printf("CORTE:%.2f\n", nota_corte);
        printf("TEMPO:%.5f\n", tempo_total);
        printf("APROVADOS:\n");
        for (int i = 0; i < qtd_vagas; i++) {
            printf("%d;%lld;%s;%.2f\n", 
                   i + 1, 
                   candidatos_curso[i].inscricao, 
                   candidatos_curso[i].nome, 
                   candidatos_curso[i].nota_final);
        }

        free(candidatos_curso);
        return 0;
    }

    // Ordenação Alfabética de Candidatos com Merge Sort
    if (argc >= 3 && strcmp(argv[1], "--merge") == 0) {
        int id_curso_desejado = atoi(argv[2]);

        Curso curso;
        if (!carregar_curso_por_id(id_curso_desejado, &curso)) {
            fprintf(stderr, "Erro ao carregar dados do curso ID %d\n", id_curso_desejado);
            return 1;
        }

        Candidato *candidatos = (Candidato *)malloc(MAX_CANDIDATOS * sizeof(Candidato));
        if (!candidatos) {
            fprintf(stderr, "Erro de memoria.\n");
            return 1;
        }

        const char *caminhos[] = {"candidatos_limpo.csv", "../candidatos_limpo.csv", "back/candidatos_limpo.csv"};
        int total_candidatos = -1;
        for (int i = 0; i < 3; i++) {
            total_candidatos = carregar_candidatos(caminhos[i], candidatos);
            if (total_candidatos > 0) break;
        }

        if (total_candidatos <= 0) {
            fprintf(stderr, "Erro ao carregar candidatos_limpo.csv\n");
            free(candidatos);
            return 1;
        }

        int total_filtrados = 0;
        Candidato *candidatos_curso = filtrar_por_curso(candidatos, total_candidatos, id_curso_desejado, &total_filtrados);
        free(candidatos);

        if (!candidatos_curso || total_filtrados == 0) {
            fprintf(stderr, "Nenhum candidato para o curso %d\n", id_curso_desejado);
            return 1;
        }

        for (int i = 0; i < total_filtrados; i++) {
            calcular_nota_ponderada(&candidatos_curso[i], &curso);
        }

        // Merge Sort alfabético pelos nomes
        clock_t inicio = clock();
        merge_sort_nomes(candidatos_curso, total_filtrados);
        clock_t fim = clock();
        double tempo_total = (double)(fim - inicio) / CLOCKS_PER_SEC;

        // Salva arquivo com os nomes do curso
        char arquivo_saida[128];
        snprintf(arquivo_saida, sizeof(arquivo_saida), "nomes_ordenados_curso_%d.txt", id_curso_desejado);
        salvar_nomes_txt(arquivo_saida, candidatos_curso, total_filtrados);

        printf("STATUS:SUCESSO\n");
        printf("CURSO:%s\n", curso.nome_curso);
        printf("TOTAL_INSCRITOS:%d\n", total_filtrados);
        printf("TEMPO:%.5f\n", tempo_total);
        printf("ARQUIVO:%s\n", arquivo_saida);
        printf("CANDIDATOS:\n");
        for (int i = 0; i < total_filtrados; i++) {
            printf("%d;%lld;%s;%.2f\n", 
                   i + 1, 
                   candidatos_curso[i].inscricao, 
                   candidatos_curso[i].nome, 
                   candidatos_curso[i].nota_final);
        }

        free(candidatos_curso);
        return 0;
    }

    fprintf(stderr, "Uso: %s --cursos | %s --simular <id> <vagas> | %s --merge <id>\n", argv[0], argv[0], argv[0]);
    return 1;
}