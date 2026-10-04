"""Problema 1 - Ecualización local de histograma."""

from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np

DATA_DIR = Path(__file__).parent / "data"
OUTPUT_DIR = Path(__file__).parent / "outputs"
IMG_PATH = DATA_DIR / "Imagen_con_detalles_escondidos.tif"


def ecualizacion_local(img, M, N):
    """Ecualización local de histograma con una ventana de M filas x N columnas.

    Para cada píxel se toma la ventana centrada en él, se calcula el histograma
    de la ventana y su transformación de ecualización T(r) = (L-1) * CDF(r),
    y se aplica T únicamente al píxel central.

    Se usa la CDF de la unidad 2, sin restar su primer valor no nulo.
    Para ventanas pares se fija el ancla en (M//2, N//2): hay un vecino más
    hacia arriba/izquierda. El borde se completa replicando píxeles.
    """
    if not isinstance(img, np.ndarray) or img.ndim != 2 or img.size == 0:
        raise ValueError("La imagen debe ser una matriz no vacía en escala de grises.")
    if img.dtype != np.uint8:
        raise TypeError("La imagen debe ser uint8 (intensidades entre 0 y 255).")
    if type(M) != int or type(N) != int:
        raise ValueError("M y N deben ser enteros positivos.")
    if M <= 0 or N <= 0:
        raise ValueError("M y N deben ser enteros positivos.")

    L = 256
    top, left = M // 2, N // 2
    bottom, right = M - 1 - top, N - 1 - left
    img_pad = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_REPLICATE)

    salida = np.zeros(img.shape, dtype=np.uint8)
    area = M * N
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            ventana = img_pad[i:i + M, j:j + N]
            # Histograma de la ventana y distribución acumulada.
            hist, bins = np.histogram(ventana.flatten(), L, [0, L])
            cdf = hist.cumsum() / area
            salida[i, j] = np.round((L - 1) * cdf[img[i, j]])
    return salida


def main():
    img = cv2.imread(str(IMG_PATH), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"No se encontró la imagen: {IMG_PATH}")
    OUTPUT_DIR.mkdir(exist_ok=True)

    # b) Global vs. local
    img_global = cv2.equalizeHist(img)
    img_local = ecualizacion_local(img, 15, 15)

    fig, axs = plt.subplots(1, 3, figsize=(15, 5), sharex=True, sharey=True)
    for ax, im, titulo in zip(
        axs,
        [img, img_global, img_local],
        ["Original", "Ecualización global", "Ecualización local 15x15"],
    ):
        ax.imshow(im, cmap="gray", vmin=0, vmax=255)
        ax.set_title(titulo)
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "p1_global_vs_local.png", dpi=150)

    # c) Influencia del tamaño de ventana
    ventanas = [(3, 3), (7, 7), (15, 15), (31, 31), (51, 51), (5, 25), (25, 5)]
    fig, axs = plt.subplots(2, 4, figsize=(18, 9), sharex=True, sharey=True)
    axs = axs.ravel()
    axs[0].imshow(img, cmap="gray", vmin=0, vmax=255)
    axs[0].set_title("Original")
    for ax, (M, N) in zip(axs[1:], ventanas):
        if (M, N) == (15, 15):
            resultado = img_local
        else:
            resultado = ecualizacion_local(img, M, N)
        ax.imshow(resultado, cmap="gray", vmin=0, vmax=255)
        ax.set_title(f"Ventana {M}x{N}")
    for ax in axs:
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "p1_tamanios_ventana.png", dpi=150)

    print(f"Figuras guardadas en {OUTPUT_DIR}")
    plt.show()
    plt.close("all")


if __name__ == "__main__":
    main()
