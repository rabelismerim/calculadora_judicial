# Deloitte JUCA


### O QUE É

System that integrates the legal, calculation and financial teams of RJ / Bankruptcy processes (liabilities monitoring)

### A QUEM SE DESTINA / OBJETIVO

* Usuários Deloitte que fazem parte das equipes jurídica, de cálculo ou financeira dos processos de RJ, para ajudar nos cálculos da RJ 
 
### INSTALAÇÃO LOCAL

* Clone o projeto da Azure repos

* `python -m venv` na raiz do diretório do projeto para isolar seu ambiente;

> Windows
>* `.\\venv\\Scripts\\activate`

> Linux
>* `source venv/bin/activate`

* `pip install -r requirements.txt` para instalar as dependências necessárias para o projeto;


### USO LOCAL

* `python manage.py makemigrations` para analisar as mudanças feitas nos modelos e gerar as migrações para o banco de
  dados
* `python manage.py migrate` para aplicar as migrações feitas no makemigrations
* `python manage.py runserver` para inicializar o servidor
* Acesse a documentação na url http://127.0.0.1:8000/djud/api/v1/docs/swagger/ (consultar versão atual dá api em config.settings)
    
* Na raiz do projeto crie um arquivo com o nome ".env". Dentro dele coloque o texto "DEBUG=True", "IS_LOCALHOST=True" e "ENV='branch' para ativar o modo de desenvolvedor

### Criação de grupo de permissões
* Na pasta raiz do backend rode o comando `python manage.py create_permissions`;

### Criação dos indices e valores
* Na url http://127.0.0.1:8000/djud/admin/rates/ratefile/ adicionar um rate file. Na lista de ratefile, marque o checkbox nos arquivos que deseja adicionar. No select action, selecione Load file e clique em Go. Os arquivos serão carregados para o banco de dados;
>* O arquivo para rate file deve estar no formato xlsx e contêr obrigatoriamente as colunas "mes" e "indice". Opcionalmente tem as colunas "acumulado" e "periodo" que são usadas em determinados indices, como o TST

###  Criação dos indices IRRF
*  `python manage.py create_indice_irrf`

###  Criação de app django
*  `django-admin startapp --template=base\app_template app_name`