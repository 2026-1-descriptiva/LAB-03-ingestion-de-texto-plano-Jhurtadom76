"""
Escriba el codigo que ejecute la accion solicitada en cada pregunta.
"""

# pylint: disable=import-outside-toplevel


def pregunta_01():
    """
    Construya y retorne un dataframe de Pandas a partir del archivo
    'files/input/clusters_report.txt'. Los requierimientos son los siguientes:

    - El dataframe tiene la misma estructura que el archivo original.
    - Los nombres de las columnas deben ser en minusculas, reemplazando los
      espacios por guiones bajos.
    - Las palabras clave deben estar separadas por coma y con un solo
      espacio entre palabra y palabra.


    """
    import os
    import re
    import pandas as pd

    # Ruta absoluta al archivo de texto (subimos un nivel desde /homework)
    filepath = os.path.join(
        os.path.dirname(__file__), "..", "files", "input", "clusters_report.txt"
    )

    # Acumuladores: lista de clusters y un cluster "en construcción"
    clusters = []
    cluster_actual = None      # dict con cluster, cantidad, porcentaje
    keywords_actuales = []     # lista de strings (cada línea de palabras clave)

    # Regex para detectar la PRIMERA línea de un cluster.
    # Formato: "   N   COUNT   PCT,DEC %      keyword1, keyword2,"
    # Grupos: (1)=N, (2)=COUNT, (3)=PCT, (4)=DEC, (5)=resto de la línea (keywords)
    patron_cluster = re.compile(r"^\s+(\d+)\s+(\d+)\s+(\d+),(\d+)\s*%\s*(.*)")

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            # Quitamos saltos de línea (CRLF o LF). Mantenemos espacios al inicio
            # porque nos sirven para detectar la primera línea de cada cluster.
            line = line.rstrip("\n").rstrip("\r")

            # 1) ¿Es la primera línea de un cluster?
            match = patron_cluster.match(line)
            if match:
                # Si ya había un cluster en construcción, lo guardamos
                if cluster_actual is not None:
                    clusters.append({
                        "cluster": cluster_actual["cluster"],
                        "cantidad_de_palabras_clave": cluster_actual["cantidad"],
                        "porcentaje_de_palabras_clave": cluster_actual["porcentaje"],
                        "principales_palabras_clave": " ".join(keywords_actuales),
                    })

                # Empezamos un nuevo cluster
                cluster_actual = {
                    "cluster": int(match.group(1)),
                    "cantidad": int(match.group(2)),
                    # El archivo usa coma decimal ("15,9") → lo pasamos a punto ("15.9")
                    "porcentaje": float(match.group(3) + "." + match.group(4)),
                }
                primera_parte = match.group(5).strip()
                keywords_actuales = [primera_parte] if primera_parte else []

            # 2) ¿Es una línea de continuación de palabras clave?
            #    (línea NO vacía, NO matchea el patrón, y hay cluster en curso)
            elif cluster_actual is not None and line.strip():
                keywords_actuales.append(line.strip())

            # 3) Si la línea está vacía o es del header/separador, la ignoramos

    # NO olvidar guardar el ÚLTIMO cluster (el bucle lo deja en "cluster_actual")
    if cluster_actual is not None:
        clusters.append({
            "cluster": cluster_actual["cluster"],
            "cantidad_de_palabras_clave": cluster_actual["cantidad"],
            "porcentaje_de_palabras_clave": cluster_actual["porcentaje"],
            "principales_palabras_clave": " ".join(keywords_actuales),
        })

    # Construimos el DataFrame con los nombres de columnas que pide el test
    df = pd.DataFrame(clusters)

    # Limpieza final de las palabras clave:
    #   1) Quitar el punto final del cluster ("partial shade." → "partial shade")
    #   2) Colapsar espacios múltiples (incluye saltos de línea) en uno solo
    #   3) Normalizar comas: ",  " o " ," o ",," → ", "
    df["principales_palabras_clave"] = (
        df["principales_palabras_clave"]
        .str.rstrip(" .")
        .str.replace(r"\s+", " ", regex=True)
        .str.replace(r"\s*,\s*", ", ", regex=True)
    )

    return df