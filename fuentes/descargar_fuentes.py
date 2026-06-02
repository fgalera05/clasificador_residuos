"""
Descarga todas las fuentes normativas y técnicas del sistema EcoAsistente.
Genera también FUENTES.md con el índice completo.
Ejecutar desde la raíz del proyecto: venv/bin/python fuentes/descargar_fuentes.py
"""
import urllib.request
import urllib.error
import os
import sys
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'es-AR,es;q=0.9,en;q=0.8',
}

# ─────────────────────────────────────────────────────────────────────────────
# CATÁLOGO DE FUENTES
# Cada entrada: (categoria, subcategoria, nombre_archivo, url, descripcion, nota)
# ─────────────────────────────────────────────────────────────────────────────
FUENTES = [

    # ── LEYES NACIONALES (InfoLEG) ────────────────────────────────────────────
    (
        'leyes_nacionales', 'html',
        'ley_25916_residuos_domiciliarios.html',
        'https://servicios.infoleg.gob.ar/infolegInternet/anexos/95000-99999/98327/norma.htm',
        'Ley Nacional 25.916 — Gestión de Residuos Domiciliarios (2004)',
        'Presupuestos mínimos para manejo integral de RSU. Sancionada 04/08/2004.',
    ),
    (
        'leyes_nacionales', 'html',
        'ley_26184_pilas_baterias.html',
        'https://servicios.infoleg.gob.ar/infolegInternet/anexos/120000-124999/123408/norma.htm',
        'Ley Nacional 26.184 — Pilas y Baterías (2006)',
        'Prohíbe comercialización de pilas que superen límites de Hg, Cd, Pb. Sancionada 29/11/2006.',
    ),
    (
        'leyes_nacionales', 'html',
        'ley_26184_texto_actualizado.html',
        'https://servicios.infoleg.gob.ar/infolegInternet/anexos/120000-124999/123408/texact.htm',
        'Ley Nacional 26.184 — Texto actualizado consolidado',
        'Versión consolidada con modificaciones posteriores.',
    ),
    (
        'leyes_nacionales', 'html',
        'ley_23922_convenio_basilea.html',
        'https://servicios.infoleg.gob.ar/infolegInternet/anexos/0-4999/322/norma.htm',
        'Ley Nacional 23.922 — Aprobación Convenio de Basilea (1991)',
        'Ratifica el Convenio sobre movimientos transfronterizos de desechos peligrosos.',
    ),
    (
        'leyes_nacionales', 'html',
        'ley_26011_convenio_estocolmo.html',
        'https://servicios.infoleg.gob.ar/infolegInternet/anexos/100000-104999/102996/norma.htm',
        'Ley Nacional 26.011 — Aprobación Convenio de Estocolmo (2005)',
        'Ratifica el Convenio sobre Contaminantes Orgánicos Persistentes (dioxinas, furanos, PCBs).',
    ),

    # ── LEYES Y DECRETOS CABA ─────────────────────────────────────────────────
    (
        'leyes_caba', 'html',
        'ley_caba_1854_basura_cero_boletin.html',
        'https://boletinoficial.buenosaires.gob.ar/normativaba/norma/81508',
        'Ley CABA 1854/2005 — "Basura Cero" (Boletín Oficial CABA)',
        'Gestión integral de RSU en CABA. Principio de reducción progresiva en rellenos sanitarios.',
    ),
    (
        'leyes_caba', 'pdf',
        'ley_caba_1854_consolidada_2023.pdf',
        'https://buenosaires.gob.ar/sites/default/files/2024-02/Ley-1854-consolidada-2023.pdf',
        'Ley CABA 1854/2005 — Texto consolidado 2023 (PDF oficial GCBA)',
        'Versión actualizada con todas las modificaciones hasta 2023.',
    ),
    (
        'leyes_caba', 'html',
        'decreto_gcba_639_07_boletin.html',
        'https://boletinoficial.buenosaires.gob.ar/normativaba/norma/98735',
        'Decreto GCBA 639/07 — Reglamentación Ley 1854 (Boletín Oficial CABA)',
        'Procedimientos de separación en origen, recolección diferenciada y tratamiento.',
    ),
    (
        'leyes_caba', 'pdf',
        'decreto_gcba_639_07.pdf',
        'https://buenosaires.gob.ar/areas/med_ambiente/basura_cero/archivos/decreto_n639.pdf',
        'Decreto GCBA 639/07 — PDF oficial',
        'Texto completo del decreto reglamentario de la Ley 1854.',
    ),
    (
        'leyes_caba', 'html',
        'ley_caba_5991_pilas_baterias.html',
        'https://boletinoficial.buenosaires.gob.ar/normativaba/norma/425139',
        'Ley CABA 5991/2018 — Gestión Ambiental de Pilas en Desuso',
        'Ley porteña vigente sobre pilas. (Nota: la cita "Ley 2.810" que circula es incorrecta.)',
    ),

    # ── PROGRAMA PUNTOS VERDES GCBA ───────────────────────────────────────────
    (
        'leyes_caba', 'html',
        'gcba_puntos_verdes_mapa.html',
        'https://buenosaires.gob.ar/espaciopublicoehigieneurbana/ciudadlimpia/mapa-de-contenedores-y-puntos-verdes',
        'GCBA — Mapa de Contenedores y Puntos Verdes',
        'Página oficial del programa con mapa interactivo de puntos de reciclaje en CABA.',
    ),
    (
        'leyes_caba', 'html',
        'gcba_ba_recicla.html',
        'https://buenosaires.gob.ar/espaciopublicoehigieneurbana/ciudad-verde/ba-recicla',
        'GCBA — BA Recicla (programa integral de reciclaje)',
        'Información sobre separación en origen, materiales aceptados y puntos de entrega.',
    ),
    (
        'leyes_caba', 'html',
        'gcba_residuos_especiales_pilas.html',
        'https://buenosaires.gob.ar/residuos-especiales/pilas',
        'GCBA — Residuos Especiales: Pilas y Baterías',
        'Página oficial de GCBA sobre dónde depositar pilas y baterías en CABA.',
    ),

    # ── CONVENIOS INTERNACIONALES ─────────────────────────────────────────────
    (
        'convenios_internacionales', 'pdf',
        'convenio_estocolmo_2023_espanol.pdf',
        'https://www.pops.int/Portals/0/download.aspx?e=UNEP-POPS-COP-CONVTEXT-2023.Spanish.pdf',
        'Convenio de Estocolmo — Texto oficial 2023 en español (pops.int)',
        'Convenio sobre Contaminantes Orgánicos Persistentes. Aplica a dioxinas/furanos del PVC quemado.',
    ),
    (
        'convenios_internacionales', 'pdf',
        'convenio_basilea_espanol.pdf',
        'https://www.basel.int/portals/4/basel%20convention/docs/text/baselconventiontext-s.pdf',
        'Convenio de Basilea — Texto completo en español (basel.int)',
        'Convenio sobre movimientos transfronterizos de desechos peligrosos. Aplica a RAEE.',
    ),
    (
        'convenios_internacionales', 'pdf',
        'convenio_basilea_arg_2019.pdf',
        'https://www.argentina.gob.ar/sites/default/files/5.1_convenio_de_basilea_-_espanol_-_v._2019.pdf',
        'Convenio de Basilea — Versión argentina 2019 (argentina.gob.ar)',
        'Copia del convenio en el portal del gobierno argentino.',
    ),
    (
        'convenios_internacionales', 'pdf',
        'convenio_estocolmo_arg_2019.pdf',
        'https://www.argentina.gob.ar/sites/default/files/5.3_convenio_de_estocolmo_espanol_2019.pdf',
        'Convenio de Estocolmo — Versión argentina 2019 (argentina.gob.ar)',
        'Copia del convenio en el portal del gobierno argentino.',
    ),

    # ── INFORMES TÉCNICOS ─────────────────────────────────────────────────────
    (
        'informes_tecnicos', 'pdf',
        'inti_guia_pilas_baterias.pdf',
        'https://www.inti.gob.ar/assets/uploads/files/ambiente/Guia-de-gestion-integral-PILAS-y-BATERIAS-EN-DESUSO.pdf',
        'INTI — Guía de gestión integral de pilas y baterías en desuso',
        'Guía técnica del INTI sobre disposición y reciclaje de pilas. Aplica a regla pilas_especial.',
    ),
    (
        'informes_tecnicos', 'pdf',
        'ceamse_estudio_rsu_caba_2015.pdf',
        'https://www.ceamse.gov.ar/wp-content/uploads/2017/05/I.Final-ECRSU-CABA-FIUBA-2015-NOV-16.pdf',
        'CEAMSE/FIUBA — Estudio de Calidad de RSU de CABA 2015',
        'Composición y caracterización de residuos domiciliarios de CABA. Base para % de reciclables.',
    ),
    (
        'informes_tecnicos', 'pdf',
        'ceamse_estudio_rsu_2009.pdf',
        'https://www.ceamse.gov.ar/wp-content/uploads/2012/06/Informe-Final-ECRSU-2009.pdf',
        'CEAMSE — Estudio de Calidad de RSU 2009',
        'Estudio anterior de composición de residuos. Línea de base histórica.',
    ),
    (
        'informes_tecnicos', 'pdf',
        'global_ewaste_monitor_2024.pdf',
        'https://ewastemonitor.info/wp-content/uploads/2024/03/GEM_2024_18-03_web_page_per_page_web.pdf',
        'Global E-waste Monitor 2024 — UNEP/UNU/ITU (en inglés)',
        'Informe global de RAEE. 62 Mt/año. Aplica a regla raee_especial. Solo disponible en inglés.',
    ),
    (
        'informes_tecnicos', 'html',
        'ecoplas_codificacion_plasticos.html',
        'https://ecoplas.org.ar/identificacion-de-plasticos-para-su-reciclado/',
        'Ecoplas — Identificación de plásticos para reciclado (IRAM 13700)',
        'Explica el sistema de codificación IRAM 13700 (norma argentina de identificación plásticos). '
        'Nota: la norma se llama IRAM 13700, no 13600 como estaba citado originalmente.',
    ),
    (
        'informes_tecnicos', 'pdf',
        'ecoplas_boletin_codificacion.pdf',
        'http://ecoplas.org.ar/pdf/42.pdf',
        'Ecoplas — Boletín técnico sobre codificación de plásticos',
        'Boletín técnico de Ecoplas sobre el sistema IRAM 13700 de identificación de resinas.',
    ),
]

