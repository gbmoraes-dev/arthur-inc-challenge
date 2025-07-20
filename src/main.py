from model.frete import Frete

def gerar_frete(peso, distancia, opcao) -> str:
    try:
        if opcao == 1:
            frete = Frete(distancia, peso)
            frete.tipo = "Normal"
            frete.calcular_preco()
        elif opcao == 2:
            frete = Frete(distancia, peso)
            frete.tipo = "Sedex"
            frete.calcular_preco()
        elif opcao == 3:
            frete = Frete(distancia, peso)
            frete.tipo = "Sedex10"
            frete.calcular_preco()
    except Exception as e:
        raise e
    return f"O valor do frete é {frete.valor:.2f}"


if __name__ == "__main__":
    peso = float(input("Entre com o peso da encomenda -> "))
    distancia = float(input("Entre com a distância a ser percorrida -> "))
    opcao = int(
        input(
            "Entre com a opcao de entrega\n\t(1)Normal\n\t(2)Sedex\n\t(3)Sedex10\n-> "
        )
    )
    print(gerar_frete(peso, distancia, opcao))
