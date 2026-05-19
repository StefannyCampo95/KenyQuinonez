# Introducción

Este laboratorio tiene como objetivo implementar monitoreo básico en un sistema distribuido compuesto por múltiples microservicios.  

Se desarrolló un sistema de pedidos utilizando Flask y Docker Compose, implementando logs, health checks, monitoreo centralizado, simulación de fallos y métricas básicas para analizar el comportamiento del sistema ante errores.

# Arquitectura del Sistema

El sistema está compuesto por 5 microservicios:

Gateway - Punto central de acceso - 5000

Pedidos - Procesamiento de pedidos - 5001

Inventario - Consulta de inventario - 5002 

Pagos - Procesamiento de pagos - 5003 

La arquitectura funciona de la siguiente manera:

Cliente → Gateway → Microservicios

# Tecnologías Utilizadas

Python
Flask
Docker
Docker Compose

# Estructura del Proyecto

─ pedidos ─ inventario ─ pagos ─ monitor ─ gateway ─ docker-compose.yml



1. **CARGAMOS TODOS LOS SERVICIOS EN DOCKER COMPOSE**
    docker-compose up --build

2. **PROBAMOS QUE EL SISTEMA ESTÉ FUNCIONANDO**
    http://127.0.0.1:5000/sistema

    ![sistema](EVIDENCIAS/sistema.png)

3. **PROBAMOS - HEALTH CHECKS**

    GATEWAY
    http://localhost:5000/health

    ![gateway](EVIDENCIAS/gateway.png)

    PEDIDOS
    http://localhost:5001/health
    
    ![pedidos](EVIDENCIAS/pedidos.png)

    INVENTARIO
    http://localhost:5002/health

    ![inventario](EVIDENCIAS/inventario.png)

    PAGOS
    http://localhost:5003/health

    ![pagos](EVIDENCIAS/pagos.png)

4. **PROBAMOS - MONITOREO**

    http://localhost:5000/monitoreo

    ![monitoreo](EVIDENCIAS/monitoreo.png)

5. **PROBAMOS - MÉTRICAS**

    http://localhost:5000/metricas

    ![metricas](EVIDENCIAS/metricas.png)

6. **LOGS DE LOS SERVICIOS**
    Abrimos una consola Power Shell y ejecutamos:
    docker compose logs

    ![logs](EVIDENCIAS/logs_dockercompose.png)

    ![logs](EVIDENCIAS/logs_compose.png)

    ![logs](EVIDENCIAS/logs_sistema.png)

    ![logs](EVIDENCIAS/logs_pagos.png)

7. **SIMULACIÓN DE FALLOS**
    Apagamos el servicio de pagos con:
    docker stop laboratorio_monitoreo-pagos-1

    ![fallos](EVIDENCIAS/fallo_pagos.png)

    Ejecutamos:
    docker logs -f laboratorio_monitoreo-gateway-1

    ![fallos](EVIDENCIAS/circuit_breaker_pagos.png)



