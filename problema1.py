"""Problema 1 - Ecualización local de histograma."""

from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np

DATA_DIR = Path(__file__).parent / "data"
OUTPUT_DIR = Path(__file__).parent / "outputs"
IMG_PATH = DATA_DIR / "Imagen_con_detalles_escondidos.tif"


def ecualizacion_local(img: np.ndarray, M: int, N: int) -> np.ndarray:
    """Ecualización local de histograma con una ventana de M filas x N columnas.

    Para cada píxel se toma la ventana centrada en él, se calcula el histograma
    de la ventana y su transformación de ecualización T(r) = (L-1) * CDF(r),
    y se aplica T únicamente al píxel central.

    Como T(r) = (L-1) * #{píxeles de la ventana <= r} / (M*N), evaluar T en el
    píxel central equivale a contar cuántos píxeles de la ventana son menores o
    iguales a él. Eso permite resolver cada fila de forma vectorizada.
    """
    if img.ndim != 2:
        raise ValueError("La imagen debe estar en escala de grises.")
    if not (isinstance(M, int) and isinstance(N, int) and M > 0 and N > 0):
        raise ValueError("M y N deben ser enteros positivos.")

    L = 256
    img = img.astype(np.uint8)
    top, left = M // 2, N // 2
    bottom, right = M - 1 - top, N - 1 - left
    img_pad = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_REPLICATE)

    # ventanas[i, j] es la ventana MxN centrada en el píxel (i, j) de la imagen original
    ventanas = np.lib.stride_tricks.sliding_window_view(img_pad, (M, N))

    salida = np.empty_like(img)
    area = M * N
    for i in range(img.shape[0]):
        centro = img[i][:, None, None]                        # (W, 1, 1)
        cdf_centro = np.count_nonzero(ventanas[i] <= centro, axis=(1, 2)) / area
        salida[i] = np.round((L - 1) * cdf_centro).astype(np.uint8)
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
        ax.imshow(ecualizacion_local(img, M, N), cmap="gray", vmin=0, vmax=255)
        ax.set_title(f"Ventana {M}x{N}")
    for ax in axs:
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "p1_tamanios_ventana.png", dpi=150)

    plt.show()


if __name__ == "__main__":
    main()
