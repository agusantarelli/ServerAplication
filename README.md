# Aplicación Servidor

## Modo de Trabajo
Para realizar el proyecto trabajamos mayormente en sesiones interactivas utilizando el paquete *teletype* de Atom y comunicandonos por Discord, 
aunque tambien hubo aportes individuales pero siempre con el conocimiento de todo el grupo.

## Protocolo HFTP
Home-made File Transfer Protocol (HFTP) es un protocolo de capa de aplicación que utiliza TCP como protocolo de transporte. TCP garantiza una entrega segura, libre de errores y en orden de todas las transacciones hechas con HFTP

### Estructura del Servidor
#### Ejercicio Estrella

Para poder manejar varias conexiones, pensamos en simultaneidad y nos llevo apensar en concurrencia o threads. Luego nos dimos cuenta de que lo unico que queriamos es que para cada conexion entrante, el servidor aceptara el socket y no "se confundiera" al enviar y recibir informacion.

La técnica que permite que una aplicación ejecute simultáneamente varias operaciones en el mismo espacio de proceso se llama Threading. A cada flujo de ejecución que se origina durante el procesamiento se le denomina hilo o subproceso, pudiendo realizar o no una misma tarea.
Ésta estructura utiliza ``threads``, módulo de Python el cual hace posible la programación con hilos, y que nos posibilitó implementar la conexión de múltiples cliente al server.
Cada vez que un cliente levanta el server, se intancia un nuevo thread, y llama a la función
```python
def threaded(connection):
```
donde dentro de la misma se va a encontrar nuestra función ```handle``` que va a manejar las diferentes solicitudes del cliente hasta que el mismo envíe el comando ``quit``, el cual procederá a su desconexión, ya que se instanciará la variable ``connected``en ``False``

### Decisiones de diseño
Algunas de las decisiones de diseño fueron:

* En ``connection.py`` la función ``handle`` va a ser la encargada de manejar lo que ocurra en consola, tanto sean el manejo de errores como el manejo de los comandos. Para esto último, en ``handle`` tenemos una función llamada ``ok_command`` la cual va a verificar que lo que el cliente está pasando es una comando válido y ``ok_arguments`` que verifica los argumentos del comando, de ser así instantaneamente se llama a la función ``do_command``, la cual está dividida por casos según cual haya sido el comando solicitado.
* Manejar las distintas conexiones por ``threads`` como hemos mencionado en la estructura del servidor.
* Hemos creado para el objeto ``Connection`` un atributo ``error_count`` que cuenta la cantidad de ocurrencia de errores de tipo no fatales y en la funcion ``handle`` verificamos que ``error_count < MAX_ERRORS`` donde ``MAX_ERRORS`` es una constante agregada en ``constants.py``. Al alcanzarlo devuelve error 101.
* En la funcion ``handle`` cuando creamos nuestro buffer decodificando la data que nos llega, tenemos en cuenta que sea un caracter de tipo ascii, pues si no lo es, devolvemos error ``101`` y cerramos la conexión.





### Preguntas
#### ¿Qué estrategias existen para poder implementar este mismo servidor pero con capacidad de atender múltiples clientes simultáneamente?
Un programa multiproceso contiene dos o más partes que pueden ejecutarse simultáneamente. Cada parte de dicho programa se denomina hilo, y cada hilo define una ruta de ejecución separada. La programación de sockets multiproceso describe que un servidor de sockets multiproceso puede comunicarse con más de un cliente al mismo tiempo en la misma red.
Como el server inicialmente sólo podía atender a un cliente a la vez, la estrategia que investigamos y que hemos implementado, como anteriormente mencionamos, es la creación de hilos multihilo o multithreaded para lograr la conexión simultánea de varios clientes. El código hace uso del módulo estándar threading, que otorga diversas funciones, como por ejemplo la que hemos utilizado:
```python
start_new_thread(threaded, (connection,)):
```
que comienza un nuevo hilo tomando la funcion ``threaded`` y los parametros que tomaría la misma.


## Autores

* **Benitez Iván** - 
* **Santarelli Agustina** - 
* **Vilar Dávila Valentín** -  

