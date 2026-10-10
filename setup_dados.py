import os
import csv
import urllib.request
import urllib.error
import gdown

def gerar_tabela_cursos():
    saida_cursos = "cursos.csv"
    print(f"Gerando tabela de cursos em: {saida_cursos}...")
    
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
    
    import random
    random.seed(42)
    
    with open(saida_cursos, mode='w', encoding='utf-8', newline='') as f_out:
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
            
    print("Tabela de cursos criada com sucesso!")

def baixar_candidatos_drive():
    file_id = '1WsxGZrNSvKYDSSPA6ly-0jQ8Gd9XB2KL'
    url = f'https://drive.google.com/uc?id={file_id}'
    output = 'candidatos_limpo.csv'
    
    if os.path.exists(output):
        print(f"O arquivo {output} já existe. Pulando download.")
        return


    print("Verificando conexão com a internet...")
    try:
        urllib.request.urlopen('https://www.google.com', timeout=3)
    except urllib.error.URLError:
        print("Erro: Sem conexão com a internet. Verifique sua rede para baixar os dados do ENEM.")
        return
    print("Iniciando o download da base de dados do Google Drive (Isso pode levar alguns instantes)...")
    try:
        gdown.download(url, output, quiet=False)
        print("Download concluído com sucesso!")
    except ImportError:
        print("Erro: A biblioteca 'gdown' não está instalada.")
        print("Abra o terminal e digite: pip install gdown")
        print("Depois tente rodar o script novamente.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante o download: {e}")

if __name__ == "__main__":
    print("--- INICIANDO SETUP DO AMBIENTE ---")
    baixar_candidatos_drive()
    gerar_tabela_cursos()
    print("--- SETUP FINALIZADO ---")
