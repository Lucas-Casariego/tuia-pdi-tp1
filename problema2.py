"""Problema 2: validación de planillas de calificaciones."""

import csv
from pathlib import Path

import cv2
import numpy as np

DATA_DIR = Path(__file__).parent / "data"
OUTPUT_DIR = Path(__file__).parent / "outputs"
CAMPOS = ("Legajo", "Nombre y Apellido", "Parcial 1", "Parcial 2",
          "Parcial 3", "Condición Final")


def intervalos(mask):
    """Tramos True de un vector, como pares [inicio, fin) para indexar."""
    cambios = np.diff(np.pad(np.asarray(mask, dtype=np.int8), 1))
    return list(zip(np.flatnonzero(cambios == 1), np.flatnonzero(cambios == -1)))


def detectar_grilla(img):
    """Detecta el espesor completo de las líneas con proyecciones (ayuda TP).

    Las líneas completas superan el 70% del máximo de su proyección.
    La división parcial de 'Notas' no llega a ese umbral horizontal.
    El formato tiene siete columnas: Nro. y los seis campos a validar.
    """
    tinta = img < 128
    filas = tinta.sum(axis=1)
    horizontales = intervalos(filas > 0.7 * filas.max())
    if len(horizontales) < 3:
        raise ValueError("No se detectaron el encabezado y los registros de la grilla.")
    # Medir columnas sólo en los registros evita que el logo o las celdas
    # fusionadas del encabezado alteren la detección en planillas cortas.
    columnas = tinta[horizontales[1][1]:horizontales[-1][0]].sum(axis=0)
    verticales = intervalos(columnas > 0.7 * columnas.max())
    if len(verticales) != 8:
        raise ValueError("No se detectó una grilla con encabezado y siete columnas.")
    return horizontales, verticales


def segmentar_caracteres(celda):
    """Agrupa componentes que se solapan en x (por ejemplo N + tilde).

    El alfabeto del TP tiene caracteres separados horizontalmente y un solo
    renglón. Se preservan componentes pequeños: un guion o un punto no es
    necesariamente ruido. Los bordes de la grilla ya quedaron fuera del crop.
    """
    tinta = (celda < 128).astype(np.uint8)
    _, _, stats, _ = cv2.connectedComponentsWithStats(tinta, connectivity=8)
    cajas = sorted((tuple(map(int, st[:4])) for st in stats[1:]), key=lambda c: c[0])
    grupos = []
    for x, y, w, h in cajas:
        if grupos and x < grupos[-1][2]:
            a, b, c, d = grupos[-1]
            grupos[-1] = (a, min(b, y), max(c, x + w), max(d, y + h))
        else:
            grupos.append((x, y, x + w, y + h))
    return [{"caja": (x, y, x2, y2), "patch": tinta[y:y2, x:x2]}
            for x, y, x2, y2 in grupos]


def contar_palabras(caracteres, altura_texto):
    """Un hueco > media altura de letra separa palabras en esta tipografía.

    La escala se estima del texto del formulario, no de la altura de las filas:
    una fila más alta no implica que sus letras sean más grandes.
    """
    if not caracteres:
        return 0
    huecos = [b["caja"][0] - a["caja"][2]
              for a, b in zip(caracteres, caracteres[1:])]
    return 1 + sum(hueco > 0.5 * altura_texto for hueco in huecos)


def validar_campos(conteos):
    """Reglas de formato; los espacios separan palabras y no cuentan como letras."""
    (cl, pl), (cn, pn), *resto = conteos
    notas, (cc, _) = resto[:3], resto[3]
    validos = [cl == 8 and pl == 1, 0 < cn <= 12 and pn >= 2]
    validos.extend(c in (1, 2) and p == 1 for c, p in notas)
    validos.append(cc == 1)
    return ["OK" if valido else "MAL" for valido in validos]


