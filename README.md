# bartola-oficina

Oficina de Bartola Beauty: estado, pendientes, manual de marca y memoria de MKT de Flor y Yeyo.

- Página: https://jehiel1311.github.io/bartola-oficina/
- Los datos salen del TABLERO de Drive (Bartola Beauty / TABLERO — Bartola Beauty). Si algo no coincide, manda Drive.
- `datos.json` está cifrado con la contraseña de la Oficina (la tiene Yeyo). La contraseña no está en este repo.
- Diseño (31/10/2026): propuesta visual de Chaty integrada por Claudia y aprobada por Yeyo. Menú lateral (Inicio, Pendientes, Manual de marca, Memoria MKT, Vistas previas, Accesos), vista Todo · Flor · Yeyo con colores por persona según la columna Decide, Copiar link y metadatos de actualización.

## Archivos

- `index.html`: la página.
- `datos.json`: datos cifrados (TABLERO + accesos + manual + memoria + avisos + propuestas + metadatos).
- `herramientas/generar.py`: arma `datos.json`.
- `herramientas/enlaces.json`, `manual.json`, `memoria.json`: contenido fijo que se cifra junto con el TABLERO. Salen de documentos de Drive.
- `LOGO Color.png`, `LOGO Blanco.png`, `favicon.png`: logos oficiales.
- `avatar-flor.png`, `avatar-yeyo.png`: avatares (se usan como máscara y toman el color de cada persona).

## Actualizar los datos

1. Exportar el TABLERO como CSV.
2. `OFICINA_CLAVE='...' python3 herramientas/generar.py tablero.csv [--aviso "..."] [--propuesta "..."]`
3. Subir solo `datos.json`.

`--listar-propuestas` muestra las propuestas actuales; `--quitar-propuesta N` saca una.
La tarea diaria (Cowork) sube solo `datos.json`; el diseño se cambia en chat con Claudia, con vista previa y aprobación de Yeyo.

Lo actualiza y publica Claudia.
