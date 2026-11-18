# Sistema de Gestión Académica

Plataforma modular para administrar estudiantes, cursos y matrículas universitarias. Diseñada bajo una **arquitectura de microservicios** independiente, donde cada servicio gestiona su propia base de datos en **PostgreSQL 16**, expone endpoints REST en **Flask (Python)**, integra mecanismos de tolerancia a fallos (**Timeout**, **Circuit Breaker** y **Health Checks**), centraliza el tráfico a través de un **API Gateway (Nginx)** y se orquesta mediante **Docker Compose**.

## Tabla de contenido

- [¿Qué problema resuelve?](#qué-problema-resuelve)
- [Integrantes del equipo](#integrantes-del-equipo)
- [Arquitectura completa del sistema](#arquitectura-completa-del-sistema)
- [Inventario de microservicios](#inventario-de-microservicios)
- [Estructura del proyecto](#estructura-del-proyecto)
- [API Gateway e Interfaz Web (Home)](#api-gateway-e-interfaz-web-home)
- [Rutas, endpoints y manejo de errores HTTP](#rutas-endpoints-y-manejo-de-errores-http)
- [Bases de datos independientes y persistencia](#bases-de-datos-independientes-y-persistencia)
- [Comunicación entre microservicios](#comunicación-entre-microservicios)
- [Tolerancia a fallos: Timeout y Circuit Breaker](#tolerancia-a-fallos-timeout-y-circuit-breaker)
- [Despliegue con Docker Compose y variables de entorno](#despliegue-con-docker-compose-y-variables-de-entorno)
- [Matriz de verificación integral y pruebas de recuperación](#matriz-de-verificación-integral-y-pruebas-de-recuperación)

## ¿Qué problema resuelve?

En los sistemas monolíticos tradicionales, cualquier fallo o saturación en un módulo específico puede dejar fuera de servicio toda la plataforma académica. `gestor_academico2` desacopla las responsabilidades en microservicios autónomos:

- **Aislamiento de fallas:** Si el servicio de cursos presenta latencia elevada o se detiene, los módulos de estudiantes y consultas de matrículas continúan operando sin interrupciones.
- **Bases de datos independientes (*Database per Service*):** Ningún microservicio accede directamente a las tablas de otro; cada uno administra su propia instancia de PostgreSQL.
- **Resiliencia en la comunicación:** El servicio de matrículas valida la existencia de estudiantes y cursos mediante peticiones HTTP protegidas con **Timeout** y **Circuit Breaker**.
- **Punto de entrada único:** Nginx actúa como servidor web para la vista Home y como Reverse Proxy / API Gateway centralizado en el puerto `8080`.

## Integrantes del equipo

| Integrante | Aportes principales en el proyecto |
| :--- | :--- |
| **Daniel Fernández** | Configuración base de `docker-compose.yml`, variables de entorno, microservicios de Estudiantes y Cursos, integración de `pybreaker` (Circuit Breaker) y desarrollo de la vista Home + Nginx. |
| **Olver Edinson Arenas Vásquez** | Implementación de endpoints `/health` en los microservicios y el Gateway, validación de arranque ordenado (`service_healthy`) en `docker-compose.yml`, desarrollo de Matrículas, gestión de ramas/PR en GitHub y documentación técnica. |

## Arquitectura completa del sistema

El usuario interactúa únicamente con el contenedor `home` (Nginx en `http://localhost:8080`), el cual entrega el frontend y enruta las peticiones REST hacia los contenedores internos dentro de la red privada de Docker:

```text
                        ┌───────────────────────────────────────┐
                        │        Usuario / Navegador Web        │
                        └───────────────────┬───────────────────┘
                                            │ HTTP (Puerto 8080)
                                            ▼
                        ┌───────────────────────────────────────┐
                        │       home — Nginx (Puerto 80)        │
                        │    Vista Home + API Gateway / Proxy   │
                        │              (/health)                │
                        └──────┬────────────┬────────────┬──────┘
                               │            │            │
              ┌────────────────┘            │            └────────────────┐
              │ /estudiantes                │ /cursos                     │ /matriculas
              ▼                             ▼                             ▼
┌───────────────────────────┐ ┌───────────────────────────┐ ┌───────────────────────────┐
│   estudiantes_service     │ │      cursos_service       │ │    matriculas_service     │
│     (Flask - :5002)       │ │     (Flask - :5000)       │ │     (Flask - :5003)       │
│         /health           │ │    /health + DELAY        │ │ /health + /circuit-status │
└─────────────┬─────────────┘ └─────────────┬─────────────┘ └──────┬─────────────┬──────┘
              │                             │                      │             │
              │                             │   GET /estudiantes   │             │
              │◄────────────────────────────┼──────────────────────┘             │
              │   (Timeout 3s + CB)         │                                    │
              │                             │   GET /cursos (Timeout 3s + CB)    │
              │                             │◄───────────────────────────────────┘
              ▼                             ▼                                    ▼
┌───────────────────────────┐ ┌───────────────────────────┐ ┌───────────────────────────┐
│      db_estudiantes       │ │         db_cursos         │ │       db_matriculas       │
│  (PostgreSQL 16 - :5432)  │ │  (PostgreSQL 16 - :5432)  │ │  (PostgreSQL 16 - :5432)  │
│  Vol: estudiantes_data    │ │     Vol: cursos_data      │ │   Vol: matriculas_data    │
└───────────────────────────┘ └───────────────────────────┘ └───────────────────────────┘
```
## Inventario de microservicios

| Microservicio / Componente | Responsabilidad | Base de datos | Comunicación con otros servicios | Estado |
| :--- | :--- | :--- | :--- | :--- |
| **`home` (Nginx)** | Servir la interfaz web (HTML, CSS, JS) y actuar como API Gateway centralizado. | No aplica | Enruta peticiones HTTP hacia `estudiantes:5002`, `cursos_service:5000` y `matriculas_service:5003`. | Implementado |
| **`estudiantes_service`** | Administrar el CRUD completo de estudiantes. | `db_estudiantes` (`estudiantes_service`) | Expone API REST interna en puerto `5002` (consumida por Gateway y `matriculas_service`). | Implementado |
| **`cursos_service`** | Administrar el CRUD completo de cursos y simular latencia (`DELAY`). | `db_cursos` (`cursos_db`) | Expone API REST interna en puerto `5000` (consumida por Gateway y `matriculas_service`). | Implementado |
| **`matriculas_service`** | Gestionar matrículas validando integridad referencial distribuida, Timeout y Circuit Breaker. | `db_matriculas` (`matriculas_db`) | Consume `GET /estudiantes/{id}` y `GET /cursos/{id}` vía HTTP con `requests` y `pybreaker`. | Implementado |

## Estructura del proyecto

    gestor_academico2/
    │
    ├── cursos_service/             # Microservicio de Cursos
    │   ├── app.py                  # Inicialización de Flask, CORS, BD y Blueprint
    │   ├── db.py                   # Conexión con reintentos a PostgreSQL y creación de tabla curso
    │   ├── routes.py               # Endpoints CRUD, simulación de DELAY y /health
    │   ├── Dockerfile              # Imagen basada en python:3.10-slim
    │   └── requirements.txt        # Flask, flask-cors, psycopg2-binary, requests
    │
    ├── estudiantes_service/        # Microservicio de Estudiantes
    │   ├── app.py                  # Inicialización de Flask, CORS, BD y Blueprint
    │   ├── db.py                   # Conexión con reintentos a PostgreSQL y creación de tabla estudiantes
    │   ├── routes.py               # Endpoints CRUD y /health
    │   ├── Dockerfile              # Imagen basada en python:3.10-slim
    │   └── requirements.txt        # Flask, flask-cors, psycopg2-binary, requests
    │
    ├── matriculas_service/         # Microservicio de Matrículas (Orquestador)
    │   ├── app.py                  # Inicialización de Flask, CORS, BD y Blueprint
    │   ├── db.py                   # Conexión con reintentos a PostgreSQL y creación de tabla matricula
    │   ├── routes.py               # Endpoints CRUD, Timeout, Circuit Breaker, /circuit-status y /health
    │   ├── Dockerfile              # Imagen basada en python:3.10-slim
    │   └── requirements.txt        # Flask, flask-cors, psycopg2-binary, requests, pybreaker
    │
    ├── home/                       # Frontend + API Gateway Nginx
    │   ├── index.html              # Tablero principal de gestión académica
    │   ├── styles.css              # Estilos visuales del panel y tarjetas
    │   ├── app.js                  # Consumo dinámico de APIs mediante fetch()
    │   ├── nginx.conf              # Configuración de proxy inverso y /health del Gateway
    │   └── Dockerfile              # Imagen basada en nginx:alpine
    │
    ├── .env                        # Variables de entorno locales (ignorado en Git)
    ├── .env.example                # Plantilla de variables de entorno del proyecto
    ├── .gitignore                  # Exclusión de .env y archivos temporales de Python
    ├── docker-compose.yml          # Orquestación de 7 contenedores, redes, volúmenes y healthchecks
    └── README.md                   # Documentación técnica completa

## API Gateway e Interfaz Web (Home)

El contenedor `home` ejecuta **Nginx (`nginx:alpine`)** escuchando en el puerto interno `80`, publicado en el host como **`http://localhost:8080`**.

### Enrutamiento configurado en `home/nginx.conf`

| Ruta pública en el Gateway | Método HTTP | Destino interno en Docker | Función |
| :--- | :--- | :--- | :--- |
| `/` | `GET` | `/usr/share/nginx/html/index.html` | Entrega la interfaz web principal del sistema. |
| `/health` | `GET` | Respuesta directa Nginx (`200`) | Verifica disponibilidad del API Gateway. |
| `/estudiantes` y `/estudiantes/{id}` | `GET, POST, PUT, DELETE` | `http://estudiantes:5002` | Reenvía operaciones de estudiantes. |
| `/cursos` y `/cursos/{id}` | `GET, POST, PUT, DELETE` | `http://cursos_service:5000` | Reenvía operaciones de cursos. |
| `/matriculas` y `/matriculas/{id}` | `GET, POST, PUT, DELETE` | `http://matriculas_service:5003` | Reenvía operaciones de matrículas. |

### Funcionalidades de la Vista Home (`home/index.html` + `home/app.js`)
- Consume las rutas del Gateway (`/estudiantes`, `/cursos`, `/matriculas`) usando `fetch()`.
- Actualiza en tiempo real las tarjetas de totales del tablero de control.
- Permite registrar nuevos estudiantes (`POST`), listar registros activos (`GET`) y eliminar estudiantes (`DELETE`) directamente desde el navegador.

## Rutas, endpoints y manejo de errores HTTP

### 1. Servicio de Estudiantes (`estudiantes_service` — Interno `:5002` / Host `:5001`)
**Campos de la tabla `estudiantes`:** `id`, `cedula`, `nombre`, `apellido`, `correo`, `programa`.

| Método | Endpoint | Descripción | Códigos HTTP |
| :--- | :--- | :--- | :--- |
| `GET` | `/estudiantes` | Lista todos los estudiantes registrados. | `200` |
| `GET` | `/estudiantes/{id}` | Consulta un estudiante por su ID. | `200`, `404` |
| `POST` | `/estudiantes` | Crea un nuevo estudiante en PostgreSQL. | `201` |
| `PUT` | `/estudiantes/{id}` | Actualiza los datos de un estudiante existente. | `200`, `404` |
| `DELETE` | `/estudiantes/{id}` | Elimina un estudiante por su ID. | `200`, `404` |
| `GET` | `/health` | Verifica estado del servicio y conexión real a BD (`SELECT 1`). | `200`, `503` |

### 2. Servicio de Cursos (`cursos_service` — Interno `:5000` / Host `:5002`)
**Campos de la tabla `curso`:** `id`, `codigo`, `nombre`, `creditos`, `semestre`, `docente_id`.

| Método | Endpoint | Descripción | Códigos HTTP |
| :--- | :--- | :--- | :--- |
| `GET` | `/cursos` | Lista todos los cursos disponibles (aplica `DELAY`). | `200` |
| `GET` | `/cursos/{id}` | Consulta un curso específico por ID (aplica `DELAY`). | `200`, `404` |
| `POST` | `/cursos` | Registra un nuevo curso. | `201` |
| `PUT` | `/cursos/{id}` | Actualiza un curso existente. | `200`, `404` |
| `DELETE` | `/cursos/{id}` | Elimina un curso por ID (aplica `DELAY`). | `200`, `404` |
| `GET` | `/health` | Verifica estado del servicio y conexión real a BD (`SELECT 1`). | `200`, `503` |

### 3. Servicio de Matrículas (`matriculas_service` — Interno `:5003` / Host `:5003`)
**Campos de la tabla `matricula`:** `id`, `estudiante_id`, `curso_id`, `fecha_matricula`, `estado`.

| Método | Endpoint | Descripción | Códigos HTTP |
| :--- | :--- | :--- | :--- |
| `GET` | `/matriculas` | Lista todas las matrículas registradas. | `200` |
| `GET` | `/matriculas/{id}` | Consulta una matrícula específica por ID. | `200`, `404` |
| `POST` | `/matriculas` | Valida existencia de estudiante y curso vía HTTP (con Timeout y Circuit Breaker) y registra la matrícula. | `201`, `400`, `404`, `502`, `503`, `504` |
| `PUT` | `/matriculas/{id}` | Actualiza una matrícula existente. | `200`, `400`, `404` |
| `DELETE` | `/matriculas/{id}` | Elimina una matrícula por ID. | `200`, `404` |
| `GET` | `/circuit-status` | Muestra el estado actual (`closed`, `open`, `half-open`) de los Circuit Breakers. | `200` |
| `GET` | `/health` | Verifica estado del servicio y conexión real a BD (`SELECT 1`). | `200`, `503` |

### Estándar de códigos de error HTTP aplicados

| Código HTTP | Significado en la aplicación | Cuándo se devuelve |
| :--- | :--- | :--- |
| **`200 OK`** | Operación exitosa | Consultas `GET`, actualizaciones `PUT`, eliminaciones `DELETE`, `/health` activo y `/circuit-status`. |
| **`201 Created`** | Recurso creado | Registro exitoso mediante `POST` en cualquiera de los 3 microservicios. |
| **`400 Bad Request`** | Petición inválida | Cuando faltan campos obligatorios en `POST` o `PUT` de matrículas. |
| **`404 Not Found`** | Recurso no encontrado | Cuando el `id` consultado/editado/eliminado no existe, o cuando el estudiante/curso a matricular no existe. |
| **`502 Bad Gateway`** | Error en servicio dependiente | Cuando un microservicio externo responde con error interno (`>= 500`). |
| **`503 Service Unavailable`** | Servicio no disponible / Circuito abierto | Cuando falla la conexión a PostgreSQL (`/health`), un servicio está detenido (`ConnectionError`) o el Circuit Breaker está en estado `OPEN`. |
| **`504 Gateway Timeout`** | Tiempo de espera agotado | Cuando `estudiantes` o `cursos_service` supera el límite de `HTTP_TIMEOUT=3` segundos sin responder. |

## Bases de datos independientes y persistencia

Cada microservicio cuenta con su propia instancia aislada de **PostgreSQL 16** y su propio volumen persistente en Docker:

| Microservicio | Contenedor BD | Base de datos | Tabla principal | Volumen Docker | Operaciones implementadas |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `estudiantes_service` | `db_estudiantes` | `estudiantes_service` | `estudiantes` | `estudiantes_data` | `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `SELECT 1` |
| `cursos_service` | `db_cursos` | `cursos_db` | `curso` | `cursos_data` | `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `SELECT 1` |
| `matriculas_service` | `db_matriculas` | `matriculas_db` | `matricula` | `matriculas_data` | `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `SELECT 1` |

### Comprobación de persistencia
Los volúmenes se montan en `/var/lib/postgresql/data`. Al detener y recrear los contenedores sin borrar volúmenes (`docker compose down` seguido de `docker compose up -d`), los registros almacenados en las tres bases de datos permanecen intactos.

## Comunicación entre microservicios

Al no existir llaves foráneas entre bases de datos separadas, `matriculas_service` garantiza la integridad referencial comunicándose por HTTP dentro de la red interna de Docker mediante el DNS de contenedores:

| Servicio solicitante | Servicio destino | Endpoint | Método HTTP | Información intercambiada |
| :--- | :--- | :--- | :--- | :--- |
| `matriculas_service` | `estudiantes` (`http://estudiantes:5002`) | `/estudiantes/{id}` | `GET` | Verifica que el `estudiante_id` exista antes de crear la matrícula (`200` o `404`). |
| `matriculas_service` | `cursos_service` (`http://cursos_service:5000`) | `/cursos/{id}` | `GET` | Verifica que el `curso_id` exista antes de crear la matrícula (`200` o `404`). |

## Tolerancia a fallos: Timeout y Circuit Breaker

### 1. Configuración de Timeout
En `matriculas_service/routes.py`, cada llamada HTTP saliente con `requests.get(...)` incorpora el parámetro `timeout=HTTP_TIMEOUT` (configurado en **`3` segundos**).
- Para simular respuestas lentas, `cursos_service/routes.py` incluye un retardo controlado mediante `time.sleep(DELAY)` (valor por defecto `5` segundos).
- Cuando `cursos_service` tarda más de 3 segundos, `requests` lanza `requests.exceptions.Timeout` y `matriculas_service` responde controladamente con **HTTP `504 Gateway Timeout`**.

### 2. Implementación de Circuit Breaker (`pybreaker`)
En `matriculas_service/routes.py` se instancian dos Circuit Breakers independientes (`breaker_estudiantes` y `breaker_cursos`):

| Parámetro | Valor implementado | Descripción |
| :--- | :--- | :--- |
| **Servicio que realiza la solicitud** | `matriculas_service` | Microservicio orquestador que protege sus dependencias HTTP. |
| **Servicios protegidos** | `estudiantes` y `cursos_service` | Circuitos independientes (`EstudiantesBreaker` y `CursosBreaker`). |
| **Umbral de fallas (`fail_max`)** | `3` fallos consecutivos | Cantidad de errores técnicos (`Timeout`, `ConnectionError`, `HTTPError >= 500`) necesarios para abrir el circuito. |
| **Tiempo de recuperación (`reset_timeout`)** | `30` segundos | Tiempo que el circuito permanece en estado `OPEN` antes de permitir una prueba en `HALF_OPEN`. |
| **Timeout configurado (`HTTP_TIMEOUT`)** | `3` segundos | Tiempo máximo de espera por petición antes de contabilizar un fallo por latencia. |
| **Endpoint de diagnóstico** | `GET /circuit-status` | Permite consultar en vivo el estado de ambos circuitos. |

### Ciclo de estados demostrado
1. **`CLOSED` (Cerrado):** Estado normal. Las solicitudes `POST /matriculas` consultan a `estudiantes` y `cursos_service`. Si ocurre un error técnico, incrementa el contador de fallos.
2. **`OPEN` (Abierto):** Al alcanzarse los `3` fallos consecutivos, el circuito se abre. Durante los siguientes `30` segundos, `matriculas_service` rechaza inmediatamente las solicitudes protegidas lanzando `pybreaker.CircuitBreakerError` y devolviendo **HTTP `503`** sin saturar la red ni esperar timeouts.
3. **`HALF_OPEN` (Semi-abierto):** Transcurridos los `30` segundos, la siguiente solicitud pasa como prueba hacia el servicio dependiente. Si responde correctamente (`200`), el circuito regresa a **`CLOSED`**; si vuelve a fallar, retorna a **`OPEN`**.

## Despliegue con Docker Compose y variables de entorno

### 1. Configuración de variables de entorno
Crear el archivo `.env` en la raíz a partir de `.env.example`:

    # Estudiantes
    ESTUDIANTES_DB_HOST=db_estudiantes
    ESTUDIANTES_DB_PORT=5432
    ESTUDIANTES_DB_NAME=estudiantes_service
    ESTUDIANTES_DB_USER=estudiante
    ESTUDIANTES_DB_PASSWORD=123456
    ESTUDIANTES_DELAY=0

    # Cursos (DELAY=0 para operación normal, DELAY=5 para simular latencia/timeout)
    CURSOS_DB_PORT=5432
    CURSOS_DB_NAME=cursos_db
    CURSOS_DB_USER=curso
    CURSOS_DB_PASSWORD=123456
    DELAY=0

    # Matrículas
    MATRICULAS_DB_PORT=5432
    MATRICULAS_DB_NAME=matriculas_db
    MATRICULAS_DB_USER=matricula
    MATRICULAS_DB_PASSWORD=123456

    # URLs internas de comunicación
    ESTUDIANTES_URL=http://estudiantes:5002
    CURSOS_URL=http://cursos_service:5000

    # Resiliencia (Timeout y Circuit Breaker)
    HTTP_TIMEOUT=3
    CB_FAIL_MAX=3
    CB_RESET_TIMEOUT=30

### 2. Comandos de ejecución y verificación

    # Construir imágenes y levantar los 7 contenedores en segundo plano
    docker compose up -d --build

    # Verificar estado y salud (healthy) de todos los contenedores
    docker compose ps

### 3. ¿Por qué no es necesario publicar todos los puertos?
En Docker Compose todos los contenedores comparten una red interna con resolución DNS automática por nombre de servicio. En producción, basta con exponer únicamente el puerto **`8080:80`** del API Gateway (`home`), manteniendo aisladas las bases de datos y los microservicios internos para reducir la superficie de exposición.

## Matriz de verificación integral y pruebas de recuperación

| Prueba | Resultado esperado | Resultado obtenido | Evidencia / Verificación |
| :--- | :--- | :--- | :--- |
| **Arquitectura completa** | Todos los servicios requeridos implementados y conectados. | Cumplido | 3 microservicios + 3 BDs PostgreSQL + API Gateway Nginx en funcionamiento. |
| **Docker Compose** | Todos los contenedores ejecutándose y saludables (`healthy`). | Cumplido | `docker compose ps` muestra los 7 servicios en estado `Up (healthy)`. |
| **CRUD Estudiantes** | Operaciones `POST`, `GET`, `PUT`, `DELETE` y manejo de `404`. | Cumplido | Verificado vía Vista Home y cliente HTTP sobre `/estudiantes`. |
| **CRUD Cursos** | Operaciones `POST`, `GET`, `PUT`, `DELETE` y manejo de `404`. | Cumplido | Verificado sobre `/cursos` con persistencia en `db_cursos`. |
| **CRUD Matrículas** | Operaciones `POST`, `GET`, `PUT`, `DELETE` y manejo de `400`/`404`. | Cumplido | Verificado sobre `/matriculas` con validación previa de IDs. |
| **Bases de datos** | Persistencia independiente tras detener y recrear contenedores. | Cumplido | Registros conservados tras `docker compose down` y `docker compose up -d`. |
| **Comunicación HTTP** | `matriculas_service` consulta a `estudiantes` y `cursos_service`. | Cumplido | Validación exitosa en `POST /matriculas` y rechazo `404` ante IDs inexistentes. |
| **Timeout** | Error controlado `504` cuando `cursos_service` supera `3s`. | Cumplido | Con `DELAY=5`, `POST /matriculas` responde `504 Gateway Timeout` a los `3s`. |
| **Circuit Breaker `CLOSED`** | Comunicación permitida en operación normal. | Cumplido | `GET /circuit-status` retorna `"cursos_circuit": "closed"`. |
| **Circuit Breaker `OPEN`** | Rechazo inmediato (`503`) tras 3 fallos consecutivos (`docker compose stop cursos_service` o latencia). | Cumplido | Tras 3 fallos, `GET /circuit-status` cambia a `"open"` y rechaza al instante con `503`. |
| **Recuperación (`HALF_OPEN` → `CLOSED`)** | Restablecimiento automático tras `30s` y reactivación del servicio (`docker compose start cursos_service`). | Cumplido | Pasados `30s`, una petición exitosa cierra el circuito a `"closed"`. |
| **API Gateway** | Enrutamiento centralizado desde `http://localhost:8080`. | Cumplido | Peticiones a `/estudiantes`, `/cursos`, `/matriculas` y `/health` resueltas por Nginx. |
| **Vista Home** | Interfaz web conectada al Gateway consumiendo datos reales. | Cumplido | Tablero en `http://localhost:8080` lista contadores y permite crear/eliminar estudiantes. |