// URL del servicio de estudiantes,
const API_ESTUDIANTES = "/estudiantes";
const API_MATRICULAS = "/matriculas";
const API_CURSOS = "/cursos";
const enlaces = document.querySelectorAll(".sidebar a");
const paneles = document.querySelectorAll(".panel");

async function cargarMatriculas() {
  const respuesta = await fetch(API_MATRICULAS);
  const matriculas = await respuesta.json();

  document.getElementById("total-matriculas").textContent = matriculas.length;

  const lista = document.getElementById("lista-matriculas");
  lista.innerHTML = "";
  matriculas.forEach((m) => {
    const li = document.createElement("li");
    li.textContent = `Matrícula ${m.id}: estudiante ${m.estudiante_id}, curso ${m.curso_id} - ${m.estado}`;
    lista.appendChild(li);
  });
}
async function cargarCursos() {
  const respuesta = await fetch(API_CURSOS);
  const cursos = await respuesta.json();

  document.getElementById("total-cursos").textContent = cursos.length;

  const lista = document.getElementById("lista-cursos");
  lista.innerHTML = "";
  cursos.forEach((c) => {
    const li = document.createElement("li");
    li.textContent = `${c.codigo} - ${c.nombre} (${c.creditos} créditos, semestre ${c.semestre})`;
    lista.appendChild(li);
  });
}
// async permite usar esperar respuestas lentas
async function cargarEstudiantes() {
  // Petición GET al servicio y espera la respuesta.
  const respuesta = await fetch(API_ESTUDIANTES);

  // Convierte el texto JSON en una lista de objetos de JavaScript
  const estudiantes = await respuesta.json();

  // Escribe en la tarjeta cuántos estudiantes hay.
  // getElementById busca el elemento id coincide
  document.getElementById("total-estudiantes").textContent = estudiantes.length;

  // Busca el ul y lo vacía, para no duplicar elementos al recargar.
  const lista = document.getElementById("lista-estudiantes");
  lista.innerHTML = "";

  // Recorre cada estudiante e de la lista.
  estudiantes.forEach((e) => {
    // Crea un li en memoria y le escribe el texto.

    const li = document.createElement("li");
    li.textContent = `${e.cedula} ${e.nombre} ${e.apellido} ${e.correo} ${e.programa}`;

    // Crea un botón propio para este estudiante.
    const boton = document.createElement("button");
    boton.textContent = "Eliminar";

    //se borra El estudiante.
    boton.addEventListener("click", async () => {
      // Petición DELETE a /estudiantes/{id}
      await fetch(`${API_ESTUDIANTES}/${e.id}`, { method: "DELETE" });

      // Vuelve a pedir la lista para que el borrado se vea en pantalla.
      cargarEstudiantes();
    });

    // El botón se agrega DESPUÉS de escribir el texto del <li>,
    li.appendChild(boton);

    // Agrega el <li> al <ul> y es cuando aparece en pantalla.
    lista.appendChild(li);
  });
}

// Se registra UNA sola vez, afuera de la función:
document
  .getElementById("form-estudiante")
  .addEventListener("submit", async (evento) => {
    // Evita que el navegador recargue la página
    evento.preventDefault();

    // Lee lo que escribió el usuario en cada campo (.value)
    const estudiante = {
      cedula: document.getElementById("cedula").value,
      nombre: document.getElementById("nombre").value,
      apellido: document.getElementById("apellido").value,
      correo: document.getElementById("correo").value,
      programa: document.getElementById("programa").value,
    };

    // Petición POST crea el estudiante.
    await fetch(API_ESTUDIANTES, {
      method: "POST",
      // Avisa que el cuerpo es JSON Sin esto Flask responde 415
      headers: { "Content-Type": "application/json" },
      // Convierte el objeto de JavaScript en texto JSON
      body: JSON.stringify(estudiante),
    });

    // Limpia el formulario y recarga la lista para ver el nuevo.
    evento.target.reset();
    cargarEstudiantes();
  });

// Muestra solo el panel cuyo id coincide y oculta los demás.
function mostrar(id) {
  paneles.forEach((p) => p.classList.toggle("activo", p.id === id));
}

// Al pulsar un enlace: evita el salto de anclaje y muestra su panel.
// href="#cursos" -> slice(1) quita el "#" y deja "cursos".
enlaces.forEach((a) => {
  a.addEventListener("click", (evento) => {
    evento.preventDefault();
    mostrar(a.getAttribute("href").slice(1));
  });
});

// Vista inicial al abrir la página.
mostrar("estudiantes");
// Se ejecuta al abrir la página: carga la lista inicial.
cargarEstudiantes();
cargarMatriculas();
cargarCursos();
