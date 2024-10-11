from ftplib import FTP
import re
import pandas as pd
import tempfile
import zipfile
import os
import numpy as np
import shutil
from unidecode import unidecode

def map_files(tipo):
    ftp = FTP('ftp.ibge.gov.br', timeout=600)
    ftp.login()
    if tipo == 't':
        ftp.cwd('/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Anual/Microdados/Trimestre/')
        paths = ftp.nlst()
        t_folders = []
        for i in paths:
            if 'trimestre' in i.lower():
                t_folders.append(i)
        df_files = pd.DataFrame()
        for i in t_folders:
            ftp.cwd('/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Anual/Microdados/Trimestre/'+ i + '/Dados/')
            files = ftp.nlst()
            index_j = []
            files_str = []
            for j, x in enumerate(files):
                index_j.append(j)
                files_str.append(x)
            df_file_i = pd.DataFrame({f'{i}': files_str}, index=index_j)
            df_files = pd.concat([df_files, df_file_i], axis = 1)
        for i in df_files.columns:
            ano = []
            for j, x in enumerate(df_files[i]):
                try: 
                    ano.append(df_files[i].str.split('_')[j][1])
                except:
                    ano.append(np.nan)
            df_files[i + '_ano'] = ano
        df_files1 = df_files[['Trimestre_1', 'Trimestre_2', 'Trimestre_3', 'Trimestre_4']].stack().reset_index()
        df_files2 = df_files[['Trimestre_1_ano', 'Trimestre_2_ano', 'Trimestre_3_ano', 'Trimestre_4_ano']].stack().reset_index()
        df_files = pd.concat([df_files1, df_files2], axis = 1)
        df_files.columns  = ['na', 't', 'nome', 'na2', 'na3', 'ano']
        df_files = df_files.pivot_table(index='ano', columns='t', values='nome', aggfunc='first').reset_index()
        df_files.columns.name = None
        df_files = df_files.reset_index(drop=True)
        df_files.index = df_files['ano'].values
        df_files = df_files.drop(columns=['ano'])
        file_list = df_files.stack()
        df_files_n = df_files.copy()
        df_files_n.columns = [1, 2, 3, 4]
        return df_files, df_files_n, file_list
    
    if tipo == 'v':
        ftp.cwd('/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Anual/Microdados/Visita/')
        paths = ftp.nlst()
        t_folders = []
        for i in paths:
            if 'visita' in i.lower():
                t_folders.append(i)
        df_files = pd.DataFrame()
        for i in t_folders:
            ftp.cwd('/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Anual/Microdados/Visita/'+ i + '/Dados/')
            files = ftp.nlst()
            index_j = []
            files_str = []
            for j, x in enumerate(files):
                index_j.append(j)
                files_str.append(x)
            df_file_i = pd.DataFrame({f'{i}': files_str}, index=index_j)
            df_files = pd.concat([df_files, df_file_i], axis = 1)
        for i in df_files.columns:
            ano = []
            for j, x in enumerate(df_files[i]):
                try: 
                    ano.append(df_files[i].str.split('_')[j][1])
                except:
                    ano.append(np.nan)
            df_files[i + '_ano'] = ano
        df_files1 = df_files[['Visita_1', 'Visita_2', 'Visita_3', 'Visita_4', 'Visita_5']].stack().reset_index()
        df_files2 = df_files[['Visita_1_ano', 'Visita_2_ano', 'Visita_3_ano', 'Visita_4_ano', 'Visita_5_ano']].stack().reset_index()
        df_files = pd.concat([df_files1, df_files2], axis = 1)
        df_files.columns  = ['na', 't', 'nome', 'na2', 'na3', 'ano']
        df_files = df_files.pivot_table(index='ano', columns='t', values='nome', aggfunc='first').reset_index()
        df_files.columns.name = None
        df_files = df_files.reset_index(drop=True)
        df_files.index = df_files['ano'].values
        df_files = df_files.drop(columns=['ano'])
        df_files = df_files.drop(index=['importante'])
        file_list = df_files.stack()
        df_files_n = df_files.copy()
        df_files_n.columns = [1, 2, 3, 4, 5]
        return df_files, df_files_n, file_list

def consulta_arquivos(tipo):
   if tipo not in ['t', 'v']:
      print("Tipo inválido. Escolha 't' para arquivos trimestrais ou 'v' para arquivos de visitas.")
      return None
   df_files_inf, _, _ =  map_files(tipo)
   return df_files_inf

