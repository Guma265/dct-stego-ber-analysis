import cv2
import numpy as np

# ====== CONFIG ======
coeff_pos = (4, 3)
q_embed = 10

# Aqui pegar EXACTAMENTE el mensaje que se embebio en el estego
ORIGINAL_MESSAGE = "DCT stego + JPEG attack: Guillermo Dia 3."

DELIM = "1111111111111110"

# ====== Utilidades ======
def text_to_bits(text: str) -> str:
    bits = ''.join(format(ord(c), '08b') for c in text)
    return bits + DELIM

def extract_bits_dct_luma(img_bgr: np.ndarray, coeff_pos=(4, 3), q=10, n_bits=480) -> str:
    """Extrae n_bits leyendo 1 bit por bloque desde el canal Y usando paridad de round(coef/q)."""
    if img_bgr is None:
        raise ValueError("La imagen es None (cv2.imread falló).")

    ycrcb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2YCrCb)
    Y = ycrcb[:, :, 0].astype(np.float32)

    h, w = Y.shape
    h8, w8 = (h // 8) * 8, (w // 8) * 8
    Yc = Y[:h8, :w8]

    u, v = coeff_pos
    if (u, v) == (0, 0):
        raise ValueError("No uses DC (0,0).")

    bits = ""
    for i in range(0, h8, 8):
        for j in range(0, w8, 8):
            if len(bits) >= n_bits:
                return bits

            block = Yc[i:i+8, j:j+8]
            dct_block = cv2.dct(block)

            c = dct_block[u, v]
            k = int(np.round(c / q))
            bits += str(k & 1)

    return bits  # por si no alcanzó n_bits (imagen pequeña)

def ber(original_bits: str, extracted_bits: str) -> float:
    """Bit Error Rate: errores / total comparado (alineado al mínimo largo)."""
    n = min(len(original_bits), len(extracted_bits))
    if n == 0:
        return 1.0
    errors = sum(1 for i in range(n) if original_bits[i] != extracted_bits[i])
    return errors / n

# ====== Main ======
if __name__ == "__main__":
    # bits originales (incluye delimitador)
    orig_bits = text_to_bits(ORIGINAL_MESSAGE)

    # Para comparar de forma justa, extraemos exactamente la misma cantidad de bits
    n_bits = len(orig_bits)

    tests = [
        ("STEGO PNG", "stego_dct_pos4_3_q10.png"),
        ("JPEG 90",   "attack_qjpeg90_from_stego.jpg"),
        ("JPEG 70",   "attack_qjpeg70_from_stego.jpg"),
        ("JPEG 50",   "attack_qjpeg50_from_stego.jpg"),
    ]

    print("=== BER (Bit Error Rate) ===")
    print(f"Mensaje original: {ORIGINAL_MESSAGE}")
    print(f"Bits comparados: {n_bits} (incluye delimitador)\n")

    for name, path in tests:
        img = cv2.imread(path)
        if img is None:
            print(f"{name:10s} -> ERROR: no pude abrir {path}")
            continue

        ext_bits = extract_bits_dct_luma(img, coeff_pos=coeff_pos, q=q_embed, n_bits=n_bits)
        b = ber(orig_bits, ext_bits)

        # También reportamos errores absolutos
        n = min(len(orig_bits), len(ext_bits))
        errors = int(b * n) if n > 0 else n_bits

        print(f"{name:10s} -> BER = {b:.4f}  | errores = {errors}/{n}")
