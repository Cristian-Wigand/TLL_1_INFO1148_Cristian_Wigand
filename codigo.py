import re
import sys
from pathlib import Path

# === Léxico (en minúscula) ===
palabras_reservadas = {"if", "else", "while", "for", "return", "int", "float"}

tokens = [
    ("identificador",        r'[a-zA-Z_]\w*'),
    ("numero",               r'\d+(\.\d+)?'),

    # Operadores compuestos
    ("incremento",                r'\+\+'),
    ("decremento",                r'--'),
    ("asignacion_suma",           r'\+='),
    ("asignacion_resta",          r'-='),
    ("asignacion_multiplicacion", r'\*='),
    ("asignacion_division",       r'/='),
    ("asignacion_mod",            r'%='),

    # Relacionales (dobles antes que simples)
    ("menor_igual",   r'<='),
    ("mayor_igual",   r'>='),
    ("igual",         r'=='),
    ("diferente",     r'!='),

    ("menor",         r'<'),
    ("mayor",         r'>'),

    # Asignación simple
    ("asignacion",    r'='),

    # Aritméticos simples
    ("suma",           r'\+'),
    ("resta",          r'-'),
    ("multiplicacion", r'\*'),
    ("division",       r'/'),
    ("mod",            r'%'),

    # Lógico simple
    ("not",            r'!'),

    # Puntuación
    ("parentesis_izquierda", r'\('),
    ("parentesis_derecha",   r'\)'),
    ("llave_izquierda",      r'\{'),
    ("llave_derecha",        r'\}'),
    ("corchete_izquierdo",   r'\['),
    ("corchete_derecho",     r'\]'),
    ("punto_y_coma",         r';'),
    ("coma",                 r','),

    # Espacios
    ("blanco",               r'[ \t\n]+'),

    # Cualquier otro símbolo
    ("desconocido",          r'.'),
]

patron_unificado = "|".join(f"(?P<{nombre}>{regex})" for nombre, regex in tokens)
escaner = re.compile(patron_unificado)

# ----------------- Tokenización -----------------

def clasificar_fragmento(texto: str):
    """
    Analiza un fragmento sin comas y devuelve lista de (tipo, lexema).
    """
    salida = []
    for m in escaner.finditer(texto):
        tipo = m.lastgroup
        lexema = m.group()

        if tipo == "blanco":
            continue

        if tipo == "identificador":
            tipo = "palabra_clave" if lexema in palabras_reservadas else "caracter"

        salida.append((tipo, lexema))
    return salida

def partir_por_comas(linea: str):
    """
    Separa por comas, limpia espacios y clasifica cada pieza.
    """
    resultado = []
    for pedazo in linea.split(","):
        frag = pedazo.strip()
        if not frag:
            continue
        resultado.extend(clasificar_fragmento(frag))
    return resultado

def main():
    print("Tokenizador listo (v2). Falta I/O de archivo y menú.")

if _name_ == "_main_":
    main()
