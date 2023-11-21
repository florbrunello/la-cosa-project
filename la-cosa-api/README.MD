# LA COSA API

API REST basada en Python y FastAPI.

Incluye la lógica de funcionamiento del juego "La Cosa", implementado como proyecto de la materia "Ingeniería del Software I" en el año 2023.

## Dependencias
El proyecto corre en Python 3.10.x. Recomendamos el uso de un entorno virtual para su ejecución. Para ello, es necesario instalar virtualenv.

## Como instalar dependencias
1. Crear un entorno virtual (virtualenv).
   - (https://itslinuxfoss.com/install-virtualenv-ubuntu-22-04/)
2. Dentro del entorno virtual, actualizar pip a la versión más reciente: $pip install -U pip
3. Instalar las dependencias del proyecto: pip install -r requirements.txt

## Correr el servidor
Dentro del directorio "src", ejecutar el siguiente comando:
 $ uvicorn --host 0.0.0.0 --port 8000 --reload main:app

## Detener el servidor
Presionar Ctrl+C en la terminal donde se está ejecutando el servidor.