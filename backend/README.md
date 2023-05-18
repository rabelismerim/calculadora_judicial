# Deloitte JUCA

### O QUE É

> * Sistema que integra as equipes jurídica, de cálculo e financeira do RJ /Processos de falência (acompanhamento de
    passivos)

### A QUEM SE DESTINA / OBJETIVO

> * Usuários Deloitte que fazem parte das equipes jurídica, de cálculo ou financeira dos processos de RJ, para ajudar
    nos
    cálculos da RJ

### INSTALAÇÃO LOCAL

> * Clone o projeto da Azure repos
> * `python -m venv` na raiz do diretório do projeto para isolar seu ambiente;
> #### Windows
>* `.\\venv\\Scripts\\activate`
> #### Linux
> * `source venv/bin/activate`>

> * `pip install -r requirements.txt` para instalar as dependências necessárias para o projeto;

### USO LOCAL

> * `python manage.py makemigrations` para analisar as mudanças feitas nos modelos e gerar as migrações para o banco de
    dados
> * `python manage.py migrate` para aplicar as migrações feitas no makemigrations
> * `python manage.py runserver` para inicializar o servidor
> * Acesse a documentação na url http://127.0.0.1:8000/juca/api/v1/docs/swagger/ (consultar versão atual dá api em
    config.settings)
> * Na raiz do projeto crie um arquivo com o nome ".env". Dentro dele coloque o texto "DEBUG=True", "IS_LOCALHOST=True"
    e "ENV='branch' para ativar o modo de desenvolvedor

### Criação de grupo de permissões

> * Essas permissões são os papéis que os usuários podem ter nos projetos
> * Na pasta raiz do backend rode o comando `python manage.py create_permissions`;

### Criação dos indices e valores

> * Na url http://127.0.0.1:8000/juca/admin/rates/ratefile/ adicionar um rate file. Na lista de ratefile, marque o
    checkbox nos arquivos que deseja adicionar. No select action, selecione Load file e clique em Go. Os arquivos serão
    carregados para o banco de dados;
> * O arquivo para rate file deve estar no formato xlsx e contêr obrigatoriamente as colunas "mes" e "indice".
    Opcionalmente tem as colunas "acumulado" e "periodo" que são usadas em determinados indices, como o TST

### Criação dos indices IRRF

> * Os indices IRRF são valores pré determinados de acordo com a receita federal e devem ser alterados todo ano.
    Substitua os valores dentro do app rates
> * Para salvar os valores use `python manage.py create_indice_irrf`

### Criação dos templates para os indices

> * Os templates auxiliam o front-end de como deve ser feito para montar as tabelas para o cadastro de verbas. Foi
    utilizado os exemplos na planilha de apoio 04, onde foi encontrado as tabelas de verbas, verbas + reflexos, IRRF e
    documentos
> * Use o comando `python manage.py create_indice_templates` para cadastrar os templates

### Criação de grupos/papeis e suas permissões

> * A plataforma baseia as permissões e o que cada usuário pode fazer de acordo com seu grupo. Os grupos podem limitar
    ou dar acesso a determinadas áreas do site, consumo de apis criação e gerenciamento admin.
> * Os papéis determinam o que cada usuário pode fazer nos determinados projetos em que ele for alocado. Tem a mesma
    definição de um grupo, controlando o que cada um pode ter dentro daquele projeto específico.
> * Use o comando `python manage.py create_groups` para cadastrar todos os grupos e papéis

### Criação de app django

> * O template já cria pré-determinadas abstrações, facilitando o desenvolvimento de um app
> * Use o comando `django-admin startapp --template=base\app_template app_name` para criar o app

### Realização dos Testes

> #### Teste de carga
> * O teste do Locust serve para gerar métricas de como as apis da plataforma estão sendo consumidas. Simule cargas
    controlando o número de usuários, requisições, duração, etc. A interface do Locust pode ser acessada por meio do
    URL http://localhost:8089/. Ao abrir esta página, você verá a aba "Swarm" que exibe um formulário para definir o
    número de usuários (clientes) e a taxa de chegada (hatch rate) que será utilizada na simulação. Após preencher essas
    informações, clique no botão "Iniciar" para iniciar a simulação. Na guia "Parar", você pode pausar ou encerrar a
    simulação. A guia "Gráficos" exibe gráficos em tempo real mostrando o desempenho do aplicativo testado. você pode
    trabalhar com diferentes tipos de gráficos selecionando as opções desejadas no menu suspenso. A aba “Tabela” exibe
    uma tabela com informações detalhadas sobre cada requisição enviada durante a simulação. Que recurso pode ser útil
    para analisar quais rotas e endpoints estão sendo mais demandados. A aba "Erros" exibe informações sobre erros
    ocorridos durante a execução da simulação. Esta aba pode te ajudar identificar e corrigir problemas com seu
    aplicativo. Em resumo, a interface Locust permite controlar e monitorar a execução de testes de carga, bem como
    visualizar Informações detalhadas sobre o desempenho do aplicativo testado.
> * Pode ser realizado através do script localizado na pasta locust `python locust/main.py`
> #### Teste funcional
> * O teste funcional testa se todos os endpoint estão em funcionamento. Esse teste sempre deve ser realizado antes de
    qualquer push ou deploy para garantir a confiabilidade e mantenimento ativo da plataforma. A pipeline falhará se não
    passar nos testes, impedindo que as mudanças feitas vá para a produção.
> * Para o realizamento dos testes rode o script `python manage.py tests`, com isso todos os endpoints e cenários de
    testes irão ser executados.
> * Algumas classes apenas monitoram a resposta 200(GET) e 201(POST). Outras como indices e cálculos verificam se os
    resultados satisfazem a condição esperada. Essas condições vem de acordo com o entendimento junto aos stakeholders e
    como são feitos os cálculos judicialmente. 