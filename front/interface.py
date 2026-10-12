import customtkinter as ctk
import os
import sys
import subprocess
import math
import threading
import csv
import random
import urllib.request
import urllib.error

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

def obter_caminho_raiz(nome_arquivo):
    """
    Retorna o caminho absoluto do arquivo priorizando a raiz do projeto.
    """
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    raiz_projeto = os.path.abspath(os.path.join(diretorio_atual, ".."))
    
    caminho_raiz = os.path.join(raiz_projeto, nome_arquivo)
    if os.path.exists(caminho_raiz):
        return caminho_raiz
        
    if os.path.exists(nome_arquivo):
        return os.path.abspath(nome_arquivo)

    caminho_back = os.path.join(raiz_projeto, "back", nome_arquivo)
    if os.path.exists(caminho_back):
        return caminho_back

    return caminho_raiz

def gerar_tabela_cursos_dinamica(caminho_csv=None, aleatorio=True):
    """
    Gera o arquivo cursos.csv com os 50 cursos oficiais do SISU.
    Se aleatorio=True, sorteia novos pesos (1 a 4) para cada matéria,
    tornando as notas de corte e classificações dinâmicas.
    """
    if caminho_csv is None:
        caminho_csv = obter_caminho_raiz("cursos.csv")

    lista_cursos_base = [
        "Medicina", "Direito", "Engenharia de Software", "Ciência da Computação", "Engenharia Civil", 
        "Psicologia", "Arquitetura e Urbanismo", "Odontologia", "Fisioterapia", "Medicina Veterinária", 
        "Enfermagem", "Relações Internacionais", "Administração", "Jornalismo", "Design Gráfico", 
        "Biomedicina", "Educação Física", "Agronomia", "Nutrição", "Ciências Contábeis", 
        "Engenharia Mecânica", "Engenharia Elétrica", "Engenharia Química", "Engenharia de Produção", 
        "Sistemas de Informação", "Farmácia", "História", "Geografia", "Letras", "Pedagogia", 
        "Ciências Biológicas", "Química", "Física", "Matemática", "Filosofia", "Sociologia", 
        "Serviço Social", "Turismo", "Gastronomia", "Música", "Artes Visuais", "Teatro", 
        "Cinema e Audiovisual", "Design de Moda", "Relações Públicas", "Publicidade e Propaganda", 
        "Estatística", "Geologia", "Zootecnia", "Fonoaudiologia"
    ]

    if not aleatorio:
        random.seed(42)

    with open(caminho_csv, mode='w', encoding='utf-8', newline='') as f_out:
        escritor = csv.writer(f_out, delimiter=',')
        escritor.writerow(["ID_Curso", "Nome_Curso", "Peso_CN", "Peso_CH", "Peso_LC", "Peso_MT", "Peso_RED"])
        for i, nome_curso in enumerate(lista_cursos_base):
            id_curso = i + 1
            p_cn = random.randint(1, 4)
            p_ch = random.randint(1, 4)
            p_lc = random.randint(1, 4)
            p_mt = random.randint(1, 4)
            p_red = random.randint(1, 4)
            escritor.writerow([id_curso, nome_curso, p_cn, p_ch, p_lc, p_mt, p_red])

    return caminho_csv

def baixar_candidatos_google_drive(callback_status=None):
    """
    Baixa o candidatos_limpo.csv do Google Drive usando gdown.
    """
    caminho_saida = obter_caminho_raiz("candidatos_limpo.csv")
    file_id = '1WsxGZrNSvKYDSSPA6ly-0jQ8Gd9XB2KL'
    url = f'https://drive.google.com/uc?id={file_id}'

    if callback_status:
        callback_status("Verificando conexão com a internet...")

    try:
        urllib.request.urlopen('https://www.google.com', timeout=4)
    except Exception:
        raise ConnectionError("Sem conexão com a internet.")

    try:
        import gdown
        if callback_status:
            callback_status("Baixando base do ENEM via Google Drive (~100 MB)...")
        gdown.download(url, caminho_saida, quiet=False)
        return caminho_saida
    except ImportError:
        raise ImportError("Biblioteca 'gdown' não instalada. Execute: pip install gdown")
    except Exception as e:
        raise RuntimeError(f"Erro no download: {e}")

