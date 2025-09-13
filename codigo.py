import re
import sys
from pathlib import Path
from collections import Counter

# === Léxico (definición de palabras clave y tokens) ===

# Palabras reservadas del lenguaje que vamos a reconocer explícitamente
palabras_reservadas = {"if", "else", "while", "for", "return", "int", "float"}

# Lista de tokens: cada tupla tiene (nombre_token, expresión_regular)
tokens = [
    # Identificadores y números
    ("identificador",        r'[a-zA-Z_]\w*'),   # empieza por letra o _, luego letras/dígitos/_
    ("numero",               r'\d+(\.\d+)?'),    # entero o decimal, ej: 42 o 3.14

    # Operadores compuestos (van antes de los simples para que no se corten mal)
    ("incremento",                r'\+\+'),   # ++
    ("decremento",                r'--'),     # --
    ("asignacion_suma",           r'\+='),    # +=
    ("asignacion_resta",          r'-='),     # -=
    ("asignacion_multiplicacion", r'\*='),    # *=
    ("asignacion_division",       r'/='),     # /=
    ("asignacion_mod",            r'%='),     # %=

    # Operadores relacionales dobles
    ("menor_igual",   r'<='),    # <=
    ("mayor_igual",   r'>='),    # >=
    ("igual",         r'=='),    # ==
    ("diferente",     r'!='),    # !=

    # Relacionales simples
    ("menor",         r'<'),
    ("mayor",         r'>'),

    # Asignación simple
    ("asignacion",    r'='),

    # Operadores aritméticos simples
    ("suma",           r'\+'),
    ("resta",          r'-'),
    ("multiplicacion", r'\*'),
    ("division",       r'/'),
    ("mod",            r'%'),

    # Operador lógico NOT
    ("not",            r'!'),

    # Signos de puntuación
    ("parentesis_izquierda", r'\('),
    ("parentesis_derecha",   r'\)'),
    ("llave_izquierda",      r'\{'),
    ("llave_derecha",        r'\}'),
    ("corchete_izquierdo",   r'\['),
    ("corchete_derecho",     r'\]'),
    ("punto_y_coma",         r';'),
    ("coma",                 r','),

    # Espacios en blanco (se ignoran luego)
    ("blanco",               r'[ \t\n]+'),

    # Cualquier otro símbolo no reconocido se marca como error
    ("desconocido",          r'.'),
]

# Unificamos todas las expresiones en una sola con nombres de grupo (?P<nombre>...)
patron_unificado = "|".join(f"(?P<{nombre}>{regex})" for nombre, regex in tokens)

# Compilamos el patrón para poder reutilizarlo de forma eficiente
escaner = re.compile(patron_unificado)

# ----------------- Tokenización -----------------

def clasificar_fragmento(texto: str):
    salida = []
    resultado = escaner.fullmatch(texto)  # exige que el fragmento completo sea un token
    if resultado:
        tipo = resultado.lastgroup

        if tipo == "blanco":
            return salida  # no devuelve nada si solo es espacio

        if tipo == "identificador":
            # Si es palabra reservada → palabra_clave, sino → caracter
            tipo = "palabra_clave" if texto in palabras_reservadas else "caracter"

        salida.append((tipo, texto))
    else:
        # Si nada coincide, marcamos todo como 'desconocido'
        salida.append(("desconocido", texto))
    return salida

def partir_por_comas(linea: str):
    """
    Separa una línea por comas, limpia espacios y clasifica cada fragmento.
    """
    resultado = []
    for pedazo in linea.split(","):
        frag = pedazo.strip()
        if not frag:
            continue  # ignora fragmentos vacíos, ej: "a,,b"
        resultado.extend(clasificar_fragmento(frag))
        print("Resultado", resultado)
    return resultado

# ----------------- Entrada/Salida de archivo -----------------

def cargar_lineas_archivo(ruta: Path):
    """
    Carga todas las líneas no vacías de un archivo de texto.
    Si el archivo no existe o está vacío, lanza error.
    """
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")
    lineas = []
    with ruta.open(encoding="utf-8") as fh:
        for linea in fh:
            s = linea.strip()
            if s:  # solo líneas no vacías
                lineas.append(s)
    if not lineas:
        raise ValueError("El archivo existe pero está vacío.")
    return lineas

def limpiar_prefijo(linea: str):
    """
    Si la línea tiene un prefijo tipo 'entrada15; ...', se elimina y se
    devuelve solo lo de la derecha del ';'.
    """
    if ";" in linea:
        _, derecha = linea.split(";", 1)
        return derecha.strip()
    return linea

# ----------------- Interfaz y salida -----------------

def imprimir_tabla(pares):
    """
    Imprime los tokens en formato tabular:
    N°, TIPO DE TOKEN y LEXEMA (valor encontrado).
    """
    print(f"{'N°':<5}{'TOKEN':<25}{'LEXEMA':<25}")
    print("-" * 60)
    for i, (tipo, lexema) in enumerate(pares, start=1):
        print(f"{i:<5}{tipo:<25}{lexema:<25}")

def pedir_opcion_menu_inicial():
    """
    Muestra un menú inicial con 3 opciones:
    1 = primeras 10 líneas, 2 = últimas 10, 3 = todo.
    Solo acepta números (1, 2, 3). Cualquier otra cosa se rechaza.
    """
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
    """
    Devuelve un subconjunto de las líneas según la opción:
    - 'primeras': primeras 10
    - 'ultimas': últimas 10
    - 'todo': todas
    Cada elemento es una tupla (numero_linea, linea_cruda, linea_limpia).
    """
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
        seleccion.append((i + 1, cruda, limpia))  # numeración desde 1
    return seleccion

def procesar_y_mostrar(seleccion):
    """
    Procesa cada línea seleccionada:
    - Muestra el número de línea y la cadena limpia.
    - Tokeniza con partir_por_comas().
    - Imprime la tabla de tokens.
    - Acumula conteos de cada tipo de token y muestra un resumen.
    """
    conteo = Counter()
    for nlinea, cruda, limpia in seleccion:
        print(f"\n=== Línea {nlinea} ===")
        print(limpia)
        pares = partir_por_comas(limpia)
        imprimir_tabla(pares)
        # Acumular conteos por tipo de token
        conteo.update([tipo for (tipo, _) in pares])
    # Al final del lote, mostrar resumen de cuántos tokens de cada tipo aparecieron
    if conteo:
        print("\n--- Resumen de tokens en este lote ---")
        for tipo, cant in sorted(conteo.items()):
            print(f"{tipo:<25}: {cant}")
        print("--------------------------------------")

# ----------------- Main -----------------

def main():
    """
    Punto de entrada principal del programa.
    - Determina la ruta del archivo (por argumento o 'entrada.txt').
    - Carga todas las líneas útiles.
    - Muestra menú al usuario para elegir primeras/últimas/todas.
    - Procesa y muestra resultados.
    - Pregunta si seguir o salir, y repite hasta que el usuario escriba 'salir'.
    """
    ruta = Path("entrada.txt")
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

# Ejecutar main si el archivo se ejecuta directamente
if __name__ == "__main__":
    main()
