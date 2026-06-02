# Fuentes normativas y técnicas — EcoAsistente CABA

Índice de fuentes que respaldan las reglas del sistema experto de reciclaje.
Cada regla en `expert_system/rules.py` cita al menos una de estas fuentes.

> ### Correcciones aplicadas a citas originales
> Durante la verificación de URLs se detectaron tres citas incorrectas que fueron corregidas en el código:
>
> | Cita original (incorrecta) | Cita corregida | Motivo |
> |---|---|---|
> | IRAM 13600:2020 | **IRAM 13700** | El número correcto de la norma argentina de codificación de plásticos es 13700, no 13600. No existe norma IRAM 13600 verificable. |
> | Ley CABA 2.810 | **Ley CABA 5.991/2018** | La numeración 2.810 no existe en el Boletín Oficial de CABA. La ley porteña vigente sobre pilas es la 5991/2018. |
> | Decreto Nacional 2642/2014 | **eliminado** | No aparece en InfoLEG vinculado a la Ley 26.184. No verificable como norma existente. |

---

## 1. Leyes Nacionales

| Archivo local | Descripción | URL canónica |
|---|---|---|
| [`ley_25916_residuos_domiciliarios.html`](leyes_nacionales/ley_25916_residuos_domiciliarios.html) | Ley 25.916 — Gestión de Residuos Domiciliarios (2004) | <https://www.argentina.gob.ar/normativa/nacional/ley-25916-98327/texto> |
| [`ley_26184_pilas_baterias.html`](leyes_nacionales/ley_26184_pilas_baterias.html) | Ley 26.184 — Pilas y Baterías (2006) | <https://www.argentina.gob.ar/normativa/nacional/ley-26184-123408/texto> |
| [`ley_26184_texto_actualizado.html`](leyes_nacionales/ley_26184_texto_actualizado.html) | Ley 26.184 — Texto consolidado con modificaciones | <https://servicios.infoleg.gob.ar/infolegInternet/anexos/120000-124999/123408/texact.htm> |
| [`ley_23922_convenio_basilea.html`](leyes_nacionales/ley_23922_convenio_basilea.html) | Ley 23.922 — Aprobación Convenio de Basilea (1991) | <https://www.argentina.gob.ar/normativa/nacional/ley-23922-322/texto> |
| [`ley_26011_convenio_estocolmo.html`](leyes_nacionales/ley_26011_convenio_estocolmo.html) | Ley 26.011 — Aprobación Convenio de Estocolmo (2005) | <https://www.argentina.gob.ar/normativa/nacional/ley-26011-102996/texto> |

**Nota técnica:** InfoLEG (`servicios.infoleg.gob.ar`) bloquea acceso automatizado con HTTP 403. Los textos legales fueron descargados desde el portal `argentina.gob.ar/normativa` (misma base de datos SAIJ/InfoLEG, sin restricciones de automatización). Las fichas con normas relacionadas siguen disponibles manualmente en InfoLEG:
- Ley 25.916: <https://servicios.infoleg.gob.ar/infolegInternet/verNorma.do?id=98327>
- Ley 26.184: <https://servicios.infoleg.gob.ar/infolegInternet/verNorma.do?id=123408>
- Ley 23.922: <https://servicios.infoleg.gob.ar/infolegInternet/verNorma.do?id=322>
- Ley 26.011: <https://servicios.infoleg.gob.ar/infolegInternet/verNorma.do?id=102996>

---

## 2. Leyes, Decretos y Programas — Ciudad de Buenos Aires (GCBA)

