# Simulador do SISU (Ordenação)

## Proposta
Este projeto tem como objetivo simular o sistema de seleção do SISU. O sistema processa uma base de dados de candidatos do ENEM, aplicando algoritmos de ordenação para classificar os candidatos de acordo com as notas e os pesos específicos de cada curso, simulando a nota de corte e a alocação de vagas.

## Arquitetura
A arquitetura do sistema é dividida em duas partes principais:
- **Python**: Utilizado para a preparação e download automatizado dos dados de candidatos e geração dos cursos (`setup_dados.py`).
- **C**: Utilizado para o núcleo do sistema, implementando os algoritmos de ordenação (como Merge Sort, Quick Sort, etc.) de forma eficiente para processar a grande quantidade de candidatos.

## Equipe
- Gabriel Diniz
- Pedro

## Como executar
1. Instale as dependências do Python necessárias para baixar a base de dados:
   ```bash
   pip install gdown
   pip install customtkinter
   ```
2. Execute o script de configuração inicial (requer internet):
   ```bash
   python setup_dados.py
   ```
