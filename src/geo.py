import math
import pandas as pd

def haversine(lat1, lon1, lat2, lon2):
    """Calcula la distancia del círculo máximo entre dos puntos en km."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def puntos_cercanos(lat, lon, df_puntos_verdes, radio_km=0.3, minimo=2, tipos=None):
    """Retorna los puntos dentro del radio (km), expandiéndolo si hay menos de `minimo` resultados.

    Si se pasa `tipos` (lista de valores del campo 'tipo'), la expansión del radio garantiza
    al menos `minimo` puntos de esos tipos, aunque devuelve todos los puntos del radio final.
    """
    if df_puntos_verdes is None or df_puntos_verdes.empty:
        return []

    df = df_puntos_verdes.copy()
    col_lat  = next((c for c in df.columns if "lat" in c.lower()), None)
    col_lon  = next((c for c in df.columns if "lon" in c.lower() or "lng" in c.lower() or "long" in c.lower()), None)
    col_nom  = next((c for c in df.columns if "nombre" in c.lower() or "name" in c.lower()), df.columns[0])
    col_dir  = next((c for c in df.columns if "direcc" in c.lower() or "address" in c.lower()), None)
    col_tipo = next((c for c in df.columns if "tipo" in c.lower() or "type" in c.lower()), None)
    col_hor  = next((c for c in df.columns if "horario" in c.lower()), None)
    col_mat  = next((c for c in df.columns if "material" in c.lower()), None)

    if not col_lat or not col_lon:
        return []

    df = df.dropna(subset=[col_lat, col_lon]).copy()
    df["_dist"] = df.apply(lambda r: haversine(lat, lon, r[col_lat], r[col_lon]), axis=1)
    df_sorted = df.sort_values("_dist")

    # Subconjunto para calcular el mínimo: solo los tipos pedidos (o todos si no se filtra)
    df_ref = df_sorted[df_sorted[col_tipo].isin(tipos)] if (tipos and col_tipo) else df_sorted

    cerca = df_sorted[df_sorted["_dist"] <= radio_km]

    # Expandir radio hasta cubrir `minimo` puntos del tipo de referencia
    cerca_ref = cerca[cerca[col_tipo].isin(tipos)] if (tipos and col_tipo) else cerca
    if len(cerca_ref) < minimo and len(df_ref) >= minimo:
        radio_km = float(df_ref.iloc[minimo - 1]["_dist"])
        cerca = df_sorted[df_sorted["_dist"] <= radio_km]

    return [
        {
            "nombre"    : row[col_nom],
            "tipo"      : row[col_tipo] if col_tipo else "—",
            "direccion" : row[col_dir]  if col_dir  else "—",
            "dist_km"   : round(row["_dist"], 3),
            "lat"       : row[col_lat],
            "lon"       : row[col_lon],
            "horario"   : str(row[col_hor]) if col_hor and pd.notna(row[col_hor]) else "",
            "materiales": str(row[col_mat]) if col_mat and pd.notna(row[col_mat]) else "",
        }
        for _, row in cerca.iterrows()
    ]
