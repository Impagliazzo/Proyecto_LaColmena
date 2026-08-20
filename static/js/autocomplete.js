/**
 * Autocompletado único de LaColmena.
 *
 * Patrón visual y de comportamiento oficial (fuente de verdad: el campo
 * "universidad" de usuarios/completar_perfil_busqueda.html). Cualquier campo
 * con sugerencias en el sitio debe usar esta función en vez de reimplementar
 * su propio dropdown — la diferencia entre campos va solo en `obtenerSugerencias`,
 * `renderItem` y `onSeleccionar`.
 *
 * Requiere las clases .autocomplete-list / .autocomplete-item /
 * .autocomplete-empty / .autocomplete-loading definidas globalmente
 * (ver templates/base.html).
 */
function crearAutocomplete(opciones) {
    const {
        input,
        minChars = 1,
        debounceMs = 0,
        obtenerSugerencias,
        renderItem,
        obtenerEtiqueta,
        onSeleccionar,
        textoVacio = null,
        textoCargando = 'Buscando…',
        // Si es true, el valor final del input tiene que coincidir con una de
        // las sugerencias (texto libre no permitido) — ej. Provincia, que
        // debe ser estricta. Si el usuario deja un texto que no matchea
        // ninguna sugerencia, se revierte a la última selección válida.
        estricto = false,
        onInvalido,
    } = opciones;

    const parent = input.parentElement;
    if (getComputedStyle(parent).position === 'static') {
        parent.style.position = 'relative';
    }

    const lista = document.createElement('div');
    lista.className = 'autocomplete-list';
    parent.appendChild(lista);

    let sugerencias = [];
    let indiceActivo = -1;
    let debounceTimer = null;
    let requestId = 0;
    let ultimaSeleccion = null;

    function escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    function etiquetaDe(item) {
        if (obtenerEtiqueta) return obtenerEtiqueta(item);
        return item && item.label !== undefined ? item.label : String(item);
    }

    function cerrar() {
        lista.style.display = 'none';
        indiceActivo = -1;
    }

    function actualizarActivo() {
        Array.from(lista.children).forEach((el, i) => {
            el.classList.toggle('is-active', i === indiceActivo);
        });
        const activo = lista.children[indiceActivo];
        if (activo) activo.scrollIntoView({ block: 'nearest' });
    }

    function seleccionar(item) {
        input.value = etiquetaDe(item);
        ultimaSeleccion = item;
        cerrar();
        if (onSeleccionar) onSeleccionar(item);
    }

    // Para campos estrictos (ej. Provincia): si al cerrar el dropdown el
    // texto no coincide con ninguna sugerencia conocida, se revierte a la
    // última selección válida en vez de dejar un valor inventado.
    function cerrarValidando() {
        if (estricto) {
            const valorActual = input.value.trim().toLowerCase();
            const coincide = valorActual !== '' && sugerencias.some(
                (item) => etiquetaDe(item).trim().toLowerCase() === valorActual
            );
            if (!coincide) {
                input.value = ultimaSeleccion ? etiquetaDe(ultimaSeleccion) : '';
                if (onInvalido) onInvalido();
            }
        }
        cerrar();
    }

    function renderLoading() {
        lista.innerHTML = '';
        const div = document.createElement('div');
        div.className = 'autocomplete-loading';
        div.textContent = textoCargando;
        lista.appendChild(div);
        lista.style.display = 'block';
    }

    function renderResultados(items) {
        sugerencias = items || [];
        indiceActivo = -1;
        lista.innerHTML = '';

        if (sugerencias.length === 0) {
            if (textoVacio) {
                const div = document.createElement('div');
                div.className = 'autocomplete-empty';
                div.innerHTML = typeof textoVacio === 'function' ? textoVacio(input.value) : textoVacio;
                lista.appendChild(div);
                lista.style.display = 'block';
            } else {
                cerrar();
            }
            return;
        }

        sugerencias.forEach((item, i) => {
            const el = document.createElement('div');
            el.className = 'autocomplete-item';
            el.dataset.index = String(i);
            if (renderItem) {
                el.innerHTML = renderItem(item);
            } else {
                el.textContent = etiquetaDe(item);
            }
            // mousedown (no click): el click dispara primero un blur en el
            // input (el ítem no es un elemento enfocable), que cerraba el
            // listado antes de que el click llegara a procesarse. Con
            // preventDefault en mousedown el input nunca pierde el foco y la
            // selección con mouse queda igual de confiable que con teclado.
            el.addEventListener('mousedown', (e) => {
                e.preventDefault();
                seleccionar(item);
            });
            lista.appendChild(el);
        });
        lista.style.display = 'block';
    }

    async function buscar(texto) {
        const miRequestId = ++requestId;
        const resultado = obtenerSugerencias(texto);
        if (resultado && typeof resultado.then === 'function') {
            renderLoading();
            const items = await resultado;
            if (miRequestId !== requestId) return; // respuesta obsoleta (llegó tarde), se ignora
            renderResultados(items);
        } else {
            renderResultados(resultado);
        }
    }

    input.addEventListener('input', function () {
        const texto = input.value.trim();
        clearTimeout(debounceTimer);
        if (texto.length < minChars) {
            cerrar();
            return;
        }
        if (debounceMs > 0) {
            debounceTimer = setTimeout(() => buscar(texto), debounceMs);
        } else {
            buscar(texto);
        }
    });

    input.addEventListener('focus', function () {
        // Al hacer click/foco ya se muestran las opciones disponibles
        // (todas si el input está vacío y minChars lo permite), no hace
        // falta empezar a escribir primero.
        const texto = input.value.trim();
        if (texto.length >= minChars) {
            buscar(texto);
        }
    });

    input.addEventListener('blur', function () {
        // Pequeña demora: un click en un item no debería contar como "salida
        // del campo" antes de que su propio listener de click lo procese.
        setTimeout(cerrarValidando, 150);
    });

    input.addEventListener('keydown', function (e) {
        if (lista.style.display !== 'block') return;
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            indiceActivo = Math.min(indiceActivo + 1, sugerencias.length - 1);
            actualizarActivo();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            indiceActivo = Math.max(indiceActivo - 1, -1);
            actualizarActivo();
        } else if (e.key === 'Enter') {
            if (indiceActivo >= 0) {
                e.preventDefault();
                seleccionar(sugerencias[indiceActivo]);
            }
        } else if (e.key === 'Escape') {
            cerrarValidando();
        }
    });

    document.addEventListener('click', function (e) {
        if (e.target !== input && !lista.contains(e.target)) {
            cerrarValidando();
        }
    });

    return { cerrar, buscar };
}
