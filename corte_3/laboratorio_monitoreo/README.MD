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

    ![logs](EVIDENCIAS/logs_sistema.png)

    ![logs](EVIDENCIAS/logs_pagos.png)