| Archivo local | Descripción | URL canónica |
|---|---|---|
| [`ley_caba_1854_basura_cero_boletin.html`](leyes_caba/ley_caba_1854_basura_cero_boletin.html) | Ley CABA 1854/2005 — "Basura Cero" (Boletín Oficial CABA, consolidado 2024) | <https://boletinoficial.buenosaires.gob.ar/normativaba/norma/81508> |
| [`ley_caba_1854_cedom.html`](leyes_caba/ley_caba_1854_cedom.html) | Ley CABA 1854/2005 — Texto consolidado (Centro de Documentación GCBA) | <https://www.cedom.gob.ar/legislacion/normas/leyes/RepoLeyes/ley1854.html> |
| [`decreto_gcba_639_07_boletin.html`](leyes_caba/decreto_gcba_639_07_boletin.html) | Decreto GCBA 639/07 — Reglamentación Ley 1854 (Boletín Oficial CABA) | <https://boletinoficial.buenosaires.gob.ar/normativaba/norma/98735> |
| [`decreto_gcba_639_07.pdf`](leyes_caba/decreto_gcba_639_07.pdf) | Decreto GCBA 639/07 — PDF oficial GCBA (144 KB) | <https://buenosaires.gob.ar/areas/med_ambiente/basura_cero/archivos/decreto_n639.pdf> |
| [`ley_caba_5991_pilas_baterias.html`](leyes_caba/ley_caba_5991_pilas_baterias.html) | Ley CABA 5.991/2018 — Gestión Ambiental de Pilas en Desuso | <https://boletinoficial.buenosaires.gob.ar/normativaba/norma/425139> |
| [`gcba_puntos_verdes_mapa.html`](leyes_caba/gcba_puntos_verdes_mapa.html) | GCBA — Mapa de Contenedores y Puntos Verdes (programa oficial) | <https://buenosaires.gob.ar/espaciopublicoehigieneurbana/ciudadlimpia/mapa-de-contenedores-y-puntos-verdes> |
| [`gcba_ba_recicla.html`](leyes_caba/gcba_ba_recicla.html) | GCBA — BA Recicla (separación en origen, materiales y puntos) | <https://buenosaires.gob.ar/espaciopublicoehigieneurbana/ciudad-verde/ba-recicla> |
| [`gcba_residuos_especiales_pilas.html`](leyes_caba/gcba_residuos_especiales_pilas.html) | GCBA — Dónde depositar pilas y baterías en CABA | <https://buenosaires.gob.ar/residuos-especiales/pilas> |

### Dataset de Puntos Verdes (Buenos Aires Data)
Los archivos del dataset ya están en la raíz del proyecto; no se duplican aquí.

| Recurso | URL |
|---|---|
| Hub del dataset | <https://data.buenosaires.gob.ar/dataset/puntos-verdes> |
| Recurso GeoJSON | <https://data.buenosaires.gob.ar/dataset/puntos-verdes/resource/ac70efe5-6eae-4076-b2e6-c66a88c9c35a> |
| Archivos en el proyecto | `../puntos_verdes.csv`, `../puntos_verdes.geojson`, `../puntos_verdes/` (shapefile) |

---

## 3. Convenios Internacionales

| Archivo local | Descripción | URL canónica |
|---|---|---|
| [`convenio_estocolmo_2023_espanol.pdf`](convenios_internacionales/convenio_estocolmo_2023_espanol.pdf) | Convenio de Estocolmo — Texto oficial 2023 en español (699 KB, pops.int) | <https://www.pops.int/Portals/0/download.aspx?e=UNEP-POPS-COP-CONVTEXT-2023.Spanish.pdf> |
| [`convenio_estocolmo_arg_2019.pdf`](convenios_internacionales/convenio_estocolmo_arg_2019.pdf) | Convenio de Estocolmo — Versión argentina 2019 (502 KB, argentina.gob.ar) | <https://www.argentina.gob.ar/sites/default/files/5.3_convenio_de_estocolmo_espanol_2019.pdf> |
| [`convenio_basilea_espanol.pdf`](convenios_internacionales/convenio_basilea_espanol.pdf) | Convenio de Basilea — Texto completo en español (544 KB, basel.int) | <https://www.basel.int/portals/4/basel%20convention/docs/text/baselconventiontext-s.pdf> |
| [`convenio_basilea_arg_2019.pdf`](convenios_internacionales/convenio_basilea_arg_2019.pdf) | Convenio de Basilea — Versión argentina 2019 (2,4 MB, argentina.gob.ar) | <https://www.argentina.gob.ar/sites/default/files/5.1_convenio_de_basilea_-_espanol_-_v._2019.pdf> |

**Uso en el sistema:**
- Convenio de Estocolmo → regla `plastico_pvc` (dioxinas/furanos del PVC quemado son COPs regulados por este convenio, que Argentina ratificó con la Ley 26.011)
- Convenio de Basilea → regla `raee_especial` (RAEE son residuos peligrosos sujetos a control de movimientos transfronterizos, ratificado con Ley 23.922)

