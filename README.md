# Sistema de Inventário de Máquinas PDV

Este projeto é um sistema web desenvolvido em Python com o framework Django para gerenciar a posse temporária de máquinas de cartão de crédito (POS) dentro de uma equipe. A aplicação é containerizada com Podman para garantir um ambiente de execução consistente e portável.

O sistema evoluiu de um modelo de confirmação por códigos para uma **dashboard dinâmica e centralizada**, onde os administradores aprovam ou negam solicitações em tempo real, proporcionando um fluxo de trabalho mais moderno e eficiente.

## Funcionalidades Principais

* **Dashboard em Tempo Real:** A interface principal atualiza-se automaticamente a cada 5 segundos, exibindo o status de todas as máquinas sem a necessidade de recarregar a página.
* **Fluxo de Aprovação Centralizado:** Administradores possuem uma visão completa de todas as solicitações pendentes (retirada, devolução e troca) e podem aprová-las ou negá-las diretamente da dashboard.
* **Solicitações Intuitivas:** Colaboradores podem solicitar máquinas disponíveis, iniciar a devolução das suas próprias máquinas ou pedir a troca de equipamentos que estão com outros colegas.
* **Organização e Pesquisa:** As máquinas são agrupadas por categorias retráteis e uma barra de pesquisa permite filtrar o inventário por nome, modelo ou património.
* **Notificações Visuais:** O sistema utiliza mensagens de feedback (sucesso, erro, aviso) para informar os utilizadores sobre o resultado das suas ações.

## Arquitetura

A aplicação segue uma arquitetura moderna e escalável, estruturada para manter a separação de responsabilidades.

### Backend (Django)

O backend é construído sobre o padrão **MVT (Model-View-Template)**:

* **Model (`core/models.py`):** Define a estrutura do banco de dados. Os modelos principais são `Maquina`, `CustomUser` (utilizador), `Operacao` (histórico) e `Solicitacao`, que é o coração do novo fluxo de aprovações.
* **View (`core/views.py`):** Contém a lógica de negócio. A view principal (`dashboard_status`) funciona como uma API, devolvendo o estado completo do inventário em formato JSON para ser renderizado dinamicamente pelo frontend.
* **Template (`templates/`):** O `home.html` serve como a base para a aplicação de página única (SPA-like), enquanto os templates parciais são utilizados para renderizar componentes específicos.

### Frontend

A interface é construída com tecnologias web padrão, com foco numa experiência reativa:

* **HTML5 e Bootstrap 5:** Estruturam o conteúdo e garantem um design responsivo e moderno.
* **JavaScript (Puro):** O frontend é altamente dinâmico. Um script em `home.html` faz chamadas periódicas (polling) a um endpoint do Django (`/dashboard-status/`), recebe os dados em JSON e reconstrói a interface do utilizador em tempo real, criando a sensação de uma aplicação reativa sem a necessidade de frameworks complexos.

### Banco de Dados

* **SQLite:** Um banco de dados leve e baseado em ficheiros, ideal para desenvolvimento e aplicações de pequeno a médio porte. Os dados são persistidos num volume externo do Podman.

### Infraestrutura

* **Podman:** A aplicação é totalmente containerizada, garantindo consistência entre ambientes.
* **Nginx (Opcional):** Em produção, um proxy reverso como o Nginx pode ser utilizado para gerir HTTPS e servir ficheiros estáticos de forma mais eficiente.

## Estrutura do Projeto

```
.
├── core/                  # Principal aplicativo Django
│   ├── migrations/        # Arquivos de migração do banco de dados
│   ├── management/        # Comandos de gestão personalizados
│   ├── static/            # Ficheiros estáticos (imagens, CSS, JS)
│   ├── admin.py           # Configuração do painel de administração
│   ├── models.py          # Definição dos modelos da base de dados
│   ├── views.py           # Lógica de negócio (controllers)
│   ├── urls.py            # Rotas específicas da aplicação 'core'
│   └── utils.py           # Funções utilitárias (ex: decoradores)
├── gestao_maquinas/       # Configurações do projeto Django
│   ├── settings.py        # Configurações principais do projeto
│   └── urls.py            # Rotas principais do projeto
├── templates/             # Templates HTML globais
│   └── core/              # Templates da aplicação 'core'
│       └── partials/      # Pequenos templates reutilizáveis (já não são usados)
├── Dockerfile             # Receita para construir a imagem do contentor
├── entrypoint.sh          # Script de inicialização do contentor
├── manage.py              # Utilitário de linha de comando do Django
└── requirements.txt       # Lista de dependências Python
```


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
