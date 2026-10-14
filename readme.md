<h1>Sistema de Gestión Académica 2 </h1>

<p>Proyecto escolar para la gestión de procesos académicos de una universidad. El sistema está construido usando una <strong>arquitectura de microservicios</strong> organizada con <strong>Flask (Python)</strong>, bases de datos independientes en <strong>PostgreSQL</strong>, una interfaz web sencilla (<strong>HTML, CSS y JavaScript</strong>) y <strong>Docker Compose</strong> para poner a funcionar todo al mismo tiempo.</p>

<hr>

<h2>Tabla de contenido</h2>
<ul>
  <li><a href="#que-problema-resuelve">¿Qué problema resuelve?</a></li>
  <li><a href="#objetivo-del-proyecto">Objetivo del proyecto</a></li>
  <li><a href="#integrantes-del-equipo">Integrantes del equipo</a></li>
  <li><a href="#como-esta-organizado-el-sistema">Cómo está organizado el sistema</a></li>
  <li><a href="#estructura-de-las-carpetas">Estructura de las carpetas</a></li>
  <li><a href="#servicios-y-puertos">Servicios y puertos</a></li>
  <li><a href="#rutas-y-datos-que-maneja-cada-servicio">Rutas y datos que maneja cada servicio</a></li>
  <li><a href="#pantalla-web-frontend">Pantalla web (Frontend)</a></li>
  <li><a href="#variables-de-entorno-env">Variables de entorno (.env)</a></li>
  <li><a href="#detalles-de-funcionamiento-y-prevencion-de-fallas">Detalles de funcionamiento y prevención de fallas</a></li>
</ul>

<hr>

<h2 id="que-problema-resuelve">¿Qué problema resuelve?</h2>
<p>Normalmente las universidades manejan mucha información y si todo se guarda en un solo programa pesado, cualquier fallo tumbaría todo el sistema o sería muy difícil de cambiar.</p>
<p><code>gestor_academico2</code> soluciona esto dividiendo el trabajo en partes pequeñas y separadas:</p>
<ul>
  <li><strong>Trabajo independiente:</strong> Se pueden registrar alumnos, crear cursos o matricular personas de forma separada sin interferir entre sí.</li>
  <li><strong>Crecer según la necesidad:</strong> Si en época de matrículas entra mucha gente al tiempo, solo se le da más fuerza a esa parte del sistema sin tocar lo demás.</li>
  <li><strong>Si algo falla, lo demás sigue funcionando:</strong> Si por alguna razón se cae el servicio de estudiantes, la parte de cursos puede seguir recibiendo consultas normalmente.</li>
</ul>

<hr>

<h2 id="objetivo-del-proyecto">Objetivo del proyecto</h2>
<p>Crear una plataforma funcional y fácil de usar para administrar los datos de una universidad, aplicando lo aprendido sobre <strong>APIs REST con Flask</strong>, respuestas organizadas en formato <strong>JSON</strong>, bases de datos separadas en <strong>PostgreSQL</strong> y el uso de <strong>Docker Compose</strong> para ejecutar todo con un solo comando.</p>

<hr>

<h2 id="integrantes-del-equipo">Integrantes del equipo</h2>

<table border="1">
  <thead>
    <tr>
      <th>Nombre</th>
      <th>Rol y tareas</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Daniel Fernández</strong></td>
      <td>Estructura general, configuración del archivo <code>.env</code>, pantalla web (<code>home/</code>) y servicios de Cursos y Estudiantes</td>
    </tr>
    <tr>
      <td><strong>Olver Edinson Arenas Vásquez</strong></td>
      <td>Creación e integración del microservicio de Matrículas (<code>matriculas_service</code>), unión de código en GitHub y documentación</td>
    </tr>
  </tbody>
</table>

<hr>

<h2 id="como-esta-organizado-el-sistema">Cómo está organizado el sistema</h2>
<p>Cada parte del sistema corre en su propio contenedor de Docker y se conectan entre sí por una red interna:</p>

