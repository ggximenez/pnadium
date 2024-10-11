# pnadium

Pacote para download e processamento dos microdados da PNAD Contínua do IBGE, facilitando o acesso aos microdados trimestrais, que contém a pesquisa básica e os microdados anuais, que também contém pesquisas suplementares (por trimestre ou visita).

## Instalação

Para instalar o pacote `pnadium`, você pode clonar o repositório e instalar localmente:

```bash
git clone https://github.com/ggximenez/pnadium.git
cd pnadium
pip install .
```

Ou, se preferir, instale diretamente via `pip` (após publicar no PyPI):

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
- `download(ano, t, caminho=None)`: Faz o download e processamento dos dados trimestrais para o ano (`ano`) e trimestre (`t`) especificados. O parâmetro `caminho` é opcional e indica o diretório onde os dados serão salvos. Se não for especificado o `caminho`, os dados serão salvos no diretório atual.
- `consulta_arquivos()`: Retorna um DataFrame com os arquivos trimestrais disponíveis.
- `consulta_var(cod=None, desc=None)`: Permite consultar o dicionário de variáveis trimestrais por código (`cod`) ou descrição (`desc`).

#### Submódulo `anual`

**Observação:** No submódulo `anual`, todas as funções requerem o parâmetro adicional `tipo`, que especifica o tipo de dados a serem manipulados. Além disso, a função `consulta_var` também requer os parâmetros `ano` e `t`.

##### Parâmetro `tipo`

O parâmetro `tipo` define o tipo de arquivo anual que será utilizado. Os valores possíveis são:

- `'t'`: Para dados por **trimestre**.
- `'v'`: Para dados por **visita**.

##### Funções

- `map_files(tipo)`: Mapeia os arquivos anuais disponíveis no FTP do IBGE para o `tipo` especificado.
- `download(ano, t, tipo, caminho=None)`: Faz o download e processamento dos dados anuais para o ano (`ano`), período (`t`) e `tipo` especificados. O parâmetro `caminho` é opcional. Se não for especificado o `caminho`, os dados serão salvos no diretório atual.
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
pnadium.trimestral.download(ano=2020, t=1, caminho='caminho/para/salvar')

# Download dos dados anuais de 2020, tipo 'v' (visita), período 1
pnadium.anual.download(ano=2020, t=1, tipo='v', caminho='caminho/para/salvar')

# Download dos dados anuais de 2020, tipo 't' (trimestre), período 2
pnadium.anual.download(ano=2020, t=2, tipo='t', caminho='caminho/para/salvar')
```

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

### Detalhes sobre os Parâmetros

#### Parâmetro `tipo` no Submódulo `anual`

O parâmetro `tipo` determina o conjunto de dados anuais que será utilizado:

- **Tipo 'v' (Visita):** Refere-se aos dados coletados por visita domiciliar. São realizadas 5 visitas ao longo do ano. 
- **Tipo 't' (Trimestre):** Refere-se aos dados agregados por trimestre.

#### Parâmetros `ano` e `t` na Função `consulta_var` do Submódulo `anual`

A função `consulta_var` no submódulo `anual` requer os parâmetros `ano` e `t` (período) porque o dicionário de variáveis pode variar de acordo com o ano e o período específico. Isso garante que a consulta retorne informações precisas para o conjunto de dados desejado.

## Dependências

O pacote `pnadium` depende das seguintes bibliotecas:

- `pandas`
- `numpy`
- `unidecode`

Certifique-se de que elas estejam instaladas no seu ambiente Python.

## Licença

Este projeto está licenciado sob a licença MIT - consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests no GitHub.

## Autor

- **Gustavo G. Ximenez**
