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
    char nome[100];
    int id_curso_pretendido;
    float nota_cn;
    float nota_ch;
    float nota_lc;
    float nota_mt;
    float nota_red;
    float nota_final;
} Candidato;

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


int main() {
    printf("--- Sistema Simulador do SISU ---\n");
    return 0; // a ser preenchida 
}