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

    Líneas 119 a 316

**Análisis final**

**-¿Qué cambió en el comportamiento del sistema?**

    Al inicio del laboratorio el gateway únicamente realizaba peticiones directas a los microservicios sin ningún mecanismo de protección.
    Cuando un servicio fallaba, el sistema seguía intentando conectarse continuamente, generando:

    -Múltiples errores
    -Tiempos de espera (timeouts)
    -Consumo innecesario de recursos
    -Saturación del gateway

    Inicialmente solo se implementó un Circuit Breaker básico en el endpoint /mascotas, donde después de varios fallos consecutivos el circuito se abría y el gateway dejaba de insistir.

    Posteriormente, el comportamiento del sistema cambió significativamente al extender la lógica a todos los endpoints:

    /usuarios
    /mascotas
    /resumen

    Con esto se logró:

    -Aislamiento de fallos por servicio
    -Protección individual de cada microservicio
    -Respuestas parciales en caso de fallos
    -Mayor estabilidad del gateway

    Finalmente, con la implementación de HALF-OPEN, el sistema dejó de depender de reinicios manuales para recuperarse.
    Ahora el gateway:

    -Detecta fallos
    -Abre el circuito
    -Espera un tiempo definido
    -Realiza una prueba de reconexión

    Decide automáticamente:

    -Cerrar el circuito si el servicio responde
    -Volver a abrirlo si sigue fallando

    Esto convirtió el sistema en una arquitectura mucho más resiliente y tolerante a fallos.

**-¿Qué decisiones tomaron en la implementación?**

    1. Circuitos independientes por servicio**

    Se decidió que cada microservicio tuviera:

    -Propio contador de fallos
    -Propio estado del circuito
    -Propio tiempo de recuperación

    Esto evitó que la caída de un servicio afectara a los demás.

    Ejemplo:

    mascotas podía estar caído
    usuarios seguía funcionando normalmente

    2. Uso de estructuras dinámicas

    En lugar de crear variables separadas para cada endpoint, se utilizó un diccionario:

    circuito = {
        "usuarios": {...},
        "mascotas": {...}
    }

    Esto permitió:

    -Reutilizar lógica
    -Evitar duplicación de código
    -Facilitar escalabilidad

    3. Implementación del estado HALF-OPEN

    Se decidió implementar recuperación automática mediante:

    -Tiempo de espera
    -Prueba de reconexión
    -Reapertura automática si fallaba nuevamente

    Esto hizo que el sistema pudiera recuperarse sin intervención manual.

    4. Manejo parcial de respuestas en /resumen

    Se decidió que el endpoint /resumen siguiera funcionando aunque uno de los servicios estuviera caído.

    Ejemplo:

    {
    "usuarios": [-----------],
    "mascotas": "No disponible"
    }

    Esto permitió degradación controlada en lugar de caída total.

    5. Uso de logs para monitoreo

    Se agregaron mensajes en consola para observar:

    -Fallos
    -Apertura del circuito
    -Transición a HALF-OPEN
    -Recuperación del servicio

    Esto facilitó las pruebas y validaciones del laboratorio.


**-¿Qué dificultades encontraron?**

    1. Manejo de estados del Circuit Breaker

    La mayor dificultad fue controlar correctamente las transiciones entre:

    CLOSED
    OPEN
    HALF-OPEN

    Especialmente evitar inconsistencias cuando el servicio volvía a fallar durante HALF-OPEN.

    2. Evitar duplicación de código

    Al aplicar el Circuit Breaker a múltiples endpoints, inicialmente se generó mucho código repetido.

    Fue necesario reorganizar la lógica manteniendo la estructura original del gateway.

    3. Manejo del tiempo de recuperación

    Controlar correctamente el tiempo de espera usando:

    time.time()

    para permitir la transición automática a HALF-OPEN.

    4. Respuestas parciales en /resumen

    Se debió validar cuidadosamente cada servicio para que un fallo individual no afectara toda la respuesta del endpoint.

    5. Pruebas de recuperación

    Durante las pruebas fue necesario:

    -Apagar contenedores
    -Reiniciar servicios
    -Esperar tiempos de recuperación
    -Validar logs

    para comprobar el comportamiento del Circuit Breaker.
