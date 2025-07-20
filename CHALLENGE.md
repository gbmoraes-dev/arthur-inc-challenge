# Teste Dev jr

Olá, bem-vindo(a) ao teste para pessoa desenvolvedora Jr! 🖖

## A quest pelo sistema de fretes: 🚚

Esse é um sistema de cálculo de fretes, o usuário entra com a distância a ser percorrida, peso da encomenda e a opção do frete. A partir daí o sistema calcula o valor do frete.
Porém há um problema, alguns testes não estão passando. Precisamos de você para fazê-los passar!
Precisamos também implementar a seguinte história de usuário:

"Eu como usuário quero inserir o CEP de partida e o de entrega da minha encomenda, peso e tipo do frete e espero que o sistema me retorne o valor do frete."

Nossas pesquisas nos mostraram que há muitas APIs públicas que retornam os dados de CEP porém preferimos seguir com a [Brasil API](https://brasilapi.com.br/).
Agora para calcular a distância entre os dois CEPs seguimos com a API do [Project OSRM](https://project-osrm.org).

Após a implementação, será necessário reescrever alguns dos testes ou até escrever novos se assim decidir.

### Como instalar as dependências? 📦

Para isso você pode tanto utilizar o requirements.txt ou instalar o [Pipenv](https://pipenv.pypa.io/en/latest/) e rodar os seguintes comandos:

- requirements:
  `pip install -r requirements.txt`
- pipenv:
  `pipenv install`

### Como executar os testes? ⚙️

Esse teste utiliza do pytest para executar testes automatizados, para rodar a suíte de testes, basta chamar o pytest com o seguinte comando no seu terminal: `pytest`.
Se você estiver usando o pipenv, será importante acessar o ambiente virtual dele antes de rodar os testes, para isso, basta utilizar o comando `pipenv shell`

Qualquer dúvidas deixe-nos saber! :)