---

## 4. Informes Técnicos y Guías

| Archivo local | Descripción | URL canónica | Idioma |
|---|---|---|---|
| [`inti_guia_pilas_baterias.pdf`](informes_tecnicos/inti_guia_pilas_baterias.pdf) | INTI — Guía de gestión integral de pilas y baterías en desuso (2,4 MB) | <https://www.inti.gob.ar/assets/uploads/files/ambiente/Guia-de-gestion-integral-PILAS-y-BATERIAS-EN-DESUSO.pdf> | ES |
| [`ceamse_estudio_rsu_caba_2015_fiuba.pdf`](informes_tecnicos/ceamse_estudio_rsu_caba_2015_fiuba.pdf) | CEAMSE/FIUBA/GCBA — Estudio de Calidad de RSU de CABA 2015, Informe Final (2,9 MB) | <https://cms.fi.uba.ar/uploads/Estudio_calidad_RSU_version_web_c3a19f9472.pdf> | ES |
| [`global_ewaste_monitor_2024.pdf`](informes_tecnicos/global_ewaste_monitor_2024.pdf) | Global E-waste Monitor 2024 — UNEP/UNU/ITU (8,2 MB, 62 Mt/año de RAEE) | <https://ewastemonitor.info/wp-content/uploads/2024/03/GEM_2024_18-03_web_page_per_page_web.pdf> | EN |
| [`ecoplas_codificacion_plasticos.html`](informes_tecnicos/ecoplas_codificacion_plasticos.html) | Ecoplas — Codificación IRAM 13700 para identificación de plásticos | <https://ecoplas.org.ar/identificacion-de-plasticos-para-su-reciclado/> | ES |
| [`ecoplas_boletin_codificacion.pdf`](informes_tecnicos/ecoplas_boletin_codificacion.pdf) | Ecoplas — Boletín técnico sobre codificación IRAM 13700 (490 KB) | <http://ecoplas.org.ar/pdf/42.pdf> | ES |

**Notas:**
- `ceamse_estudio_rsu_caba_2015_fiuba.pdf`: la URL original en `ceamse.gov.ar` devolvió 404 (URL caída). Se descargó la copia idéntica alojada en el servidor de FIUBA (Instituto de Ingeniería Sanitaria, UBA), que co-produjo el informe junto con CEAMSE y el GCBA.
- `global_ewaste_monitor_2024.pdf`: disponible solo en inglés. No existe versión oficial en español del informe 2024.
- CEAMSE Estudio RSU 2009: URL original caída (`ceamse.gov.ar/wp-content/uploads/2012/06/Informe-Final-ECRSU-2009.pdf`), no se encontró copia alternativa verificable. Se reemplaza en las citas por el estudio 2015, que es más reciente y completo.

---

## 5. Fuentes de consulta — no descargables automáticamente

### IRAM 13700 — Identificación de plásticos para reciclaje
Las normas IRAM son documentos de pago, sin PDF público oficial.
- Compra: <https://catalogo.iram.org.ar/>
- Descripción técnica pública (Ecoplas): <https://ecoplas.org.ar/identificacion-de-plasticos-para-su-reciclado/>

### ASTM D7611 — Códigos SPI de resinas plásticas
Norma de pago de la American Society for Testing and Materials.
- Referencia: <https://www.astm.org/d7611_d7611m-21.html>

### Portal temático Argentina.gob.ar — Pilas y baterías
- <https://www.argentina.gob.ar/interior/ambiente/control/productos-quimicos/metales-pesados/pilas-y-baterias>

---

## Resumen de archivos descargados

| Categoría | Cant. archivos | Tamaño aprox. |
|---|---|---|
| Leyes nacionales | 5 HTML | ~462 KB |
| Leyes y programas CABA | 8 (6 HTML + 2 PDF) | ~519 KB |
| Convenios internacionales | 4 PDF | ~4,2 MB |
| Informes técnicos | 3 PDF + 2 HTML | ~14,3 MB |
| **Total** | **22 archivos** | **~19,5 MB** |
