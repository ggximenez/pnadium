from ftplib import FTP
import re
import pandas as pd
import zipfile
import os
import numpy as np
import shutil
from unidecode import unidecode
from appdirs import user_cache_dir

def clear_cache():
    cache_dir = user_cache_dir("pnadium")
    shutil.rmtree(cache_dir)

def get_default_path():
    cache_dir = user_cache_dir("pnadium")
    return os.path.join(cache_dir, 'dados_pnad')

def get_dict_path():
    cache_dir = user_cache_dir("pnadium")
    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, 'dict_pnad')
    
def map_files():
    ftp = FTP('ftp.ibge.gov.br', timeout=600)
    ftp.login()
    ftp.cwd('/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados/')
    paths = ftp.nlst()
    year_folders = []
    patt_anos = r'\A\d{4}\Z'
    for i in paths:
        try:
            year_folders.extend(re.findall(patt_anos, i))
        except:
            pass
    df_files = pd.DataFrame()
    for i in year_folders:
        ftp.cwd('/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados/'+i)
        files = ftp.nlst()
        files
        index_j = []
        files_str = []
        for j, x in enumerate(files):
            index_j.append(j)
            files_str.append(x)
        df_file_i = pd.DataFrame({f'{i}': files_str}, index=index_j)
        df_files = pd.concat([df_files, df_file_i], axis = 1)
    df_n = df_files.copy().stack().reset_index()
    df_n = df_n.sort_values(by=['level_1', 'level_0'])
    df_n = df_n.reset_index(drop=True)
    file_list = df_n[0].to_list()
    df_files_inf = df_files.copy()
    for i in df_files.columns:
        df_files_inf[i] = df_files_inf[i].replace('PNADC_', '',regex=True)
        df_files_inf[i] = df_files_inf[i].replace(r'_\d{8}\.zip|\.zip', '',regex=True)
        df_files_inf[i] = df_files_inf[i].astype(str).apply(lambda x: x[:2] + '-' + x[2:])
        df_files_inf[i] = df_files_inf[i].str.replace('na/n', '')
    df_files_inf['Trimestre'] = [
        '1º Trimestre',
        '2º Trimestre',    
        '3º Trimestre',
        '4º Trimestre',
    ]
    last_col = df_files_inf.columns[-1]
    cols_rest = list(df_files_inf.columns[0:-1])
    df_files_inf = df_files_inf[[last_col] + cols_rest]
    return df_files, df_files_inf, file_list

def download(ano, t, caminho = None, colunas = None, save_file = None):
    
    file_path = get_default_path()
    if not os.path.exists(file_path):
        os.makedirs(file_path)

    doc_file_path = get_dict_path()
    if not os.path.exists(doc_file_path):
        os.makedirs(doc_file_path)

    ftp = FTP('ftp.ibge.gov.br', timeout=600)
    ftp.login()
    
    df_files, df_files_inf, file_list = map_files()

    def pick_files(year, t):
        if str(year) not in df_files.columns:
            print(f'Ano não disponível. Tente: ' + ', '.join(map(str, df_files.columns)))
            quebra = False
            return quebra
        if (t-1) not in df_files.index:
            print(f'Trimestre não disponível. Tente: ' + ', '.join(map(str, df_files.index+1)))
            quebra = False
            return quebra
        return df_files.loc[t-1, str(year)]
    
    chosen_file_i = pick_files(ano, t)
    if chosen_file_i is False:
        return None
    chosen_file_d = '/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados/' + str(ano) + '/' + chosen_file_i
    # Cria um diretório temporário para todos os arquivos
    print(f'Iniciou o download: Trimestre {t}/{ano} - aguarde.')
    
    # Arquivo temporário para o arquivo principal
    local_file_path = os.path.join(file_path, chosen_file_i)
    with open(local_file_path, 'wb') as temp_file:
            ftp.retrbinary(f'RETR {chosen_file_d}', temp_file.write)

    # Download de arquivos de documentação
    doc_path = '/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados/Documentacao/'
    ftp.cwd(doc_path)
    docs_files = ftp.nlst()

    doc = None
    for i in docs_files:
        if 'dicionario' in i.lower():
            doc = i

    # Caminhos para os arquivos de documentação
    doc_temp_file_path = os.path.join(doc_file_path, doc)

    with open(doc_temp_file_path, 'wb') as doc_temp_file:
        ftp.retrbinary(f'RETR {doc_path + doc}', doc_temp_file.write)
    print(f'Download finalizado.')

    with zipfile.ZipFile(local_file_path, 'r') as zip_ref:
            pnad_txt = zip_ref.namelist()[0]
            zip_ref.extractall(file_path)  # Altere para o diretório desejado

    with zipfile.ZipFile(doc_temp_file_path, 'r') as zip_ref:
        files_zip = zip_ref.namelist()
        for i in files_zip:
            if '.xls' in i:
                vars_dic_xlsx = i
        zip_ref.extractall(doc_file_path)
    df_dic_path = os.path.join(doc_file_path, vars_dic_xlsx)
    df_dic = pd.read_excel(df_dic_path, header = 1)
    df_dic = df_dic[['Tamanho', 'Código\nda\nvariável', 'Unnamed: 4']]
    df_dic.columns = ['len', 'cod', 'desc']
    df_dic = df_dic.dropna(subset=['len'])
    print(f'Iniciou a criação do DataFrame Pandas: esta etapa pode demorar alguns minutos.')
    pnad_file = os.path.join(file_path, pnad_txt)
    # Definir nome do arquivo final
    pnad_file_name = f'pnad_trimestral_trimestre_0{t}{ano}.parquet'
    # Ler o arquivo em chunks e salvar partes no diretório `file_path`
    chunk_size = 100000  # Ajuste conforme necessário
    file_list = []  # Lista para armazenar os caminhos dos arquivos Parquet temporários

    if colunas:
        # Verifica se todas as colunas desejadas existem em df_dic['cod']
        colunas_existentes = df_dic['cod'].values
        missing = [col for col in colunas if col not in colunas_existentes]
        if missing:
            raise ValueError(f"As seguintes colunas não foram encontradas: {missing}")
        
        widths = list(df_dic['len'].astype(int))
        starts = np.concatenate(([0], np.cumsum(widths)[:-1]))
        ends = np.cumsum(widths)
        colspecs = list(zip(starts, ends))
        colunas = ['UPA', 'V1008', 'V1014', 'V2003'] + colunas
        indices = [i for i, nome in enumerate(df_dic['cod']) if nome in colunas]
        colspecs_filtrados = [colspecs[i] for i in indices]
        names_filtrados = [df_dic['cod'].iloc[i] for i in indices]

        pnad_iter = pd.read_fwf(
            pnad_file,
            colspecs=colspecs_filtrados,
            names=names_filtrados,
            na_values=" ",
            chunksize=chunk_size

        )
    else:
        pnad_iter = pd.read_fwf(pnad_file, widths=list(df_dic['len'].astype(int)), 
                                names=list(df_dic['cod']), na_values=" ", chunksize=chunk_size)
    
    for i, chunk in enumerate(pnad_iter):
        temp_file = os.path.join(file_path, f'pnad_temp_part_{i}.parquet')
        chunk.to_parquet(temp_file, index=False)
        file_list.append(temp_file)
    
    print("Chunks processados e salvos.")
    # Concatenar os arquivos Parquet em um único DataFrame
    pnad = pd.concat([pd.read_parquet(f) for f in file_list], ignore_index=True)
    pnad['UPA'] = pnad['UPA'].astype(str)
    pnad['V1008'] = pnad['V1008'].astype(str).str.zfill(pnad['V1008'].astype(str).apply(len).max())
    pnad['V1014'] = pnad['V1014'].astype(str).str.zfill(pnad['V1014'].astype(str).apply(len).max())
    pnad['V2003'] = pnad['V2003'].astype(str).str.zfill(pnad['V2003'].astype(str).apply(len).max())
    pnad['COD_FAM'] = pnad['UPA'] + pnad['V1008'] + pnad['V1014']
    pnad['COD_PESSOA'] = pnad['UPA'] + pnad['V1008'] + pnad['V1014'] + pnad['V2003']
    print("DataFrame criado.")
    # Definir caminho de salvamento final
    if caminho:
        final_path = os.path.join(caminho, pnad_file_name)
    else:
        final_path = os.path.join(os.getcwd(), pnad_file_name)
    if save_file:
        pnad.to_parquet(final_path)
        print(f'DataFrame "{pnad_file_name}" salvo como arquivo Parquet em: {final_path}')
    # Remover arquivos temporários do `file_path`
    for f in file_list:
        os.remove(f)
    pnad_final = pnad.copy()
    del(pnad)
    clear_cache()
    return pnad_final