<pre>
                        ┌───────────────────────────────┐
                        │         Pantalla Web          │
                        │    (home/index.html + JS)     │
                        └───────────────┬───────────────┘
                                        │ Peticiones HTTP
             ┌──────────────────────────┼──────────────────────────┐
             │ (Puerto 5002)            │ (Puerto 5000)            │ (Puerto 5003)
             ▼                          ▼                          ▼
┌─────────────────────────┐┌─────────────────────────┐┌─────────────────────────┐
│  Servicio Estudiantes   ││     Servicio Cursos     ││   Servicio Matrículas   │
│    (Flask / Python)     ││     (Raíz / Flask)      ││    (Flask / Python)     │
└────────────┬────────────┘└────────────┬────────────┘└────────────┬────────────┘
             │                          │                          │
             ▼                          └──────────────┬───────────┘
┌─────────────────────────┐                            ▼
│   Base de Estudiantes   │               ┌─────────────────────────┐
│     (PostgreSQL 16)     │               │     Base de Cursos      │
└─────────────────────────┘               │     (PostgreSQL 16)     │
                                          └─────────────────────────┘
</pre>

<hr>

<h2 id="estructura-de-las-carpetas">Estructura de las carpetas</h2>

<pre>
gestor_academico2/
│
├── app.py                  # Archivo principal para arrancar el servicio de Cursos
├── db.py                   # Conexión a la base de datos de Cursos
├── routes.py               # Rutas del servicio de Cursos
├── requirements.txt        # Librerías necesarias de Python
│
├── estudiantes_service/    # Carpeta del servicio de Estudiantes
│   ├── app.py              # Inicia el servicio de Estudiantes
│   ├── db.py               # Conexión a la base de datos de Estudiantes
│   ├── routes.py           # Rutas para crear, ver, editar y borrar estudiantes
│   ├── Dockerfile          # Instrucciones para crear el contenedor
│   └── requirements.txt    # Librerías de Python
│
├── matriculas_service/     # Carpeta del servicio de Matrículas
│   ├── app.py              # Inicia el servicio de Matrículas
│   ├── db.py               # Conexión a la base de datos compartida
│   ├── routes.py           # Rutas para consultar y registrar matrículas
│   ├── Dockerfile          # Instrucciones para crear el contenedor
│   └── requirements.txt    # Librerías de Python
│
├── home/                   # Vista o pantalla del usuario
│   ├── index.html          # Diseño visual de la página
│   ├── styles.css          # Colores y estilos
│   └── app.js              # Código que conecta la página con las APIs
│
├── .env                    # Claves y datos de conexión a las bases de datos
├── .gitignore              # Archivos que no se suben a GitHub
├── docker-compose.yml      # Archivo que arranca todos los contenedores
└── README.md               # Este documento explicativo
</pre>

<hr>

<h2 id="servicios-y-puertos">Servicios y puertos</h2>

<table border="1">
  <thead>
    <tr>
      <th>Servicio</th>
      <th>Puerto en el equipo</th>
      <th>Base de datos que usa</th>
      <th>Contenedor de la Base de Datos</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Cursos</strong> (en la raíz)</td>
      <td><code>5000</code></td>
      <td><code>gestion_academica</code></td>
      <td><code>db_cursos</code></td>
    </tr>
    <tr>
      <td><strong>Estudiantes</strong></td>
      <td><code>5002</code></td>
      <td><code>gestion_academica</code></td>
      <td><code>db_estudiantes</code></td>
    </tr>
    <tr>
      <td><strong>Matrículas</strong></td>
      <td><code>5003</code></td>
      <td><code>gestion_academica</code></td>
      <td><code>db_cursos</code></td>
    </tr>
  </tbody>
</table>

<hr>

<h2 id="rutas-y-datos-que-maneja-cada-servicio">Rutas y datos que maneja cada servicio</h2>

<p>Todos los datos entran y salen en formato <strong>JSON</strong> usando respuestas claras como <code>200</code> cuando todo sale bien o <code>404</code> si algo no se encuentra.</p>

