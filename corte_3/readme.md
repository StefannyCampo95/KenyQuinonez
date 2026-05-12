**FASE 1 – OBSERVAR (sin modificar código)**

**-¿Qué hace el sistema actualmente?**

    *Cuando el servicio backend (mascotas) está funcionando:
    El gateway recibe la petición y permite la conexión.
    *Cuando el servicio no está disponible, la petición enviada falla dentro del try (no se ejecuta el bloque de código), y posteriormente pasa al except si para ejecutar las acciones debido al error presentado
    *Inicia a contabilizar el número de intentos para conectarse (fallos)
    *Muestra los logs.
    *Finalmente luego del número de fallos establecidos en el código (en este caso 3), abre el circuito y el gateway deja de intentar conectarse al backend y retorna un mensaje de error, informando que el servicio no está disponible.


**-¿Se protege o insiste?**

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

 **Analizar y decidir:**

**-¿Cada servicio debe tener su propio contador de fallos?**

    Sí, cada servicio debería tener su propio contador para el estado (abierto o cerrado) del Circuit Breaker, porque cada microservicio puede fallar de manera independiente.

    Ej: El servicio de usuarios puede estar activo y el servicio de mascotas puede estar caído.

**-¿El circuito debe abrirse de forma independiente por servicio?**

    Sí, cada microservicio debe tener:

    -Contador
    -Estado de circuito
    -Tiempo de recuperación

    Si el circuito fuese global, una falla en el servicio mascotas bloquearía al servicio de usuarios y el gateway quedaría completamente inutilizable.
    

**-¿Qué pasa si falla un servicio pero el otro sigue funcionando?**

    El gateway debe seguir respondiendo con los servicios disponibles, la idea es evitar que una falla derribe el sistema en su totalidad.

**FASE 3 – INVESTIGAR (Half-Open)**

**-¿Qué significa “half-open”?**

    El estado Half-Open es una etapa intermedia del Circuit Breaker. (medio abierto, semiabierto)

**-¿Cuándo se vuelve a intentar una llamada?**

    Después de cierto tiempo de espera.

    El gateway permite una sola petición de prueba, si responde correctamente:
    el circuito se cierra
    y si vuelve a fallar:
    el circuito se abre nuevamente

**-¿Qué pasa si el servicio vuelve a fallar?**

    El circuito vuelve inmediatamente a abrirse, evitando así:
    -Sobrecarga
    -Múltiples timeouts
    -Saturación del sistema
    
**FASE 4 – IMPLEMENTAR (Recuperación)**
