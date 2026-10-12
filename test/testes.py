#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
==============================================================================
Suíte Unificada de Testes Automatizados - EDA 2 (Ordenação SISU / ENEM)
Testa de ponta a ponta:
  1. Backend C (GCC, --cursos, Radix Sort O(N), Merge Sort O(N log N))
  2. Validação Matemática de Invariantes (notas decrescentes, ordem alfabética)
  3. Frontend e Interface Gráfica (CustomTkinter, abas, paginação, integração)
  4. Análise Estrita de Memória com Valgrind (zero memory leaks)
==============================================================================
"""

import os
import sys
import math
import shutil
import tempfile
import argparse
import subprocess
from pathlib import Path

# Habilita suporte a ANSI em terminais Windows se aplicável
if sys.platform == "win32":
    os.system("")

# Cores ANSI
GREEN = "\033[0;32m"
RED = "\033[0;31m"
BLUE = "\033[0;34m"
YELLOW = "\033[1;33m"
CYAN = "\033[0;36m"
BOLD = "\033[1m"
NC = "\033[0m"

# Diretórios e caminhos
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
os.chdir(PROJECT_ROOT)

# Adiciona o diretório front ao path do python para importar os módulos da UI
sys.path.insert(0, str(PROJECT_ROOT / "front"))

IS_WIN = sys.platform == "win32"
BIN_NAME = "main.exe" if IS_WIN else "main.out"
BIN_PATH = PROJECT_ROOT / "back" / BIN_NAME

TOTAL_TESTES = 0
TESTES_PASSARAM = 0
TESTES_FALHARAM = 0


def registrar_passou(nome: str):
    global TOTAL_TESTES, TESTES_PASSARAM
    print(f"  [{GREEN}PASSOU{NC}] {nome}")
    TOTAL_TESTES += 1
    TESTES_PASSARAM += 1


def registrar_falhou(nome: str, detalhe: str = ""):
    global TOTAL_TESTES, TESTES_FALHARAM
    print(f"  [{RED}FALHOU{NC}] {nome}")
    if detalhe:
        print(f"          {RED}↳ Detalhe:{NC} {detalhe}")
    TOTAL_TESTES += 1
    TESTES_FALHARAM += 1


# ==============================================================================
# 1. TESTES DO BACKEND C
# ==============================================================================

def testar_compilacao_c() -> bool:
    print(f"{BOLD}{CYAN}[C-1] Compilando backend C com GCC (-g -O3 -Wall -Wextra)...{NC}")
    (PROJECT_ROOT / "back").mkdir(parents=True, exist_ok=True)

    cmd = [
        "gcc",
        "-g",
        "-O3",
        "-Wall",
        "-Wextra",
        "back/main.c",
        "back/funcoes auxiliares/auxiliares.c",
        "back/radixSort/radix.c",
        "back/mergeSort/merge.c",
        "-o",
        str(BIN_PATH),
    ]

    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode == 0 and BIN_PATH.is_file():
            registrar_passou(f"Compilação do backend C '{BIN_PATH.relative_to(PROJECT_ROOT)}'")
            print()
            return True
        else:
            registrar_falhou(
                f"Compilação do backend C '{BIN_PATH.relative_to(PROJECT_ROOT)}'",
                proc.stderr.strip() or "Erro de compilação GCC",
            )
            print()
            return False
    except Exception as e:
        registrar_falhou("Compilação do backend C", str(e))
        print()
        return False


def testar_backend_cursos():
    print(f"{BOLD}{CYAN}[C-2] Testando comando de listagem de cursos (--cursos)...{NC}")
    try:
        proc = subprocess.run(
            [str(BIN_PATH), "--cursos"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if proc.returncode == 0 and "1;Medicina" in proc.stdout:
            qtd_cursos = sum(1 for line in proc.stdout.splitlines() if ";" in line)
            registrar_passou(f"Listagem de cursos retornou com sucesso ({qtd_cursos} cursos encontrados)")
        else:
            registrar_falhou("Listagem de cursos (--cursos)", "Saída não contém '1;Medicina' ou status de erro")
    except Exception as e:
        registrar_falhou("Listagem de cursos (--cursos)", str(e))
    print()


def testar_radix_sort():
    print(f"{BOLD}{CYAN}[C-3] Testando simulação do SISU com Radix Sort (--simular 1 40)...{NC}")
    try:
        proc = subprocess.run(
            [str(BIN_PATH), "--simular", "1", "40"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if proc.returncode == 0 and "STATUS:SUCESSO" in proc.stdout:
            registrar_passou("Execução do Radix Sort finalizada com STATUS:SUCESSO")
        else:
            registrar_falhou(
                "Execução do Radix Sort (--simular 1 40)",
                f"Return code {proc.returncode} ou status de erro",
            )
            print()
            return

        # Validação da invariante matemática decrescente
        lines = proc.stdout.strip().splitlines()
        corte_declarado = None
        aprovados = []
        is_aprovados = False

        for l in lines:
            l = l.strip()
            if l.startswith("CORTE:"):
                try:
                    corte_declarado = float(l.split(":")[1])
                except ValueError:
                    pass
            elif l == "APROVADOS:":
                is_aprovados = True
            elif is_aprovados and ";" in l:
                parts = l.split(";")
                if len(parts) >= 4:
                    try:
                        pos = int(parts[0])
                        insc = parts[1]
                        nome = parts[2]
                        nota = float(parts[3])
                        aprovados.append((pos, insc, nome, nota))
                    except ValueError:
                        pass

        if len(aprovados) != 40:
            registrar_falhou(
                "Invariante do Radix Sort",
                f"Quantidade de aprovados incorreta: {len(aprovados)} (esperado 40)",
            )
            print()
            return

        # Verificar se as notas são não-crescentes: nota[i] >= nota[i+1]
        invariante_valida = True
        for i in range(len(aprovados) - 1):
            if aprovados[i][3] < aprovados[i + 1][3]:
                registrar_falhou(
                    "Invariante do Radix Sort",
                    f"Invariante violada: pos {i+1} ({aprovados[i][3]}) < pos {i+2} ({aprovados[i+1][3]})",
                )
                invariante_valida = False
                break

        if invariante_valida:
            if corte_declarado is not None and abs(corte_declarado - aprovados[-1][3]) > 0.01:
                registrar_falhou(
                    "Invariante do Radix Sort",
                    f"Nota de corte declarada ({corte_declarado}) difere da nota do 40º ({aprovados[-1][3]})",
                )
            else:
                registrar_passou("Invariante do Radix Sort: 40 aprovados estritamente ordenados de forma decrescente")
    except Exception as e:
        registrar_falhou("Teste Radix Sort", str(e))
    print()


def testar_merge_sort():
    print(f"{BOLD}{CYAN}[C-4] Testando ordenação alfabética com Merge Sort (--merge 1)...{NC}")
    try:
        proc = subprocess.run(
            [str(BIN_PATH), "--merge", "1"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if proc.returncode == 0 and "STATUS:SUCESSO" in proc.stdout:
            registrar_passou("Execução do Merge Sort finalizada com STATUS:SUCESSO")
        else:
            registrar_falhou(
                "Execução do Merge Sort (--merge 1)",
                f"Return code {proc.returncode} ou status diferente de SUCESSO",
            )
            print()
            return

        # Validação da invariante de ordenação alfabética
        lines = proc.stdout.strip().splitlines()
        candidatos = []
        is_candidatos = False

        for l in lines:
            l = l.strip()
            if l == "CANDIDATOS:":
                is_candidatos = True
            elif is_candidatos and ";" in l:
                parts = l.split(";")
                if len(parts) >= 3:
                    candidatos.append(parts[2])

        if not candidatos:
            registrar_falhou("Invariante do Merge Sort", "Nenhum candidato retornado pelo backend")
        else:
            ordem_alfabetica = True
            for i in range(len(candidatos) - 1):
                if candidatos[i] > candidatos[i + 1]:
                    registrar_falhou(
                        "Invariante do Merge Sort",
                        f"Invariante violada: '{candidatos[i]}' > '{candidatos[i+1]}'",
                    )
                    ordem_alfabetica = False
                    break
            if ordem_alfabetica:
                registrar_passou(
                    f"Invariante do Merge Sort: todos os {len(candidatos)} candidatos ordenados alfabeticamente"
                )

        # Checar arquivo txt gerado
        arquivo_saida = PROJECT_ROOT / "nomes_ordenados_curso_1.txt"
        if arquivo_saida.is_file() and arquivo_saida.stat().st_size > 0:
            with open(arquivo_saida, "r", encoding="utf-8", errors="ignore") as f:
                linhas_txt = sum(1 for _ in f)
            registrar_passou(f"Arquivo 'nomes_ordenados_curso_1.txt' gerado com sucesso ({linhas_txt} linhas)")
            arquivo_saida.unlink(missing_ok=True)
        else:
            registrar_falhou(
                "Arquivo 'nomes_ordenados_curso_1.txt'",
                "Arquivo não foi gerado ou está vazio",
            )

    except Exception as e:
        registrar_falhou("Teste Merge Sort", str(e))
    print()


# ==============================================================================
# 2. TESTES DA INTERFACE GRÁFICA (FRONTEND)
# ==============================================================================

def testar_interface_utilitarios():
    print(f"{BOLD}{CYAN}[UI-1] Testando funções utilitárias da interface (arquivos e pesos)...{NC}")
    try:
        import io
        import contextlib
        with contextlib.redirect_stderr(io.StringIO()):
            from interface import obter_caminho_raiz, gerar_tabela_cursos_dinamica, requisitar_cursos_ao_backend_c

        # 1. Teste obter_caminho_raiz
        caminho_cursos = obter_caminho_raiz("cursos.csv")
        if os.path.exists(caminho_cursos):
            registrar_passou("obter_caminho_raiz localizou 'cursos.csv' corretamente")
        else:
            registrar_falhou("obter_caminho_raiz", f"Caminho não encontrado: {caminho_cursos}")

        # 2. Teste gerar_tabela_cursos_dinamica em arquivo temporário
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            gerar_tabela_cursos_dinamica(tmp_path, aleatorio=True)
            with open(tmp_path, "r", encoding="utf-8") as f:
                linhas = [l.strip() for l in f if l.strip()]

            # 1 cabeçalho + 50 cursos = 51 linhas
            if len(linhas) == 51 and "ID_Curso,Nome_Curso" in linhas[0]:
                registrar_passou("gerar_tabela_cursos_dinamica gerou 50 cursos válidos com pesos sorteados")
            else:
                registrar_falhou("gerar_tabela_cursos_dinamica", f"Linhas esperadas 51, obtidas: {len(linhas)}")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

        # 3. Teste requisitar_cursos_ao_backend_c
        mapa_cursos = requisitar_cursos_ao_backend_c()
        if isinstance(mapa_cursos, dict) and "Medicina" in mapa_cursos:
            id_med = mapa_cursos["Medicina"].get("id")
            pesos = mapa_cursos["Medicina"].get("pesos", [])
            if id_med == 1 and len(pesos) == 5:
                registrar_passou(f"requisitar_cursos_ao_backend_c retornou {len(mapa_cursos)} cursos mapeados via C")
            else:
                registrar_falhou("requisitar_cursos_ao_backend_c", f"Dados inválidos para Medicina: id={id_med}, pesos={pesos}")
        else:
            registrar_falhou("requisitar_cursos_ao_backend_c", "Dicionário vazio ou Medicina não encontrada")

    except Exception as e:
        registrar_falhou("Funções Utilitárias da Interface", str(e))
    print()


def testar_interface_componentes():
    print(f"{BOLD}{CYAN}[UI-2] Testando componentes gráficos e lógica de paginação (SisuApp)...{NC}")
    try:
        import io
        import contextlib
        with contextlib.redirect_stderr(io.StringIO()):
            from interface import SisuApp
            # Instancia a aplicação em modo headless (sem exibir janela física)
            app = SisuApp()
            app.withdraw()

        # 1. Validação de inicialização da janela principal
        if app.title() == "Simulador SISU - EDA 2":
            registrar_passou("SisuApp inicializada com sucesso (título e layout válidos)")
        else:
            registrar_falhou("SisuApp título", f"Título inesperado: {app.title()}")

        # 2. Validação das 2 abas requeridas
        if hasattr(app, "tab_radix") and hasattr(app, "tab_merge"):
            registrar_passou("Abas 'Classificação SISU (Radix Sort)' e 'Relação de Candidatos (Merge Sort)' presentes")
        else:
            registrar_falhou("Abas do Tabview", "Abas tab_radix ou tab_merge ausentes no aplicativo")

        # 3. Validação do seletor de cursos modal
        if hasattr(app, "combo_cursos") and len(app.lista_cursos) >= 12:
            curso_selecionado = app.combo_cursos.get()
            registrar_passou(f"Seletor de cursos operacional (curso padrão: '{curso_selecionado}')")
        else:
            registrar_falhou("Seletor de cursos", "Componente combo_cursos ou lista_cursos ausente")

        # 4. Validação da lógica de paginação da aba Merge Sort
        # Simula uma lista de 250 candidatos para testar navegação e limites
        app.candidatos_merge = [(i, str(1000000 + i), f"Candidato Teste {i}", 700.0) for i in range(1, 251)]
        app.itens_por_pagina = 50
        app.pagina_atual_merge = 1
        app.renderizar_pagina_merge()

        total_paginas = math.ceil(len(app.candidatos_merge) / app.itens_por_pagina)  # 5 páginas
        paginacao_correta = True

        # Na página 1: botão anterior deve estar disabled, próximo normal
        if app.pagina_atual_merge != 1 or app.btn_ant_pagina.cget("state") != "disabled" or app.btn_prox_pagina.cget("state") != "normal":
            paginacao_correta = False
            registrar_falhou("Paginação Página 1", "Estados dos botões incorretos na primeira página")

        # Avança para página 2
        app.proxima_pagina_merge()
        if app.pagina_atual_merge != 2 or app.btn_ant_pagina.cget("state") != "normal":
            paginacao_correta = False
            registrar_falhou("Paginação Avanço", "Falha ao navegar para a página 2")

        # Salta para a última página (5)
        app.pagina_atual_merge = total_paginas
        app.renderizar_pagina_merge()
        if app.pagina_atual_merge != 5 or app.btn_prox_pagina.cget("state") != "disabled":
            paginacao_correta = False
            registrar_falhou("Paginação Limite Superior", "Botão próximo não desabilitou na última página")

        # Tentar avançar além da última página não deve alterar a página
        app.proxima_pagina_merge()
        if app.pagina_atual_merge != 5:
            paginacao_correta = False
            registrar_falhou("Paginação Overflow", "Página ultrapassou o total máximo")

        # Volta para página 4
        app.pagina_anterior_merge()
        if app.pagina_atual_merge != 4 or app.btn_prox_pagina.cget("state") != "normal":
            paginacao_correta = False
            registrar_falhou("Paginação Retorno", "Falha ao retroceder página")

        if paginacao_correta:
            registrar_passou(f"Lógica de paginação validada (5 páginas de 50 itens, botões e limites 100% íntegros)")

        # Fecha a aplicação
        app.destroy()

    except Exception as e:
        registrar_falhou("Componentes da Interface", str(e))
    print()


# ==============================================================================
# 3. TESTE DE VALGRIND (VAZAMENTOS DE MEMÓRIA)
# ==============================================================================

def testar_valgrind():
    print(f"{BOLD}{CYAN}[MEM-1] Verificação de Vazamento de Memória com Valgrind...{NC}")
    valgrind_bin = shutil.which("valgrind")

    if valgrind_bin and not IS_WIN:
        print("  Executando Valgrind no Radix Sort (--simular 1 40)...")
        proc_radix = subprocess.run(
            [
                valgrind_bin,
                "--leak-check=full",
                "--show-leak-kinds=all",
                "--error-exitcode=42",
                str(BIN_PATH),
                "--simular",
                "1",
                "40",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if proc_radix.returncode == 0 and "0 errors from 0 contexts" in proc_radix.stderr:
            registrar_passou("Valgrind Radix Sort: 0 memory leaks, 0 erros de contexto")
        else:
            registrar_falhou(
                "Valgrind Radix Sort",
                "Vazamentos ou erros detectados pelo Valgrind",
            )
            for linha in proc_radix.stderr.splitlines():
                if any(x in linha for x in ["definitely lost", "indirectly lost", "possibly lost", "still reachable", "ERROR SUMMARY"]):
                    print(f"    {linha}")

        print("  Executando Valgrind no Merge Sort (--merge 1)...")
        proc_merge = subprocess.run(
            [
                valgrind_bin,
                "--leak-check=full",
                "--show-leak-kinds=all",
                "--error-exitcode=42",
                str(BIN_PATH),
                "--merge",
                "1",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        (PROJECT_ROOT / "nomes_ordenados_curso_1.txt").unlink(missing_ok=True)

        if proc_merge.returncode == 0 and "0 errors from 0 contexts" in proc_merge.stderr:
            registrar_passou("Valgrind Merge Sort: 0 memory leaks, 0 erros de contexto")
        else:
            registrar_falhou(
                "Valgrind Merge Sort",
                "Vazamentos ou erros detectados pelo Valgrind",
            )
            for linha in proc_merge.stderr.splitlines():
                if any(x in linha for x in ["definitely lost", "indirectly lost", "possibly lost", "still reachable", "ERROR SUMMARY"]):
                    print(f"    {linha}")
    else:
        print(f"  [{YELLOW}AVISO{NC}] 'valgrind' não foi detectado no PATH do ambiente atual.")
        print("         Para executar manualmente:")
        print(f"         {BOLD}valgrind --leak-check=full --show-leak-kinds=all ./back/main.out --simular 1 40{NC}")
    print()


# ==============================================================================
# MAIN & CLI
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Suíte Unificada de Testes - EDA 2 (Ordenação SISU / ENEM)"
    )
    parser.add_argument(
        "--quick", "--sem-valgrind",
        dest="quick",
        action="store_true",
        help="Executa rapidamente todos os testes (Backend e Interface), pulando a análise pesada do Valgrind."
    )
    parser.add_argument(
        "--interface", "--front",
        dest="apenas_interface",
        action="store_true",
        help="Executa apenas os testes da interface gráfica e utilitários da UI."
    )
    parser.add_argument(
        "--backend", "--back",
        dest="apenas_backend",
        action="store_true",
        help="Executa apenas os testes do backend C e invariantes de ordenação."
    )
    parser.add_argument(
        "--valgrind",
        dest="apenas_valgrind",
        action="store_true",
        help="Executa apenas a checagem de memória Valgrind no backend C."
    )

    args = parser.parse_args()

    print(f"{BOLD}{BLUE}========================================================================{NC}")
    print(f"{BOLD}{BLUE}   SUÍTE DE TESTES AUTOMATIZADOS - EDA 2 (PYTHON RUNNER)               {NC}")
    print(f"{BOLD}{BLUE}========================================================================{NC}\n")

    # Caso 1: Apenas testes da interface
    if args.apenas_interface:
        testar_interface_utilitarios()
        testar_interface_componentes()
    # Caso 2: Apenas testes do Valgrind
    elif args.apenas_valgrind:
        if not BIN_PATH.is_file():
            testar_compilacao_c()
        testar_valgrind()
    # Caso 3: Apenas testes do Backend
    elif args.apenas_backend:
        if not testar_compilacao_c():
            sys.exit(1)
        testar_backend_cursos()
        testar_radix_sort()
        testar_merge_sort()
        if not args.quick:
            testar_valgrind()
    # Caso 4: Execução Completa (Backend + Interface + [Valgrind])
    else:
        if not testar_compilacao_c():
            print(f"{BOLD}{RED}Interrompendo suíte devido a falha na compilação.{NC}\n")
            sys.exit(1)

        testar_backend_cursos()
        testar_radix_sort()
        testar_merge_sort()
        testar_interface_utilitarios()
        testar_interface_componentes()

        if not args.quick:
            testar_valgrind()
        else:
            print(f"[{YELLOW}INFO{NC}] Modo rápido ativado: teste do Valgrind ignorado.\n")

    # Resumo Final
    print(f"{BOLD}{BLUE}========================================================================{NC}")
    print(f"{BOLD}{BLUE}   RESUMO DOS TESTES                                                    {NC}")
    print(f"{BOLD}{BLUE}========================================================================{NC}")
    print(f"  Total de testes executados: {BOLD}{TOTAL_TESTES}{NC}")
    print(f"  Testes aprovados:          {GREEN}{BOLD}{TESTES_PASSARAM}{NC}")
    print(f"  Testes reprovados:         {RED}{BOLD}{TESTES_FALHARAM}{NC}")

    if TESTES_FALHARAM == 0:
        print(f"\n{BOLD}{GREEN}✔ TODOS OS TESTES PASSARAM COM SUCESSO! BACKEND E INTERFACE VALIDADOS!{NC}\n")
        sys.exit(0)
    else:
        print(f"\n{BOLD}{RED}✘ ALGUNS TESTES FALHARAM. VERIFIQUE OS DETALHES ACIMA.{NC}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
