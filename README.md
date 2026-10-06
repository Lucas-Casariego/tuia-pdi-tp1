# TUIA - Procesamiento de Imágenes I - TP1 (2026, 2° semestre)

Resolución de los dos problemas del trabajo práctico. Las imágenes de entrada están
incluidas en `data/` y el informe de la resolución está en `Informe_TP1_PDI.pdf`.

## Archivos principales

```text
data/                imágenes de entrada provistas por la cátedra
outputs/             figuras, imágenes y CSV generados
problema1.py         ecualización local de histograma
problema2.py         validación de planillas de calificaciones
Informe_TP1_PDI.pdf  descripción, resultados y conclusiones
requirements.txt     dependencias de Python
```

## Versiones utilizadas

La entrega se verificó con estas versiones:

| Componente | Versión |
| --- | --- |
| Python | 3.14.7 |
| NumPy | 2.5.2 |
| OpenCV (`cv2`) | 5.0.0 |
| Matplotlib | 3.11.1 |

En el entorno de verificación, `cv2` proviene de `opencv-contrib-python`
5.0.0.93. El archivo `requirements.txt` instala `opencv-python`; los scripts
utilizan funciones disponibles en ese paquete.

## Instalación

Desde la carpeta del repositorio, crear y activar un entorno virtual e instalar
las dependencias:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

En Windows, activar el entorno con `.venv\Scripts\activate.bat` en CMD o con
`.\.venv\Scripts\Activate.ps1` en PowerShell. Después, ejecutar
`python -m pip install -r requirements.txt`.

## Ejecución

Ejecutar los comandos desde la carpeta del repositorio. Las rutas de entrada y
salida también se resuelven desde la ubicación de los scripts.

### Problema 1: ecualización local

```bash
python problema1.py
```

Procesa `data/Imagen_con_detalles_escondidos.tif`, muestra las comparaciones y
guarda estas figuras en `outputs/`:

- `p1_global_vs_local.png`: imagen original, ecualización global y local.
- `p1_tamanios_ventana.png`: comparación de distintos tamaños de ventana.

Para procesar otra imagen, cambiar `IMG_PATH` al principio de `problema1.py`.

### Problema 2: validación de planillas

```bash
python problema2.py
```

Procesa, en orden, `data/grade_sheet_1.png` a `data/grade_sheet_4.png`. Para cada
registro imprime `OK` o `MAL` en cada campo. Por cada planilla guarda en
`outputs/`:

- `validacion_grade_sheet_<id>.csv`: ID y resultado de los seis campos.
- `no_aprobados_grade_sheet_<id>.png`: recortes de nombres de registros válidos
  cuya condición final es `L` o `R`, con una etiqueta para distinguirlos.

Para procesar una sola planilla, se puede llamar a `procesar_planilla` desde
Python. Por ejemplo:

```bash
python -c "from problema2 import procesar_planilla; procesar_planilla('data/grade_sheet_1.png')"
```
