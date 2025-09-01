# Sistema de Gestão de Máquinas (POS Controle)

Este projeto é um sistema web desenvolvido em Python com o framework Django para gerenciar a posse temporária de máquinas de cartão de crédito (POS) dentro de uma equipe. A aplicação é containerizada com Podman para garantir um ambiente de execução consistente e portável.

## Arquitetura

A aplicação segue uma arquitetura moderna e escalável, estruturada de forma a manter a separação de responsabilidades entre backend, frontend, banco de dados e infraestrutura.

### Backend (Django)

O backend é construído sobre o framework Django, utilizando o padrão arquitetural **MVT (Model-View-Template)**:

* **Model (`core/models.py`):** Define a estrutura do banco de dados através de classes Python. O ORM (Object-Relational Mapper) do Django converte essas classes em tabelas e consultas SQL, abstraindo a complexidade da comunicação com o banco de dados. Os modelos principais são `Maquina`, `CustomUser` (usuário), `Operacao` (histórico) e `CodigoConfirmacao`.
* **View (`core/views.py`):** Contém a lógica de negócio da aplicação. Cada função (ou classe) em `views.py` é responsável por receber uma requisição HTTP, processar os dados necessários (consultando os Models), e renderizar uma resposta, geralmente na forma de um template HTML.
* **Template (`templates/`):** São os arquivos HTML que compõem a interface do usuário. Eles são renderizados pelas Views e podem exibir dados dinâmicos passados pelo backend.

### Frontend

A interface do usuário é construída com tecnologias web padrão, focando em simplicidade e responsividade:

* **HTML5:** Estrutura o conteúdo das páginas.
* **Bootstrap 5:** Framework CSS utilizado para estilização, layout em grid, e componentes de interface (botões, cards, formulários). Garante que a aplicação seja totalmente responsiva e se adapte a diferentes tamanhos de tela.
* **JavaScript (Puro):** Utilizado para adicionar interatividade e funcionalidades em tempo real, como o contador de expiração do código e a atualização dinâmica das páginas de confirmação via AJAX, que se comunica com o backend sem a necessidade de recarregar a página.

### Banco de Dados

* **SQLite:** Um banco de dados leve e baseado em arquivo, ideal para desenvolvimento e aplicações de pequeno a médio porte. O arquivo do banco de dados é persistido em um volume externo do Podman para garantir que os dados não sejam perdidos quando o contêiner é recriado.

### Infraestrutura

* **Podman:** A aplicação é totalmente containerizada, o que garante que ela rode da mesma forma em qualquer ambiente. O `Dockerfile` define todas as dependências e configurações necessárias para construir a imagem da aplicação.
* **Nginx:** Em um ambiente de produção, um servidor web como o Nginx atua como um proxy reverso, recebendo as requisições externas (HTTPS na porta 443), gerenciando os certificados de segurança (SSL/TLS) e repassando o tráfego para a aplicação Django que roda dentro do contêiner.

## Estrutura do Projeto

```
.
├── core/                  # Principal aplicativo Django
│   ├── migrations/        # Arquivos de migração do banco de dados
│   ├── management/        # Comandos de gerenciamento customizados
│   ├── static/            # Arquivos estáticos (imagens, CSS, JS do app)
│   ├── admin.py           # Configuração do painel de administração
│   ├── models.py          # Definição dos modelos do banco de dados
│   ├── views.py           # Lógica de negócio (controllers)
│   └── urls.py            # Rotas específicas do aplicativo 'core'
├── gestao_maquinas/       # Configurações do projeto Django
│   ├── settings.py        # Configurações principais do projeto
│   └── urls.py            # Rotas principais do projeto
├── templates/             # Templates HTML globais
│   ├── admin/             # Templates para customizar o painel de admin
│   └── core/              # Templates do aplicativo 'core'
├── Dockerfile             # Receita para construir a imagem do contêiner
├── entrypoint.sh          # Script de inicialização do contêiner
├── manage.py              # Utilitário de linha de comando do Django
└── requirements.txt       # Lista de dependências Python
```

## Como Executar o Projeto

Siga os passos abaixo para configurar e executar a aplicação em um novo ambiente com Podman.

### Pré-requisitos

* Podman instalado no sistema.

### Passos para Execução

1.  **Clonar o Repositório**
    Obtenha o código-fonte do projeto.
    ```bash
    git clone https://github.com/ornan-matos/Inventory.git
    cd Inventory
    ```

2.  **Criar o Volume de Dados**
    Crie um diretório no seu sistema hospedeiro que será usado para armazenar os dados persistentes (banco de dados e imagens).
    ```bash
    mkdir -p /caminho/para/seu/volume
    ```

3.  **Construir a Imagem do Podman**
    Este comando lê o `Dockerfile` e constrói a imagem da aplicação com todas as dependências.
    ```bash
    podman build -t imagem-sistema .
    ```

4.  **Criar o Arquivo de Migração Inicial (Apenas na primeira vez)**
    Este passo crucial cria as "instruções" para o banco de dados.
    ```bash
    # Limpe migrações antigas se existirem
    rm -rf core/migrations/
    # Crie o novo arquivo de migração
    podman run --rm -it --entrypoint python -v "$(pwd)":/app:Z imagem-sistema manage.py makemigrations core
    # Reconstrua a imagem para incluir a nova migração
    podman build -t imagem-sistema .
    ```

5.  **Executar o Contêiner**
    Inicie o contêiner em modo detached (`-d`), mapeando as portas e o volume de dados. Lembre-se de usar a flag `:Z` no volume se estiver usando um sistema com SELinux (como Fedora, CentOS).
    ```bash
    podman run -d \
      --name sistema-maquinas \
      -v /caminho/para/seu/volume:/app/dados:Z \
      -p 8000:8000 \
      imagem-sistema
    ```
    O script `entrypoint.sh` irá automaticamente aplicar as migrações, coletar os arquivos estáticos e iniciar o servidor.

6.  **Criar um Superusuário**
    Para acessar o painel administrativo, crie o primeiro usuário.
    ```bash
    podman exec -it sistema-maquinas python manage.py createsuperuser
    ```
    Siga as instruções para definir nome de usuário, e-mail e senha.

7.  **Acessar o Sistema**
    * **Aplicação Principal:** `http://localhost:8000`
    * **Painel Administrativo:** `http://localhost:8000/superadmin/`

    Após o primeiro login com o superusuário, acesse o painel administrativo, edite seu usuário e defina o "User type" como "Administrador" para ter acesso a todas as funcionalidades.

---
## Screen Shots

#### Dashboard
![Dashboard](/img/Screen_Capture/captura1.png)

#### Painel Super Admin
![SuperAdmin](/img/Screen_Capture/captura2.png)

#### Painel Histórico de Operações
![Operações](/img/Screen_Capture/captura3.png)

---