# ─────────────────────────────────────────────────────────────────────────────
# FUNCIONES DE DESCARGA
# ─────────────────────────────────────────────────────────────────────────────

def descargar(url: str, destino: str) -> tuple[bool, str]:
    """Descarga url a destino. Retorna (éxito, mensaje)."""
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            if len(data) < 500:
                return False, f'Respuesta muy pequeña ({len(data)} bytes) — posible error del servidor'
            with open(destino, 'wb') as f:
                f.write(data)
            return True, f'{len(data):,} bytes'
    except urllib.error.HTTPError as e:
        return False, f'HTTP {e.code}: {e.reason}'
    except urllib.error.URLError as e:
        return False, f'URL Error: {e.reason}'
    except Exception as e:
        return False, str(e)


def main():
    print('=' * 70)
    print('EcoAsistente CABA — Descarga de fuentes normativas y técnicas')
    print('=' * 70)

    resultados = []

    for categoria, tipo, nombre_archivo, url, descripcion, nota in FUENTES:
        carpeta = os.path.join(BASE_DIR, categoria)
        os.makedirs(carpeta, exist_ok=True)
        destino = os.path.join(carpeta, nombre_archivo)

        print(f'\n[{categoria}] {nombre_archivo}')
        print(f'  URL: {url[:80]}...' if len(url) > 80 else f'  URL: {url}')

        ok, msg = descargar(url, destino)
        estado = 'OK' if ok else 'FALLO'
        print(f'  {estado}: {msg}')

        resultados.append({
            'categoria': categoria,
            'tipo': tipo,
            'archivo': nombre_archivo,
            'url': url,
            'descripcion': descripcion,
            'nota': nota,
            'ok': ok,
            'msg': msg,
        })
        time.sleep(0.5)  # cortesía hacia los servidores

    # ── Generar FUENTES.md ────────────────────────────────────────────────────
    generar_md(resultados)

    # ── Resumen ───────────────────────────────────────────────────────────────
    ok_count = sum(1 for r in resultados if r['ok'])
    fail_count = len(resultados) - ok_count
    print(f'\n{"=" * 70}')
    print(f'Resultado: {ok_count} descargados correctamente, {fail_count} fallidos')
    if fail_count:
        print('Fallidos:')
        for r in resultados:
            if not r['ok']:
                print(f'  - {r["archivo"]}: {r["msg"]}')
    print(f'Índice generado en: {os.path.join(BASE_DIR, "FUENTES.md")}')


