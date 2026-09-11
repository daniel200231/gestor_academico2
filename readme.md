# Sistema Académico Distribuido

Sistema de gestión académica basado en una **arquitectura de microservicios**, diseñado para centralizar y automatizar procesos relacionados con docentes, cursos, estudiantes, matrículas y calificaciones.

## Tabla de contenido

- [Problema que resuelve](#problema-que-resuelve)
- [Objetivo del proyecto](#objetivo-del-proyecto)
- [Integrantes y roles](#integrantes-y-roles)
- [Arquitectura del sistema](#arquitectura-del-sistema)
- [Servicios del sistema](#servicios-del-sistema)
- [Comunicación entre servicios](#comunicación-entre-servicios)
- [Tipo de arquitectura](#tipo-de-arquitectura)
- [Modelo de datos y dominio](#modelo-de-datos-y-dominio)
- [Usuarios del sistema](#usuarios-del-sistema)
- [Arquitectura interna de los microservicios](#arquitectura-interna-de-los-microservicios)
- [Manejo de fallas](#manejo-de-fallas)
- [Docker](#docker)
- [Docker-compose](#docker-compose)
- [Estado del proyecto](#estado-del-proyecto)

---

## Problema que resuelve

El sistema resuelve la necesidad de **centralizar y automatizar la gestión académica** de una institución educativa. Sin una plataforma integrada, estos procesos tendrían que manejarse de forma manual, dispersa o mediante hojas de cálculo y sistemas aislados.

En concreto, permite:

- Integrar los procesos de **docentes, cursos, estudiantes, matrículas y notas** bajo una arquitectura común accesible mediante API.
- Mejorar la **escalabilidad y mantenibilidad** del software, ya que cada dominio puede crecer, desplegarse y mantenerse de forma independiente.
- Reducir errores, inconsistencias de datos y procesos manuales poco escalables.

### ¿Quién lo usará?

- **Personal administrativo/académico:** registrar docentes, crear cursos y gestionar matrículas.
- **Docentes:** consultar y gestionar información de los cursos que dictan y, potencialmente, registrar notas.
- **Estudiantes:** consultar sus matrículas, cursos inscritos y calificaciones.

### ¿Qué pasaría si no existiera?

La institución tendría que depender de procesos manuales o herramientas no integradas, lo que aumentaría el riesgo de errores e inconsistencias, además de generar procesos más lentos y difíciles de escalar.

---

## Objetivo del proyecto

El propósito principal de este proyecto es **diseñar e implementar una plataforma integral para la administración de procesos académicos universitarios**, facilitando el control y seguimiento de docentes, cursos, estudiantes, matrículas y calificaciones.

Para lograrlo, el sistema adopta un enfoque modular basado en microservicios:

- **Autonomía y escalabilidad:** desacoplar cada área funcional para que pueda evolucionar y mantenerse de forma independiente.
- **Punto de acceso unificado:** centralizar las peticiones de los clientes mediante un **API Gateway**.
- **Aislamiento de datos:** respaldar cada servicio con su propia base de datos **PostgreSQL**, evitando dependencias directas entre módulos.

---

## Integrantes y roles

| Integrante                       | Rol                         |
| -------------------------------- | --------------------------- |
| **Cristian Girón**               | Líder de Proyecto           |
| **Dayan Fajardo**                | Líder Técnico / DevOps      |
| **Olver Edinson Arenas Vásquez** | Documentación Técnica       |
| **Daniel Fernández**             | Presentación y Comunicación |

---

## Arquitectura del sistema

```text
┌───────────────────────────┐
│          Usuario          │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│          Frontend         │
│     Home / Interfaz UI    │
└─────────────┬─────────────┘
              │ HTTP
              ▼
┌───────────────────────────┐
│        API Gateway        │
└─────────────┬─────────────┘
              │
       ┌──────┼──────┬──────────┬─────────┐
       ▼      ▼      ▼          ▼         ▼
  Docentes  Cursos  Estudiantes Matrículas Notas
  Service   Service   Service    Service   Service
      │        │        │          │         │
      ▼        ▼        ▼          ▼         ▼
 PostgreSQL PostgreSQL PostgreSQL PostgreSQL PostgreSQL
```

Cada microservicio posee su propia lógica de negocio, base de datos y contenedor Docker. El **API Gateway** funciona como punto de entrada único para los clientes.

---

## Servicios del sistema

Los principales servicios del sistema académico son:

1. **Docentes:** gestiona la información de los profesores, como cédula, nombre, correo, departamento y género.
2. **Cursos:** administra los cursos ofrecidos, incluyendo código, nombre, créditos y semestre.
3. **Estudiantes:** gestiona los datos de los estudiantes, como cédula, nombre, correo y programa académico.
4. **Matrículas:** administra la relación entre estudiantes y cursos.
5. **Notas:** almacena las calificaciones asociadas a cada matrícula.

### Independencia de los microservicios

Cada microservicio puede desarrollarse y mantenerse de manera independiente porque cuenta con:

- Su propia **base de datos**.
- Su propia **lógica de negocio**.
- Su propio **contenedor Docker**.
- Su propio **Dockerfile** para el despliegue.

También son independientes los procesos de:

- **Despliegue**.
- **Modelado de base de datos**.
- **Pruebas**.

---

## Comunicación entre servicios

La comunicación entre los microservicios funciona de manera **síncrona** mediante peticiones **HTTP/REST**, utilizando **JSON** como formato de intercambio de datos.

El **API Gateway** recibe las peticiones del cliente y las enruta al servicio correspondiente según el recurso solicitado:

```text
/docentes
/cursos
/estudiantes
/matriculas
/notas
```

Algunos servicios también necesitan comunicarse directamente entre sí para validar información:

1. **Matrículas → Estudiantes y Cursos:** antes de crear una matrícula, se valida que existan el `estudiante_id` y el `curso_id`.
2. **Notas → Matrículas:** antes de registrar una nota, se valida que exista el `matricula_id`.

### Formato de datos

Los servicios exponen y consumen información en formato **JSON**, lo que facilita la interoperabilidad entre ellos aunque cada microservicio tenga una base de datos independiente.

### ¿Qué pasa si un servicio no responde?

Si, por ejemplo, el servicio de Matrículas necesita validar un estudiante y el servicio de Estudiantes no responde, la operación de matrícula **no debería completarse**, con el fin de evitar inconsistencias.

Para manejar este escenario se propone:

- Definir **timeouts** en las peticiones entre servicios.
- Retornar códigos de error claros, como `503 Service Unavailable`, cuando falle un servicio dependiente.

---

## Tipo de arquitectura

Se eligió una **arquitectura de microservicios** porque permite dividir el sistema en servicios independientes, facilitando el mantenimiento, el despliegue y el crecimiento según la demanda.

Cada módulo puede escalar o actualizarse sin afectar directamente a los demás, lo que ofrece mayor flexibilidad frente a una arquitectura monolítica tradicional.

---

## Modelo de datos y dominio

Cada microservicio administra su propio dominio y su propia tabla principal.

### 1. Servicio de Docentes (`docentes-service`)

**Tabla:** `docente`

| Campo          | Tipo de dato   | Restricciones / Reglas               |
| -------------- | -------------- | ------------------------------------ |
| `id`           | `INTEGER`      | Primary Key, autogenerado (`SERIAL`) |
| `cedula`       | `VARCHAR(20)`  | `NOT NULL`, `UNIQUE`                 |
| `nombre`       | `VARCHAR(100)` | `NOT NULL`                           |
| `correo`       | `VARCHAR(100)` | `NOT NULL`, `UNIQUE`                 |
| `departamento` | `VARCHAR(100)` | `NOT NULL`                           |
| `genero`       | `VARCHAR(20)`  | Opcional                             |

### 2. Servicio de Cursos (`cursos-service`)

**Tabla:** `curso`

| Campo        | Tipo de dato   | Restricciones / Reglas               |
| ------------ | -------------- | ------------------------------------ |
| `id`         | `INTEGER`      | Primary Key, autogenerado (`SERIAL`) |
| `codigo`     | `VARCHAR(20)`  | `NOT NULL`, `UNIQUE`                 |
| `nombre`     | `VARCHAR(100)` | `NOT NULL`                           |
| `creditos`   | `INTEGER`      | `NOT NULL`                           |
| `semestre`   | `INTEGER`      | `NOT NULL`                           |
| `docente_id` | `INTEGER`      | `NOT NULL` (clave foránea lógica)    |

### 3. Servicio de Estudiantes (`estudiantes-service`)

**Tabla:** `estudiante`

| Campo      | Tipo de dato   | Restricciones / Reglas               |
| ---------- | -------------- | ------------------------------------ |
| `id`       | `INTEGER`      | Primary Key, autogenerado (`SERIAL`) |
| `cedula`   | `VARCHAR(20)`  | `NOT NULL`, `UNIQUE`                 |
| `nombre`   | `VARCHAR(100)` | `NOT NULL`                           |
| `correo`   | `VARCHAR(100)` | `NOT NULL`, `UNIQUE`                 |
| `programa` | `VARCHAR(100)` | `NOT NULL`                           |

### 4. Servicio de Matrículas (`matriculas-service`)

**Tabla:** `matricula`

| Campo           | Tipo de dato  | Restricciones / Reglas               |
| --------------- | ------------- | ------------------------------------ |
| `id`            | `INTEGER`     | Primary Key, autogenerado (`SERIAL`) |
| `estudiante_id` | `INTEGER`     | `NOT NULL` (clave foránea lógica)    |
| `curso_id`      | `INTEGER`     | `NOT NULL` (clave foránea lógica)    |
| `anio`          | `INTEGER`     | `NOT NULL` (año lectivo)             |
| `periodo`       | `VARCHAR(10)` | `NOT NULL` (ej.: `1`, `2`, `2026-1`) |

### 5. Servicio de Notas (`notas-service`)

**Tabla:** `nota`

| Campo          | Tipo de dato   | Restricciones / Reglas               |
| -------------- | -------------- | ------------------------------------ |
| `id`           | `INTEGER`      | Primary Key, autogenerado (`SERIAL`) |
| `matricula_id` | `INTEGER`      | `NOT NULL` (clave foránea lógica)    |
| `calificacion` | `NUMERIC(3,2)` | `NOT NULL` (ej.: `4.50`)             |
| `observacion`  | `VARCHAR(200)` | Opcional                             |

### Relaciones del sistema

- **Docente → Curso:** un curso referencia al docente responsable mediante `docente_id`.
- **Estudiante → Matrícula:** una matrícula referencia al estudiante mediante `estudiante_id`.
- **Curso → Matrícula:** una matrícula referencia al curso mediante `curso_id`.
- **Matrícula → Nota:** una nota referencia a la matrícula mediante `matricula_id`.

### Datos críticos

1. **Cédula** de docentes y estudiantes: identifica de forma única a la persona.
2. **`docente_id`:** permite identificar al responsable de un curso.
3. **`estudiante_id` y `curso_id`:** conectan al estudiante con el curso matriculado.
4. **`matricula_id`:** vincula una calificación con una matrícula.
5. **Calificación:** representa el resultado académico del estudiante.

### Impacto de la pérdida de datos

- Si se pierden **docentes**, algunos cursos podrían quedar asociados a un `docente_id` inexistente.
- Si se pierden **estudiantes**, algunas matrículas quedarían con referencias huérfanas.
- Si se pierden **cursos**, se perdería la relación entre determinadas matrículas y sus asignaturas.
- Si se pierden **notas**, se afectaría directamente el historial académico.

---

## Usuarios del sistema

| Usuario                      | Descripción                                          | Acciones principales                                    |
| ---------------------------- | ---------------------------------------------------- | ------------------------------------------------------- |
| **Administrativo/Académico** | Personal encargado de la gestión general del sistema | Registrar docentes, crear cursos y gestionar matrículas |
| **Docente**                  | Profesor responsable de uno o más cursos             | Consultar o gestionar sus cursos y registrar notas      |
| **Estudiante**               | Usuario matriculado en uno o más cursos              | Consultar matrículas, cursos inscritos y calificaciones |

Aunque todos ingresan a través del mismo **API Gateway**, el nivel de acceso depende del rol. Un estudiante debería poder consultar únicamente su propia información, mientras que el personal administrativo y los docentes tendrían permisos de creación o modificación según sus responsabilidades.

---

## Arquitectura interna de los microservicios

La estructura base propuesta para cada microservicio es:

```text
microservicio/
│
├── app.py
│
├── src/
│   ├── routes.py
│   └── services.py
│
├── db.py
│
├── requirements.txt
│
└── Dockerfile
```

### Responsabilidad de los componentes

- **`app.py`:** punto de entrada de la aplicación.
- **`src/routes.py`:** definición de endpoints y rutas HTTP.
- **`src/services.py`:** lógica de negocio del microservicio.
- **`db.py`:** configuración y manejo de la conexión con la base de datos.
- **`requirements.txt`:** dependencias de Python necesarias para ejecutar el servicio.
- **`Dockerfile`:** instrucciones para construir la imagen Docker del microservicio.

---

## Manejo de fallas

### Fallas en un servicio

Si se presenta una falla en un servicio, por ejemplo **Notas**, las demás funcionalidades independientes pueden continuar operando. Sin embargo, cualquier operación que dependa directamente de dicho servicio no podrá completarse correctamente.

Como medidas de manejo se propone:

- Implementar un endpoint `/health` en cada servicio para verificar su disponibilidad.
- Implementar **reintentos exponenciales** cuando un servicio se encuentre temporalmente reiniciándose o no disponible.
- Utilizar **timeouts** para evitar peticiones bloqueadas indefinidamente.
- Retornar códigos HTTP adecuados ante fallas controladas.

### Fallas en la base de datos

Una falla o pérdida de información en una base de datos puede generar inconsistencias debido a las referencias lógicas existentes entre los distintos servicios.

**Medidas propuestas:**

- Implementar **backups automáticos y periódicos**.
- Utilizar **réplicas de lectura** en los servicios con mayor volumen de consultas.
- Monitorear recursos como conexiones activas, espacio en disco y disponibilidad para detectar problemas antes de una caída total.

---

## Docker

La vista `frontend/index.html` es un archivo estático. Actualmente no tiene un contenedor propio ni un proceso de compilación independiente. Se sirve desde el contenedor `gateway`, que utiliza Nginx como servidor web y también como API Gateway.

## Recorrido de la vista

```text
Navegador
   ↓ http://localhost:8000
Docker
   ↓ puerto 8000 → puerto 80
Contenedor gateway
   ↓
Nginx
   ↓
/usr/share/nginx/html/index.html
   ↓
frontend/index.html
```

## Docker-compose

El proyecto cuenta con un archivo `docker-compose.yml` que permite levantar todos los servicios y sus bases de datos de manera coordinada.

Para ejecutarlo se debe utilizar el comando:

```bash
docker-compose up --build -d
```

## Estado del proyecto

Proyecto académico en desarrollo, orientado a aplicar conceptos de **sistemas distribuidos, microservicios, APIs REST, Docker y PostgreSQL**.
