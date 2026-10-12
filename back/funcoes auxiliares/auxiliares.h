#ifndef AUXILIARES_H
#define AUXILIARES_H

#include "../main.h"

int carregar_candidatos(const char *caminho, Candidato *arr);

Candidato* filtrar_por_curso(const Candidato *todos, int total, int id_curso_alvo, int *total_filtrados);

void calcular_nota_ponderada(Candidato *candidato, const Curso *curso);

int salvar_nomes_txt(const char *caminho_saida, const Candidato *arr, int total);

int listar_cursos(void);

int carregar_curso_por_id(int id_curso, Curso *curso_out);

#endif
