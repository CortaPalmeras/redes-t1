# Tarea 1 - Redes

## Como ejecutar

Esta tarea fue hecha en python utilizando modulos de la librería estandar,
por lo que no es necesario instalar dependencias, recomiendo usar linux
para ejecutarla, solo la he probado en Debian con Python 3.11.2.

Para ejeutar la tarea es necesario crear bases de datos de sqlite,
el script `csv_to_db.py` transforma un archivo csv al formato requerido,
este se puede ejecutar de la siguiente manera:

```bash
python3 python3 csv_to_db.py names.csv
```

`names.csv` es el archivo que yó utilicé para probar mi tarea, pero debería
funcionar con cualquier csv que tenga la misma estructura.


Completé hasta la parte 2.a de la tarea, para ejecutarla se usa el archivo 
`runserver.py`, este recibe como primer argumento el nombre del servidor que 
se desea ejecutar, las opciones validas son `instagram`, `whatsapp`, `others`,
y `master`. `others` es el servidor que quecibe requests para redes sociales que 
no son instagram o whatsapp, mientras que `master` es el servidor que recibe
requests para todas las redes sociales y le pregunta a los otros tres servidores.

Para ejecutar los 4 servidores es necesario correr estos comandos en paralelo,
recomiendo utilizar una terminal (o tab) distinta para cada servidor.

```bash
python runserver.py whatsapp
python runserver.py instagram
python runserver.py others
python runserver.py master
```

cada servidor va a imprimir la url a la que va a estar escuchando, si lanzan un 
error porque el puerto está en uso, se puede cambiar para cada servidor en el 
archivo `servers.csv`


## El codigo

La tarea tiene esta estructura:

```
.
├── servers
│   ├── __init__.py
│   ├── databases.py
│   ├── http.py
│   ├── master_server.py
│   ├── query_validation.py
│   ├── social_media_server.py
│   └── thread_pool.py
├── csv_to_db.py
├── names.csv
├── README.md
├── runserver.py
└── servers.csv
```

El directorio `servers` es un mudulo que contiene la mayorría del codigo fuente,
el archivo `social_media_server.py` tiene la lógica de los servidores que devuelven
datos de las bases de datos, mientas que `master_server.py` tiene el servidor `master`
ambos tipos de servidores utilizan `http.py` y `query_validation.py` para parsear
y validar las requests que reciben, el archivo `databases.py` tiene las queries de SQL 
que usan los servidores, y `thread_pool.py` es usado por el servidor `master` para
enviar equests de http en paralelo a los otros servidores.



