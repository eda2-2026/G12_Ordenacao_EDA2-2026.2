import customtkinter as ctk
import csv
import os
import sys

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

def carregar_cursos_ordenados():
    #carrega os cursos da base de dados e ordena
    caminhos = ["back/cursos.csv", "cursos.csv", "../back/cursos.csv"]
    cursos = []
    
    for caminho in caminhos:
        if os.path.exists(caminho):
            with open(caminho, mode='r', encoding='utf-8') as f:
                leitor = csv.reader(f)
                next(leitor, None) 
                for linha in leitor:
                    if len(linha) >= 2:
                        cursos.append(linha[1])
            break

    #caso setup_dados.py ainda nao tenha sido executado
    if not cursos:
        cursos = [
            "Medicina", "Direito", "Engenharia de Software", "Ciência da Computação", 
            "Engenharia Civil", "Psicologia", "Arquitetura e Urbanismo", "Odontologia", 
            "Fisioterapia", "Medicina Veterinária", "Enfermagem", "Administração"
        ]

    #ordena alfabeticamente
    return sorted(cursos)

class SisuApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Simulador SISU - EDA 2")
        self.geometry("650x600")
        self.resizable(False, False)

        #cabeçalho
        self.label_titulo = ctk.CTkLabel(
            self, 
            text="Simulador do SISU", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.label_titulo.pack(pady=(20, 5))

        self.label_subtitulo = ctk.CTkLabel(
            self, 
            text="Classificação de candidatos utilizando Algoritmos de Ordenação", 
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        self.label_subtitulo.pack(pady=(0, 20))

        self.frame_inputs = ctk.CTkFrame(self)
        self.frame_inputs.pack(padx=30, pady=10, fill="x")

        #1. Menu de Selecao de Curso
        self.label_curso = ctk.CTkLabel(
            self.frame_inputs, 
            text="Curso Pretendido:", 
            font=ctk.CTkFont(weight="bold")
        )
        self.label_curso.grid(row=0, column=0, padx=15, pady=15, sticky="w")

        self.lista_cursos = carregar_cursos_ordenados()
        self.combo_cursos = ctk.CTkComboBox(
            self.frame_inputs, 
            values=self.lista_cursos, 
            width=260
        )
        self.combo_cursos.grid(row=0, column=1, padx=15, pady=15, sticky="e")
        self.combo_cursos.set(self.lista_cursos[0])

        # 2. Vagas Disponiveis
        self.label_vagas = ctk.CTkLabel(
            self.frame_inputs, 
            text="Vagas Disponíveis:", 
            font=ctk.CTkFont(weight="bold")
        )
        self.label_vagas.grid(row=1, column=0, padx=15, pady=15, sticky="w")

        self.entry_vagas = ctk.CTkEntry(
            self.frame_inputs, 
            placeholder_text="Ex: 40", 
            width=260
        )
        self.entry_vagas.grid(row=1, column=1, padx=15, pady=15, sticky="e")

        #Botões
        self.frame_botoes = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_botoes.pack(pady=15)

        self.btn_radix = ctk.CTkButton(
            self.frame_botoes, 
            text="Simular (Radix Sort - Notas)", 
            command=self.simular_radix,
            fg_color="#1f538d"
        )
        self.btn_radix.pack(side="left", padx=10)

        self.btn_merge = ctk.CTkButton(
            self.frame_botoes, 
            text="Simular (Merge Sort - Nomes)", 
            command=self.simular_merge,
            fg_color="#2e7d32"
        )
        self.btn_merge.pack(side="left", padx=10)

        #Resultados
        self.textbox_resultado = ctk.CTkTextbox(self, width=590, height=200)
        self.textbox_resultado.pack(padx=30, pady=10)
        self.textbox_resultado.insert("1.0", "Selecione o curso, informe o total de vagas e clique em simular.\n")

    def simular_radix(self):
        curso = self.combo_cursos.get()
        vagas = self.entry_vagas.get().strip() or "Não informada"
        self.textbox_resultado.delete("1.0", "end")
        self.textbox_resultado.insert("end", f"--- Simulação com Radix Sort ---\n")
        self.textbox_resultado.insert("end", f"Curso: {curso}\nVagas: {vagas}\n\n")
        self.textbox_resultado.insert("end", "[Pronto para receber a integração com o binário C]\n")

    def simular_merge(self):
        curso = self.combo_cursos.get()
        vagas = self.entry_vagas.get().strip() or "Não informada"
        self.textbox_resultado.delete("1.0", "end")
        self.textbox_resultado.insert("end", f"--- Simulação com Merge Sort ---\n")
        self.textbox_resultado.insert("end", f"Curso: {curso}\nVagas: {vagas}\n\n")
        self.textbox_resultado.insert("end", "[Pronto para receber a integração com o binário C]\n")

if __name__ == "__main__":
    app = SisuApp()
    app.mainloop()