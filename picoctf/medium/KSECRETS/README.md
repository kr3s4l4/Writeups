Writeup: KSECRETS - picoCTF 2026
📋 Información del Reto

    Nombre: KSECRETS

    Categoría: General Skills

    Dificultad: Medium

    Puntos: 100

    Autor: Darkraicg492

    Descripción: We have a kubernetes cluster setup and flag is in the secrets. You think you can get it?

🔍 Conceptos Previos
¿Qué es kubectl?

kubectl es la herramienta de línea de comandos oficial de Kubernetes que permite interactuar con un clúster. Con ella podemos:

    Desplegar aplicaciones

    Inspeccionar y administrar recursos del clúster

    Ver logs

    Gestionar secrets, pods, servicios, etc.

¿Qué son los Namespaces en Kubernetes?

Los namespaces son un mecanismo de aislamiento lógico dentro de un clúster de Kubernetes. Permiten dividir los recursos del clúster entre múltiples usuarios, equipos o aplicaciones. Piensa en ellos como "carpetas virtuales" que organizan y separan recursos.

Namespaces comunes:

    default: Namespace por defecto donde se crean los recursos si no se especifica otro

    kube-system: Namespace para objetos creados por el sistema de Kubernetes

    picoctf: En este reto, el namespace personalizado donde se ocultó la flag

¿Qué son los Secrets?

Los Secrets en Kubernetes son objetos diseñados para almacenar información sensible como contraseñas, tokens, claves SSH, etc. Los datos dentro de un secret se almacenan codificados en base64 (no cifrados), por lo que es importante controlar el acceso a ellos mediante RBAC.
🚀 Proceso de Resolución
Paso 1: Configuración Inicial

Al iniciar el reto, descargamos el archivo kubeconfig.yaml proporcionado por la plataforma:
bash

┌──(root㉿kali)-[/home/kr3s4l4/picoctf/medium/KSECRETS]
└─# ls -la
total 8
drwxr-xr-x  2 root root   4096 jul  3 15:43 .
drwxr-xr-x 11 root root   4096 jul  3 15:40 ..
-rwxrwx---  1 root vboxsf    0 jul  3 15:42 kubeconfig.yaml

Problema: El archivo inicial estaba corrupto/vacío (0 bytes), por lo que tuvimos que volver a descargarlo.
Paso 2: Instalación de kubectl

Nuestra máquina Kali no tenía kubectl instalado:
bash

┌──(root㉿kali)-[/home/kr3s4l4/picoctf/medium/KSECRETS]
└─# kubectl --kubeconfig=kubeconfig.yaml get secrets
No se ha encontrado la orden «kubectl», pero se puede instalar con:
apt install kubectl
¿Quiere instalarlo? (N/y)y
apt install kubectl

Paso 3: Primer Intento de Conexión

Al intentar conectarnos directamente, obtuvimos un error de certificado TLS:
bash

┌──(root㉿kali)-[/home/kr3s4l4/picoctf/medium/KSECRETS]
└─# kubectl --kubeconfig=kubeconfig.yaml --server=https://green-hill.picoctf.net:51759 get secrets
E0703 15:46:45.179360  540420 memcache.go:265] "Unhandled Error" err="couldn't get current server API group list: 
Get \"https://green-hill.picoctf.net:51759/api?timeout=32s\": tls: failed to verify certificate: x509: certificate 
is valid for challenge, kubernetes, kubernetes.default, kubernetes.default.svc, kubernetes.default.svc.cluster.local, 
localhost, not green-hill.picoctf.net"

Explicación: El certificado SSL/TLS del servidor no coincide con el nombre de dominio green-hill.picoctf.net, ya que está emitido para nombres internos del clúster. Esto es normal en entornos de CTF.
Paso 4: Corrección del Archivo kubeconfig

Al inspeccionar el archivo descargado, descubrimos que apuntaba a localhost en lugar del servidor del reto:
bash

┌──(root㉿kali)-[/home/kr3s4l4/picoctf/medium/KSECRETS]
└─# cat kubeconfig.yaml
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: LS0tLS1CRUdJTiB...
    server: https://127.0.0.1:6443  # ❌ Apunta a localhost
  name: default
contexts:
- context:
    cluster: default
    user: default
  name: default
current-context: default
kind: Config
users:
- name: default
  user:
    client-certificate-data: LS0tLS1CRUdJTiB...
    client-key-data: LS0tLS1CRUdJTiBFQy...

Solución: Editamos el archivo con nano y cambiamos:
yaml

server: https://127.0.0.1:6443

Por:
yaml

server: https://green-hill.picoctf.net:51759

Paso 5: Conexión Exitosa al Clúster

Usamos el flag --insecure-skip-tls-verify para omitir la verificación del certificado:
bash

