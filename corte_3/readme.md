**FASE 1 – OBSERVAR (sin modificar código)**

-¿Qué hace el sistema actualmente?

    *Cuando el servicio backend (mascotas) está funcionando:
    El gateway recibe la petición y permite la conexión.
    *Cuando el servicio no está disponible, la petición enviada falla dentro del try (no se ejecuta el bloque de código), y posteriormente pasa al except si para ejecutar las acciones debido al error presentado
    *Inicia a contabilizar el número de intentos para conectarse (fallos)
    *Muestra los logs.
    *Finalmente luego del número de fallos establecidos en el código (en este caso 3), abre el circuito y el gateway deja de intentar conectarse al backend y retorna un mensaje de error, informando que el servicio no está disponible.


-¿Se protege o insiste?

    El sistema se protege, ya que implementa una estrategia donde:

    -Primero intenta conectarse al backend.
    -Detecta fallos consecutivos.
    -Después de cierto límite (3 fallos), deja de insistir.

    Evitando:
    -Saturar el backend caído.
    -Consumir recursos innecesarios.
    -Generar esperas largas por timeout.
    -Acumular conexiones fallidas.


**FASE 2 – APLICAR (Extensión del Circuit Breaker)**

 **analizar y decidir:**

-¿Cada servicio debe tener su propio contador de fallos?

    Sí, cada servicio debería tener su propio contador para el estado (abierto o cerrado) del Circuit Breaker, porque cada microservicio puede fallar de manera independiente.

-¿El circuito debe abrirse de forma independiente por servicio?

    Sí, cada microservicio debe tener:

    -su contador
    -su estado de circuito
    -sus reglas de recuperación

-¿Qué pasa si falla un servicio pero el otro sigue funcionando?

    El gateway debe seguir respondiendo con los servicios disponibles, la idea es evitar que una falla derribe el sistema en su totalidad.

FASE 3 – INVESTIGAR (Half-Open)

-¿Qué significa “half-open”?
-¿Cuándo se vuelve a intentar una llamada?
-¿Qué pasa si el servicio vuelve a fallar?

FASE 4 – IMPLEMENTAR (Recuperación)
