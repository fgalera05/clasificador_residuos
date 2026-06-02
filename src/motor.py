# Asegurar que el parche de compatibilidad se aplique antes de importar experta
from . import compat

from experta import KnowledgeEngine, Rule, Fact, MATCH, AS, NOT

# Hechos para el motor de reglas de experta
class Residuo(Fact):
    """
    Hecho de entrada: representa el residuo a clasificar y su estado físico.
    """
    pass


class Clasificado(Fact):
    """
    Hecho intermedio: representa el resultado de la inferencia lógica y su justificación.
    """
    pass


class Clasificacion(Fact):
    """
    Hecho de salida: generado por el motor luego de la inferencia.
    """
    pass


class ClasificadorBase(KnowledgeEngine):
    """
    Base del motor de inferencia con reglas lógicas declarativas 
    para evaluar el estado físico del residuo (limpio, seco, roto).
    """

    # Regla 1: Papel o cartón que esté sucio o húmedo
    @Rule(
        AS.r << Residuo(tipo='papel', limpio=False) |
        AS.r << Residuo(tipo='papel', seco=False) |
        AS.r << Residuo(tipo='carton', limpio=False) |
        AS.r << Residuo(tipo='carton', seco=False),
        salience=10
    )
    def regla_papel_sucio(self, r):
        estado_detalle = []
        if not r.get('limpio', True):
            estado_detalle.append("está sucio/con grasa")
        if not r.get('seco', True):
            estado_detalle.append("está húmedo")
        detalle = " y ".join(estado_detalle)
        
        self.declare(Clasificado(
            tipo='papel_no_reciclable',
            explicacion=f"Se reclasificó '{r['tipo']}' a 'papel no reciclable' porque {detalle}. El papel y cartón mojados o con grasa/comida contaminan el lote y no pueden ser reciclados."
        ))

    # Regla 2: Vidrio que esté roto
    @Rule(
        AS.r << Residuo(tipo='vidrio', roto=True),
        salience=10
    )
    def regla_vidrio_roto(self, r):
        self.declare(Clasificado(
            tipo='vidrio_no_reciclable',
            explicacion="Se reclasificó a 'vidrio no reciclable' porque está roto. El vidrio roto es extremadamente peligroso para los operarios de recolección y debe desecharse de manera segura en basura común (bien envuelto)."
        ))

    # Regla 3: Plásticos que estén sucios o húmedos (PET, bolsas y rígidos)
    @Rule(
        AS.r << Residuo(tipo='plastico_pet', limpio=False) |
        AS.r << Residuo(tipo='plastico_pet', seco=False) |
        AS.r << Residuo(tipo='plastico_bolsa', limpio=False) |
        AS.r << Residuo(tipo='plastico_bolsa', seco=False) |
        AS.r << Residuo(tipo='plastico_decoracion', limpio=False) |
        AS.r << Residuo(tipo='plastico_decoracion', seco=False),
        salience=10
    )
    def regla_plastico_sucio(self, r):
        estado_detalle = []
        if not r.get('limpio', True):
            estado_detalle.append("está sucio/con grasa")
        if not r.get('seco', True):
            estado_detalle.append("está húmedo")
        detalle = " y ".join(estado_detalle)
        
        self.declare(Clasificado(
            tipo='reciclable_sucio',
            explicacion=f"Se reclasificó '{r['tipo']}' a 'no apto (sucio/húmedo)' porque {detalle}. Los plásticos deben estar completamente limpios y secos para poder reciclarse. De lo contrario, deben desecharse como basura común."
        ))

    # Regla 5: Envase de tetrabrik sucio o húmedo
    @Rule(
        AS.r << Residuo(tipo='tetrabrik', limpio=False) |
        AS.r << Residuo(tipo='tetrabrik', seco=False),
        salience=10
    )
    def regla_tetrabrik_sucio(self, r):
        estado_detalle = []
        if not r.get('limpio', True):
            estado_detalle.append("está sucio")
        if not r.get('seco', True):
            estado_detalle.append("está húmedo")
        detalle = " y ".join(estado_detalle)
        
        self.declare(Clasificado(
            tipo='reciclable_sucio',
            explicacion=f"Se reclasificó 'tetrabrik' a 'no apto (sucio/húmedo)' porque {detalle}. Los envases multicapa deben estar enjuagados y secos para evitar olores y bacterias en el circuito de reciclaje."
        ))

    # Regla 6: Latas de metal sucias
    @Rule(
        AS.r << Residuo(tipo='metal_lata', limpio=False),
        salience=10
    )
    def regla_metal_sucio(self, r):
        self.declare(Clasificado(
            tipo='reciclable_sucio',
            explicacion="Se reclasificó a 'no apto (sucio/húmedo)' porque está sucio. Las latas de metal deben enjuagarse para eliminar restos orgánicos antes de descartarse en el contenedor de reciclables."
        ))

    # Regla 4: Caso por defecto
    @Rule(
        AS.r << Residuo(tipo=MATCH.t),
        NOT(Clasificado()),
        salience=-10
    )
    def regla_por_defecto(self, r, t):
        # Si el residuo es de tipo especial (peligroso, electrónico, etc.), se aclara que mantiene su canal especial.
        es_especial = t in ['pila_bateria', 'bateria_auto', 'medicamento', 'aceite_cocina',
                            'aceite_motor', 'electronico', 'bombilla', 'bombilla_led',
                            'pintura_solvente', 'plastico_pvc']
        estado_detalle = []
        if not r.get('limpio', True):
            estado_detalle.append("sucio")
        if not r.get('seco', True):
            estado_detalle.append("húmedo")
        if r.get('roto', False):
            estado_detalle.append("roto")

        if es_especial:
            if estado_detalle:
                detalle = " e ".join(estado_detalle) if "sucio" in estado_detalle else " y ".join(estado_detalle)
                explicacion = f"Aunque el residuo está {detalle}, mantiene su clasificación especial de '{t}' y debe ser descartado únicamente en su contenedor específico por su alta peligrosidad."
            else:
                explicacion = f"Se clasificó como '{t}'. Debe ser descartado en su punto de recolección especial."
        else:
            if estado_detalle:
                detalle = " e ".join(estado_detalle) if "sucio" in estado_detalle else " y ".join(estado_detalle)
                explicacion = f"Se clasificó directamente como '{t}' (el estado {detalle} no altera su circuito de descarte en este material)."
            else:
                explicacion = "Se clasificó directamente según el material identificado en la base de conocimientos."

        self.declare(Clasificado(
            tipo=t,
            explicacion=explicacion
        ))


