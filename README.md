# Calculadora de Fretes

## Sobre o Projeto

Este sistema realiza o cálculo de fretes baseado na distância, peso da encomenda e opção de frete selecionada. O usuário pode inserir o CEP de origem e destino, ou uma distância específica, além do peso da encomenda e o tipo de frete desejado (Normal, Sedex ou Sedex10).

## Decisões Técnicas

### Padrões de Design

#### Strategy Pattern
O cálculo de frete foi implementado utilizando o **Strategy Pattern**, permitindo diferentes algoritmos de cálculo (Normal, Sedex, Sedex10) que podem ser selecionados em tempo de execução. Esta abordagem facilita a adição de novos tipos de frete no futuro sem modificar o código existente.

#### Factory Pattern
O **Factory Pattern** é utilizado para criar as diferentes estratégias de cálculo de frete. A classe `FreightStrategyFactory` cria instâncias concretas de estratégias baseadas na opção escolhida pelo usuário.

### Princípios SOLID

#### Single Responsibility Principle (SRP)
Cada classe tem uma única responsabilidade:
- `Freight`: Representa o frete e suas propriedades
- `FreightStrategy`: Define a interface para estratégias de cálculo
- `CepProvider`: Abstrai a obtenção de dados de CEP
- `DistanceProvider`: Abstrai o cálculo de distância

#### Open/Closed Principle (OCP)
O sistema é aberto para extensão (novas estratégias de frete podem ser adicionadas) e fechado para modificação (não é necessário modificar o código existente).

#### Liskov Substitution Principle (LSP)
As classes derivadas (NormalFreight, SedexFreight, Sedex10Freight) podem ser usadas onde a classe base (FreightStrategy) é esperada.

#### Interface Segregation Principle (ISP)
Interfaces específicas são definidas (FreightStrategy, CepProvider, DistanceProvider) em vez de uma interface genérica, garantindo que as classes implementem apenas o que realmente precisam.

#### Dependency Inversion Principle (DIP)
Módulos de alto nível não dependem de módulos de baixo nível, ambos dependem de abstrações. Por exemplo, a função `get_distance_between_ceps` depende da abstração `CepProvider`, não de uma implementação concreta.

### Estrutura do Projeto

O projeto está organizado da seguinte forma:

```
src/
├── exceptions.py         # Exceções customizadas
├── factories/            # Implementações do Factory Pattern
│   └── freight_factory.py
├── main.py               # Ponto de entrada da aplicação
├── model/                # Modelos de dados
│   └── freight.py
├── provider/             # Provedores de serviços externos
│   ├── cep.py            # Interface para provedores de CEP
│   ├── distance.py       # Interface para provedores de distância
│   └── services/         # Implementações concretas de provedores
│       ├── brasil_api.py # Integração com Brasil API
│       └── osrm_api.py   # Integração com OSRM API
├── services.py           # Serviços da aplicação
├── strategies/           # Implementações do Strategy Pattern
│   ├── freight_calulator.py
│   └── freight_strategy.py
└── validation.py         # Validações de dados

test/                     # Testes automatizados
├── test_integration.py
├── test_main.py
├── test_providers.py
├── test_services.py
└── test_strategy.py
```

Esta estrutura reflete a separação de responsabilidades e a aplicação dos padrões de design mencionados anteriormente.

### Containerização com Docker

O projeto utiliza Docker para garantir consistência entre ambientes:

- **Multi-stage build** para otimizar o tamanho da imagem final
- Separação de camadas para melhor cache e reconstrução mais rápida
- Execução como usuário não-root para segurança
- Configuração via variáveis de ambiente
- Docker Compose para orquestração simplificada

### Integração Contínua (CI)

A pipeline de CI implementada no GitHub Actions inclui:

- Verificação automática em pushes para a branch principal e pull requests
- Instalação de dependências via Pipenv
- Verificação de formatação com Black
- Análise estática de código com Ruff
- Verificação de tipos com MyPy
- Execução de testes com pytest e verificação de cobertura (mínimo 80%)

## Como Executar o Projeto

### Requisitos

- Python 3.12 ou superior
- Pipenv (opcional)
- Docker e Docker Compose (opcional)

### Execução Local

#### Com Pipenv:

```bash
# Adicionar as envs
cp .env.example .env

# Instalar dependências
pipenv install

# Ativar o ambiente virtual
pipenv shell

# Executar o projeto
PYTHONPATH=./src python -m src.main
```

### Execução com Docker

```bash
# Construir e iniciar o container
docker compose up --build

# Ou para executar em segundo plano
docker compose up --build -d

# Para acessar o shell no container
docker exec -it freight-calculator bash

# Executar o projeto
python -m src.main
```

## Execução de Testes

### Local:

```bash
# Com Pipenv
pipenv run pytest

# Com cobertura de código
pipenv run pytest --cov=src
```

### Com Docker:

```bash
# Executar testes
docker compose run --entrypoint "python -m pytest" app
```bash
