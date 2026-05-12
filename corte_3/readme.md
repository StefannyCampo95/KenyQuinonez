FASE 1 – OBSERVAR (sin modificar código)

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


FASE 2 – APLICAR (Extensión del Circuit Breaker)

### **analizar y decidir:**

-¿Cada servicio debe tener su propio contador de fallos?
-¿El circuito debe abrirse de forma independiente por servicio?
-¿Qué pasa si falla un servicio pero el otro sigue funcionando?

FASE 3 – INVESTIGAR (Half-Open)

-¿Qué significa “half-open”?
-¿Cuándo se vuelve a intentar una llamada?
-¿Qué pasa si el servicio vuelve a fallar?

FASE 4 – IMPLEMENTAR (Recuperación)
