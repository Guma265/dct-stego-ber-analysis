# dct-stego-ber-analysis
Análisis experimental de esteganografía basada en DCT mediante PSNR y BER bajo ataques de compresión JPEG

# dct-stego-ber-analysis

Análisis experimental de esteganografía basada en DCT mediante PSNR y BER bajo ataques de compresión JPEG.

## Descripción
Este repositorio presenta una implementación reproducible de esteganografía de imágenes
en el dominio de la Transformada Discreta del Coseno (DCT), junto con un análisis experimental
de su fidelidad visual y de la recuperación del mensaje oculto frente a ataques de compresión JPEG.
El sistema evalúa el compromiso entre imperceptibilidad y robustez utilizando las métricas
PSNR (Peak Signal-to-Noise Ratio) y BER (Bit Error Rate).

## Metodología
- Espacio de color: YCrCb (canal de luminancia Y)
- Transformada: DCT 2D aplicada sobre bloques de 8×8 píxeles
- Embebido: modulación por paridad de un coeficiente AC de frecuencia media
- Fuerza de embebido: paso de cuantización \( q \)
- Ataque: compresión JPEG con distintas calidades
- Métricas de evaluación: PSNR y BER

## Contenido del repositorio
- `src/dia4.py`  
  Script para generar la imagen estego mediante DCT, aplicar ataques de compresión JPEG
  (calidades 90, 70 y 50) y calcular la métrica PSNR.

- `src/dia4.1.py`  
  Script para la extracción del mensaje oculto y el cálculo de la tasa de error de bits (BER)
  comparando el mensaje original con el mensaje extraído tras cada ataque.

## Experimentos realizados
1. Generación de imagen estego sin pérdidas (formato PNG)
2. Aplicación de ataques de compresión JPEG
3. Evaluación de fidelidad visual mediante PSNR
4. Evaluación de robustez del mensaje mediante BER

## Resultados principales
- PSNR (original vs estego): ~54.6 dB

### BER (344 bits, incluye delimitador)
- Stego PNG: 0.0029 (1 / 344)
- JPEG 90: 0.0174 (6 / 344)
- JPEG 70: 0.4535 (156 / 344)
- JPEG 50: 0.4273 (147 / 344)

Estos resultados evidencian el compromiso entre fidelidad visual y robustez característico
de los esquemas de esteganografía en el dominio de la transformada.

## Requisitos
- Python 3.x
- OpenCV (`cv2`)
- NumPy

## Uso

Ejecutar primero el script de embebido y ataque:
python3 src/dia4.py

Posteriormente ejecutar el script de extracción y análisis de BER:
python3 src/dia4.1.py

Trabajo futuro

Inclusión de códigos de corrección de errores (ECC)
Comparación con métodos de esteganografía basados en LSB
Esteganálisis estadístico y mediante aprendizaje automático