def crear_metodo_regla(tipo: str, datos: dict):
    """
    Genera un método de regla experta para un tipo de residuo,
    evaluando ahora sobre el hecho intermedio Clasificado.
    """
    def metodo(self, _datos=datos):
        self.declare(Clasificacion(
            categoria       = _datos['categoria'],
            subcategoria    = _datos['subcategoria'],
            contenedor      = _datos['contenedor'],
            instrucciones   = _datos['instrucciones'],
            errores_comunes = _datos['errores_comunes'],
            impacto         = _datos['impacto'],
            urgencia        = _datos['urgencia'],
        ))

    metodo.__name__ = f'regla_{tipo}'
    metodo_con_regla = Rule(Clasificado(tipo=tipo))(metodo)
    return metodo_con_regla


def construir_motor(reglas_dict: dict):
    """
    Construye dinámicamente una clase KnowledgeEngine
    que hereda de ClasificadorBase con una @Rule por cada tipo de residuo en el CSV.
    """
    atributos = {}
    for tipo, datos in reglas_dict.items():
        nombre_metodo = f'regla_{tipo}'
        atributos[nombre_metodo] = crear_metodo_regla(tipo, datos)

    ClasificadorDinamico = type(
        'ClasificadorDinamico',
        (ClasificadorBase,),
        atributos
    )
    return ClasificadorDinamico


def normalizar(texto: str) -> str:
    texto = texto.lower().strip()
    for src, dst in [("á","a"),("é","e"),("í","i"),("ó","o"),("ú","u"),
                     ("à","a"),("è","e"),("ì","i"),("ò","o"),("ù","u"),
                     ("ñ","n"),("ä","a"),("ë","e"),("ï","i"),("ö","o"),("ü","u")]:
        texto = texto.replace(src, dst)
    return texto


import re