def consulta_arquivos():
   _, df_files_inf, _ =  map_files()
   return df_files_inf

def consulta_var(cod = None, desc = None):

    file_path = get_default_path()
    if not os.path.exists(file_path):
        os.makedirs(file_path)

    doc_file_path = get_dict_path()
    if not os.path.exists(doc_file_path):
        os.makedirs(doc_file_path)

    ftp = FTP('ftp.ibge.gov.br', timeout=600)
    ftp.login()
    doc_path = '/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados/Documentacao/'
    ftp.cwd(doc_path)
    docs_files = ftp.nlst()
    dic = None
    for i in docs_files:
        if 'dicionario' in i.lower():
            dic = i
    doc_temp_file_path = os.path.join(doc_file_path, dic)
    with open(doc_temp_file_path, 'wb') as doc_temp_file:
        ftp.retrbinary(f'RETR {doc_path + dic}', doc_temp_file.write)
    with zipfile.ZipFile(doc_temp_file_path, 'r') as zip_ref:
        files_zip = zip_ref.namelist()
        for i in files_zip:
            if '.xls' in i:
                vars_dic_xlsx = i
        zip_ref.extractall(doc_file_path)
    df_dic_path = os.path.join(doc_file_path, vars_dic_xlsx)
    df_dic = pd.read_excel(df_dic_path, header = 1)
    df_dic = df_dic[['Tamanho', 'Código\nda\nvariável', 'Unnamed: 4']]
    df_dic.columns = ['Tamanho', 'Código', 'Descrição']
    df_dic = df_dic.dropna(subset=['Tamanho'])
    if desc is not None and cod is None:
        desc = unidecode(desc.lower())
        df_dic['Descrição2'] = df_dic['Descrição'].str.lower()
        df_dic['Descrição2'] = df_dic['Descrição2'].astype(str).apply(unidecode)
        df_dic_n = df_dic[df_dic['Descrição2'].str.contains(desc)]
        clear_cache()
        return df_dic_n[['Tamanho', 'Código', 'Descrição']]
    if cod is not None and desc is None:
        cod = unidecode(cod.lower())
        df_dic['Código2'] = df_dic['Código'].str.lower()
        df_dic['Código2'] = df_dic['Código2'].astype(str).apply(unidecode)
        df_dic_n = df_dic[df_dic['Código2'].str.contains(cod)]
        clear_cache()
        return df_dic_n[['Tamanho', 'Código', 'Descrição']]
    else:
        clear_cache()
        return df_dic
