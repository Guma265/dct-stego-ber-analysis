import cv2
import numpy as np

DELIM = "1111111111111110"  # mismo delimitador que se uso parq ocultar

def bits_to_text(bits: str) -> str:
    """Convierte una cadena de bits ('0101...') a texto ASCII (8 bits por caracter)."""
    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) < 8:
            break
        chars.append(chr(int(byte, 2)))
    return ''.join(chars)

def extract_dct_luma(img_bgr: np.ndarray, coeff_pos=(4, 3), q=10, max_chars=200, stop_on_delim=True) -> str:
    """
    Se extrae un mensaje oculto en DCT usando paridad de k = round(coef/q).
    - Se trabaja en canal Y de YCrCb
    - Con Bloques 8x8
    - Se lee 1 bit por bloque
    - Si stop_on_delim=True: se detiene cuando encuentra el delimitador
    - Si stop_on_delim=False: se extrae max_chars caracteres (longitud fija)
    """
    if img_bgr is None:
        raise ValueError("La imagen es None. Revisa cv2.imread().")

    # Se convierte a YCrCb y se tom a Y (luminancia)
    ycrcb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2YCrCb)
    Y = ycrcb[:, :, 0].astype(np.float32)

    h, w = Y.shape
    h8, w8 = (h // 8) * 8, (w // 8) * 8
    Yc = Y[:h8, :w8]

    u, v = coeff_pos
    if (u, v) == (0, 0):
        raise ValueError("No uses DC (0,0).")

    bits = ""
    max_bits = max_chars * 8

    for i in range(0, h8, 8):
        for j in range(0, w8, 8):
            if len(bits) >= max_bits:
                break

            block = Yc[i:i+8, j:j+8]
            dct_block = cv2.dct(block)

            c = dct_block[u, v]
            k = int(np.round(c / q))   # cuantización
            bits += str(k & 1)         # paridad (bit)

            if stop_on_delim and bits.endswith(DELIM):
                bits = bits[:-len(DELIM)]
                return bits_to_text(bits)

        if len(bits) >= max_bits:
            break

    # Si no hay delimitador (o stop_on_delim=False), se devuelve lo extraído hasta max_chars
    return bits_to_text(bits)

if __name__ == "__main__":
    
    coeff_pos = (4, 3)
    q_embed = 10

    # 1) Prueba con el PNG estego (sin pérdidas) -> usando delimitador
    stego_path = "stego_dct_pos4_3_q10.png"
    stego = cv2.imread(stego_path)
    if stego is None:
        raise FileNotFoundError(f"No pude abrir '{stego_path}'.")

    msg_png = extract_dct_luma(
        stego,
        coeff_pos=coeff_pos,
        q=q_embed,
        max_chars=200,
        stop_on_delim=True
    )

    print("=== MENSAJE EXTRAÍDO (STEGO PNG) ===")
    print("texto:")
    print(msg_png)
    print("repr:")
    print(repr(msg_png))
    print("len:", len(msg_png))
    print()

    # 2) Prueba con los JPEG atacados -> longitud fija (sin delimitador)
    for qjpeg in [90, 70, 50]:
        attacked_path = f"attack_qjpeg{qjpeg}_from_stego.jpg"
        attacked = cv2.imread(attacked_path)
        if attacked is None:
            raise FileNotFoundError(f"No pude abrir '{attacked_path}'.")

        msg_jpg = extract_dct_luma(
            attacked,
            coeff_pos=coeff_pos,
            q=q_embed,
            max_chars=60,          # extrae 60 caracteres (480 bits)
            stop_on_delim=False    # no esperar delimitador (puede desaparecer por JPEG)
        )

        print(f"=== EXTRAÍDO (JPEG {qjpeg}) ===")
        print("texto:")
        print(msg_jpg)
        print("repr:")
        print(repr(msg_jpg))
        print("len:", len(msg_jpg))
        print()
