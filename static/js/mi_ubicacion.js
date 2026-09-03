/**
 * "Mi ubicación" del navbar: elegir una ciudad/provincia para que el
 * backend le dé más relevancia a las propiedades cercanas (ver
 * propiedades/context_processors.py y propiedades/views.py -
 * GEO_BONUS_CIUDAD/GEO_BONUS_PROVINCIA en inicio(), y el order_by geo en
 * listado_propiedades()).
 *
 * Todo el estado vive del lado del cliente:
 *   - cookie "lc_ubicacion" (1 año): la ubicación ELEGIDA, es la única que
 *     lee el backend. Se escribe acá mismo, nunca desde una vista.
 *   - localStorage "lc_ubicaciones_recientes": historial corto para pintar
 *     "Ubicaciones recientes" en el dropdown y en el modal del mapa.
 *   - sessionStorage "lc_toast_pendiente": mensaje a mostrar apenas
 *     recargue la página siguiente (después de guardar una ubicación).
 *
 * El markup del botón+dropdown se repite dos veces en templates/base.html
 * (desktop y mobile, mismo patrón que ya usa el resto del navbar) - las
 * funciones de más abajo trabajan sobre CUALQUIER elemento con
 * [data-ubicacion-widget] indistintamente. El modal del mapa ("Elegí tu
 * ubicación", Leaflet + OpenStreetMap) es uno solo para todo el sitio.
 */
