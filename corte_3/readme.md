FASE 1 – OBSERVAR (sin modificar código)

-¿Qué hace el sistema actualmente?


-¿Se protege o insiste?


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
