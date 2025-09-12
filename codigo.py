import re
import sys
from pathlib import Path
from collections import Counter

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
    resultado = []
    for pedazo in linea.split(","):
        frag = pedazo.strip()
        if not frag:
            continue
        resultado.extend(clasificar_fragmento(frag))
    return resultado

# ----------------- E/S de archivo -----------------

def cargar_lineas_archivo(ruta: Path):
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")
    lineas = []
    with ruta.open(encoding="utf-8") as fh:
        for linea in fh:
            s = linea.strip()
            if s:
                lineas.append(s)
    if not lineas:
        raise ValueError("El archivo existe pero está vacío.")
    return lineas

def limpiar_prefijo(linea: str):
    if ";" in linea:
        _, derecha = linea.split(";", 1)
        return derecha.strip()
    return linea

# ----------------- Interfaz y salida -----------------

def imprimir_tabla(pares):
    print(f"{'N°':<5}{'TOKEN':<25}{'LEXEMA':<25}")
    print("-" * 60)
    for i, (tipo, lexema) in enumerate(pares, start=1):
        print(f"{i:<5}{tipo:<25}{lexema:<25}")

def pedir_opcion_menu_inicial():
    print("¿Qué quieres procesar del archivo?")
    print("  [1] Primeras 10  |  [2] Últimas 10  |  [3] Todo")
    while True:
        try:
            opcion = input("Elige una opción (1/2/3): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEntrada interrumpida. Saliendo.")
            return None
        if opcion == "1":
            return "primeras"
        if opcion == "2":
            return "ultimas"
        if opcion == "3":
            return "todo"
        print("Opción no válida. Intenta nuevamente…")

def seleccionar_segmento(lineas, opcion):
    n = len(lineas)
    if opcion == "primeras":
        indices = range(0, min(10, n))
    elif opcion == "ultimas":
        indices = range(max(0, n - 10), n)
    else:
        indices = range(0, n)
    seleccion = []
    for i in indices:
        cruda = lineas[i]
        limpia = limpiar_prefijo(cruda)
        seleccion.append((i + 1, cruda, limpia))
    return seleccion

def procesar_y_mostrar(seleccion):
    conteo = Counter()
    for nlinea, cruda, limpia in seleccion:
        print(f"\n=== Línea {nlinea} ===")
        print(limpia)
        pares = partir_por_comas(limpia)
        imprimir_tabla(pares)
        # Acumular conteos por tipo de token
        conteo.update([tipo for (tipo, _) in pares])
    # Resumen del lote
    if conteo:
        print("\n--- Resumen de tokens en este lote ---")
        for tipo, cant in sorted(conteo.items()):
            print(f"{tipo:<25}: {cant}")
        print("--------------------------------------")

# ----------------- Main -----------------

def main():
    ruta = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("entrada.txt")
    try:
        lineas = cargar_lineas_archivo(ruta)
    except Exception as e:
        print(f"[ERROR] {e}")
        return

    print(f"Archivo cargado: {ruta}  (líneas útiles: {len(lineas)})\n")

    while True:
        opcion = pedir_opcion_menu_inicial()
        if opcion is None:
            return
        seleccion = seleccionar_segmento(lineas, opcion)
        procesar_y_mostrar(seleccion)

        try:
            decision = input("\n¿Quieres seguir en el programa o quieres salir? Para salir ingrese 'salir': ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nEntrada interrumpida. Saliendo.")
            return

        if decision == "salir":
            print("Hasta luego.")
            return
        # cualquier otra cosa → vuelve al menú inicial

if __name__ == "__main__":
    main()
