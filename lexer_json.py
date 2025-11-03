import re
from pathlib import Path

# Definición de tokens
TOKENS = [
    ("L_CORCHETE", re.compile(r"\[")),
    ("R_CORCHETE", re.compile(r"\]")),
    ("L_LLAVE", re.compile(r"\{")),
    ("R_LLAVE", re.compile(r"\}")),
    ("COMA", re.compile(r",")),
    ("DOS_PUNTOS", re.compile(r":")),
    ("STRING", re.compile(r"\"(?:[^\"\\]|\\.)*\"")),
    ("NUMBER", re.compile(r"[0-9]+(?:\.[0-9]+)?(?:(?:e|E)(?:\+|-)?[0-9]+)?")),
    ("PR_TRUE", re.compile(r"(?:true|TRUE)")),
    ("PR_FALSE", re.compile(r"(?:false|FALSE)")),
    ("PR_NULL", re.compile(r"(?:null|NULL)")),
]

WHITESPACE = re.compile(r"\s+")

def tokenize_line(line: str):
    """
    Devuelve tokens de una línea o ["error"] si falla.
    """
    pos, n = 0, len(line)
    result = []
    while pos < n:
        # Ignorar espacios
        m = WHITESPACE.match(line, pos)
        if m:
            pos = m.end()
            if pos >= n:
                break

        matched = False
        for name, rx in TOKENS:
            m = rx.match(line, pos)
            if m:
                result.append(name)
                pos = m.end()
                matched = True
                break
        if not matched:
            return ["error"]
    return result

def analizar_fuente(entrada: str, salida: str):
    in_path = Path(entrada)
    out_path = Path(salida)

    lines = in_path.read_text(encoding="utf-8").splitlines()

    with out_path.open("w", encoding="utf-8") as f:
        for ln in lines:
            # Guardar indentación original (espacios/tabs al inicio)
            indent = re.match(r"^\s*", ln).group(0)
            tokens = tokenize_line(ln)
            if tokens:
                f.write(indent + " ".join(tokens) + "\n")
            else:
                f.write(indent + "\n")

    print(f"Análisis completado. Archivo de salida: {out_path}")

# Ejemplo de uso
if __name__ == "__main__":
    analizar_fuente("fuente.txt", "salida.txt")
