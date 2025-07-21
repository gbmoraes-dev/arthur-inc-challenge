# Calculadora de Fretes

## Sobre o Projeto

Este sistema realiza o cálculo de fretes baseado na distância, peso da encomenda e opção de frete selecionada. O usuário pode inserir o CEP de origem e destino, ou uma distância específica, além do peso da encomenda e o tipo de frete desejado (Normal, Sedex ou Sedex10).

## Decisões Técnicas

### Padrões de Design

#### Strategy Pattern
O cálculo de frete foi implementado utilizando o **Strategy Pattern**, permitindo diferentes algoritmos de cálculo (Normal, Sedex, Sedex10) que podem ser selecionados em tempo de execução. Esta abordagem facilita a adição de novos tipos de frete no futuro sem modificar o código existente.

#### Factory Pattern
O **Factory Pattern** é utilizado para criar as diferentes estratégias de cálculo de frete. A classe `FreightStrategyFactory` cria instâncias concretas de estratégias baseadas na opção escolhida pelo usuário.

#### Retry Pattern
O **Retry Pattern** foi implementado usando a biblioteca **tenacity** para aumentar a resiliência do sistema contra falhas temporárias nas APIs externas (Brasil API e OSRM). Este padrão permite que as requisições que falham sejam automaticamente tentadas novamente com um tempo de espera exponencial entre as tentativas, aumentando a chance de sucesso em casos de instabilidade momentânea da rede ou dos serviços externos.

#### Circuit Breaker Pattern
O **Circuit Breaker Pattern** foi implementado com a biblioteca **pybreaker** para evitar chamadas repetidas a serviços externos que estejam falhando consistentemente. Quando um serviço apresenta falhas consecutivas, o circuit breaker "abre" e para de fazer requisições por um tempo determinado, evitando sobrecarga no serviço e permitindo sua recuperação, além de falhar rapidamente para o usuário ao invés de esperar timeouts.

#### Cache Pattern
O **Cache Pattern** foi implementado utilizando **Redis** como armazenamento para dados recuperados das APIs externas (Brasil API e OSRM). Esta abordagem reduz significativamente o tempo de resposta para consultas repetidas, diminui a carga nos serviços externos e melhora a experiência do usuário. O sistema utiliza um decorator `@cached` que automaticamente gerencia o ciclo de vida dos dados em cache, implementado como um Singleton para garantir uma única conexão com o Redis.

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

### Utilizando Docker (recomendado)

1. Clone o repositório
   ```bash
   git clone https://github.com/gbmoraes-dev/arthur-inc-challenge.git
   cd arthur-inc-challenge
   ```

2. Construa e execute os containers com Docker Compose
   ```bash
   docker-compose up -d
   ```

   Isso iniciará automaticamente o container da aplicação e o Redis para cache.

3. Acesse o container da aplicação para interagir com o sistema
   ```bash
   docker exec -it freight-calculator bash
   python src/main.py
   ```

### Instalação Local

1. Clone o repositório
   ```bash
   git clone https://github.com/gbmoraes-dev/arthur-inc-challenge.git
   cd arthur-inc-challenge
   ```

2. Configure um ambiente virtual
   - Utilizando Pipenv:
     ```bash
     pip install pipenv
     pipenv install
     pipenv shell
     ```

3. Configure as variáveis de ambiente
   ```bash
   cp .env.example .env
   ```

4. Execute o Redis localmente (opcional, mas recomendado para cache)
   ```bash
   docker run -d -p 6379:6379 --name freight-redis redis:7.0-alpine
   ```

5. Execute a aplicação
   ```bash
   python src/main.py
   ```

## Execução de Testes

### Local:

```bash
# Executar testes
pipenv run pytest

# Com cobertura de código
pipenv run pytest --cov=src
```

### Com Docker:

```bash
# Executar testes
docker compose run --entrypoint "python -m pytest" app
```
