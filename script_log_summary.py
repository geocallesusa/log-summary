import os
import re
import sys
from typing import Iterable, NamedTuple, TextIO


# ---------------------------------------------------------------------------
# Compiled regex constants
# ---------------------------------------------------------------------------

SEVERITY_PATTERN = re.compile(r'^\[(INFO|WARNING|ERROR)\]', re.IGNORECASE)

TIMESTAMP_PATTERN = re.compile(
    r'\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])'
)

class ParseResult(NamedTuple):
    severity: str | None          # "INFO" | "WARNING" | "ERROR" | None
    has_valid_timestamp: bool     # True if a YYYY-MM-DD date is present and valid
    is_blank: bool                # True if line is empty or whitespace-only

class AnalysisResult(NamedTuple):
    total: int       
    info: int        
    warning: int
    error: int
    malformed: int

def abrir_log_file(path: str) -> TextIO:
    try:
        return open(path, encoding="utf-8")
    except FileNotFoundError:
        print("Error: El archivo '{path}' no fue encontrado.")
        sys.exit(1)
    except PermissionError:
        print("Error: No se tienen permisos para leer el archivo '{path}'.")
        sys.exit(1)

def obtener_path_archivo() -> str:
    try:
        path = input("Ingrese la ruta del archivo de logs: ").strip()
    except EOFError:
        path = ""
    if not path:
        print("Error: Debe proporcionar una ruta de archivo válida.")
        sys.exit(1)
    return path

# parsea y valida el tipo de log y la fecha en cada línea del archivo de log
def parse_line(line: str) -> ParseResult:
    stripped = line.strip()

    if not stripped:
        return ParseResult(severity=None, has_valid_timestamp=False, is_blank=True)

    severity_match = SEVERITY_PATTERN.match(stripped)
    severity = severity_match.group(1).upper() if severity_match else None

    has_valid_timestamp = bool(TIMESTAMP_PATTERN.search(stripped))

    return ParseResult(
        severity=severity,
        has_valid_timestamp=has_valid_timestamp,
        is_blank=False,
    )


def analyze(lines: Iterable[str]) -> AnalysisResult:
    total = info = warning = error = malformed = 0

    for line in lines:
        parsed = parse_line(line)

        if parsed.is_blank:
            continue

        total += 1

        if parsed.severity == "INFO":
            info += 1
        elif parsed.severity == "WARNING":
            warning += 1
        elif parsed.severity == "ERROR":
            error += 1

        # Malformed if missing severity OR missing valid timestamp
        if parsed.severity is None or not parsed.has_valid_timestamp:
            malformed += 1

    return AnalysisResult(
        total=total,
        info=info,
        warning=warning,
        error=error,
        malformed=malformed,
    )

def print_report(result: AnalysisResult, filename: str) -> None:
    basename = os.path.basename(filename)

    if result.total == 0:
        print("El archivo no contiene entradas para analizar.")

    print("========== RESUMEN DE ANÁLISIS ==========")
    print(f"Archivo analizado : {basename}")
    print(f"Total de eventos  : {result.total}")
    print("-----------------------------------------")
    print(f"  INFO            : {result.info}")
    print(f"  WARNING         : {result.warning}")
    print(f"  ERROR           : {result.error}")
    print("-----------------------------------------")
    print(f"Entradas mal formateadas: {result.malformed}")
    print("=========================================")            



def main() -> None:
    path = obtener_path_archivo()
    file_handle = abrir_log_file(path)
    with file_handle:
        result = analyze(file_handle)
    print_report(result, path)


if __name__ == "__main__":
    main()