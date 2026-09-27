# Seismic Pipe Monitor API
Este repositório contém o **back-end** da **API Seismic Pipe Monitor**, uma aplicação web desenvolvida para monitorar a interação entre pipelines e terremotos em tempo real e além disso, armazenar os dutos na base de dados com informações básicas: nome do duto, país, operadora, produto, coordenadas iniciais e coordenadas finais do duto.

---

## Funcionalidades Principais

Com esta interface, o usuário é capaz de:
* **Inserir um novo duto** na base de dados;
* **Visualizar todos os dutos cadastrados** na base de dados;
* **Editar** as informações de um duto existente;
* **Remover** um duto existente;
* **Visualizar** a trajetoria do duto no mapa e os terremotos ocorridos num raio de 1000 km a partir do ponto inicial do duto.

---

## Arquitetura do Seismic Pipe Monitor
![Arquitetura do Seismic Pipe Monitor](/img/Seismic-pipe-monitor-arquitetura.png)

---

## Instalação

Será necessário ter todas as libs python listadas no requirements.txt instaladas. Após clonar o repositório, é necessário ir ao diretório raiz, pelo terminal, para poder executar os comandos descritos abaixo.

> É fortemente recomendado o uso de ambientes virtuais do tipo [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html).

Uma vez criado um ambiente, para ativá-lo, execute o comando:

```bash
(base)$ conda activate env
```


Automáticamente ficará em andamento o ambiente "env". Para instalar as dependências descritas no arquivo 'requirements.txt' do projeto execute o comando:

```
(env)$ pip install -r requirements.txt
```

Para executar a API  basta executar:

```
(env)$ flask run --host 0.0.0.0 --port 5000
```
Abra o [http://localhost:5000/#/](http://localhost:5000/#/) no navegador para verificar o status da API em execução.

## Como executar através do Docker

Certifique-se de ter o Docker instalado e em execução em sua máquina.

Navegue até o diretório que contém o Dockerfile no terminal e seus arquivos de aplicação e Execute como administrador o seguinte comando para construir a imagem Docker:

```bash
$ docker build -t seismic-pipe-monitor-rest-api .
```

Uma vez criada a imagem, para executar o container basta executar, como administrador, o seguinte comando:

```bash
$ docker compose up --build
```

Uma vez executando, para acessar a API, basta abrir o http://localhost:5000/#/ no navegador.

---

## Comandos úteis

Para verificar se o container está em execução você pode executar o comando:

```bash
$ docker container ls --all
```

Para parar o container execute:

```bash
$ docker stop seismic-pipe-monitor-rest-api
```
---
## Funcionamento da API

Na API será possível ver as diferentes requisições que podem ser feitas:

![Rotas da API](/img/img1.png)

Para consultar todos os terremotos ocorridos nos últimos 15 dias num raio de 1000 km a partir do ponto inicial do duto, basta clicar na opção GET, depois clicar em "Try it out" e, em seguida, preencher as coordenadas de início do duto e executar:

![Get Terremotos por coordenadas](/img/img2.png)

A API Externa da USGS devolverá a lista de terremotos em formato JSON:

![Lista de terremotos por coordenadas](/img/img3.png)

Para adicionar um novo duto á base de dados basta clicar na opção "POST /pipelines", depois clicar em "Try it out" e, em seguida, preencher os campos com os dados do duto e executar:

![Adicionar novo duto](/img/img4.png)

Se o nome do duto ainda não foi adicionado, receberemos uma resposta 200 e o duto será adicionado á base:

![Adicionar novo duto](/img/img5.png)

A rota GET /pipelines consulta todos os dutos que já estão armazenados na base de dados, então não é necessário preencher o formulário, simplesmente clicar em "Try it out" e executar:

![Lista de dutos](/img/img6.png)

A resposta do servidor será em formato JSON com as informações dos dutos armazenados na base:

![Lista de dutos](/img/img7.png)

Na requisição PUT /pipelines é possível atualizar todos os campos do duto, exceptuando o ID. É importante que o duto esteja cadastrado na base para poder ser atualizado. Ao clicar em "Try it out" será necessário preencher os campos com os dados que deseja atualizar:

![Atualizar duto](/img/img8.png)

Se o duto estiver cadastrado, receberemos uma resposta 200 e o duto será atualizado:

![Atualizar duto](/img/img9.png)

Finalmente, para deletar um duto, basta clicar na opção "DELETE /pipelines", depois clicar em "Try it out" e, em seguida, preencher o ID do duto a ser removido:

![Deletar duto](/img/img10.png)

Se o duto estiver cadastrado, receberemos uma resposta 200 e o duto será removido:

![Deletar duto](/img/img11.png)
