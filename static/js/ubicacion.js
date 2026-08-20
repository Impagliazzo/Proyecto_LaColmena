/**
 * Selector de ubicación único de LaColmena: Provincia → Localidad → Distrito/Barrio.
 *
 * Componente reutilizable para CUALQUIER formulario del sitio que pida
 * ubicación (propiedades, publicaciones de compañero, perfiles, etc.) — no
 * reimplementar esta lógica por formulario, llamar a esta función.
 *
 * - Provincia: estricta (solo las 24 jurisdicciones reales, catálogo propio
 *   importado del Georef). El input visible NO es el campo del formulario:
 *   al seleccionar, se guarda el id real en `provinciaId` (un input oculto).
 * - Localidad: sugerida desde el catálogo del Georef, filtrada por la
 *   provincia elegida, pero admite texto libre si no está en el catálogo.
 * - Distrito/Barrio: sugerido desde datos ya cargados en el sitio (nunca un
 *   catálogo fijo), admite texto libre siempre.
 *
 * Uso:
 *   crearSelectorUbicacion({
 *       provinciaTexto: document.getElementById('provincia-busqueda'),
 *       provinciaId: document.getElementById('id_provincia'),
 *       localidadInput: document.getElementById('id_ciudad'),
 *       distritoInput: document.getElementById('id_distrito'),   // opcional
 *       urlProvincias: '/ubicaciones/api/provincias/',
 *       urlLocalidades: '/ubicaciones/api/localidades/',
 *       urlDistritos: '/ubicaciones/api/distritos/',              // opcional
 *   });
 */
function crearSelectorUbicacion(opciones) {
    const {
        provinciaTexto,
        provinciaId,
        localidadInput,
        distritoInput,
        urlProvincias,
        urlLocalidades,
        urlDistritos,
    } = opciones;

    async function pedirJson(url, params) {
        const resp = await fetch(`${url}?${new URLSearchParams(params)}`);
        const data = await resp.json();
        return data.resultados || [];
    }

    let autocompleteDistrito = null;
    if (distritoInput) {
        autocompleteDistrito = crearAutocomplete({
            input: distritoInput,
            minChars: 1,
            debounceMs: 250,
            obtenerEtiqueta: (item) => item.distrito,
            obtenerSugerencias: (q) => pedirJson(urlDistritos, { q, ciudad: localidadInput.value.trim() }),
        });
    }

    const autocompleteLocalidad = crearAutocomplete({
        input: localidadInput,
        minChars: 0,
        debounceMs: 200,
        obtenerEtiqueta: (item) => item.nombre,
        obtenerSugerencias: (q) => {
            if (!provinciaId.value) return [];
            return pedirJson(urlLocalidades, { provincia_id: provinciaId.value, q });
        },
        textoVacio: () => (provinciaId.value ? null : 'Elegí primero una provincia.'),
        onSeleccionar: () => {
            if (distritoInput) {
                distritoInput.value = '';
                autocompleteDistrito.cerrar();
            }
        },
    });

    // Si la Localidad cambia (no solo al elegir una sugerencia, también al
    // tipear y salir del campo), se limpia el Distrito/Barrio.
    localidadInput.addEventListener('change', () => {
        if (distritoInput) {
            distritoInput.value = '';
            autocompleteDistrito.cerrar();
        }
    });

    crearAutocomplete({
        input: provinciaTexto,
        minChars: 0,
        debounceMs: 150,
        estricto: true,
        obtenerEtiqueta: (item) => item.nombre,
        obtenerSugerencias: (q) => pedirJson(urlProvincias, { q }),
        onSeleccionar: (item) => {
            provinciaId.value = item.id;
            localidadInput.value = '';
            distritoInput && (distritoInput.value = '');
            autocompleteLocalidad.cerrar();
            autocompleteDistrito && autocompleteDistrito.cerrar();
        },
        onInvalido: () => {
            // El usuario borró/invalidó el texto sin elegir una provincia real.
            if (!provinciaTexto.value) provinciaId.value = '';
        },
    });
}
