# Sistema de Gestión Académica 2

Una plataforma modular para administrar estudiantes, cursos y matrículas universitarias. Diseñada bajo una **arquitectura de microservicios** independiente, donde cada servicio gestiona su propia base de datos en **PostgreSQL**, expone endpoints REST en **Flask (Python)** y se orquesta de manera centralizada mediante **Docker Compose**.

---

## Tabla de contenido

- [<a name="toc-problema"></a>¿Qué problema resuelve?](#problema)
- [<a name="toc-objetivo"></a>Objetivo del proyecto](#objetivo)
- [<a name="toc-integrantes"></a>Integrantes del equipo](#integrantes)
- [<a name="toc-arquitectura"></a>Cómo está organizado el sistema](#arquitectura)
- [<a name="toc-estructura"></a>Estructura de las carpetas](#estructura)
- [<a name="toc-puertos"></a>Servicios, puertos y bases de datos](#puertos)
- [<a name="toc-rutas"></a>Rutas y endpoints de cada servicio](#rutas)
- [<a name="toc-frontend"></a>Interfaz web (Frontend)](#frontend)
- [<a name="toc-env"></a>Variables de entorno (.env)](#env)
- [<a name="toc-detalles"></a>Persistencia de datos y prevención de fallas](#detalles)

---

<a name="problema"></a>
## ¿Qué problema resuelve?

En los sistemas monolíticos tradicionales, cualquier fallo en el módulo de matrículas o estudiantes puede tumbar toda la plataforma académica. 

`gestor_academico2` desacopla estas responsabilidades en microservicios autónomos:

- **Aislamiento de fallas:** Si el servicio de estudiantes requiere mantenimiento o se cae, el catálogo de cursos sigue operando sin interrupciones.
- **Bases de datos independientes:** Ningún servicio accede directamente a la tabla de otro; cada uno tiene su propio servidor de PostgreSQL.
- **Comunicación HTTP transparente:** El servicio de matrículas valida la información conectándose directamente a las APIs de Cursos y Estudiantes mediante peticiones web internas.

---

<a name="objetivo"></a>
## Objetivo del proyecto

Desplegar una arquitectura distribuida lista para producción que permita registrar estudiantes, crear la oferta académica de cursos y gestionar las matrículas universitarias, garantizando la persistencia de datos mediante volúmenes de Docker y la configuración segura a través de variables de entorno.

---

<a name="integrantes"></a>
## Integrantes del equipo

| Nombre | Rol y responsabilidades |
| ------ | ----------------------- |
| **Daniel Fernández** | Configuración general de infraestructura (`docker-compose.yml`), variables de entorno (`.env`), interfaz gráfica (`home/`) y microservicios de Cursos y Estudiantes. |
| **Olver Edinson Arenas Vásquez** | Desarrollo e integración del microservicio de Matrículas (`matriculas_service`), consumo inter-servicio de APIs, gestión de ramas en GitHub y documentación técnica. |

---

<a name="arquitectura"></a>
## Cómo está organizado el sistema

Cada servicio se ejecuta dentro de su propio contenedor en una red privada virtual de Docker:

```text
                             ┌───────────────────────────────┐
                             │         Interfaz Web          │
                             │    (home/index.html + JS)     │
                             └───────────────┬───────────────┘
                                             │
                        ┌────────────────────┼────────────────────┐
                        │ Peticiones HTTP    │ Peticiones HTTP    │ Peticiones HTTP
                        ▼ (Puerto 5001)      ▼ (Puerto 5002)      ▼ (Puerto 5003)
┌───────────────────────────┐┌───────────────────────────┐┌───────────────────────────┐
│   Servicio Estudiantes    ││      Servicio Cursos      ││    Servicio Matrículas    │
│  (estudiantes_service)    ││     (cursos_service)      ││   (matriculas_service)    │
└─────────────┬─────────────┘└─────────────┬─────────────┘└─────────────┬─────────────┘
              │                            │                            │
              │                            │     Consumo de API HTTP    │
              │                            ├───────────────────────────►│ (Valida Alumnos
              │                            │                            │  y Cursos)
              ▼                            ▼                            ▼
┌───────────────────────────┐┌───────────────────────────┐┌───────────────────────────┐
│    db_estudiantes (BD)    ││      db_cursos (BD)       ││    db_matriculas (BD)     │
│   (PostgreSQL - Port 5432)││   (PostgreSQL - Port 5432)││   (PostgreSQL - Port 5432)│
└───────────────────────────┘└───────────────────────────┘└───────────────────────────┘

gestor_academico2/
│
├── cursos_service/         # Microservicio para la gestión de catálogo de cursos
│   ├── app.py              # Punto de entrada de la aplicación Flask
│   ├── db.py               # Módulo de conexión a la BD PostgreSQL (cursos_db)
│   ├── routes.py           # Endpoints REST (GET, POST, DELETE)
│   ├── Dockerfile          # Configuración de imagen Docker
│   └── requirements.txt    # Dependencias de Python
│
├── estudiantes_service/    # Microservicio para administración de estudiantes
│   ├── app.py              # Punto de entrada de la aplicación Flask
│   ├── db.py               # Módulo de conexión a la BD PostgreSQL (estudiantes_service)
│   ├── routes.py           # Endpoints REST (GET, POST, PUT, DELETE)
│   ├── Dockerfile          # Configuración de imagen Docker
│   └── requirements.txt    # Dependencias de Python
│
├── matriculas_service/     # Microservicio para el registro e historial de matrículas
│   ├── app.py              # Punto de entrada de la aplicación Flask
│   ├── db.py               # Módulo de conexión a la BD PostgreSQL (matriculas_db)
│   ├── routes.py           # Endpoints REST e integración vía HTTP con otros servicios
│   ├── Dockerfile          # Configuración de imagen Docker
│   └── requirements.txt    # Dependencias de Python
│
├── home/                   # Cliente Frontend web
│   ├── index.html          # Interfaz visual interactiva
│   ├── styles.css          # Hojas de estilo
│   └── app.js              # Lógica de consumo de las APIs REST
│
├── .env                    # Credenciales y parámetros de conexión global
├── .gitignore              # Reglas de exclusión para Git
├── docker-compose.yml      # Orquestador de contenedores, puertos y volúmenes
└── README.md               # Documentación general del proyecto

  Servicios, puertos y bases de datos

| Servicio | Puerto Host (Equipo) | Puerto Contenedor | Nombre de la BD | Usuario BD | Contenedor BD |
| :--- | :---: | :---: | :--- | :--- | :--- |
| **Estudiantes** | `5001` | `5002` | `estudiantes_service` | `estudiante` | `db_estudiantes` |
| **Cursos** | `5002` | `5000` | `cursos_db` | `curso` | `db_cursos` |
| **Matrículas** | `5003` | `5003` | `matriculas_db` | `matricula` | `db_matriculas` |

---

Rutas y endpoints de cada servicio
Todas las respuestas utilizan códigos de estado HTTP estandarizados (200 OK, 201 Created, 400 Bad Request, 404 Not Found) e intercambian información en formato JSON.

1. Servicio de Estudiantes (:5001)
Campos: id, cedula, nombre, apellido, correo, programa.

Endpoints:

GET /estudiantes — Obtiene la lista completa de estudiantes.

GET /estudiantes/<id> — Obtiene los detalles de un estudiante específico.

POST /estudiantes — Registra un nuevo estudiante.

PUT /estudiantes/<id> — Actualiza la información de un estudiante.

DELETE /estudiantes/<id> — Elimina un registro de estudiante.

2. Servicio de Cursos (:5002)
Campos: id, codigo, nombre, creditos, profesor, fecha_creacion.

Endpoints:

GET /cursos — Obtiene la oferta completa de cursos disponibles.

POST /cursos — Crea un nuevo curso en el sistema.

DELETE /cursos/<id> — Remueve un curso según su ID.

3. Servicio de Matrículas (:5003)
Campos: id, estudiante_id, curso_id, anio, periodo.

Endpoints:

GET /matriculas — Consulta todas las matrículas registradas.

POST /matriculas — Valida la existencia del alumno y del curso mediante peticiones HTTP a los servicios respectivos antes de guardar la inscripción.

Interfaz web (Frontend)
El proyecto incluye una aplicación web estática ubicada en la carpeta /home. Permite interactuar con la plataforma de forma intuitiva directamente desde cualquier navegador web sin requerir herramientas como Postman o cURL para efectuar operaciones CRUD.

Variables de entorno (.env)
El archivo .env concentra la configuración centralizada de acceso a la infraestructura:                                                          Base de datos: Servicio de Estudiantes
ESTUDIANTES_DB_HOST=db_estudiantes
ESTUDIANTES_DB_PORT=5432
ESTUDIANTES_DB_NAME=estudiantes_service
ESTUDIANTES_DB_USER=estudiante
ESTUDIANTES_DB_PASSWORD=123456

 Base de datos: Servicio de Cursos
CURSOS_DB_PORT=5432
CURSOS_DB_NAME=cursos_db
CURSOS_DB_USER=curso
CURSOS_DB_PASSWORD=123456

 Base de datos: Servicio de Matrículas
MATRICULAS_DB_PORT=5432
MATRICULAS_DB_NAME=matriculas_db
MATRICULAS_DB_USER=matricula
MATRICULAS_DB_PASSWORD=123456

Persistencia de datos y prevención de fallas
Persistencia garantizada: Se definen tres volúmenes independientes de Docker (estudiantes_data, cursos_data y matriculas_data) asignados a los directorios de almacenamiento de PostgreSQL /var/lib/postgresql/data. Esto asegura que los datos se conserven aunque se detengan o reconstruyan los contenedores.

Políticas de reinicio: Los contenedores de aplicaciones están configurados con restart: always u on-failure para reanimar automáticamente los procesos en caso de un cierre inesperado.

Desacoplamiento de red: La comunicación inter-servicio se resuelve mediante DNS interno de Docker en la red compartida, evitando el acoplamiento rígido de IP estáticas.
