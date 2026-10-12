/*guarda la URL en un solo lugar*/
const API_ESTUDIANTES = "http://localhost:5001/estudiantes";
/*declara una función que puede esperar respuestas lentas para no congelar pagina*/
async function cargarEstudiantes() {
  const respuesta =
    await fetch(
      API_ESTUDIANTES,
    ); /*hace la petición GET a tu servicio y espera la respuesta*/
  const estudiantes =
    await respuesta.json(); /*convierte el texto JSON en una lista de objetos de JavaScript*/

  document.getElementById("total-estudiantes").textContent =
    /*Aquí se pondra cuántos elementos tiene la lista*/
    estudiantes.length; /*busca en la página el elemento con ese id*/

  const lista = document.getElementById("lista-estudiantes");
  lista.innerHTML = "";
  estudiantes.forEach((e) => {
    /*recorre cada estudiante */
    const li = document.createElement("li");
    li.textContent = `${e.cedula} ${e.nombre} ${e.apellido} ${e.correo} ${e.programa}`; /*escribe su texto con las plantillas de texto */
    lista.appendChild(
      li,
    ); /*lo agrega al <ul>, y entonces aparece en pantalla */
  });
}

cargarEstudiantes();