┌──(root㉿kali)-[/home/kr3s4l4/picoctf/medium/KSECRETS]
└─# kubectl --kubeconfig=kubeconfig.yaml --insecure-skip-tls-verify get secrets --all-namespaces
NAMESPACE     NAME                       TYPE                               DATA   AGE
kube-system   chart-values-traefik       helmcharts.helm.cattle.io/values   1      8m38s
kube-system   chart-values-traefik-crd   helmcharts.helm.cattle.io/values   0      8m38s
kube-system   k3s-serving                kubernetes.io/tls                  2      8m40s
picoctf       ctf-secret                 Opaque                             1      8m32s

Análisis del output:

    NAMESPACE: Columna que muestra los diferentes namespaces del clúster

    NAME: Nombre del recurso secret

    TYPE: Tipo de secret

        helmcharts.helm.cattle.io/values: Secrets de Helm (gestor de paquetes)

        kubernetes.io/tls: Secret para certificados TLS

        Opaque: Secret genérico (el más común para datos arbitrarios)

    DATA: Número de campos/keys dentro del secret

    AGE: Tiempo desde su creación

¡Encontramos algo interesante! En el namespace picoctf hay un secret llamado ctf-secret de tipo Opaque con 1 dato.
Paso 6: Extracción de la Flag

Obtenemos el contenido del secret en formato YAML:
bash

┌──(root㉿kali)-[/home/kr3s4l4/picoctf/medium/KSECRETS]
└─# kubectl --kubeconfig=kubeconfig.yaml --insecure-skip-tls-verify get secret ctf-secret -n picoctf -o yaml
apiVersion: v1
data:
  flag: cGljb0NUR*******************************MWYwNzF9Cg==
kind: Secret
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"v1","data":{"flag":"cGljb0NURntrczNjcjM3NV80MW43X3M0ZjNfOTZhMWYwNzF9Cg=="},"kind":"Secret","metadata":{"annotations":{},"name":"ctf-secret","namespace":"picoctf"},"type":"Opaque"}
  creationTimestamp: "2026-07-03T13:41:12Z"
  name: ctf-secret
  namespace: picoctf
  resourceVersion: "390"
  uid: 4577f959-1a65-43ed-8936-6b33275c0b6d
type: Opaque

Vemos claramente el campo flag con un valor en base64: cGljb0NURntrczNjcjM3NV80MW43X3M0ZjNfOTZhMWYwNzF9Cg==
Paso 7: Decodificación Base64

Los secrets en Kubernetes almacenan sus datos codificados en base64, no cifrados. Para obtener el valor original:
bash

┌──(root㉿kali)-[/home/kr3s4l4/picoctf/medium/KSECRETS]
└─# echo cGljb0NURn***********************MWYwNzF9Cg== | base64 -d
picoCTF{************************}

📚 Lecciones Aprendidas

    Kubernetes Secrets no están cifrados por defecto: Solo están codificados en base64, por lo que cualquiera con acceso al clúster y permisos puede decodificarlos fácilmente.

    Namespaces como mecanismo de organización: El secreto estaba en el namespace picoctf, no en default. Siempre hay que buscar en todos los namespaces con --all-namespaces.

    Certificados en CTFs: Es común que los certificados SSL/TLS en entornos de CTF no coincidan con el dominio, requiriendo --insecure-skip-tls-verify.

    Verificación de archivos de configuración: El archivo kubeconfig inicial estaba corrupto y luego apuntaba a localhost. Siempre verificar el contenido de los archivos descargados.

    Tipos de Secrets: Kubernetes tiene diferentes tipos (Opaque, kubernetes.io/tls, helmcharts..., etc.). Los genéricos (Opaque) son los más comunes para almacenar datos arbitrarios.

🛡️ Buenas Prácticas de Seguridad

En un entorno real, para proteger los secrets en Kubernetes se recomienda:

    Usar RBAC (Role-Based Access Control) para limitar quién puede acceder a los secrets

    Cifrar los secrets en reposo (encryption at rest)

    Usar herramientas externas como HashiCorp Vault o Sealed Secrets

    No incluir archivos kubeconfig en repositorios públicos

    Rotar regularmente las credenciales

🔧 Comandos Utilizados
Comando	Descripción
kubectl --kubeconfig=<file> get secrets	Lista secrets en el namespace default
kubectl --kubeconfig=<file> get secrets --all-namespaces	Lista secrets en todos los namespaces
kubectl --kubeconfig=<file> get secret <name> -n <namespace> -o yaml	Muestra el contenido de un secret en YAML
kubectl --kubeconfig=<file> --insecure-skip-tls-verify	Omite la verificación de certificados TLS
echo "<base64>" | base64 -d	Decodifica una cadena en base64
