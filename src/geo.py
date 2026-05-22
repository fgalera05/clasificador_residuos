import math
import pandas as pd

def haversine(lat1, lon1, lat2, lon2):
    """Calcula la distancia del círculo máximo entre dos puntos en km."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def puntos_cercanos(lat, lon, df_puntos_verdes, n=3):
    """Retorna los n puntos verdes más cercanos al punto (lat, lon)."""
    if df_puntos_verdes is None or df_puntos_verdes.empty:
        return []

    df = df_puntos_verdes.copy()
    col_lat = next((c for c in df.columns if "lat" in c.lower()), None)
    col_lon = next((c for c in df.columns if "lon" in c.lower() or "lng" in c.lower() or "long" in c.lower()), None)
    col_nom = next((c for c in df.columns if "nombre" in c.lower() or "name" in c.lower()), df.columns[0])
    col_dir = next((c for c in df.columns if "direcc" in c.lower() or "address" in c.lower()), None)

    if not col_lat or not col_lon:
        return []

    df = df.dropna(subset=[col_lat, col_lon]).copy()
    df["dist"] = df.apply(lambda r: haversine(lat, lon, r[col_lat], r[col_lon]), axis=1)
    cerca = df.nsmallest(n, "dist")

    resultado = []
    for _, row in cerca.iterrows():
        resultado.append({
            "nombre"   : row[col_nom],
            "direccion": row[col_dir] if col_dir else "—",
            "dist_km"  : round(row["dist"], 2),
            "lat"      : row[col_lat],
            "lon"      : row[col_lon],
        })
    return resultado