def requisitar_cursos_ao_backend_c():
    """
    Requisita ao backend em C a listagem de todos os cursos do CSV com seus pesos.
    O executável C é chamado com o argumento '--cursos' e retorna 'ID;Nome;P_CN;P_CH;P_LC;P_MT;P_RED'.
    """
    caminhos_binario = ["./back/main.out", "../back/main.out", "main.out", "./main.out"]
    binario = None
    for caminho in caminhos_binario:
        if os.path.exists(caminho):
            binario = caminho
            break

    mapa_cursos = {}

    if binario:
        try:
            resultado = subprocess.run(
                [binario, "--cursos"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            for linha in resultado.stdout.strip().split("\n"):
                if ";" in linha:
                    partes = linha.strip().split(";")
                    if len(partes) >= 7:
                        id_curso = int(partes[0])
                        nome_curso = partes[1]
                        pesos = [int(p) for p in partes[2:7]]  # [CN, CH, LC, MT, RED]
                        mapa_cursos[nome_curso] = {"id": id_curso, "pesos": pesos}
                    elif len(partes) >= 2:
                        id_curso = int(partes[0])
                        nome_curso = partes[1]
                        mapa_cursos[nome_curso] = {"id": id_curso, "pesos": [1, 1, 1, 1, 1]}
        except Exception as e:
            print(f"[Aviso] Falha ao requisitar cursos via C: {e}")

    if not mapa_cursos:
        cursos_padrao = [
            "Medicina", "Direito", "Engenharia de Software", "Ciência da Computação", 
            "Engenharia Civil", "Psicologia", "Arquitetura e Urbanismo", "Odontologia", 
            "Fisioterapia", "Medicina Veterinária", "Enfermagem", "Administração"
        ]
        mapa_cursos = {nome: {"id": i + 1, "pesos": [2, 2, 2, 3, 3]} for i, nome in enumerate(cursos_padrao)}

    return mapa_cursos


class SeletorCursoModal(ctk.CTkFrame):
    """
    Componente substituto para o CTkComboBox padrão quando a lista tem muitos itens.
    Resolve o vazamento de tela no Linux, adiciona barra de rolagem nativa e busca em tempo real.
    """
    def __init__(self, master, values, default_val=None, width=260, on_change=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.values = values
        self.on_change = on_change
        self.current_val = default_val or (values[0] if values else "")

        self.btn = ctk.CTkButton(
            self,
            text=f"{self.current_val}  ▾",
            width=width,
            height=32,
            fg_color=("gray85", "gray20"),
            text_color=("gray10", "gray90"),
            border_width=1,
            border_color=("gray70", "gray35"),
            hover_color=("gray75", "gray28"),
            anchor="w",
            font=ctk.CTkFont(size=13),
            command=self.abrir_modal
        )
        self.btn.pack()

    def get(self):
        return self.current_val

    def set(self, val):
        self.current_val = val
        self.btn.configure(text=f"{val}  ▾")
        if self.on_change:
            self.on_change(val)

    def atualizar_valores(self, novos_valores, valor_selecionado=None):
        self.values = novos_valores
        if valor_selecionado and valor_selecionado in novos_valores:
            self.set(valor_selecionado)
        elif self.current_val in novos_valores:
            self.set(self.current_val)
        elif novos_valores:
            self.set(novos_valores[0])

    def abrir_modal(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Selecionar Curso Pretendido")
        dialog.geometry("400x480")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        dialog.update_idletasks()
        try:
            px = self.winfo_toplevel().winfo_x() + (self.winfo_toplevel().winfo_width() // 2) - 200
            py = self.winfo_toplevel().winfo_y() + (self.winfo_toplevel().winfo_height() // 2) - 240
            dialog.geometry(f"+{max(0, px)}+{max(0, py)}")
        except Exception:
            pass

        ctk.CTkLabel(
            dialog, 
            text="Cursos Disponíveis (SISU)", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 5))

        entry_busca = ctk.CTkEntry(
            dialog, 
            placeholder_text="Digite para pesquisar...",
            height=34
        )
        entry_busca.pack(fill="x", padx=20, pady=(5, 10))
        entry_busca.focus()

        scroll = ctk.CTkScrollableFrame(dialog, height=320)
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        def preencher_lista(itens):
            for widget in scroll.winfo_children():
                widget.destroy()

            if not itens:
                ctk.CTkLabel(scroll, text="Nenhum curso encontrado.", text_color="gray").pack(pady=20)
                return

            for curso in itens:
                eh_selecionado = (curso == self.current_val)
                btn_curso = ctk.CTkButton(
                    scroll,
                    text=curso,
                    anchor="w",
                    height=32,
                    fg_color="#1f538d" if eh_selecionado else "transparent",
                    text_color="white" if eh_selecionado else ("gray10", "gray90"),
                    hover_color=("gray75", "gray30"),
                    command=lambda c=curso: [self.set(c), dialog.destroy()]
                )
                btn_curso.pack(fill="x", pady=2)

        preencher_lista(self.values)
        entry_busca.bind("<KeyRelease>", lambda e: preencher_lista([v for v in self.values if entry_busca.get().lower() in v.lower()]))
        dialog.bind("<Escape>", lambda e: dialog.destroy())


class SisuApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Simulador SISU - EDA 2")
        self.geometry("860x960")
        self.resizable(True, True)
        self.minsize(820, 750)

        # Cabeçalho Principal
        self.label_titulo = ctk.CTkLabel(
            self, 
            text="Simulador do SISU", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.label_titulo.pack(pady=(10, 2))

        self.label_subtitulo = ctk.CTkLabel(
            self, 
            text="Radix Sort e Merge Sort", 
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        self.label_subtitulo.pack(pady=(0, 6))

        # Carrega dados dos cursos via C
        self.mapa_cursos = requisitar_cursos_ao_backend_c()
        self.lista_cursos = sorted(list(self.mapa_cursos.keys()))
        self.curso_inicial = self.lista_cursos[0] if self.lista_cursos else "Medicina"

        # Barra Superior de Gerenciamento de Dados (CSVs)
        self.construir_barra_dados_topo()

        # Tabview com as 2 Abas Solicitadas
        self.tabview = ctk.CTkTabview(self, width=820)
        self.tabview.pack(padx=20, pady=(0, 12), fill="both", expand=True)

        self.tab_radix = self.tabview.add("Classificação SISU (Radix Sort)")
        self.tab_merge = self.tabview.add("Relação de Candidatos (Merge Sort)")

        # Estado de Paginação (Aba Merge Sort)
        self.candidatos_merge = []
        self.pagina_atual_merge = 1
        self.itens_por_pagina = 50

        # Estado de Expansão (Aba Radix Sort)
        self.tabela_radix_expandida = False
        self.ultimos_aprovados_radix = []

        # Montagem de cada Aba
        self.construir_aba_radix()
        self.construir_aba_merge()
        self.atualizar_badges_dados()

    def construir_barra_dados_topo(self):
        frame_barra = ctk.CTkFrame(self, fg_color=("gray85", "gray17"), corner_radius=8)
        frame_barra.pack(fill="x", padx=20, pady=(0, 8))

        # Linha 1: Botões de Ação e Badges
        frame_linha1 = ctk.CTkFrame(frame_barra, fg_color="transparent")
        frame_linha1.pack(fill="x", padx=10, pady=(8, 4))

        self.btn_baixar_csv = ctk.CTkButton(
            frame_linha1,
            text="Baixar Base ENEM (CSV)",
            width=180,
            height=32,
            fg_color="#0284c7",
            hover_color="#0369a1",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.iniciar_download_enem
        )
        self.btn_baixar_csv.pack(side="left", padx=(0, 10))

        self.btn_novos_pesos = ctk.CTkButton(
            frame_linha1,
            text="Sortear Novos Pesos (Cursos)",
            width=210,
            height=32,
            fg_color="#7c3aed",
            hover_color="#6d28d9",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.sortear_novos_pesos_cursos
        )
        self.btn_novos_pesos.pack(side="left", padx=(0, 10))

        self.lbl_badge_cursos = ctk.CTkLabel(
            frame_linha1,
            text="Cursos: 50 Ativos",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#4ade80"
        )
        self.lbl_badge_cursos.pack(side="right", padx=(5, 0))

        self.lbl_badge_enem = ctk.CTkLabel(
            frame_linha1,
            text="Base ENEM: Verificando...",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="gray"
        )
        self.lbl_badge_enem.pack(side="right", padx=(10, 12))

        # Linha 2: Status Dinâmico
        self.lbl_status_dados = ctk.CTkLabel(
            frame_barra,
            text="Dados carregados. Clique em 'Sortear Novos Pesos' para gerar novas ponderações para os 50 cursos.",
            font=ctk.CTkFont(size=11),
            text_color="#94a3b8"
        )
        self.lbl_status_dados.pack(fill="x", padx=10, pady=(0, 6))

    def atualizar_badges_dados(self):
        caminho_enem = obter_caminho_raiz("candidatos_limpo.csv")
        if os.path.exists(caminho_enem):
            tam_mb = os.path.getsize(caminho_enem) / (1024 * 1024)
            self.lbl_badge_enem.configure(
                text=f"Base ENEM: Presente ({tam_mb:.0f} MB)",
                text_color="#4ade80"
            )
        else:
            self.lbl_badge_enem.configure(
                text="Base ENEM: Não Encontrado",
                text_color="#ef4444"
            )

        total_cursos = len(self.mapa_cursos)
        if total_cursos > 0:
            self.lbl_badge_cursos.configure(
                text=f"Cursos: {total_cursos} Ativos",
                text_color="#4ade80"
            )
        else:
            self.lbl_badge_cursos.configure(
                text="Cursos: Não Encontrado",
                text_color="#ef4444"
            )

    def sortear_novos_pesos_cursos(self):
        try:
            caminho_cursos = obter_caminho_raiz("cursos.csv")
            gerar_tabela_cursos_dinamica(caminho_cursos, aleatorio=True)

            # Requisita nova lista de cursos com pesos atualizados ao backend C
            self.mapa_cursos = requisitar_cursos_ao_backend_c()
            self.lista_cursos = sorted(list(self.mapa_cursos.keys()))

            # Atualiza os seletores de cursos em ambas as abas
            curso_atual_radix = self.combo_cursos.get()
            self.combo_cursos.atualizar_valores(self.lista_cursos, curso_atual_radix)

            curso_atual_merge = self.combo_merge_curso.get()
            self.combo_merge_curso.atualizar_valores(self.lista_cursos, curso_atual_merge)

            # Atualiza pesos exibidos na tela e recalcula nota se preenchida
            self.ao_mudar_curso(self.combo_cursos.get())
            self.atualizar_badges_dados()

            self.lbl_status_dados.configure(
                text="Novos pesos sorteados (1 a 4) para todos os 50 cursos! Ponderações atualizadas.",
                text_color="#c084fc"
            )
        except Exception as e:
            self.lbl_status_dados.configure(
                text=f"Erro ao sortear pesos: {e}",
                text_color="#ef4444"
            )

    def iniciar_download_enem(self):
        caminho_enem = obter_caminho_raiz("candidatos_limpo.csv")
        if os.path.exists(caminho_enem):
            self.lbl_status_dados.configure(
                text="Arquivo local já existe. Baixando novamente do Google Drive...",
                text_color="#38bdf8"
            )
        else:
            self.lbl_status_dados.configure(
                text="⏳ Conectando ao Google Drive para baixar candidatos_limpo.csv...",
                text_color="#38bdf8"
            )

        self.btn_baixar_csv.configure(state="disabled")
        t = threading.Thread(target=self._executar_download_thread, daemon=True)
        t.start()

    def _executar_download_thread(self):
        try:
            def callback(msg):
                self.after(0, lambda: self.lbl_status_dados.configure(text=msg, text_color="#38bdf8"))

            baixar_candidatos_google_drive(callback_status=callback)

            self.after(0, lambda: [
                self.lbl_status_dados.configure(text="Base do ENEM (candidatos_limpo.csv) pronta no disco!", text_color="#4ade80"),
                self.btn_baixar_csv.configure(state="normal"),
                self.atualizar_badges_dados()
            ])
        except Exception as e:
            self.after(0, lambda: [
                self.lbl_status_dados.configure(text=f"Falha no download: {e}", text_color="#ef4444"),
                self.btn_baixar_csv.configure(state="normal")
            ])

    def construir_aba_radix(self):
        self.frame_inputs = ctk.CTkFrame(self.tab_radix)
        self.frame_inputs.pack(padx=10, pady=5, fill="x")

        # 1. Curso Pretendido
        lbl_curso = ctk.CTkLabel(self.frame_inputs, text="Curso Pretendido:", font=ctk.CTkFont(weight="bold"))
        lbl_curso.grid(row=0, column=0, padx=15, pady=8, sticky="w")

        self.combo_cursos = SeletorCursoModal(
            self.frame_inputs, 
            values=self.lista_cursos, 
            default_val=self.curso_inicial,
            width=280,
            on_change=self.ao_mudar_curso
        )
        self.combo_cursos.grid(row=0, column=1, padx=15, pady=8, sticky="e")

        # 2. Vagas Disponíveis
        lbl_vagas = ctk.CTkLabel(self.frame_inputs, text="Vagas Disponíveis:", font=ctk.CTkFont(weight="bold"))
        lbl_vagas.grid(row=1, column=0, padx=15, pady=8, sticky="w")

        self.entry_vagas = ctk.CTkEntry(self.frame_inputs, placeholder_text="Ex: 40", width=280)
        self.entry_vagas.grid(row=1, column=1, padx=15, pady=8, sticky="e")

        # 3. Notas do ENEM
        lbl_secao_notas = ctk.CTkLabel(self.frame_inputs, text="Suas Notas do ENEM:", font=ctk.CTkFont(size=13, weight="bold"))
        lbl_secao_notas.grid(row=2, column=0, columnspan=2, padx=15, pady=(8, 4))

        frame_notas_grid = ctk.CTkFrame(self.frame_inputs, fg_color="transparent")
        frame_notas_grid.grid(row=3, column=0, columnspan=2, padx=10, pady=(0, 6))

        materias = [
            ("Natureza (CN)", "entry_cn"),
            ("Humanas (CH)", "entry_ch"),
            ("Linguagens (LC)", "entry_lc"),
            ("Matemática (MT)", "entry_mt"),
            ("Redação (RED)", "entry_red")
        ]

        self.entries_notas = {}
        for idx, (rotulo, var_nome) in enumerate(materias):
            col_frame = ctk.CTkFrame(frame_notas_grid, fg_color="transparent")
            col_frame.grid(row=0, column=idx, padx=5)

            ctk.CTkLabel(col_frame, text=rotulo, font=ctk.CTkFont(size=11, weight="bold")).pack(pady=(0, 2))
            ent = ctk.CTkEntry(col_frame, placeholder_text="Ex: 720.5", width=95, justify="center")
            ent.pack()
            self.entries_notas[var_nome] = ent

        # Pesos do curso
        self.label_pesos = ctk.CTkLabel(self.frame_inputs, text="", font=ctk.CTkFont(size=12), text_color="gray")
        self.label_pesos.grid(row=4, column=0, columnspan=2, padx=15, pady=(2, 8))

        # Cálculo da nota individual
        frame_calc = ctk.CTkFrame(self.frame_inputs, fg_color="transparent")
        frame_calc.grid(row=5, column=0, columnspan=2, padx=15, pady=(0, 10))

        btn_calc = ctk.CTkButton(
            frame_calc, text="Calcular Minha Nota", command=self.calcular_nota_candidato,
            fg_color="#d97706", hover_color="#b45309", width=160
        )
        btn_calc.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(frame_calc, text="Nota Ponderada:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0, 8))
        self.entry_nota_calculada = ctk.CTkEntry(frame_calc, width=100, justify="center", font=ctk.CTkFont(size=14, weight="bold"), placeholder_text="---")
        self.entry_nota_calculada.pack(side="left")
        self.entry_nota_calculada.configure(state="readonly")

        self.ao_mudar_curso(self.curso_inicial)

        # Botão de Simulação Radix Sort
        self.btn_simular = ctk.CTkButton(
            self.tab_radix, text="Simular Classificação SISU", command=self.simular_sisu,
            fg_color="#1f538d", hover_color="#14375e", font=ctk.CTkFont(size=15, weight="bold"), width=360, height=36
        )
        self.btn_simular.pack(pady=8)

        # Seção de Resultados Radix
        self.frame_res_radix = ctk.CTkFrame(self.tab_radix)
        self.frame_res_radix.pack(padx=10, pady=(0, 10), fill="both", expand=True)

        # Banner de Status com Botão de Expandir Tabela no canto direito
        self.frame_banner = ctk.CTkFrame(self.frame_res_radix, corner_radius=8, border_width=1, fg_color="#1e293b", border_color="#334155")
        self.frame_banner.pack(fill="x", padx=15, pady=(8, 4))

        frame_banner_info = ctk.CTkFrame(self.frame_banner, fg_color="transparent")
        frame_banner_info.pack(side="left", fill="both", expand=True, padx=(12, 5), pady=6)

        self.label_banner_titulo = ctk.CTkLabel(frame_banner_info, text="Pronto para Simular", font=ctk.CTkFont(size=14, weight="bold"), text_color="#94a3b8", anchor="w")
        self.label_banner_titulo.pack(fill="x", pady=(1, 1))
        self.label_banner_sub = ctk.CTkLabel(frame_banner_info, text="Informe as vagas e clique em 'Simular' para ver a nota de corte e os classificados.", font=ctk.CTkFont(size=12), text_color="#cbd5e1", anchor="w")
        self.label_banner_sub.pack(fill="x")

        # Botões de Ação para Expandir Tabela
        frame_banner_botoes = ctk.CTkFrame(self.frame_banner, fg_color="transparent")
        frame_banner_botoes.pack(side="right", padx=(5, 12), pady=6)

        self.btn_expandir_radix = ctk.CTkButton(
            frame_banner_botoes,
            text="⛶ Expandir Tabela",
            width=140,
            height=32,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.alternar_expansao_tabela_radix
        )
        self.btn_expandir_radix.pack(side="left", padx=3)

        self.btn_modal_radix = ctk.CTkButton(
            frame_banner_botoes,
            text="🗖 Nova Janela",
            width=110,
            height=32,
            fg_color="#475569",
            hover_color="#334155",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.abrir_modal_tabela_radix
        )
        self.btn_modal_radix.pack(side="left", padx=3)

        # Cards de Métricas
        frame_cards = ctk.CTkFrame(self.frame_res_radix, fg_color="transparent")
        frame_cards.pack(fill="x", padx=15, pady=4)
        for c in range(4): frame_cards.grid_columnconfigure(c, weight=1)

        self.card_corte = ctk.CTkFrame(frame_cards, corner_radius=8, border_width=1, border_color="gray30")
        self.card_corte.grid(row=0, column=0, padx=4, sticky="ew")
        ctk.CTkLabel(self.card_corte, text="Nota de Corte", font=ctk.CTkFont(size=11), text_color="gray").pack(pady=(5, 1))
        self.lbl_card_corte = ctk.CTkLabel(self.card_corte, text="---", font=ctk.CTkFont(size=15, weight="bold"), text_color="#f59e0b")
        self.lbl_card_corte.pack(pady=(0, 5))

        self.card_sua_nota = ctk.CTkFrame(frame_cards, corner_radius=8, border_width=1, border_color="gray30")
        self.card_sua_nota.grid(row=0, column=1, padx=4, sticky="ew")
        ctk.CTkLabel(self.card_sua_nota, text="Sua Nota", font=ctk.CTkFont(size=11), text_color="gray").pack(pady=(5, 1))
        self.lbl_card_sua_nota = ctk.CTkLabel(self.card_sua_nota, text="---", font=ctk.CTkFont(size=15, weight="bold"), text_color="#38bdf8")
        self.lbl_card_sua_nota.pack(pady=(0, 5))

        self.card_inscritos = ctk.CTkFrame(frame_cards, corner_radius=8, border_width=1, border_color="gray30")
        self.card_inscritos.grid(row=0, column=2, padx=4, sticky="ew")
        ctk.CTkLabel(self.card_inscritos, text="Concorrentes", font=ctk.CTkFont(size=11), text_color="gray").pack(pady=(5, 1))
        self.lbl_card_inscritos = ctk.CTkLabel(self.card_inscritos, text="---", font=ctk.CTkFont(size=15, weight="bold"), text_color="#60a5fa")
        self.lbl_card_inscritos.pack(pady=(0, 5))

        self.card_tempo = ctk.CTkFrame(frame_cards, corner_radius=8, border_width=1, border_color="gray30")
        self.card_tempo.grid(row=0, column=3, padx=4, sticky="ew")
        ctk.CTkLabel(self.card_tempo, text="Tempo Radix", font=ctk.CTkFont(size=11), text_color="gray").pack(pady=(5, 1))
        self.lbl_card_tempo = ctk.CTkLabel(self.card_tempo, text="---", font=ctk.CTkFont(size=15, weight="bold"), text_color="#a855f7")
        self.lbl_card_tempo.pack(pady=(0, 5))

        # Cabeçalho da Tabela
        header = ctk.CTkFrame(self.frame_res_radix, fg_color=("gray75", "gray22"), height=28, corner_radius=6)
        header.pack(fill="x", padx=15, pady=(6, 2))
        ctk.CTkLabel(header, text="Pos", width=50, font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=(10, 5))
        ctk.CTkLabel(header, text="Nome do Candidato", width=280, anchor="w", font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Nota Final", width=100, font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Inscrição", width=120, font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Situação", width=110, font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=5)

        # Tabela Scrollable
        self.scroll_tabela = ctk.CTkScrollableFrame(self.frame_res_radix, height=220)
        self.scroll_tabela.pack(fill="both", expand=True, padx=15, pady=(0, 10))

    def alternar_expansao_tabela_radix(self):
        """
        Alterna a visualização entre o formulário completo e a tabela expandida em 100% da tela.
        """
        self.tabela_radix_expandida = not self.tabela_radix_expandida
        if self.tabela_radix_expandida:
            self.frame_inputs.pack_forget()
            self.btn_simular.pack_forget()
            self.btn_expandir_radix.configure(text="🗗 Recolher Tabela", fg_color="#475569", hover_color="#334155")
            self.scroll_tabela.configure(height=580)
        else:
            self.frame_res_radix.pack_forget()
            self.frame_inputs.pack(padx=10, pady=5, fill="x")
            self.btn_simular.pack(pady=8)
            self.frame_res_radix.pack(padx=10, pady=(0, 10), fill="both", expand=True)
            self.btn_expandir_radix.configure(text="⛶ Expandir Tabela", fg_color="#2563eb", hover_color="#1d4ed8")
            self.scroll_tabela.configure(height=220)

    def abrir_modal_tabela_radix(self):
        """
        Abre uma janela pop-up separada com a tabela completa em tela cheia.
        """
        if not self.ultimos_aprovados_radix:
            return

        curso_nome = self.combo_cursos.get()
        total_vagas = len(self.ultimos_aprovados_radix)

        modal = ctk.CTkToplevel(self)
        modal.title(f"Classificação Completa — {curso_nome} ({total_vagas} Vagas)")
        modal.geometry("860x720")
        modal.minsize(700, 500)
        modal.transient(self)

        top_info = ctk.CTkFrame(modal, fg_color="transparent")
        top_info.pack(fill="x", padx=20, pady=(15, 8))

        ctk.CTkLabel(
            top_info, 
            text=f"Lista Completa de Aprovados: {curso_nome}", 
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(anchor="w")

        nota_corte_val = self.ultimos_aprovados_radix[-1][3] if self.ultimos_aprovados_radix else 0.0
        ctk.CTkLabel(
            top_info, 
            text=f"Total de {total_vagas} vagas preenchidas  |  Nota de corte: {nota_corte_val:.1f} pontos", 
            font=ctk.CTkFont(size=13), 
            text_color="#94a3b8"
        ).pack(anchor="w", pady=(2, 0))

        header_m = ctk.CTkFrame(modal, fg_color=("gray75", "gray22"), height=30, corner_radius=6)
        header_m.pack(fill="x", padx=20, pady=(6, 2))
        ctk.CTkLabel(header_m, text="Pos", width=50, font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(10, 5))
        ctk.CTkLabel(header_m, text="Nome do Candidato", width=300, anchor="w", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header_m, text="Nota Final", width=100, font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header_m, text="Inscrição", width=120, font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header_m, text="Situação", width=120, font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=5)

        scroll_m = ctk.CTkScrollableFrame(modal, height=560)
        scroll_m.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        for pos, inscricao, nome, nota in self.ultimos_aprovados_radix:
            eh_corte = (pos == total_vagas)
            cor_linha = ("#fef3c7", "#1e1b18") if eh_corte else (("gray95", "gray17") if pos % 2 == 0 else ("gray90", "gray14"))
            row = ctk.CTkFrame(scroll_m, fg_color=cor_linha, corner_radius=6, height=30)
            row.pack(fill="x", pady=2, padx=2)

            ctk.CTkLabel(row, text=f"{pos}º", width=50, font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(10, 5))
            ctk.CTkLabel(row, text=nome, width=300, anchor="w", font=ctk.CTkFont(size=12)).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=f"{nota:.1f}", width=100, font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=str(inscricao), width=120, font=ctk.CTkFont(size=11), text_color="gray").pack(side="left", padx=5)

            badge = ctk.CTkLabel(
                row, text="Nota de Corte" if eh_corte else "Aprovado", width=120, 
                fg_color="#b45309" if eh_corte else "#047857", text_color="white", 
                corner_radius=4, font=ctk.CTkFont(size=10, weight="bold")
            )
            badge.pack(side="left", padx=5, pady=4)

    def construir_aba_merge(self):
        frame_top = ctk.CTkFrame(self.tab_merge)
        frame_top.pack(padx=10, pady=8, fill="x")

        lbl_curso = ctk.CTkLabel(frame_top, text="Selecione o Curso para Listar Candidatos:", font=ctk.CTkFont(weight="bold"))
        lbl_curso.pack(pady=(8, 4))

        self.combo_merge_curso = SeletorCursoModal(
            frame_top, 
            values=self.lista_cursos, 
            default_val=self.curso_inicial,
            width=320
        )
        self.combo_merge_curso.pack(pady=4)

        btn_ordenar_merge = ctk.CTkButton(
            frame_top,
            text="Ordenar Nomes (Ordem Alfabética)",
            command=self.executar_merge_sort,
            fg_color="#2e7d32",
            hover_color="#1e5622",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=36
        )
        btn_ordenar_merge.pack(pady=(6, 10))

        # Cards de Métricas do Merge Sort
        self.frame_cards_merge = ctk.CTkFrame(self.tab_merge, fg_color="transparent")
        self.frame_cards_merge.pack(fill="x", padx=10, pady=4)
        for c in range(3): self.frame_cards_merge.grid_columnconfigure(c, weight=1)

        # Card 1: Curso
        self.card_m_curso = ctk.CTkFrame(self.frame_cards_merge, corner_radius=8, border_width=1, border_color="gray30")
        self.card_m_curso.grid(row=0, column=0, padx=4, sticky="ew")
        ctk.CTkLabel(self.card_m_curso, text="Curso Pretendido", font=ctk.CTkFont(size=11), text_color="gray").pack(pady=(5, 1))
        self.lbl_merge_curso = ctk.CTkLabel(self.card_m_curso, text="---", font=ctk.CTkFont(size=14, weight="bold"), text_color="#38bdf8")
        self.lbl_merge_curso.pack(pady=(0, 5))

        # Card 2: Concorrentes
        self.card_m_total = ctk.CTkFrame(self.frame_cards_merge, corner_radius=8, border_width=1, border_color="gray30")
        self.card_m_total.grid(row=0, column=1, padx=4, sticky="ew")
        ctk.CTkLabel(self.card_m_total, text="Total de Concorrentes", font=ctk.CTkFont(size=11), text_color="gray").pack(pady=(5, 1))
        self.lbl_merge_total = ctk.CTkLabel(self.card_m_total, text="---", font=ctk.CTkFont(size=15, weight="bold"), text_color="#60a5fa")
        self.lbl_merge_total.pack(pady=(0, 5))

        # Card 3: Tempo Merge Sort
        self.card_m_tempo = ctk.CTkFrame(self.frame_cards_merge, corner_radius=8, border_width=1, border_color="gray30")
        self.card_m_tempo.grid(row=0, column=2, padx=4, sticky="ew")
        ctk.CTkLabel(self.card_m_tempo, text="Tempo Merge Sort O(N log N)", font=ctk.CTkFont(size=11), text_color="gray").pack(pady=(5, 1))
        self.lbl_merge_tempo = ctk.CTkLabel(self.card_m_tempo, text="---", font=ctk.CTkFont(size=15, weight="bold"), text_color="#22c55e")
        self.lbl_merge_tempo.pack(pady=(0, 5))

        # Banner de Arquivo Gerado
        self.label_merge_arquivo = ctk.CTkLabel(
            self.tab_merge, 
            text="Clique em 'Ordenar Nomes' para gerar o relatório alfabético completo.",
            font=ctk.CTkFont(size=12),
            text_color="#94a3b8"
        )
        self.label_merge_arquivo.pack(pady=(4, 6))

        # Cabeçalho da Tabela do Merge Sort
        frame_tabela_merge = ctk.CTkFrame(self.tab_merge)
        frame_tabela_merge.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        header_m = ctk.CTkFrame(frame_tabela_merge, fg_color=("gray75", "gray22"), height=28, corner_radius=6)
        header_m.pack(fill="x", padx=10, pady=(6, 2))
        ctk.CTkLabel(header_m, text="Nº", width=50, font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=(10, 5))
        ctk.CTkLabel(header_m, text="Nome do Candidato (Ordem Alfabética)", width=280, anchor="w", font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header_m, text="Inscrição", width=120, font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header_m, text="Nota Ponderada", width=110, font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=5)

        self.scroll_tabela_merge = ctk.CTkScrollableFrame(frame_tabela_merge, height=260)
        self.scroll_tabela_merge.pack(fill="both", expand=True, padx=10, pady=(0, 4))

        # Barra de Navegação e Paginação (50 por página)
        self.frame_paginacao = ctk.CTkFrame(frame_tabela_merge, fg_color="transparent")
        self.frame_paginacao.pack(fill="x", padx=10, pady=(4, 6))

        self.btn_ant_pagina = ctk.CTkButton(
            self.frame_paginacao,
            text="Anterior",
            width=110,
            height=30,
            command=self.pagina_anterior_merge,
            state="disabled"
        )
        self.btn_ant_pagina.pack(side="left", padx=5)

        self.lbl_info_pagina = ctk.CTkLabel(
            self.frame_paginacao,
            text="Página 0 de 0 (0 candidatos)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="gray"
        )
        self.lbl_info_pagina.pack(side="left", expand=True)

        self.btn_prox_pagina = ctk.CTkButton(
            self.frame_paginacao,
            text="Próxima",
            width=110,
            height=30,
            command=self.proxima_pagina_merge,
            state="disabled"
        )
        self.btn_prox_pagina.pack(side="right", padx=5)

    # =========================================================================
    # LÓGICA DE EXECUÇÃO E EVENTOS
    # =========================================================================
    def ao_mudar_curso(self, novo_curso):
        info = self.mapa_cursos.get(novo_curso, {})
        pesos = info.get("pesos", [1, 1, 1, 1, 1])
        self.label_pesos.configure(
            text=f"Pesos de {novo_curso}: CN ({pesos[0]}) | CH ({pesos[1]}) | LC ({pesos[2]}) | MT ({pesos[3]}) | RED ({pesos[4]})"
        )
        if any(self.entries_notas[k].get().strip() for k in self.entries_notas):
            self.calcular_nota_candidato()

    def calcular_nota_candidato(self):
        curso = self.combo_cursos.get()
        info = self.mapa_cursos.get(curso, {})
        pesos = info.get("pesos", [1, 1, 1, 1, 1])

        try:
            notas = []
            for chave in ["entry_cn", "entry_ch", "entry_lc", "entry_mt", "entry_red"]:
                val_txt = self.entries_notas[chave].get().strip().replace(",", ".")
                if not val_txt:
                    raise ValueError("Nota em branco")
                val_float = float(val_txt)
                if val_float < 0 or val_float > 1000:
                    raise ValueError("Nota fora do intervalo (0 a 1000)")
                notas.append(val_float)

            soma_pesos = sum(pesos) if sum(pesos) > 0 else 1
            soma_ponderada = sum(n * p for n, p in zip(notas, pesos))
            nota_final = soma_ponderada / soma_pesos

            resultado_txt = f"{nota_final:.1f}"

            self.entry_nota_calculada.configure(state="normal")
            self.entry_nota_calculada.delete(0, "end")
            self.entry_nota_calculada.insert(0, resultado_txt)
            self.entry_nota_calculada.configure(state="readonly")
            self.lbl_card_sua_nota.configure(text=resultado_txt, text_color="#10b981")

        except ValueError:
            self.entry_nota_calculada.configure(state="normal")
            self.entry_nota_calculada.delete(0, "end")
            self.entry_nota_calculada.insert(0, "Erro")
            self.entry_nota_calculada.configure(state="readonly")
            self.lbl_card_sua_nota.configure(text="---", text_color="gray")

    def simular_sisu(self):
        curso_nome = self.combo_cursos.get()
        info_curso = self.mapa_cursos.get(curso_nome, {})
        id_curso = info_curso.get("id", 1)

        vagas_str = self.entry_vagas.get().strip() or "40"
        try:
            vagas = int(vagas_str)
            if vagas <= 0: vagas = 40
        except ValueError:
            vagas = 40

        tem_notas = any(self.entries_notas[k].get().strip() for k in self.entries_notas)
        minha_nota = None
        if tem_notas:
            try:
                self.calcular_nota_candidato()
                txt_calc = self.entry_nota_calculada.get().strip()
                if txt_calc and txt_calc != "Erro" and txt_calc != "---":
                    minha_nota = float(txt_calc)
            except Exception:
                minha_nota = None

        caminhos_binario = ["./back/main.out", "../back/main.out", "main.out", "./main.out"]
        binario = None
        for caminho in caminhos_binario:
            if os.path.exists(caminho):
                binario = caminho
                break

        if not binario:
            self.label_banner_titulo.configure(text="Erro de Execução", text_color="#ef4444")
            self.label_banner_sub.configure(text="Executável do backend C ('main.out') não encontrado!")
            return

        self.label_banner_titulo.configure(text="Processando Radix Sort...", text_color="#38bdf8")
        self.label_banner_sub.configure(text="Executando backend em C com ordenação de alta performance...")
        self.update_idletasks()

        try:
            cmd = [binario, "--simular", str(id_curso), str(vagas)]
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)

            linhas = res.stdout.strip().split("\n")
            dados = {}
            aprovados = []
            lendo_aprovados = False

            for l in linhas:
                l = l.strip()
                if not l: continue
                if l == "APROVADOS:":
                    lendo_aprovados = True
                    continue
                if lendo_aprovados:
                    partes = l.split(";")
                    if len(partes) >= 4:
                        pos = int(partes[0])
                        inscricao = partes[1]
                        nome = partes[2]
                        nota = float(partes[3])
                        aprovados.append((pos, inscricao, nome, nota))
                elif ":" in l:
                    k, v = l.split(":", 1)
                    dados[k] = v

            corte = float(dados.get("CORTE", "0.0"))
            tempo = float(dados.get("TEMPO", "0.0"))
            total_inscritos = int(dados.get("TOTAL_INSCRITOS", "0"))

            self.lbl_card_corte.configure(text=f"{corte:.1f}")
            self.lbl_card_inscritos.configure(text=f"{total_inscritos:,}".replace(",", "."))
            self.lbl_card_tempo.configure(text=f"{tempo:.4f}s")

            if minha_nota is not None:
                self.lbl_card_sua_nota.configure(text=f"{minha_nota:.1f}")
                diferenca = minha_nota - corte

                if minha_nota >= corte:
                    self.frame_banner.configure(fg_color="#064e3b", border_color="#059669")
                    self.label_banner_titulo.configure(
                        text="PARABÉNS! VOCÊ SERIA APROVADO(A) NESTE CURSO!", text_color="#6ee7b7"
                    )
                    self.label_banner_sub.configure(
                        text=f"Sua Nota: {minha_nota:.1f}  |  Nota de Corte: {corte:.1f}  (Margem de segurança: +{diferenca:.1f} pontos)",
                        text_color="#d1fae5"
                    )
                    self.lbl_card_sua_nota.configure(text_color="#10b981")
                else:
                    self.frame_banner.configure(fg_color="#450a0a", border_color="#dc2626")
                    self.label_banner_titulo.configure(
                        text="VOCÊ NÃO PASSARIA NESTA EDIÇÃO DO SISU", text_color="#fca5a5"
                    )
                    self.label_banner_sub.configure(
                        text=f"Sua Nota: {minha_nota:.1f}  |  Nota de Corte: {corte:.1f}  (Faltaram {abs(diferenca):.1f} pontos para a última vaga)",
                        text_color="#fee2e2"
                    )
                    self.lbl_card_sua_nota.configure(text_color="#ef4444")
            else:
                self.lbl_card_sua_nota.configure(text="---", text_color="gray")
                self.frame_banner.configure(fg_color="#1e293b", border_color="#3b82f6")
                self.label_banner_titulo.configure(
                    text=f"Classificação para {vagas} vagas em {curso_nome}", text_color="#93c5fd"
                )
                self.label_banner_sub.configure(
                    text=f"Nota de Corte: {corte:.1f} pontos | Simulação sem nota individual informada.",
                    text_color="#e2e8f0"
                )

            self.ultimos_aprovados_radix = aprovados

            for w in self.scroll_tabela.winfo_children():
                w.destroy()

            for pos, inscricao, nome, nota in aprovados:
                eh_corte = (pos == len(aprovados))
                cor_linha = ("#fef3c7", "#1e1b18") if eh_corte else (("gray95", "gray17") if pos % 2 == 0 else ("gray90", "gray14"))
                
                row = ctk.CTkFrame(self.scroll_tabela, fg_color=cor_linha, corner_radius=6, height=30)
                row.pack(fill="x", pady=2, padx=2)

                ctk.CTkLabel(row, text=f"{pos}º", width=50, font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(10, 5))
                ctk.CTkLabel(row, text=nome, width=280, anchor="w", font=ctk.CTkFont(size=12)).pack(side="left", padx=5)
                ctk.CTkLabel(row, text=f"{nota:.1f}", width=100, font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=5)
                ctk.CTkLabel(row, text=str(inscricao), width=120, font=ctk.CTkFont(size=11), text_color="gray").pack(side="left", padx=5)

                badge = ctk.CTkLabel(
                    row, text="Nota de Corte" if eh_corte else "Aprovado", width=110, 
                    fg_color="#b45309" if eh_corte else "#047857", text_color="white", 
                    corner_radius=4, font=ctk.CTkFont(size=10, weight="bold")
                )
                badge.pack(side="left", padx=5, pady=4)

        except Exception as e:
            self.label_banner_titulo.configure(text="Erro ao Executar Simulação", text_color="#ef4444")
            self.label_banner_sub.configure(text=str(e))

    def executar_merge_sort(self):
        curso_nome = self.combo_merge_curso.get()
        info_curso = self.mapa_cursos.get(curso_nome, {})
        id_curso = info_curso.get("id", 1)

        caminhos_binario = ["./back/main.out", "../back/main.out", "main.out", "./main.out"]
        binario = None
        for caminho in caminhos_binario:
            if os.path.exists(caminho):
                binario = caminho
                break

        if not binario:
            self.label_merge_arquivo.configure(text="[Erro] Binário C não encontrado!", text_color="#ef4444")
            return

        self.label_merge_arquivo.configure(text=f"Executando Merge Sort em todos os inscritos de {curso_nome}...", text_color="#38bdf8")
        self.update_idletasks()

        try:
            cmd = [binario, "--merge", str(id_curso)]
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)

            linhas = res.stdout.strip().split("\n")
            dados = {}
            candidatos = []
            lendo_candidatos = False

            for l in linhas:
                l = l.strip()
                if not l: continue
                if l == "CANDIDATOS:":
                    lendo_candidatos = True
                    continue
                if lendo_candidatos:
                    partes = l.split(";")
                    if len(partes) >= 4:
                        pos = int(partes[0])
                        inscricao = partes[1]
                        nome = partes[2]
                        nota = float(partes[3])
                        candidatos.append((pos, inscricao, nome, nota))
                elif ":" in l:
                    k, v = l.split(":", 1)
                    dados[k] = v

            tempo = float(dados.get("TEMPO", "0.0"))
            total = int(dados.get("TOTAL_INSCRITOS", "0"))
            arquivo = dados.get("ARQUIVO", f"nomes_ordenados_curso_{id_curso}.txt")

            # Atualiza os Cards da Aba Merge
            self.lbl_merge_curso.configure(text=curso_nome)
            self.lbl_merge_total.configure(text=f"{total:,}".replace(",", ".") + " alunos")
            self.lbl_merge_tempo.configure(text=f"{tempo:.4f}s")
            self.label_merge_arquivo.configure(
                text=f"Relatório completo gerado no disco: '{arquivo}' (com todos os {total:,} nomes ordenados de A a Z)".replace(",", "."),
                text_color="#4ade80"
            )

            # Armazena todos os candidatos e inicializa paginação de 50 por página
            self.candidatos_merge = candidatos
            self.pagina_atual_merge = 1
            self.renderizar_pagina_merge()

        except Exception as e:
            self.label_merge_arquivo.configure(text=f"[Erro]: {e}", text_color="#ef4444")

    def renderizar_pagina_merge(self):
        total = len(self.candidatos_merge)
        if total == 0:
            for w in self.scroll_tabela_merge.winfo_children():
                w.destroy()
            self.lbl_info_pagina.configure(text="Página 0 de 0 (0 candidatos)")
            self.btn_ant_pagina.configure(state="disabled")
            self.btn_prox_pagina.configure(state="disabled")
            return

        total_paginas = max(1, math.ceil(total / self.itens_por_pagina))
        if self.pagina_atual_merge > total_paginas:
            self.pagina_atual_merge = total_paginas
        if self.pagina_atual_merge < 1:
            self.pagina_atual_merge = 1

        idx_inicio = (self.pagina_atual_merge - 1) * self.itens_por_pagina
        idx_fim = min(idx_inicio + self.itens_por_pagina, total)
        fatia = self.candidatos_merge[idx_inicio:idx_fim]

        # Limpa widgets da página anterior
        for w in self.scroll_tabela_merge.winfo_children():
            w.destroy()

        # Renderiza os 50 itens da página atual
        for pos, inscricao, nome, nota in fatia:
            cor_linha = ("gray95", "gray17") if pos % 2 == 0 else ("gray90", "gray14")
            row = ctk.CTkFrame(self.scroll_tabela_merge, fg_color=cor_linha, corner_radius=6, height=28)
            row.pack(fill="x", pady=2, padx=2)

            ctk.CTkLabel(row, text=f"{pos}º", width=50, font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=(10, 5))
            ctk.CTkLabel(row, text=nome, width=280, anchor="w", font=ctk.CTkFont(size=12)).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=str(inscricao), width=120, font=ctk.CTkFont(size=11), text_color="gray").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=f"{nota:.1f} pts", width=110, font=ctk.CTkFont(size=11, weight="bold"), text_color="#38bdf8").pack(side="left", padx=5)

        # Atualiza controles de paginação
        self.lbl_info_pagina.configure(
            text=f"Página {self.pagina_atual_merge} de {total_paginas} (Mostrando {idx_inicio + 1:,} a {idx_fim:,} de {total:,} inscritos)".replace(",", ".")
        )
        self.btn_ant_pagina.configure(state="normal" if self.pagina_atual_merge > 1 else "disabled")
        self.btn_prox_pagina.configure(state="normal" if self.pagina_atual_merge < total_paginas else "disabled")

    def proxima_pagina_merge(self):
        total_paginas = max(1, math.ceil(len(self.candidatos_merge) / self.itens_por_pagina))
        if self.pagina_atual_merge < total_paginas:
            self.pagina_atual_merge += 1
            self.renderizar_pagina_merge()

    def pagina_anterior_merge(self):
        if self.pagina_atual_merge > 1:
            self.pagina_atual_merge -= 1
            self.renderizar_pagina_merge()

if __name__ == "__main__":
    app = SisuApp()
    app.mainloop()