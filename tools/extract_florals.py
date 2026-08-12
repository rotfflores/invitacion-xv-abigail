from pathlib import Path
from PIL import Image, ImageFilter

SOURCE = Path(r"C:\Users\Lenovo\Desktop\temporales\WhatsApp Image 2026-08-11 at 2.52.08 PM - copia.jpeg")
OUTPUT = Path(__file__).resolve().parents[1] / "assets" / "florals"
SCALE = 4

# Recortes medidos sobre la referencia original de 381 × 492 px.
CROPS = {
    "top-left": (31, 12, 190, 108),
    "left-upper": (31, 57, 111, 169),
    "top-right": (196, 0, 340, 102),
    "right-upper": (278, 78, 340, 209),
    "left-middle": (31, 211, 91, 371),
    "right-middle": (302, 198, 340, 365),
    "bottom-left": (43, 326, 181, 485),
    "tiara": (112, 340, 258, 414),
    "bottom-right": (196, 326, 340, 476),
}


def remove_paper(image: Image.Image) -> Image.Image:
    """Conserva la tinta coral y elimina el papel rosa/blanco del JPEG."""
    rgba = image.convert("RGBA")
    alpha = Image.new("L", rgba.size)
    pixels = []

    for r, g, b, _ in rgba.getdata():
        red_bias = r - (g + b) / 2
        chroma = max(r, g, b) - min(r, g, b)
        darkness = 255 - (r + g + b) / 3

        # La tinta original es coral: dominante roja y con mayor cromaticidad
        # que el papel. La transición suave conserva el antialias del trazo.
        strength = max((red_bias - 13) * 12, (chroma - 22) * 6)
        if red_bias < 11 or darkness < 9:
            strength = 0
        value = max(0, min(255, round(strength)))
        pixels.append(0 if value < 38 else value)

    alpha.putdata(pixels)
    alpha = alpha.filter(ImageFilter.GaussianBlur(0.35))
    rgba.putalpha(alpha)
    return rgba


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    source = Image.open(SOURCE).convert("RGB")
    # Supermuestreo para que los PNG mantengan nitidez en pantallas HD/Retina.
    source = source.resize(
        (source.width * SCALE, source.height * SCALE),
        Image.Resampling.LANCZOS,
    ).filter(ImageFilter.MedianFilter(3))
    for name, box in CROPS.items():
        hd_box = tuple(value * SCALE for value in box)
        result = remove_paper(source.crop(hd_box))
        if name == "top-left":
            # El número dorado invade unos píxeles del recorte en el original.
            # Se elimina solo esa zona; el trazo floral queda intacto.
            result.paste(
                (0, 0, 0, 0),
                (136 * SCALE, 64 * SCALE, result.width, result.height),
            )
        # Realce moderado sobre RGB sin alterar la transparencia ni redibujar.
        rgb = result.convert("RGB").filter(
            ImageFilter.UnsharpMask(radius=1.2, percent=115, threshold=4)
        )
        rgb.putalpha(result.getchannel("A"))
        result = rgb
        result.save(OUTPUT / f"{name}.png", optimize=True)


if __name__ == "__main__":
    main()