def generar_md(resultados: list):
    """Genera el archivo FUENTES.md con el índice completo."""
    categorias_orden = [
        ('leyes_nacionales', 'Leyes Nacionales'),
        ('leyes_caba', 'Leyes y Programas — Ciudad de Buenos Aires'),
        ('convenios_internacionales', 'Convenios Internacionales'),
        ('informes_tecnicos', 'Informes Técnicos y Guías'),
    ]

    lineas = [
        '# Fuentes normativas y técnicas — EcoAsistente CABA',
        '',
        'Índice de fuentes que respaldan las reglas del sistema experto.',
        'Generado automáticamente por `fuentes/descargar_fuentes.py`.',
        '',
        '> **Nota sobre dos correcciones aplicadas:**',
        '> - La norma argentina de identificación de plásticos es **IRAM 13700**, no IRAM 13600.',
        '> - La ley porteña de pilas es **Ley CABA 5991/2018**, no "Ley 2.810" (ese número no existe en el BO de CABA).',
        '> - El Decreto Nacional 2642/2014 no aparece en InfoLEG vinculado a la Ley 26.184; se eliminó de las citas.',
        '',
    ]

    for cat_key, cat_titulo in categorias_orden:
        items = [r for r in resultados if r['categoria'] == cat_key]
        if not items:
            continue
        lineas.append(f'## {cat_titulo}')
        lineas.append('')
        lineas.append('| Archivo local | Descripción | URL | Estado |')
        lineas.append('|---|---|---|---|')
        for r in items:
            icono = '' if r['ok'] else ''
            ruta_rel = f"{r['categoria']}/{r['archivo']}"
            url_corta = r['url'][:70] + '…' if len(r['url']) > 70 else r['url']
            lineas.append(
                f"| [{r['archivo']}]({ruta_rel}) "
                f"| {r['descripcion']} "
                f"| [{url_corta}]({r['url']}) "
                f"| {icono} {r['msg'] if not r['ok'] else 'OK'} |"
            )
        lineas.append('')
        # Notas de cada item
        for r in items:
            if r['nota']:
                lineas.append(f"**`{r['archivo']}`** — {r['nota']}")
                lineas.append('')

    lineas += [
        '---',
        '',
        '## Fuentes no descargables automáticamente',
        '',
        '### IRAM 13700 — Identificación de plásticos para reciclaje',
        'Las normas IRAM son documentos de pago. No hay PDF público oficial.',
        '- Compra/consulta: <https://catalogo.iram.org.ar/>',
        '- Descripción pública en Ecoplas: <https://ecoplas.org.ar/identificacion-de-plasticos-para-su-reciclado/>',
        '',
        '### InfoLEG — Leyes nacionales en HTML',
        'InfoLEG bloquea scraping directo desde curl/wget pero responde a requests con headers de navegador.',
        'Los archivos HTML en `leyes_nacionales/` fueron descargados con headers de navegador.',
        'URLs de ficha (con normas relacionadas):',
        '- Ley 25.916: <https://servicios.infoleg.gob.ar/infolegInternet/verNorma.do?id=98327>',
        '- Ley 26.184: <https://servicios.infoleg.gob.ar/infolegInternet/verNorma.do?id=123408>',
        '- Ley 23.922: <https://servicios.infoleg.gob.ar/infolegInternet/verNorma.do?id=322>',
        '- Ley 26.011: <https://servicios.infoleg.gob.ar/infolegInternet/verNorma.do?id=102996>',
        '',
        '### Dataset Puntos Verdes — Buenos Aires Data',
        'Los archivos CSV y GeoJSON ya están en la raíz del proyecto (`puntos_verdes.csv`, `puntos_verdes.geojson`).',
        '- Hub del dataset: <https://data.buenosaires.gob.ar/dataset/puntos-verdes>',
        '- Recurso GeoJSON: <https://data.buenosaires.gob.ar/dataset/puntos-verdes/resource/ac70efe5-6eae-4076-b2e6-c66a88c9c35a>',
        '',
    ]

    md_path = os.path.join(BASE_DIR, 'FUENTES.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lineas))


if __name__ == '__main__':
    main()