def pattern_para_palabra(word: str) -> str:
    """
    Retorna un patrón regex para una palabra que acepta tanto singular como plural en español.
    """
    if not word:
        return ""
    # Si termina en "ces", ej. "lapices" -> lapi(z|ces)
    if word.endswith('ces'):
        base = re.escape(word[:-3])
        return rf'{base}(z|ces)'
    # Si termina en "es" y la letra anterior es una consonante de plural común (l, r, n, d) -> ej. "papeles" -> papel(es)?
    elif word.endswith('es') and len(word) > 2 and word[-3] in ('l', 'r', 'n', 'd'):
        base = re.escape(word[:-2])
        return rf'{base}(es)?'
    # Si termina en "s" y la letra anterior es una vocal -> ej. "juguetes" -> juguete, "botellas" -> botella
    elif word.endswith('s') and len(word) > 1 and word[-2] in ('a', 'e', 'i', 'o', 'u'):
        base = re.escape(word[:-1])
        return rf'{base}s?'
    # Si es singular terminando en 'z' -> ej. "lapiz" -> lapi(z|ces)
    elif word.endswith('z'):
        base = re.escape(word[:-1])
        return rf'{base}(z|ces)'
    # Si es singular terminando en vocal -> ej. "juguete" -> juguetes?
    elif word[-1] in ('a', 'e', 'i', 'o', 'u'):
        return rf'{re.escape(word)}s?'
    # Si es singular terminando en consonante común -> ej. "papel" -> papel(es)?
    elif word[-1] in ('l', 'r', 'n', 'd'):
        return rf'{re.escape(word)}(es)?'
    else:
        return re.escape(word)

def coincide_keyword(kw: str, texto_normalizado: str) -> bool:
    """
    Verifica si una keyword coincide con el texto normalizado,
    respetando límites de palabra e incluyendo plurales y singulares
    flexibles en español para cada palabra del término.
    """
    kw_norm = normalizar(kw)
    if not kw_norm:
        return False
    
    palabras = kw_norm.split()
    patrones_palabras = [pattern_para_palabra(p) for p in palabras if p]
    if not patrones_palabras:
        return False
    
    # Unir las palabras con límites de palabra a los extremos y espacios intermedios
    pattern = rf'\b' + r'\s+'.join(patrones_palabras) + rf'\b'
    return bool(re.search(pattern, texto_normalizado))


def detectar_tipo(texto_usuario: str, keywords_dict: dict, ambiguos_dict: dict) -> str:
    """
    Detecta el tipo de residuo evaluando keywords
    de mayor a menor longitud (más específicas primero).
    """
    texto = normalizar(texto_usuario)

    # Ordenar todas las keywords por longitud descendente
    todas = []
    for tipo, kws in keywords_dict.items():
        for kw in kws:
            todas.append((len(kw), tipo, kw))
    todas.sort(reverse=True)

    for _, tipo, kw in todas:
        if coincide_keyword(kw, texto):
            return tipo

    # Verificar términos ambiguos
    for termino in ambiguos_dict:
        if coincide_keyword(termino, texto):
            return f"ambiguo:{termino}"

    return "desconocido"


def obtener_regla(tipo: str, clasificador_dinamico, reglas_dict: dict, limpio: bool = True, seco: bool = True, roto: bool = False) -> dict:
    """
    Ejecuta el motor de reglas experta pasando variables de estado físicas y retorna el
    diccionario de la regla resultante enriquecido con la justificación del razonamiento.
    """
    if clasificador_dinamico is None:
        fallback = reglas_dict.get(tipo, reglas_dict.get("desconocido", {}))
        fallback["_final_tipo"] = tipo
        fallback["_explicacion"] = "Clasificación de fallback (motor no disponible)."
        return fallback

    motor = clasificador_dinamico()
    motor.reset()
    # Declaramos el hecho de entrada con el tipo detectado y las variables de estado físico
    motor.declare(Residuo(tipo=tipo, limpio=limpio, seco=seco, roto=roto))
    motor.run()

    # Buscamos el tipo final inferido y la explicación del razonamiento
    tipo_final = tipo
    explicacion = ""
    for fact in motor.facts.values():
        if isinstance(fact, Clasificado):
            tipo_final = fact.get("tipo", tipo)
            explicacion = fact.get("explicacion", "")

    # Buscamos la clasificación final generada
    for fact in motor.facts.values():
        if isinstance(fact, Clasificacion):
            res = dict(fact)
            if "instrucciones" in res:
                res["instrucciones"] = list(res["instrucciones"])
            if "errores_comunes" in res:
                res["errores_comunes"] = list(res["errores_comunes"])
            # Guardamos la inferencia final y explicación de forma retrocompatible
            res["_final_tipo"] = tipo_final
            res["_explicacion"] = explicacion
            return res

    # Si por alguna razón no se dispararon reglas de clasificación, usamos el diccionario estático
    fallback = reglas_dict.get(tipo_final, reglas_dict.get("desconocido", {}))
    fallback["_final_tipo"] = tipo_final
    fallback["_explicacion"] = explicacion
    return fallback
