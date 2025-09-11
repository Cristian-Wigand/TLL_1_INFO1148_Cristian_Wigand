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

def main():
    print("Esqueleto léxico listo (v1).")

if __name__ == "__main__":
    main()
