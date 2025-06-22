[![DOI](https://zenodo.org/badge/871387862.svg)](https://doi.org/10.5281/zenodo.13958877)

# pnadium

Pacote para download e processamento dos microdados da PNAD Contínua do IBGE, facilitando o acesso aos microdados trimestrais, que contém a pesquisa básica e os microdados anuais, que também contém pesquisas suplementares (por trimestre ou visita).

## Instalação

Para instalar o pacote `pnadium`, você pode clonar o repositório e instalar localmente:

```bash
git clone https://github.com/ggximenez/pnadium.git
cd pnadium
pip install .
```

Ou, se preferir, instale diretamente via `pip`:

```bash
pip install pnadium
```

## Uso

O pacote `pnadium` possui dois submódulos: `trimestral` e `anual`. Cada submódulo oferece funções para manipular os dados correspondentes. O submódulo `trimestral` se refere aos microdados de divulgação trimestral, respectivos à pesquisa básica da PNAD contínua. Já o submódulo `anual` se refere aos microdados de divulgação anual, que contenham pesquisas suplementares (temáticas), que são divulgados por trimestre ou por visita ao domicílio. Para saber mais, acesse [aqui](https://ftp.ibge.gov.br/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados/LEIA-ME.pdf)

### Importação dos Submódulos

```python
import pnadium

# Acessando o submódulo trimestral
from pnadium import trimestral

# Acessando o submódulo anual
from pnadium import anual
```

### Funções Disponíveis

#### Submódulo `trimestral`

- `map_files()`: Mapeia os arquivos trimestrais disponíveis no FTP do IBGE.
- `download(ano, t, caminho=None, colunas=None, save_file=None)`: Faz o download e processamento dos dados trimestrais para o ano (`ano`) e trimestre (`t`) especificados. Os argumentos opcionais são: `caminho`, `colunas` e `save_file`. `caminho` é uma string que indica o caminho, incluindo nome, do arquivo da base de dados a ser salvo em `.parquet`; `colunas` é uma lista de strings com os nomes das colunas de interesse, caso queira carregar apenas parte das colunas e não a base de dados integral; e `save_file` é uma variável bool, que quando assume o valor `True` salva o arquivo da base de dados, caso contrário apenas retorna o DataFrame à variável indicada.
- `consulta_arquivos()`: Retorna um DataFrame com os arquivos trimestrais disponíveis.
- `consulta_var(cod=None, desc=None)`: Permite consultar o dicionário de variáveis trimestrais por código (`cod`) ou descrição (`desc`).

#### Submódulo `anual`

**Observação:** No submódulo `anual`, todas as funções requerem o argumento adicional `tipo`, que especifica o tipo de dados a serem manipulados. Além disso, a função `consulta_var` também requer os argumentos `ano` e `t`.

##### Argumento `tipo`

O argumento `tipo` define o tipo de arquivo anual que será utilizado. Os valores possíveis são:

- `'t'`: Para dados por **trimestre**.
- `'v'`: Para dados por **visita**.

##### Funções

- `map_files(tipo)`: Mapeia os arquivos anuais disponíveis no FTP do IBGE para o `tipo` especificado.
- `download(ano, t, tipo, caminho=None, colunas=None, save_file=True)`: Faz o download e processamento dos dados anuais para o ano (`ano`), período (`t`) e `tipo` especificados. O argumento `caminho` é opcional. Se não for especificado o `caminho`, os dados serão salvos no diretório atual. O argumento opcional `colunas`: agora você pode passar uma lista com o código das colunas de interesse, e o DataFrame final conterá apenas as colunas de interesse e as colunas chave; e `save_file` é uma variável bool, que quando assume o valor `True` salva o arquivo da base de dados, caso contrário apenas retorna o DataFrame à variável indicada.
- `consulta_arquivos(tipo)`: Retorna um DataFrame com os arquivos anuais disponíveis para o `tipo` especificado.
- `consulta_var(ano, t, tipo, cod=None, desc=None)`: Permite consultar o dicionário de variáveis anuais para o ano (`ano`), período (`t`) e `tipo` especificados, podendo filtrar por código (`cod`) ou descrição (`desc`).

### Exemplos de Uso

#### Exemplo 1: Consultar Arquivos Disponíveis

```python
import pnadium

# Consultar arquivos trimestrais disponíveis
df_trimestral = pnadium.trimestral.consulta_arquivos()
print(df_trimestral)

# Consultar arquivos anuais disponíveis (tipo 'v' - visita)
df_anual_visita = pnadium.anual.consulta_arquivos(tipo='v')
print(df_anual_visita)

# Consultar arquivos anuais disponíveis (tipo 't' - trimestre)
df_anual_trimestre = pnadium.anual.consulta_arquivos(tipo='t')
print(df_anual_trimestre)
```

#### Exemplo 2: Fazer Download dos Dados

```python
# Download dos dados do 1º trimestre de 2020 (dados trimestrais)
pnadium.trimestral.download(ano=2020, t=1, caminho='caminho/para/salvar', save_file=True)
```

No caso acima, a base de dados final em arquivo `.parquet` será salva no caminho designado. Se quiser atribuir o DataFrame final a uma variável sem salvar a base de dados em arquivo `.parquet`, basta designar uma variável à função download, no caso abaixo `pnad_01_20`:

```python
# Download dos dados do 1º trimestre de 2020 (dados trimestrais)
pnad_01_20 = pnadium.trimestral.download(ano=2020, t=1)
```

Para salvar um arquivo `.parquet` com a base de dados e também obter os dados em uma variável, basta combinar as duas abordagens:

```python
# Download dos dados do 1º trimestre de 2020 (dados trimestrais)
pnad_01_20 = pnadium.trimestral.download(ano=2020, t=1, caminho='caminho/para/salvar', save_file=True)
```

Para economizar memória em seu ambiente virtual, você pode limitar o DataFrame final às colunas de interesse através do argumento `colunas`, descartando colunas com informações que não serão utilizadas em seu estudo. No exemplo a seguir, além das colunas necessárias para as chaves, apenas as seguintes serão carregadas:

- `"V1028"`: Peso do domicílio e das pessoas com calibragem por projeção da população;
- `"V2001"`: Número de pessoas no domicílio;
- `"V2005"`: Condição da pessoa no domicílio (Responsável, cônjuge, filho(a), etc);
- `"V2007"`: Sexo da pessoa;
- `"V2009"`: Idade da pessoa em anos;
- `"V2010"`: Cor ou raça da pessoa.

Assim é o código a ser executado:

```python

# Colunas de interesse:
cols = [
"V1028",
"V2001",
"V2005",
"V2007",
"V2009",
"V2010",
]
# Download dos dados do 1º trimestre de 2020 (dados trimestrais), apenas com colunas de interesse
pnad_01_20 = pnadium.trimestral.download(ano=2020, t=1, colunas = cols)
```

As colunas usadas para criar as chaves de domicílio e de pessoa serão sempre carregadas:

- `"UPA"`: Código da Unidade Primária de Amostragem;
- `"V1008"`: Número de seleção do domicílio;
- `"V1014"`: Número do painel;
- `"V2003"`: Número de ordem do morador do domicílio.

Com as colunas base são criadas duas chaves, uma para domicílio e outra para a pessoa, de acordo com a composição das chaves informada pelo [IBGE](https://ftp.ibge.gov.br/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados/Documentacao/Chaves_PNADC.pdf)
:
- `COD_FAM`: Código do domicílio ou família, composto por `"UPA" + "V1008" + "V1014"`;
- `COD_PESSOA`: Código da pessoa ou morador, composto por `"UPA" + "V1008" + "V1014" + "V2003"`

Assim, o DataFrame final *sempre* seguirá o seguinte formato:

|index|   UPA   | V1008 | V1014 | V2003 |  COD_FAM   |  COD_PESSOA  | Colunas de interesse...|
|-----|---------|-------|-------|-------|------------|--------------|---|
|  0  |110000016|  01   |  7    |  01   |110000016017|11000001601701|...|
|  1  |110000016|  01   |  7    |  02   |110000016017|11000001601702|...|
| ... |...|  ...   |  ...    |  ...   |...|...|...|

Certifique-se de consultar os códigos das colunas no dicionário dos microdados de interesse. Pesquisas suplementares tem códigos distintos, sendo necessária a consulta previamente.

#### Exemplo 3: Consultar Variáveis

```python
# Consultar variáveis trimestrais que contêm 'renda' na descrição
variaveis_trimestral = pnadium.trimestral.consulta_var(desc='renda')
print(variaveis_trimestral)

# Consultar variáveis anuais para o ano 2020, período 1, tipo 'v', pelo código 'V2009'
variaveis_anual = pnadium.anual.consulta_var(ano=2020, t=1, tipo='v', cod='V2009')
print(variaveis_anual)

# Consultar variáveis anuais para o ano 2020, período 2, tipo 't', que contêm 'emprego' na descrição
variaveis_anual_emprego = pnadium.anual.consulta_var(ano=2020, t=2, tipo='t', desc='emprego')
print(variaveis_anual_emprego)
```

### Detalhes sobre os argumentos

#### Argumento `tipo` no Submódulo `anual`

O argumento `tipo` determina o conjunto de dados anuais que será utilizado:

- **Tipo 'v' (Visita):** Refere-se aos dados coletados por visita domiciliar. São realizadas 5 visitas ao longo do ano. 
- **Tipo 't' (Trimestre):** Refere-se aos dados agregados por trimestre.

#### Argumentos `ano` e `t` na Função `consulta_var` do Submódulo `anual`

A função `consulta_var` no submódulo `anual` requer os argumentos `ano` e `t` (período) porque o dicionário de variáveis pode variar de acordo com o ano e o período específico. Isso garante que a consulta retorne informações precisas para o conjunto de dados desejado.

## Dependências

O pacote `pnadium` depende das seguintes bibliotecas:

- `pandas`
- `numpy`
- `unidecode`
- `appdirs`

Certifique-se de que elas estejam instaladas no seu ambiente Python.

## Licença

Este projeto está licenciado sob a licença MIT - consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests no GitHub.

## Autor

- **Gustavo G. Ximenez**
