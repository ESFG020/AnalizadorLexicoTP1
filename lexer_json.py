"""
=============================================================================
  ANALIZADOR LÉXICO PARA JSON SIMPLIFICADO
  Tarea 1 - Analisis Léxico
=============================================================================
  Descripción:
      Lee un archivo fuente con formato JSON, realiza analisis léxico línea
      por línea y escribe en un archivo de salida la secuencia de componentes
      léxicos encontrados en cada línea, separados por espacios, preservando
      la indentación original.

      En caso de error léxico:
        - Imprime un mensaje descriptivo en consola (stderr) indicando el
          número de línea y el caracter invalido encontrado.
        - Escribe "error" en la línea correspondiente del archivo de salida.
        - Continúa procesando las líneas siguientes del archivo sin detenerse.

  Gramatica BNF soportada (JSON simplificado):
      json            => element eof
      element         => object | array
      array           => [ element-list ] | []
      element-list    => element-list , element | element
      object          => { attributes-list } | {}
      attributes-list => attribute-list , attribute | attribute
      attribute       => attribute-name : attribute-value
      attribute-name  => string
      attribute-value => element | string | number | true | false | null

  Tokens reconocidos:
      LEXEMA        COMPONENTE LÉXICO
      [             L_CORCHETE
      ]             R_CORCHETE
      {             L_LLAVE
      }             R_LLAVE
      ,             COMA
      :             DOS_PUNTOS
      "..."         LITERAL_CADENA
      number        LITERAL_NUM
      true | TRUE   PR_TRUE
      false | FALSE PR_FALSE
      null | NULL   PR_NULL

  Uso:
      python lexer_json.py                          -> fuente.txt a salida.txt
      python lexer_json.py entrada.txt              -> entrada personalizada
      python lexer_json.py entrada.txt salida.txt   -> entrada y salida personalizadas
"""
import re
from pathlib import Path
import sys

# Definicion de tokens a usar en el analisis léxico para el JSON simplificado
TOKENS = [
    # Delimitadores estructurales
    ("L_CORCHETE",     re.compile(r"\[")),    # Corchete de apertura [
    ("R_CORCHETE",     re.compile(r"\]")),    # Corchete de cierre ]
    ("L_LLAVE",        re.compile(r"\{")),    # Llave de apertura {
    ("R_LLAVE",        re.compile(r"\}")),    # Llave de cierre }
    ("COMA",           re.compile(r",")),     # Separador de elementos
    ("DOS_PUNTOS",     re.compile(r":")),     # Separador clave:valor
    # Literales
    ("LITERAL_CADENA", re.compile(r"\"(?:[^\"\\]|\\.)*\"")),#Expresion regular para cadenas JSON que empiecen y terminen con comillas dobles

    # Número: entero o decimal con exponente opcional (e|E)(+|-)digits.
    ("LITERAL_NUM",    re.compile(r"[0-9]+(?:\.[0-9]+)?(?:(?:e|E)(?:\+|-)?[0-9]+)?")),#Expresion regular para números enteros y decimales con notación científica opcional
    
    # Palabras reservadas
    ("PR_TRUE",        re.compile(r"(?:true|TRUE)")),
    ("PR_FALSE",       re.compile(r"(?:false|FALSE)")),
    ("PR_NULL",        re.compile(r"(?:null|NULL)")),
]

WHITESPACE = re.compile(r"[ \t]+")# Expresión regular para consumir espacios en blanco (espacio y tab).

def tokenizar_linea(linea: str):
    """
    Analiza léxicamente una línea completa del archivo fuente.

    Recorre la línea usando un cursor (pos), ignorando espacios en blanco
    y reconociendo tokens según la tabla TOKENS.
    """
    pos = 0                  # Posición actual dentro de la línea
    longitud = len(linea)    # Longitud total; usado en condición de parada del bucle
    tokens_encontrados = []  # Acumulador de los tokens reconocidos

    while pos < longitud:

        # Saltar espacios en blanco
        m = WHITESPACE.match(linea, pos)
        if m:
            pos = m.end()
            if pos >= longitud:
                break         # Fin de línea alcanzado tras los espacios
            continue          # Volver al inicio del bucle

        # Intentar reconocer un token valido 
        reconocido = False
        for nombre_token, patron in TOKENS:
            m = patron.match(linea, pos)
            if m:
                tokens_encontrados.append(nombre_token)  # Registrar el token
                pos = m.end()                             # Avanzar el cursor
                reconocido = True
                break  # Primer match gana; no probar patrones restantes

        # Error léxico: ningún patrón hizo match, el caracter en la posición actual no pertenece a ningún token valido.
        if not reconocido:
            return [], True  # Señal de error, no continuar con el analisis de esta línea

    # Línea procesada completamente sin errores
    return tokens_encontrados, False

