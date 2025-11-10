import re
from pathlib import Path

# Definicion de tokens a usar en el analisis léxico para el JSON simplificado
TOKENS = [
    ("L_CORCHETE", re.compile(r"\[")),
    ("R_CORCHETE", re.compile(r"\]")),
    ("L_LLAVE", re.compile(r"\{")),
    ("R_LLAVE", re.compile(r"\}")),
    ("COMA", re.compile(r",")),
    ("DOS_PUNTOS", re.compile(r":")),
    ("STRING", re.compile(r"\"(?:[^\"\\]|\\.)*\"")),#Expresion regular para cadenas JSON que empiecen y terminen con comillas dobles
    ("NUMBER", re.compile(r"[0-9]+(?:\.[0-9]+)?(?:(?:e|E)(?:\+|-)?[0-9]+)?")),#Expresion regular para números enteros y decimales con notación científica opcional
    ("PR_TRUE", re.compile(r"(?:true|TRUE)")),
    ("PR_FALSE", re.compile(r"(?:false|FALSE)")),
    ("PR_NULL", re.compile(r"(?:null|NULL)")),
]

WHITESPACE = re.compile(r"\s+")# Expresion regular para espacios en blanco

"""
Funcion que tokeniza una linea dada y devuelve los tokens encontrados 
o un error si no se puede tokenizar
"""
def tokenizar_linea(line: str):
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


"""
Función principal que analiza un archivo de entrada linea por linea,
tokeniza cada linea y escribe los resultados en un archivo de salida.
"""
def analizar_fuente(entrada: str, salida: str):
    in_path = Path(entrada)
    out_path = Path(salida)

    lines = in_path.read_text(encoding="utf-8").splitlines()

    with out_path.open("w", encoding="utf-8") as f:
        for ln in lines:
            # Escribe en el archivo de salida la indentación original(espacios/tabs al inicio)
            indent = re.match(r"^\s*", ln).group(0)
            tokens = tokenizar_linea(ln)
            if tokens:
                f.write(indent + " ".join(tokens) + "\n")
            else:
                f.write(indent + "\n")

    print(f"Análisis completado. Archivo de salida: {out_path}")

if __name__ == "__main__":
    analizar_fuente("fuente.txt", "salida.txt")#Archivos de entrada y salida por defecto
    #Los archivos deben estar en la misma ubicacion que el script para que funcione correctamente