def identificar_lr(patch):
    """Reconoce L/R por trazos y huecos; cualquier otro carácter devuelve None.

    Esto sólo decide qué recortes mostrar; no cambia la validez del campo.
    Se aplica a la letra de imprenta sin inclinación de estas planillas.
    """
    tinta = patch.astype(bool)
    h, w = tinta.shape
    if h < 3 or w < 2:
        return None
    # El trazo izquierdo de L y R recorre casi toda la altura.
    ancho_trazo = max(1, int(np.ceil(w * 0.25)))
    if tinta[:, :ancho_trazo].any(axis=1).mean() < 0.9:
        return None
    # Conectividad 4 del fondo complementaria a la conectividad 8 de la tinta.
    fondo = np.pad(~tinta, 1, constant_values=True).astype(np.uint8)
    _, etiquetas, stats, _ = cv2.connectedComponentsWithStats(fondo, connectivity=4)
    exterior = etiquetas[0, 0]
    huecos = [st for i, st in enumerate(stats) if i not in (0, exterior)]
    if not huecos:
        # L: brazo inferior ancho y zona superior derecha vacía.
        inferior = tinta[int(0.8 * h):].any(axis=0).mean()
        superior_derecha = tinta[:int(0.75 * h), int(np.ceil(0.4 * w)):].mean()
        if inferior >= 0.85 and superior_derecha <= 0.05:
            return "L"
    elif len(huecos) == 1:
        hueco = huecos[0]
        fin_hueco = hueco[cv2.CC_STAT_TOP] - 1 + hueco[cv2.CC_STAT_HEIGHT]
        # R: hueco arriba; dos patas separadas abajo. Descarta P, B, D y A.
        patas = intervalos(tinta[-max(1, h // 6):].any(axis=0))
        if fin_hueco <= 0.7 * h and len(patas) == 2 and patas[-1][1] >= 0.85 * w:
            return "R"
    return None


def analizar_planilla(img):
    """Devuelve registros y geometría, sin escribir archivos ni mostrar ventanas."""
    if not isinstance(img, np.ndarray) or img.ndim != 2 or img.size == 0:
        raise ValueError("Se espera una imagen no vacía en escala de grises.")
    if img.dtype != np.uint8:
        raise TypeError("Se espera una imagen uint8.")
    filas, columnas = detectar_grilla(img)
    registros = []
    # Se omite el encabezado; la cantidad de registros surge de las líneas.
    for i in range(1, len(filas) - 1):
        campos = []
        for j in range(1, len(columnas) - 1):
            y1, y2 = filas[i][1], filas[i + 1][0]
            x1, x2 = columnas[j][1], columnas[j + 1][0]
            crop = img[y1:y2, x1:x2].copy()
            campos.append({"crop": crop, "caja": (x1, y1, x2, y2),
                           "caracteres": segmentar_caracteres(crop)})
        registros.append({"id": i, "campos": campos})
    alturas = [c["patch"].shape[0] for r in registros for f in r["campos"]
               for c in f["caracteres"]]
    altura_texto = float(np.median(alturas)) if alturas else 1.0
    for registro in registros:
        conteos = []
        for campo in registro["campos"]:
            caracteres = campo["caracteres"]
            campo["cantidad"] = len(caracteres)
            campo["palabras"] = contar_palabras(caracteres, altura_texto)
            conteos.append((campo["cantidad"], campo["palabras"]))
        registro["validacion"] = validar_campos(conteos)
        condicion = registro["campos"][-1]["caracteres"]
        registro["condicion_lr"] = identificar_lr(condicion[0]["patch"]) if len(condicion) == 1 else None
    return registros, filas, columnas


def guardar_imagen(path, img):
    if not cv2.imwrite(str(path), img):
        raise OSError(f"No se pudo guardar {path}")


def imagen_no_aprobados(alumnos):
    """Una imagen con crops originales y etiquetas explícitas de L/R."""
    alto_crop = max((a["crop"].shape[0] for a in alumnos), default=24)
    ancho_crop = max((a["crop"].shape[1] for a in alumnos), default=250)
    alto_fila = max(38, alto_crop + 12)
    ancho = max(720, ancho_crop + 460)
    canvas = np.full((75 + max(1, len(alumnos)) * alto_fila, ancho, 3), 255, np.uint8)
    cv2.putText(canvas, "No aprobados - solo registros completos OK", (15, 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (30, 30, 30), 1, cv2.LINE_AA)
    if not alumnos:
        cv2.putText(canvas, "No hay registros validos con condicion L o R.", (15, 85),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (30, 30, 30), 1, cv2.LINE_AA)
    for i, alumno in enumerate(alumnos):
        y = 60 + i * alto_fila
        crop = alumno["crop"]
        h, w = crop.shape
        cv2.putText(canvas, alumno["origen"], (15, y + 24),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (50, 50, 50), 1, cv2.LINE_AA)
        canvas[y:y + h, 220:220 + w] = cv2.cvtColor(crop, cv2.COLOR_GRAY2BGR)
        condicion = alumno["condicion"]
        texto = "RECUPERA (R)" if condicion == "R" else "LIBRE (L)"
        color = (0, 120, 180) if condicion == "R" else (0, 0, 190)
        cv2.putText(canvas, texto, (240 + ancho_crop, y + 24),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 1, cv2.LINE_AA)
    return canvas


def procesar_planilla(path, salida=OUTPUT_DIR):
    path, salida = Path(path), Path(salida)
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"No se pudo leer {path}")
    registros, _, _ = analizar_planilla(img)
    salida.mkdir(parents=True, exist_ok=True)
    alumnos = []
    print(f"\nPlanilla: {path.name}")
    with (salida / f"validacion_{path.stem}.csv").open("w", newline="", encoding="utf-8") as archivo:
        writer = csv.writer(archivo)
        writer.writerow(("ID", *CAMPOS))
        for registro in registros:
            writer.writerow((registro["id"], *registro["validacion"]))
            print(f"Registro {registro['id']}:")
            for nombre, estado in zip(CAMPOS, registro["validacion"]):
                print(f"  {nombre}: {estado}")
            if all(v == "OK" for v in registro["validacion"]) and registro["condicion_lr"]:
                alumnos.append({"origen": f"{path.stem} / {registro['id']}",
                                "crop": registro["campos"][1]["crop"],
                                "condicion": registro["condicion_lr"]})
    guardar_imagen(salida / f"no_aprobados_{path.stem}.png", imagen_no_aprobados(alumnos))
    validos = sum(all(v == "OK" for v in r["validacion"]) for r in registros)
    print(f"Resumen: {len(registros)} registros, {validos} completos OK, {len(alumnos)} no aprobados válidos.")
    return registros, alumnos


def main():
    for i in range(1, 5):
        path = DATA_DIR / f"grade_sheet_{i}.png"
        procesar_planilla(path)
    print(f"\nResultados guardados en {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