def _encontrar_posicion_error(linea: str) -> int:
    """
    Recorre la línea reproduciendo la misma lógica de tokenizar_linea para
    ubicar la posición exacta (índice base 0) del primer caracter invalido.
    """
    pos = 0
    longitud = len(linea)

    while pos < longitud:
        m = WHITESPACE.match(linea, pos)
        if m:
            pos = m.end()
            if pos >= longitud:
                break
            continue

        reconocido = False
        for _, patron in TOKENS:
            m = patron.match(linea, pos)
            if m:
                pos = m.end()
                reconocido = True
                break

        if not reconocido:
            return pos  # Posición del caracter que causó el error

    return pos

def analizar_fuente(entrada: str, salida: str):
    """
    Lee el archivo fuente línea por línea, tokeniza cada una y escribe los
    resultados en el archivo de salida.

    Ante un error léxico:
        - Imprime mensaje en stderr con número de línea y carácter inválido.
        - Escribe "error" en el archivo de salida para esa línea.
        - Continúa con las líneas restantes sin detenerse.

    Parámetros:
        ruta_entrada : ruta del archivo fuente JSON a analizar.
        ruta_salida  : ruta del archivo donde se escribirán los tokens.
    """
    path_entrada = Path(entrada)
    path_salida = Path(salida)

    lineas = path_entrada.read_text(encoding="utf-8").splitlines() #Leer todas las líneas del archivo fuente

    errores_totales = 0  # Contador de líneas con error léxico

    with path_salida.open("w", encoding="utf-8") as archivo_salida:
        # Iterar cada línea con su número
        for num_linea, linea in enumerate(lineas, start=1):
            # Escribe en el archivo de salida la indentación original(espacios/tabs al inicio)
            indentacion = re.match(r"^[ \t]*", linea).group(0)
            # Tokenizar la línea
            tokens, hubo_error = tokenizar_linea(linea)

            if hubo_error:# Manejo de errores, en caso de existir
                errores_totales += 1

                # Localizar el carácter el error
                pos_error = _encontrar_posicion_error(linea)
                char_invalido = linea[pos_error] if pos_error < len(linea) else "?"

                # Imprime en consola el número de línea y carácter del error
                print(
                    f"[ERROR LÉXICO] Línea {num_linea}: "
                    f"carácter inesperado '{char_invalido}'",
                    file=sys.stderr
                )

                # Escribir "error" en el archivo de salida con la indentación correspondiente
                archivo_salida.write(indentacion + "error\n")

            # En caso de no haber un error
            else:
                if tokens:
                    # Línea con tokens: indentación + nombres separados por espacio
                    archivo_salida.write(indentacion + " ".join(tokens) + "\n")
                else:
                    # Línea vacía o solo espacios: preservar solo la indentación
                    archivo_salida.write(indentacion + "\n")

    # Resumen final en consola
    print(f"Análisis léxico completado.")
    print(f"  Archivo fuente   : {path_entrada}")
    print(f"  Archivo de salida: {path_salida}")
    print(f"  Líneas procesadas: {len(lineas)}")
    if errores_totales > 0:
        print(f"  Errores léxicos  : {errores_totales}", file=sys.stderr)


if __name__ == "__main__":
    # Permite que se ingresen los nombres de los archivos de entrada y salida, en caso de no hacerlo toma los por defecto
    #Archivos de entrada y salida por defecto
    archivo_entrada = "fuente.txt"
    archivo_salida  = "salida.txt"

    if len(sys.argv) >= 2:
        archivo_entrada = sys.argv[1]
    if len(sys.argv) >= 3:
        archivo_salida = sys.argv[2]

    analizar_fuente(archivo_entrada, archivo_salida)#Los archivos deben estar en la misma ubicacion que el script para que funcione correctamente