def download(ano, t, tipo, caminho = None):
    if tipo not in ['t', 'v']:
        print("Tipo inválido. Escolha 't' para arquivos trimestrais ou 'v' para arquivos de visitas.")
        return None
    ftp = FTP('ftp.ibge.gov.br', timeout=600)
    ftp.login()
    
    df_files_n, df_files, file_list = map_files(tipo)

    if tipo == 't':
        def pick_files(year, t):
            if (str(year) not in df_files.index) or (t not in df_files.columns):
                quebra = False
                return quebra
            else:
                return df_files.loc[str(year), t]
        
        chosen_file_i = pick_files(ano, t)
        if chosen_file_i is False or str(chosen_file_i) == 'nan':
            print(f'Ano ou trimestre não disponível. Os arquivos disponíveis são os seguintes:')
            print(df_files_n.stack())
            return None
        
        trimestre = df_files_n.columns[t-1]
        
        chosen_file_d = '/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Anual/Microdados/Trimestre/' + trimestre + '/Dados/' + chosen_file_i
        # Cria um diretório temporário para todos os arquivos
        with tempfile.TemporaryDirectory(delete=False) as temp_dir:
            print(f'Iniciou o download: Trimestre {t}/{ano} - aguarde.')
            
            # Arquivo temporário para o arquivo principal
            temp_file_path = os.path.join(temp_dir, chosen_file_i)
            with open(temp_file_path, 'wb') as temp_file:
                ftp.retrbinary(f'RETR {chosen_file_d}', temp_file.write)

            # Download de arquivos de documentação
            doc_path = '/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Anual/Microdados/Trimestre/' + trimestre + '/Documentacao/'
            ftp.cwd(doc_path)
            docs_files = ftp.nlst()

            doc = None
            for i in docs_files:
                if 'dicionario' in i.lower():
                    doc = i
            # Caminhos para os arquivos de documentação
            doc_temp_file_path = os.path.join(temp_dir, doc)

            with open(doc_temp_file_path, 'wb') as doc_temp_file:
                ftp.retrbinary(f'RETR {doc_path + doc}', doc_temp_file.write)
            print(f'Download finalizado.')

        with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
            pnad_txt = zip_ref.namelist()[0]
            zip_ref.extractall(temp_dir)  # Altere para o diretório desejado
        df_dic = pd.read_excel(doc_temp_file_path, header = 1)
        df_dic = df_dic[['Tamanho', 'Código\nda\nvariável', 'Unnamed: 4']]
        df_dic.columns = ['len', 'cod', 'desc']
        df_dic = df_dic.dropna(subset=['len'])
        print(f'Iniciou a criação do DataFrame Pandas: esta etapa pode demorar alguns minutos.')
        pnad = pd.read_fwf(temp_dir + '/' + pnad_txt, widths=list(df_dic['len'].astype(int)), names=list(df_dic['cod']), na_values=" ")
        print(f'DataFrame criado.')
        pnad_file_name = '0' + str(t) + str(ano)
        pnad_file_name = f'pnad_anual_trimestre_{pnad_file_name}.parquet'
        if caminho is not None:
            pnad.to_parquet(caminho + '/' + pnad_file_name)
            print(f'DataFrame "{pnad_file_name}" salvo como arquivo parquet na pasta atribuída: {caminho}.')
        else:
            pnad.to_parquet(pnad_file_name)
            print(f'DataFrame "{pnad_file_name}" salvo como arquivo parquet na pasta de trabalho atual.')
        shutil.rmtree(temp_dir)

    if tipo == 'v':
        def pick_files(year, t):
            if (str(year) not in df_files.index) or (t not in df_files.columns):
                quebra = False
                return quebra
            else:
                return df_files.loc[str(year), t]
        
        chosen_file_i = pick_files(ano, t)
        if (chosen_file_i is False) or str(chosen_file_i) == 'nan':
            print(f'Ano ou trimestre não disponível. Os arquivos disponíveis são os seguintes:')
            print(df_files_n.stack())
            return None
        
        visita = df_files_n.columns[t-1]
        
        chosen_file_d = '/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Anual/Microdados/Visita/' + visita + '/Dados/' + chosen_file_i
        # Cria um diretório temporário para todos os arquivos
        with tempfile.TemporaryDirectory(delete=False) as temp_dir:
            print(f'Iniciou o download: Visita {t}/{ano} - aguarde.')
            
            # Arquivo temporário para o arquivo principal
            temp_file_path = os.path.join(temp_dir, chosen_file_i)
            with open(temp_file_path, 'wb') as temp_file:
                ftp.retrbinary(f'RETR {chosen_file_d}', temp_file.write)

            # Download de arquivos de documentação
            doc_path = '/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Anual/Microdados/Visita/' + visita + '/Documentacao/'
            ftp.cwd(doc_path)
            docs_files = ftp.nlst()

            docs = []
            for i in docs_files:
                if '.xls' in i and 'dicionario' in i:
                    docs.append(i)
            patt = r'(?<=microdados_)[\s\S]*(?=_visita)'
            ini = []
            fim = []
            for i in docs:
                ini_i = re.findall(patt, i)[0].split('_a_')[0]
                ini.append(int(ini_i))
                try:
                    fim_i = re.findall(patt, i)[0].split('_a_')[1]
                    fim.append(int(fim_i))
                except IndexError:
                    fim_i = re.findall(patt, i)[0].split('_a_')[0]
                    fim.append(int(fim_i))
            docs_range = pd.DataFrame({'ini': ini, 'fim': fim, 'file': docs})
            doc = docs_range.loc[(docs_range['ini']<=ano) & (docs_range['fim']>=ano)]['file'].values[0]

            # Caminhos para os arquivos de documentação
            doc_temp_file_path = os.path.join(temp_dir, doc)

            with open(doc_temp_file_path, 'wb') as doc_temp_file:
                ftp.retrbinary(f'RETR {doc_path + doc}', doc_temp_file.write)

            print(f'Download finalizado.')

        with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
            pnad_txt = zip_ref.namelist()[0]
            zip_ref.extractall(temp_dir)  # Altere para o diretório desejado
        df_dic = pd.read_excel(doc_temp_file_path, header = 1)
        df_dic = df_dic[['Tamanho', 'Código\nda\nvariável', 'Unnamed: 4']]
        df_dic.columns = ['len', 'cod', 'desc']
        df_dic = df_dic.dropna(subset=['len'])
        print(f'Iniciou a criação do DataFrame Pandas: esta etapa pode demorar alguns minutos.')
        pnad = pd.read_fwf(temp_dir + '/' + pnad_txt, widths=list(df_dic['len'].astype(int)), names=list(df_dic['cod']), na_values=" ")
        print(f'DataFrame criado.')
        pnad_file_name = '0' + str(t) + str(ano)
        pnad_file_name = f'pnad_anual_visita_{pnad_file_name}.parquet'
        if caminho is not None:
            pnad.to_parquet(caminho + '/' + pnad_file_name)
            print(f'DataFrame "{pnad_file_name}" salvo como arquivo parquet na pasta atribuída: {caminho}.')
        else:
            pnad.to_parquet(pnad_file_name)
            print(f'DataFrame "{pnad_file_name}" salvo como arquivo parquet na pasta de trabalho atual.')
        shutil.rmtree(temp_dir)

