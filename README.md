# Introdução

| Aplicação      | Backend | Front-end | Banco de Dados |
| ----------- | ----------- | ----------- | ----------- |
| Web      | Django       | VueJS   | Postgres        |

## Contem
- Authenticação MSAL
- Integração Front-Back
- Exigencias de Segurança após Penetration Test

# Inicialização

Para inicializar esta aplicação, é necessário seguir os passos abaixo:

1.	Software dependencies.
    * git + gitbash
    * Python 3
    * Virtualenv ou Pypenv
    * npm
  
2.	Installation process.
    * Clonar o repositório utilizando o gitbash:
        ```
        git clone URL_do_repo
        ```

    ### Frontend
    * CD para o diretório correto:
        ```
        cd Webapp_django_vuejs_postgres/frontend/
        ```
    * Instalar as dependencias do projeto:
        ```
        npm install
        ```
    * rodar o front-end:
        ```
        npm serve
        ```

    ### Backend
    * CD para o diretório correto:
        ```
        cd Webapp_django_vuejs_postgres/backend/
        ```
    * criar o ambiente virtual:
        ```
        virtualenv venv
        ```
    * Ativar o ambiente virtual:
        ```
        Source venv/Scrips/Activate
        ```
    * Instalar as dependencias do projeto:
        ```
        pip install -r requirements.txt
        ```
    
    * crie uma cópia do arquivo .env.example renomeie para .env e preencha os dados.
      * Secret_key = string aleatória
      * Dados de acesso ao banco de dados
      * Dados de acesso ao MSAL ( verificar com infra sobre acesso )
    <br><br>

    * Realizar primeiro migration
        ```
        python manage.py makemigrations
        ```

    * Realizar as migrações no banco de dados:
        ```
        python manage.py migrate
        ```

    * Será necessário a criação de um usuário inicial, será feito via banco. Utilize software de sua preferencia, no meu caso utilizo DBeaver. Inclui um usuário com id 1. 
  
    * Por solicitação da equipe de segurança da Deloitte, a criação de superuser via linha de comando foi desabilitada. Para criar um super user é necesário acessar o models.py da classe de DTTUser e incluir o id do usuário na lista hardcoded.

    * É necessário obter um certificado SSl auto-assinado para o ambiente de desenvolvimento que queira usar essa applicação. Será dois arquivos> cert.pem e key.pem. Cole estes arquivos no mesmo local que está seu arquivo manage.py
     

    * Rodar o ambiente de desenvolvimento: ( Verifique sobre a utilização de portas, pode existir outras pessoas usando a porta 8000 no servidor de desenvolvimento que voce está)
        ```
        python .\manage.py 'runserver_plus' '0.0.0.0:8000' '--cert-file' 'cert.pem' '--key-file' 'key.pem'
        ```

    * Acessar a aplicação no http://\<IpDoAmbiente>:8000/

# Build e Test para deploy

* Antes do run server:
  > python manage.py collectstatic

# Arquitetura Original

### Projeto: Dare
### Squad: V&M

### Responsáveis Técnicos:
* Raphael Lucas Mendes - rapmendes@deloitte.com
* Gustavo Donio Goldryng  - ggoldryng@deloitte.com
* Rafael Marcos Katz  - rafkatz@deloitte.com
* Stenyo Borges  - stborges@deloitte.com