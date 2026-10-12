# Simulador do SISU (Ordenação)

## Proposta
Este projeto tem como objetivo simular o sistema de seleção do SISU. O sistema processa uma base de dados de candidatos do ENEM, aplicando os algoritmos de ordenação **Merge Sort** e **Radix Sort** para classificar os candidatos de acordo com as notas e os pesos específicos de cada curso, simulando a nota de corte e a alocação de vagas.

## Arquitetura
A arquitetura do sistema é dividida em duas partes principais:
- **Python**: Utilizado para a preparação e download automatizado dos dados de candidatos e geração dos cursos (`setup_dados.py`).
- **C**: Utilizado para o núcleo do sistema, implementando os algoritmos de ordenação de forma eficiente para processar a grande quantidade de candidatos.

## 📹 Apresentação
* **Assista ao Vídeo:** [Apresentação da dupla](https://www.youtube.com/watch?v=R5o7hZw-pRM)

## Equipe
*   [Gabriel Diniz](https://github.com/GabrielDiniz12) - 241025630
*   [Pedro Americo](https://github.com/dev-americo) - 241025980

## Como executar
Execute os comandos abaixo no terminal, a partir da pasta raiz do projeto. É necessário ter Python, `pip` e um compilador C (`gcc`) instalados.

1. Instale as dependências do Python necessárias para preparar os dados e abrir a interface:
   ```bash
   python -m pip install gdown customtkinter
   ```
2. Gere os arquivos de dados. O download da base de candidatos requer conexão com a internet:
   ```bash
   python back/setup_dados.py
   ```
3. Compile o programa em C:
   ```bash
   gcc back/main.c back/mergeSort/merge.c "back/funcoes auxiliares/auxiliares.c" back/radixSort/radix.c -o back/main.out
   ```
4. Inicie a interface:
   ```bash
   python front/interface.py
   ```

## Como rodar os testes

Execute os comandos a partir da pasta raiz do projeto, com Python, `gcc` e as dependências da interface instaladas.

- Para rodar a suíte completa, incluindo a tentativa de análise com Valgrind:
   ```bash
   python test/testes.py
   ```
