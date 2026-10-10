#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    int id_curso;
    char nome_curso[100];
    int peso_cn;
    int peso_ch;
    int peso_lc;
    int peso_mt;
    int peso_red;
}Curso;

typedef struct {
    long long inscricao; 
    float nota_cn;
    float nota_ch;
    float nota_lc;
    float nota_mt;
    float nota_red;
    float nota_final;
} Candidato;

int main() {
    printf("--- Sistema Simulador do SISU ---\n");
    return 0; // a ser preenchida 
}