# TUIA - Procesamiento de Imágenes I - TP1 (2026, 2° semestre)

## Estructura

```
data/          imágenes de entrada provistas por la cátedra
outputs/       figuras generadas
problema1.py   ecualización local de histograma
```

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecución

Las imágenes provistas ya están incluidas en `data/`. Desde esta carpeta:

```bash
python problema1.py
```

El problema 1 guarda dos figuras comparativas en `outputs/` y las muestra:

- `p1_global_vs_local.png`: imagen original, ecualización global y local.
- `p1_tamanios_ventana.png`: comparación de distintos tamaños de ventana.

Para usar otra imagen, se cambia `IMG_PATH` al principio de `problema1.py`.

Las rutas predeterminadas se resuelven desde la ubicación del script, de modo
que también se puede ejecutar desde otra carpeta usando su ruta completa.
