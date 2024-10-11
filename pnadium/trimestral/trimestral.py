from ftplib import FTP
import re
import pandas as pd
import tempfile
import zipfile
import os
import numpy as np
import shutil
from unidecode import unidecode

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

def download(ano, t, caminho = None):
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
    with tempfile.TemporaryDirectory(delete=False) as temp_dir:
        print(f'Iniciou o download: Trimestre {t}/{ano} - aguarde.')
        
        # Arquivo temporário para o arquivo principal
        temp_file_path = os.path.join(temp_dir, chosen_file_i)
        with open(temp_file_path, 'wb') as temp_file:
            ftp.retrbinary(f'RETR {chosen_file_d}', temp_file.write)

        # Download de arquivos de documentação
        doc_path = '/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados/Documentacao/'
        ftp.cwd(doc_path)
        docs_files = ftp.nlst()

        doc = None
        vars = None
        for i in docs_files:
            if 'dicionario' in i.lower():
                doc = i
            elif 'Variaveis_PNADC_Trimestral' in i:
                vars = i

        # Caminhos para os arquivos de documentação
        doc_temp_file_path = os.path.join(temp_dir, doc)
        vars_temp_file_path = os.path.join(temp_dir, vars)

        with open(doc_temp_file_path, 'wb') as doc_temp_file:
            ftp.retrbinary(f'RETR {doc_path + doc}', doc_temp_file.write)

        with open(vars_temp_file_path, 'wb') as vars_temp_file:
            ftp.retrbinary(f'RETR {doc_path + vars}', vars_temp_file.write)

        print(f'Download finalizado.')
    with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
        pnad_txt = zip_ref.namelist()[0]
        zip_ref.extractall(temp_dir)  # Altere para o diretório desejado
    with zipfile.ZipFile(doc_temp_file_path, 'r') as zip_ref:
        files_zip = zip_ref.namelist()
        for i in files_zip:
            if '.xls' in i:
                vars_dic_xlsx = i
        zip_ref.extractall(temp_dir)  # Altere para o diretório desejado
    df_var = pd.read_excel(vars_temp_file_path, header = 0)
    df_var.columns = ['cod'] + file_list
    df_var = df_var.loc[:,['cod', chosen_file_i]]
    df_dic = pd.read_excel(temp_dir + '/' + vars_dic_xlsx, header = 1)
    df_dic = df_dic[['Tamanho', 'Código\nda\nvariável', 'Unnamed: 4']]
    df_dic.columns = ['len', 'cod', 'desc']
    df_dic = df_dic.dropna(subset=['len'])
    var_dic = pd.merge(df_dic, df_var, on = 'cod', how='left')
    var_dic = var_dic.dropna(subset=[chosen_file_i])
    print(f'Iniciou a criação do DataFrame Pandas: esta etapa pode demorar alguns minutos.')
    pnad = pd.read_fwf(temp_dir + '/' + pnad_txt, widths=list(var_dic['len'].astype(int)), names=list(var_dic['cod']), na_values=" ")
    print(f'DataFrame criado.')
    pnad_file_name = df_files_inf.loc[t-1, str(ano)]
    pnad_file_name = f'pnad-{pnad_file_name}.parquet'
    if caminho is not None:
        pnad.to_parquet(caminho + '/' + pnad_file_name)
        print(f'DataFrame "{pnad_file_name}" salvo como arquivo parquet na pasta atribuída: {caminho}.')
    else:
        pnad.to_parquet(pnad_file_name)
        print(f'DataFrame "{pnad_file_name}" salvo como arquivo parquet na pasta de trabalho atual.')
    shutil.rmtree(temp_dir)

def consulta_arquivos():
   _, df_files_inf, _ =  map_files()
   return df_files_inf
def consulta_var(cod = None, desc = None):
    ftp = FTP('ftp.ibge.gov.br', timeout=600)
    ftp.login()
    doc_path = '/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados/Documentacao/'
    ftp.cwd(doc_path)
    docs_files = ftp.nlst()
    dic = None
    for i in docs_files:
        if 'dicionario' in i.lower():
            dic = i
    with tempfile.TemporaryDirectory() as temp_dir:
        doc_temp_file_path = os.path.join(temp_dir, dic)
        with open(doc_temp_file_path, 'wb') as doc_temp_file:
            ftp.retrbinary(f'RETR {doc_path + dic}', doc_temp_file.write)
        with zipfile.ZipFile(doc_temp_file_path, 'r') as zip_ref:
            files_zip = zip_ref.namelist()
            for i in files_zip:
                if '.xls' in i:
                    vars_dic_xlsx = i
            zip_ref.extractall(temp_dir)
        df_dic = pd.read_excel(temp_dir + '/' + vars_dic_xlsx, header = 1)
        df_dic = df_dic[['Tamanho', 'Código\nda\nvariável', 'Unnamed: 4']]
        df_dic.columns = ['Tamanho', 'Código', 'Descrição']
        df_dic = df_dic.dropna(subset=['Tamanho'])
        if desc is not None and cod is None:
            desc = unidecode(desc.lower())
            df_dic['Descrição2'] = df_dic['Descrição'].str.lower()
            df_dic['Descrição2'] = df_dic['Descrição2'].astype(str).apply(unidecode)
            df_dic_n = df_dic[df_dic['Descrição2'].str.contains(desc)]
            return df_dic_n[['Tamanho', 'Código', 'Descrição']]
        if cod is not None and desc is None:
            cod = unidecode(cod.lower())
            df_dic['Código2'] = df_dic['Código'].str.lower()
            df_dic['Código2'] = df_dic['Código2'].astype(str).apply(unidecode)
            df_dic_n = df_dic[df_dic['Código2'].str.contains(cod)]
            return df_dic_n[['Tamanho', 'Código', 'Descrição']]
        else:
            return df_dic