def consulta_var(ano, t, tipo, cod = None, desc = None):

    if tipo not in ['t', 'v']:

        print("Tipo inválido. Escolha 't' para arquivos trimestrais ou 'v' para arquivos de visitas.")
        return None
    ftp = FTP('ftp.ibge.gov.br', timeout=600)
    ftp.login()
    df_files_n, df_files, _ = map_files(tipo)
    
    if tipo == 't':
        def pick_files(year, t):
            if (str(year) not in df_files.index) or (t not in df_files.columns):
                quebra = False
                return quebra
            else:
                return df_files.loc[str(year), t]
            
        chosen_file_i = pick_files(ano, t)
        if chosen_file_i is False or str(chosen_file_i) == 'nan':
            print(f'Ano ou trimestre escolhido não possui arquivo disponível.')
            return None
        
        trimestre = df_files_n.columns[t-1]
        with tempfile.TemporaryDirectory(delete=False) as temp_dir:
            # Download de arquivos de documentação
            doc_path = '/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Anual/Microdados/Trimestre/' + trimestre + '/Documentacao/'
            ftp.cwd(doc_path)
            docs_files = ftp.nlst()
            doc = None
            for i in docs_files:
                if 'dicionario' in i.lower():
                    doc = i
            # Caminhos para os arquivos de documentação
            doc_temp_file_path = os.path.join(temp_dir, doc)
            with open(doc_temp_file_path, 'wb') as doc_temp_file:
                ftp.retrbinary(f'RETR {doc_path + doc}', doc_temp_file.write)
            df_dic = pd.read_excel(doc_temp_file_path, header = 1)
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
            
    if tipo == 'v':

        def pick_files(year, t):
            if (str(year) not in df_files.index) or (t not in df_files.columns):
                quebra = False
                return quebra
            else:
                return df_files.loc[str(year), t]
            
        chosen_file_i = pick_files(ano, t)
        if chosen_file_i is False or str(chosen_file_i) == 'nan':
            print(f'Ano ou visita escolhida não possui arquivo disponível.')
            return None
        
        visita = df_files_n.columns[t-1]
        with tempfile.TemporaryDirectory(delete=False) as temp_dir:
            doc_path = '/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Anual/Microdados/Visita/' + visita + '/Documentacao/'
            ftp.cwd(doc_path)
            docs_files = ftp.nlst()
            docs = []
            for i in docs_files:
                if '.xls' in i and 'dicionario' in i:
                    docs.append(i)
            patt = r'(?<=microdados_)[\s\S]*(?=_visita)'
            ini = []
            fim = []
            for i in docs:
                ini_i = re.findall(patt, i)[0].split('_a_')[0]
                ini.append(int(ini_i))
                try:
                    fim_i = re.findall(patt, i)[0].split('_a_')[1]
                    fim.append(int(fim_i))
                except IndexError:
                    fim_i = re.findall(patt, i)[0].split('_a_')[0]
                    fim.append(int(fim_i))
            docs_range = pd.DataFrame({'ini': ini, 'fim': fim, 'file': docs})
            doc = docs_range.loc[(docs_range['ini']<=ano) & (docs_range['fim']>=ano)]['file'].values[0]
            # Caminhos para os arquivos de documentação
            doc_temp_file_path = os.path.join(temp_dir, doc)
            with open(doc_temp_file_path, 'wb') as doc_temp_file:
                ftp.retrbinary(f'RETR {doc_path + doc}', doc_temp_file.write)
            df_dic = pd.read_excel(doc_temp_file_path, header = 1)
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
