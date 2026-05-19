# Gestor de Turnos para Banco

## Descripción

Este proyecto implementa un prototipo de sistema distribuido para la gestión de turnos en un banco.
El sistema permite registrar usuarios mediante su número de identificación y teléfono, y generar turnos teniendo en cuenta la prioridad de atención (general o preferencial).

La arquitectura está basada en microservicios, donde cada servicio se ejecuta en un contenedor independiente utilizando Docker.

## Servicios implementados

Servicio de usuarios: permite registrar y consultar usuarios.
Servicio de turnos: permite generar y consultar los turnos asignados.

## Tecnologías utilizadas

* Backend: Python (Flask)
* Contenedores: Docker
* Orquestación de servicios: Docker Compose

## Estructura del proyecto
gestor-turnos
    users-service
        app.py
        Dockerfile
        requirements.txt

    turns-service
        app.py
        Dockerfile
        requirements.txt
        
    docker-compose.yml

## Requisitos
* Tener instalado Docker Desktop
* Tener Docker Compose disponible

## Cómo ejecutar el proyecto

1. Abrir una terminal en la carpeta del proyecto.

2. Ejecutar el siguiente comando:

docker-compose up --build

3. Esperar a que Docker construya y levante los servicios.

## Cómo probar los servicios

Servicio de usuarios:

http://localhost:5001/users

Servicio de turnos:

http://localhost:5002/turns

Si el sistema está funcionando correctamente, el navegador mostrará un mensaje indicando que el servicio está activo.
