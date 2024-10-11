from setuptools import setup, find_packages

setup(
    name='pnadium',  # Nome do pacote
    version='0.1.0',  # Versão inicial
    description='Pacote para download e processamento dos microdados da PNAD Contínua do IBGE.',
    long_description=open('README.md', encoding='utf-8').read(),  # Certifique-se de que o README.md existe
    long_description_content_type='text/markdown',
    author='Seu Nome',  # Substitua pelo seu nome
    author_email='ggximenez@gmail.com',  # Substitua pelo seu email
    url='https://github.com/seu_usuario/pnadium',  # Substitua pelo URL do seu repositório, se houver
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'unidecode',
        # Adicione outras dependências necessárias
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Escolha a licença apropriada
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