(function () {
    const COOKIE_UBICACION = 'lc_ubicacion';
    const KEY_RECIENTES = 'lc_ubicaciones_recientes';
    const KEY_TOAST = 'lc_toast_pendiente';
    const MAX_RECIENTES = 4;
    const NOMINATIM_BASE = 'https://nominatim.openstreetmap.org';

    // Centroides aproximados de las 24 provincias argentinas (dato público
    // y estable). Es el RESPALDO de la detección automática cuando Nominatim
    // no responde (red caída, timeout) - normalmente se usa reverse
    // geocoding real, esto solo evita que la función quede totalmente rota
    // si el servicio externo falla.
    const PROVINCIAS_CENTROIDES = [
        { nombre: 'Buenos Aires', lat: -36.6769, lng: -60.5588 },
        { nombre: 'Ciudad Autónoma de Buenos Aires', lat: -34.6037, lng: -58.3816 },
        { nombre: 'Catamarca', lat: -28.4696, lng: -65.7852 },
        { nombre: 'Chaco', lat: -27.4514, lng: -58.9867 },
        { nombre: 'Chubut', lat: -43.3002, lng: -65.1023 },
        { nombre: 'Córdoba', lat: -31.4201, lng: -64.1888 },
        { nombre: 'Corrientes', lat: -27.4692, lng: -58.8306 },
        { nombre: 'Entre Ríos', lat: -31.7333, lng: -60.5238 },
        { nombre: 'Formosa', lat: -26.1849, lng: -58.1731 },
        { nombre: 'Jujuy', lat: -24.1858, lng: -65.2995 },
        { nombre: 'La Pampa', lat: -36.6167, lng: -64.2833 },
        { nombre: 'La Rioja', lat: -29.4131, lng: -66.8558 },
        { nombre: 'Mendoza', lat: -32.8895, lng: -68.8458 },
        { nombre: 'Misiones', lat: -27.3621, lng: -55.9008 },
        { nombre: 'Neuquén', lat: -38.9516, lng: -68.0591 },
        { nombre: 'Río Negro', lat: -40.8135, lng: -63.0000 },
        { nombre: 'Salta', lat: -24.7859, lng: -65.4117 },
        { nombre: 'San Juan', lat: -31.5375, lng: -68.5364 },
        { nombre: 'San Luis', lat: -33.3017, lng: -66.3378 },
        { nombre: 'Santa Cruz', lat: -51.6230, lng: -69.2168 },
        { nombre: 'Santa Fe', lat: -31.6333, lng: -60.7000 },
        { nombre: 'Santiago del Estero', lat: -27.7951, lng: -64.2615 },
        { nombre: 'Tierra del Fuego', lat: -54.8019, lng: -68.3030 },
        { nombre: 'Tucumán', lat: -26.8241, lng: -65.2226 },
    ];

    function distanciaHaversineKm(lat1, lng1, lat2, lng2) {
        const R = 6371;
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLng = (lng2 - lng1) * Math.PI / 180;
        const a = Math.sin(dLat / 2) ** 2 +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLng / 2) ** 2;
        return 2 * R * Math.asin(Math.sqrt(a));
    }

    function provinciaMasCercana(lat, lng) {
        let mejor = null;
        let mejorDistancia = Infinity;
        PROVINCIAS_CENTROIDES.forEach(function (p) {
            const d = distanciaHaversineKm(lat, lng, p.lat, p.lng);
            if (d < mejorDistancia) {
                mejorDistancia = d;
                mejor = p;
            }
        });
        return mejor;
    }

    // --- Reverse geocoding / búsqueda de lugares vía Nominatim (OSM) -------
    // Servicio público y gratuito, sin API key. Politica de uso: max 1
    // req/seg (los inputs están debounced bien por encima de eso) y requiere
    // identificar la app via Referer - el navegador ya lo manda solo.

    function extraerCiudad(address) {
        const nombre = address.city || address.town || address.village ||
            address.municipality || address.county || null;
        if (!nombre) return null;
        // El OSM argentino suele nombrar el municipio como "Municipio de X"
        // en vez de "X" a secas (ej. "Municipio de Presidencia Roque Sáenz
        // Peña") - para Localidad interesa el nombre limpio de la ciudad.
        return nombre.replace(/^municipio de\s+/i, '');
    }

    function extraerDistrito(address) {
        return address.suburb || address.neighbourhood || address.quarter || address.city_district || null;
    }

    function extraerDireccion(address) {
        return [address.road, address.house_number].filter(Boolean).join(' ') || null;
    }

    async function reverseGeocode(lat, lon) {
        try {
            const url = NOMINATIM_BASE + '/reverse?format=jsonv2&lat=' + lat + '&lon=' + lon +
                '&accept-language=es&zoom=18&addressdetails=1';
            const resp = await fetch(url, { headers: { 'Accept': 'application/json' } });
            if (!resp.ok) throw new Error('reverse geocoding fallo');
            const datos = await resp.json();
            const address = datos.address || {};
            const ciudad = extraerCiudad(address);
            const provincia = address.state || null;
            if (ciudad || provincia) {
                return {
                    ciudad: ciudad,
                    provincia: provincia,
                    distrito: extraerDistrito(address),
                    direccion: extraerDireccion(address),
                };
            }
            throw new Error('sin address utilizable');
        } catch (e) {
            // Nominatim no respondio: al menos resolvemos la provincia mas
            // cercana con los centroides fijos, sin depender de la red.
            const provincia = provinciaMasCercana(lat, lon);
            return { ciudad: null, provincia: provincia ? provincia.nombre : null, distrito: null, direccion: null };
        }
    }

    // Búsqueda de DIRECCIONES completas vía Nominatim (a diferencia de
    // buscarUbicaciones de abajo, que busca ciudades/provincias en el
    // catálogo propio): la usa el selector de "Usar el mapa" del formulario
    // de propiedad (crear.html/editar.html) para encontrar una calle y
    // número puntuales, algo que el catálogo de localidades no tiene. Acá sí
    // conviene Nominatim porque una dirección completa ("Av. San Martín 123,
    // Merlo") le da contexto de sobra - el problema de resultados basura de
    // Nominatim es solo con texto corto/ambiguo (ver buscarUbicaciones).
    async function buscarDirecciones(texto) {
        const url = NOMINATIM_BASE + '/search?format=jsonv2&addressdetails=1&limit=6' +
            '&countrycodes=ar&accept-language=es&q=' + encodeURIComponent(texto);
        const resp = await fetch(url, { headers: { 'Accept': 'application/json' } });
        if (!resp.ok) return [];
        const resultados = await resp.json();
        return resultados.map(function (r) {
            const address = r.address || {};
            return {
                etiqueta: r.display_name,
                lat: parseFloat(r.lat),
                lon: parseFloat(r.lon),
                ciudad: extraerCiudad(address),
                provincia: address.state || null,
                distrito: extraerDistrito(address),
                direccion: extraerDireccion(address),
            };
        });
    }

    // Nominatim da resultados excelentes para un nombre COMPLETO y bien
    // formado ("Sáenz Peña, Chaco, Argentina" - ver reverseGeocode arriba),
    // pero para texto corto/parcial ("pe", "pen") busca por substring en
    // cualquier tipo de lugar (restaurantes, picos, plazas...) y el
    // resultado es basura. Por eso el AUTOCOMPLETADO de texto usa el
    // catálogo propio de localidades/provincias del sitio (poblado desde
    // Georef, ver ubicaciones/management/commands/importar_ubicaciones.py)
    // y Nominatim se llama recién despues, solo para geocodificar el
    // nombre YA elegido y poder ubicarlo en el mapa.
    async function buscarUbicaciones(texto, urlProvincias, urlLocalidades) {
        const [respProvincias, respLocalidades] = await Promise.all([
            fetch(urlProvincias + '?q=' + encodeURIComponent(texto)),
            fetch(urlLocalidades + '?q=' + encodeURIComponent(texto)),
        ]);
        const datosProvincias = respProvincias.ok ? await respProvincias.json() : { resultados: [] };
        const datosLocalidades = respLocalidades.ok ? await respLocalidades.json() : { resultados: [] };

        const provincias = (datosProvincias.resultados || []).map(function (p) {
            return { tipo: 'provincia', ciudad: null, provincia: p.nombre };
        });
        const localidades = (datosLocalidades.resultados || []).map(function (l) {
            return { tipo: 'localidad', ciudad: l.nombre, provincia: l.provincia };
        });
        return provincias.concat(localidades).slice(0, 8);
    }

    // Convierte un nombre YA elegido (ciudad+provincia, o solo provincia) en
    // coordenadas para poder centrar el mapa y poner el marcador ahí.
    async function geocodificarNombre(loc) {
        const texto = etiquetaUbicacion(loc) + ', Argentina';
        try {
            const url = NOMINATIM_BASE + '/search?format=jsonv2&limit=1&countrycodes=ar&accept-language=es&q=' +
                encodeURIComponent(texto);
            const resp = await fetch(url, { headers: { 'Accept': 'application/json' } });
            const resultados = resp.ok ? await resp.json() : [];
            if (resultados.length > 0) {
                return { lat: parseFloat(resultados[0].lat), lon: parseFloat(resultados[0].lon) };
            }
        } catch (e) { /* sigue al respaldo de abajo */ }
        // Sin resultado de Nominatim: al menos centramos en la provincia
        // (mismos centroides fijos que usa la deteccion automatica).
        const provinciaInfo = PROVINCIAS_CENTROIDES.find(function (p) {
            return loc.provincia && p.nombre.toLowerCase().indexOf(loc.provincia.toLowerCase()) !== -1;
        });
        return provinciaInfo ? { lat: provinciaInfo.lat, lon: provinciaInfo.lng } : { lat: -38.4, lon: -63.6 };
    }

    // --- Cookie / recientes / toast -----------------------------------

    function obtenerUbicacionActual() {
        const match = document.cookie.match(new RegExp('(?:^|; )' + COOKIE_UBICACION + '=([^;]*)'));
        if (!match) return null;
        try {
            return JSON.parse(decodeURIComponent(match[1]));
        } catch (e) {
            return null;
        }
    }

    function mismaUbicacion(a, b) {
        if (!a || !b) return false;
        return (a.ciudad || null) === (b.ciudad || null) && (a.provincia || null) === (b.provincia || null);
    }

    function obtenerRecientes() {
        try {
            const crudo = localStorage.getItem(KEY_RECIENTES);
            return crudo ? JSON.parse(crudo) : [];
        } catch (e) {
            return [];
        }
    }

    function agregarReciente(loc) {
        try {
            let recientes = obtenerRecientes().filter(function (r) { return !mismaUbicacion(r, loc); });
            recientes.unshift(loc);
            localStorage.setItem(KEY_RECIENTES, JSON.stringify(recientes.slice(0, MAX_RECIENTES)));
        } catch (e) {
            // localStorage lleno/deshabilitado: no rompe nada, solo no queda historial.
        }
    }

    function etiquetaUbicacion(loc) {
        if (!loc) return '';
        if (loc.ciudad && loc.provincia) return loc.ciudad + ', ' + loc.provincia;
        return loc.ciudad || loc.provincia || '';
    }

    function guardarUbicacion(loc, mensajeToast) {
        loc = { ciudad: (loc.ciudad || '').trim() || null, provincia: (loc.provincia || '').trim() || null };
        if (!loc.ciudad && !loc.provincia) return;
        document.cookie = COOKIE_UBICACION + '=' + encodeURIComponent(JSON.stringify(loc)) +
            '; path=/; max-age=31536000; samesite=lax';
        agregarReciente(loc);
        try {
            sessionStorage.setItem(KEY_TOAST, mensajeToast || ('Mostrando propiedades en ' + etiquetaUbicacion(loc)));
        } catch (e) { /* sin sessionStorage no hay toast, pero la ubicacion se guarda igual */ }
        window.location.reload();
    }

    function mostrarToastPendienteSiHay() {
        let mensaje = null;
        try {
            mensaje = sessionStorage.getItem(KEY_TOAST);
            if (mensaje) sessionStorage.removeItem(KEY_TOAST);
        } catch (e) { return; }
        if (!mensaje) return;

        const toast = document.createElement('div');
        toast.className = 'fixed top-20 left-1/2 -translate-x-1/2 z-[70] bg-white border border-gray-100 shadow-lg rounded-xl px-4 py-3 flex items-center gap-3 max-w-sm';
        toast.innerHTML =
            '<span class="w-8 h-8 rounded-full bg-green-100 text-green-600 flex items-center justify-center flex-shrink-0"><i class="fas fa-check text-sm"></i></span>' +
            '<span class="text-sm text-gray-800">' + mensaje.replace(/</g, '&lt;') + '</span>';
        document.body.appendChild(toast);
        setTimeout(function () { toast.remove(); }, 4000);
    }

    // --- Carga perezosa de Leaflet (solo si se abre el modal del mapa) ----

    let leafletCargando = null;
    function cargarLeaflet() {
        if (window.L) return Promise.resolve(window.L);
        if (leafletCargando) return leafletCargando;
        leafletCargando = new Promise(function (resolve, reject) {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
            document.head.appendChild(link);

            const script = document.createElement('script');
            script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
            script.onload = function () { resolve(window.L); };
            script.onerror = reject;
            document.head.appendChild(script);
        });
        return leafletCargando;
    }

    document.addEventListener('DOMContentLoaded', function () {
        mostrarToastPendienteSiHay();

        const instancias = Array.from(document.querySelectorAll('[data-ubicacion-widget]'));
        if (instancias.length > 0) inicializarDropdowns(instancias);

        const modal = document.getElementById('ubicacion-modal');
        if (modal) inicializarModal(modal);
    });

    function inicializarDropdowns(instancias) {
        function cerrarTodos() {
            instancias.forEach(function (inst) {
                inst.querySelector('[data-ubicacion-panel]').classList.add('hidden');
            });
        }

        function renderRecientes(instancia) {
            const cont = instancia.querySelector('[data-ubicacion-recientes]');
            const titulo = instancia.querySelector('[data-ubicacion-recientes-titulo]');
            pintarListaRecientes(cont, titulo, function (loc) { guardarUbicacion(loc); });
        }

        instancias.forEach(function (instancia) {
            const boton = instancia.querySelector('[data-ubicacion-boton]');
            const panel = instancia.querySelector('[data-ubicacion-panel]');
            const btnDetectar = instancia.querySelector('[data-ubicacion-detectar]');
            const estadoDetectar = instancia.querySelector('[data-ubicacion-detectar-estado]');
            const btnAbrirMapa = instancia.querySelector('[data-ubicacion-abrir-mapa]');

            renderRecientes(instancia);

            boton.addEventListener('click', function (e) {
                e.stopPropagation();
                const estabaAbierto = !panel.classList.contains('hidden');
                cerrarTodos();
                if (!estabaAbierto) panel.classList.remove('hidden');
            });
            panel.addEventListener('click', function (e) { e.stopPropagation(); });

            btnDetectar.addEventListener('click', function () {
                detectarUbicacion(estadoDetectar, function (loc) {
                    guardarUbicacion(loc, 'Ubicación detectada: mostrando propiedades en ' + etiquetaUbicacion(loc));
                });
            });

            btnAbrirMapa.addEventListener('click', function () {
                cerrarTodos();
                abrirModalUbicacion();
            });
        });

        document.addEventListener('click', function (e) {
            instancias.forEach(function (instancia) {
                if (!instancia.contains(e.target)) {
                    instancia.querySelector('[data-ubicacion-panel]').classList.add('hidden');
                }
            });
        });

        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') cerrarTodos();
        });
    }

    function detectarUbicacion(elementoEstado, alExito) {
        if (!navigator.geolocation) {
            if (elementoEstado) {
                elementoEstado.textContent = 'Tu navegador no admite geolocalización. Buscala manualmente.';
                elementoEstado.classList.remove('hidden');
            }
            return;
        }
        if (elementoEstado) {
            elementoEstado.textContent = 'Detectando tu ubicación…';
            elementoEstado.classList.remove('hidden');
        }
        navigator.geolocation.getCurrentPosition(
            async function (posicion) {
                const loc = await reverseGeocode(posicion.coords.latitude, posicion.coords.longitude);
                if (elementoEstado) elementoEstado.classList.add('hidden');
                alExito(loc, posicion.coords.latitude, posicion.coords.longitude);
            },
            function () {
                // Permiso rechazado o error: nunca un alert, solo un texto
                // chico e inline - el resto del sitio sigue funcionando
                // normal y "Buscar otra ubicación" sigue disponible.
                if (elementoEstado) {
                    elementoEstado.textContent = 'No pudimos acceder a tu ubicación. Podés buscarla manualmente.';
                    elementoEstado.classList.remove('hidden');
                }
            },
            { timeout: 8000 }
        );
    }

    function pintarListaRecientes(contenedor, elementoTitulo, alElegir) {
        const recientes = obtenerRecientes();
        const actual = obtenerUbicacionActual();

        contenedor.innerHTML = '';
        if (recientes.length === 0) {
            if (elementoTitulo) elementoTitulo.classList.add('hidden');
            return;
        }
        if (elementoTitulo) elementoTitulo.classList.remove('hidden');

        recientes.forEach(function (loc) {
            const esActual = mismaUbicacion(actual, loc);
            const boton = document.createElement('button');
            boton.type = 'button';
            boton.className = 'w-full flex items-center justify-between gap-2 px-4 py-2 hover:bg-gray-50 text-left transition rounded-lg';
            boton.innerHTML =
                '<span class="flex items-center gap-2 text-sm text-gray-800 truncate min-w-0">' +
                '<i class="fas ' + (esActual ? 'fa-map-marker-alt text-yellow-500' : 'fa-clock text-gray-400') + ' w-4 text-center flex-shrink-0"></i>' +
                '<span class="truncate">' + etiquetaUbicacion(loc).replace(/</g, '&lt;') + '</span>' +
                '</span>' +
                (esActual ? '<i class="fas fa-check text-yellow-500 flex-shrink-0"></i>' : '');
            boton.addEventListener('click', function () { alElegir(loc); });
            contenedor.appendChild(boton);
        });
    }

    // --- Modal "Elegí tu ubicación" (mapa Leaflet) -------------------------

    let mapaInstancia = null;
    let marcadorInstancia = null;
    let circuloInstancia = null;
    let candidato = null; // {ciudad, provincia, distrito, direccion} de lo marcado en el mapa ahora mismo

    // El modal es UNO SOLO para todo el sitio (navbar "Mi ubicación" Y el
    // selector de dirección del formulario de propiedad) - lo que cambia
    // entre usos es el modo de búsqueda y qué hacer al confirmar, no el
    // mapa/modal en sí. Ver DEFAULTS_MODAL para el comportamiento de navbar.
    const DEFAULTS_MODAL = {
        modo: 'catalogo', // 'catalogo' (ciudad/provincia) | 'direccion' (calle puntual, vía Nominatim)
        onConfirmar: null, // se completa mas abajo con guardarUbicacion (evita referenciarla antes de definirse)
        titulo: 'Elegí tu ubicación',
        descripcion: 'Buscá una ciudad o seleccioná un punto en el mapa para ver propiedades en esa zona.',
    };
    let modoModal = DEFAULTS_MODAL.modo;
    let onConfirmarModal = null;

    // opciones: { modo, onConfirmar, titulo, descripcion } - todas opcionales,
    // si se omiten toma el comportamiento de "Mi ubicación" del navbar.
    function abrirModalUbicacion(opciones) {
        opciones = opciones || {};
        const modal = document.getElementById('ubicacion-modal');
        if (!modal) return;

        modoModal = opciones.modo || DEFAULTS_MODAL.modo;
        onConfirmarModal = opciones.onConfirmar || guardarUbicacion;
        candidato = null;

        const tituloEl = modal.querySelector('[data-ubicacion-modal-titulo]');
        const descripcionEl = modal.querySelector('[data-ubicacion-modal-descripcion]');
        if (tituloEl) tituloEl.textContent = opciones.titulo || DEFAULTS_MODAL.titulo;
        if (descripcionEl) descripcionEl.textContent = opciones.descripcion || DEFAULTS_MODAL.descripcion;

        const btnConfirmar = modal.querySelector('[data-ubicacion-modal-confirmar]');
        if (btnConfirmar) btnConfirmar.disabled = true;

        modal.classList.remove('hidden');
        window.dispatchEvent(new Event('lc-ubicacion-modal-abierto'));
        cargarLeaflet().then(function (L) {
            inicializarMapaSiHaceFalta(L);
            setTimeout(function () { mapaInstancia.invalidateSize(); }, 50);
        });
    }

    function cerrarModalUbicacion() {
        const modal = document.getElementById('ubicacion-modal');
        if (modal) modal.classList.add('hidden');
    }

    function inicializarMapaSiHaceFalta(L) {
        if (mapaInstancia) return;
        mapaInstancia = L.map('ubicacion-mapa').setView([-38.4, -63.6], 4);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
            maxZoom: 18,
        }).addTo(mapaInstancia);

        mapaInstancia.on('click', function (e) {
            ubicarMarcador(e.latlng.lat, e.latlng.lng, true);
        });
    }

    function ubicarMarcador(lat, lon, resolverDireccion) {
        const L = window.L;
        if (!marcadorInstancia) {
            marcadorInstancia = L.marker([lat, lon], { draggable: true }).addTo(mapaInstancia);
            marcadorInstancia.on('dragend', function () {
                const pos = marcadorInstancia.getLatLng();
                ubicarMarcador(pos.lat, pos.lng, true);
            });
        } else {
            marcadorInstancia.setLatLng([lat, lon]);
        }

        if (!circuloInstancia) {
            circuloInstancia = L.circle([lat, lon], { radius: 10000, color: '#F2B705', weight: 1, fillOpacity: 0.08 }).addTo(mapaInstancia);
        } else {
            circuloInstancia.setLatLng([lat, lon]);
        }

        const btnConfirmar = document.querySelector('[data-ubicacion-modal-confirmar]');
        if (resolverDireccion) {
            btnConfirmar.disabled = true;
            reverseGeocode(lat, lon).then(function (loc) {
                candidato = loc;
                btnConfirmar.disabled = !(loc.ciudad || loc.provincia);
            });
        }
    }

    function inicializarModal(modal) {
        modal.querySelectorAll('[data-ubicacion-modal-cerrar]').forEach(function (el) {
            el.addEventListener('click', cerrarModalUbicacion);
        });
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && !modal.classList.contains('hidden')) cerrarModalUbicacion();
        });

        const input = modal.querySelector('[data-ubicacion-modal-input]');
        const btnDetectar = modal.querySelector('[data-ubicacion-modal-detectar]');
        const estadoDetectar = modal.querySelector('[data-ubicacion-modal-estado]');
        const btnConfirmar = modal.querySelector('[data-ubicacion-modal-confirmar]');
        const contRecientes = modal.querySelector('[data-ubicacion-modal-recientes]');
        const tituloRecientes = modal.querySelector('[data-ubicacion-modal-recientes-titulo]');

        // "Recientes" son ciudades/provincias ya elegidas alguna vez para
        // "Mi ubicación" - no tienen sentido cuando se está buscando una
        // dirección puntual de una propiedad, así que se ocultan en ese modo.
        function actualizarRecientesSegunModo() {
            const mostrar = modoModal !== 'direccion';
            if (mostrar) {
                pintarListaRecientes(contRecientes, tituloRecientes, function (loc) {
                    onConfirmarModal(loc);
                    cerrarModalUbicacion();
                });
            } else {
                contRecientes.innerHTML = '';
                if (tituloRecientes) tituloRecientes.classList.add('hidden');
            }
        }
        if (typeof crearAutocomplete === 'function') {
            const urlProvincias = input.dataset.urlProvincias;
            const urlLocalidades = input.dataset.urlLocalidades;
            crearAutocomplete({
                input: input,
                minChars: 2,
                debounceMs: 300,
                obtenerSugerencias: function (texto) {
                    if (modoModal === 'direccion') return buscarDirecciones(texto);
                    return buscarUbicaciones(texto, urlProvincias, urlLocalidades);
                },
                obtenerEtiqueta: function (item) {
                    return modoModal === 'direccion' ? item.etiqueta : etiquetaUbicacion(item);
                },
                onSeleccionar: async function (item) {
                    if (modoModal === 'direccion') {
                        candidato = { ciudad: item.ciudad, provincia: item.provincia, distrito: item.distrito, direccion: item.direccion };
                        mapaInstancia.setView([item.lat, item.lon], 17);
                        ubicarMarcador(item.lat, item.lon, false);
                        btnConfirmar.disabled = !(candidato.ciudad || candidato.provincia);
                        return;
                    }
                    candidato = { ciudad: item.ciudad, provincia: item.provincia };
                    btnConfirmar.disabled = true;
                    const coords = await geocodificarNombre(candidato);
                    const zoom = candidato.ciudad ? 13 : 7;
                    mapaInstancia.setView([coords.lat, coords.lon], zoom);
                    ubicarMarcador(coords.lat, coords.lon, false);
                    btnConfirmar.disabled = !(candidato.ciudad || candidato.provincia);
                },
            });
        }

        btnDetectar.addEventListener('click', function () {
            detectarUbicacion(estadoDetectar, function (loc, lat, lon) {
                candidato = loc;
                mapaInstancia.setView([lat, lon], modoModal === 'direccion' ? 17 : 13);
                ubicarMarcador(lat, lon, false);
                btnConfirmar.disabled = !(loc.ciudad || loc.provincia);
            });
        });

        btnConfirmar.addEventListener('click', function () {
            if (!candidato) return;
            onConfirmarModal(candidato);
            cerrarModalUbicacion();
        });

        // Enganchado a abrirModalUbicacion: cada vez que se abre el modal
        // (desde cualquier página) hay que repintar "recientes" acorde al
        // modo con el que se abrió esta vez.
        window.addEventListener('lc-ubicacion-modal-abierto', actualizarRecientesSegunModo);
    }

    // API pública minima para que OTRAS páginas (ej. el buscador del home,
    // inicio.html) lean la misma ubicación que usa el botón del navbar, sin
    // duplicar el parseo de la cookie ni reimplementar el modal del mapa.
    window.LaColmenaUbicacion = {
        obtenerActual: obtenerUbicacionActual,
        etiqueta: etiquetaUbicacion,
        abrirModal: abrirModalUbicacion,
    };
})();