<h3>1. Servicio de Cursos — Puerto 5000</h3>
<ul>
  <li><strong>Datos:</strong> <code>id</code>, <code>codigo</code>, <code>nombre</code>, <code>creditos</code>, <code>profesor</code>, <code>fecha_creacion</code>.</li>
  <li><strong>Rutas:</strong>
    <ul>
      <li><code>GET /cursos</code>: Muestra la lista de todos los cursos.</li>
      <li><code>POST /cursos</code>: Guarda un curso nuevo.</li>
      <li><code>DELETE /cursos/&lt;id&gt;</code>: Elimina un curso usando su ID.</li>
    </ul>
  </li>
</ul>

<h3>2. Servicio de Estudiantes — Puerto 5002</h3>
<ul>
  <li><strong>Datos:</strong> <code>id</code>, <code>cedula</code>, <code>nombre</code>, <code>apellido</code>, <code>correo</code>, <code>programa</code>.</li>
  <li><strong>Rutas:</strong>
    <ul>
      <li><code>GET /estudiantes</code>: Muestra todos los estudiantes.</li>
      <li><code>GET /estudiantes/&lt;id&gt;</code>: Busca a un estudiante por su ID.</li>
      <li><code>POST /estudiantes</code>: Guarda a un estudiante nuevo.</li>
      <li><code>PUT /estudiantes/&lt;id&gt;</code>: Actualiza los datos de un estudiante.</li>
      <li><code>DELETE /estudiantes/&lt;id&gt;</code>: Borra a un estudiante.</li>
    </ul>
  </li>
</ul>

<h3>3. Servicio de Matrículas — Puerto 5003</h3>
<ul>
  <li><strong>Datos:</strong> <code>id</code>, <code>estudiante_id</code>, <code>curso_id</code>, <code>anio</code>, <code>periodo</code>.</li>
  <li><strong>Rutas:</strong>
    <ul>
      <li><code>GET /matriculas</code>: Muestra las matrículas hechas.</li>
      <li><code>POST /matriculas</code>: Guarda una matrícula uniendo el estudiante y el curso.</li>
    </ul>
  </li>
</ul>

<hr>

<h2 id="pantalla-web-frontend">Pantalla web (Frontend)</h2>
<p>En la carpeta <code>home/</code> dejamos una página web hecha con HTML, CSS y JavaScript.</p>
<p>Sirve para probar el sistema directamente desde el navegador de forma visual, sin tener que usar programas externos como Postman para enviar las peticiones.</p>

<hr>

<h2 id="variables-de-entorno-env">Variables de entorno (.env)</h2>
<p>Usamos un archivo llamado <code>.env</code> en la raíz para guardar la información de la base de datos de forma ordenada:</p>

<pre>
# Datos para la base de datos de Estudiantes
ESTUDIANTES_DB_NAME=gestion_academica
ESTUDIANTES_DB_USER=postgres
ESTUDIANTES_DB_PASSWORD=postgres

# Datos para la base de datos de Cursos y Matrículas
CURSOS_DB_PORT=5432
CURSOS_DB_NAME=gestion_academica
CURSOS_DB_USER=postgres
CURSOS_DB_PASSWORD=postgres
</pre>
<h2 id="detalles-de-funcionamiento-y-prevencion-de-fallas">Detalles de funcionamiento y prevención de fallas</h2>
<ol>
  <li><strong>Los datos no se borran al apagar:</strong> Configuramos volúmenes en Docker (<code>estudiantes_data</code> y <code>cursos_data</code>) para que la información guardada en las bases de datos no se pierda al reiniciar el equipo o los contenedores.</li>
  <li><strong>Reinicio si hay un fallo:</strong> Los contenedores están configurados para volver a levantarse automáticamente si ocurre un error inesperado.</li>
  <li><strong>Relación entre datos:</strong> Como cada servicio maneja su propia base de datos, las relaciones (como saber qué estudiante pertenece a qué matrícula) se controlan directamente desde el código de Python.</li>
</ol>
