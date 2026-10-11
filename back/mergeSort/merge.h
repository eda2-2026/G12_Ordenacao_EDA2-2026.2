#ifndef MERGE_H
#define MERGE_H

#include "../main.h"

void merge_nomes(Candidato *arr, Candidato *aux, int inicio, int meio, int fim);

void merge_sort_nomes_recursivo(Candidato *arr, Candidato *aux, int inicio, int fim);

void merge_sort_nomes(Candidato *arr, int n);

#endif
