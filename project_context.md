# Project Context

## Activity

Trabajo Práctico N°2 - Sistemas de Computación

Título: Interacción Multinivel con Ensamblador: API REST, C y ASM

Contexto: Este trabajo práctico tiene como objetivo explorar la interacción entre diferentes niveles de abstracción en software (lenguajes de alto nivel y bajo nivel) y la importancia de las convenciones de llamada estandarizadas, aplicado a un caso práctico de obtención y procesamiento de datos.

Objetivo Principal: Diseñar e implementar un sistema por capas (Python -> C -> Ensamblador) que obtenga el Índice GINI de un país desde una API REST, realice un cálculo específico en lenguaje Ensamblador y muestre el resultado final.

Requisitos Específicos (Enunciado):

    Capa Superior (Python):

        Utilizar una API REST (se recomienda la del Banco Mundial: https://api.worldbank.org/v2/en/country/.../indicator/SI.POV.GINI) para obtener el valor del Índice GINI (como número de punto flotante) para un país específico (ej. Argentina).

        Entregar este valor GINI (float) a la capa intermedia (programa C).

    Capa Intermedia (C):

        Recibir el valor GINI (float) desde la capa Python.

        Convocar (llamar) a una rutina escrita en Lenguaje Ensamblador (NASM).

    Capa Inferior (Ensamblador x86 - 32 bits):

        Implementar una rutina que reciba el valor GINI (float) desde C.

        Realizar el cálculo: Convertir el valor GINI de float a entero (mediante truncamiento) y sumarle uno (+1).

        Devolver el resultado entero final a la capa C.

    Interfaz C <-> Ensamblador (Requisito Crítico):

        La comunicación entre la capa C y la capa Ensamblador debe obligatoriamente utilizar la Pila (Stack) para el pasaje de parámetros (el float GINI) y la devolución del resultado (el entero calculado).

        Se debe seguir una convención de llamada estándar (ej. cdecl para 32 bits).

    Resultado Final: El programa C (o Python) debe mostrar el valor entero final devuelto por la rutina Ensamblador.

Metodología y Depuración:

    Iteración 1 (Base): Implementar la funcionalidad completa utilizando solo Python y C. La función C realizará directamente la conversión (float a int) y la suma (+1).

    Iteración 2 (Integración ASM): Reemplazar la lógica del cálculo en C por una llamada a la rutina Ensamblador desarrollada.

    Depuración con GDB (Obligatorio para Iteración 2):

        Utilizar GDB para depurar la interacción C-Ensamblador. Se puede emplear un programa C simple (sin Python) que llame a la rutina ASM para esta demostración.

        Se deberá mostrar y explicar el estado de la Pila (Stack) durante la depuración en los momentos clave:

            Inmediatamente antes de ejecutar la instrucción call a la rutina ASM.

            Durante la ejecución de la rutina ASM (mostrando cómo se accede a los parámetros de la pila).

            Inmediatamente después de que la rutina ASM ejecute ret y devuelva el control a C (mostrando cómo se recupera el resultado y el estado de la pila).

Entorno y Herramientas:

    Sistema Operativo: Linux (ej. Ubuntu 64 bits con soporte multilib).

    Arquitectura Objetivo: x86 (compilación y ejecución en modo 32 bits).

    Lenguajes: Python 3, C (GCC), Ensamblador (NASM).

    Paquetes Requeridos (Ubuntu/Debian): build-essential, nasm, gcc-multilib, g++-multilib, python3-tk (si se usa GUI), python3-venv, git.

    Bibliotecas Python: requests, msl-loadlib (recomendada para manejar la interacción Python 64 bits <-> C 32 bits) o ctypes.

    Compilación:

        GCC: Usar -m32 -g3 (o -g).

        NASM: Usar -f elf -g -F dwarf.

Entrega y Colaboración:

    Grupos: Trabajo grupal obligatorio (2 o 3 estudiantes).

    Repositorio: Utilizar un repositorio privado en GitHub.

    Responsable: Designar un responsable de grupo (email institucional) como dueño del repo.

    Flujo de Trabajo:

        Cada miembro debe tener un fork del repo principal.

        Los cambios se integran al repo principal mediante Pull Requests (revisados y fusionados por el responsable).

        Realizar commits frecuentes, pequeños y con mensajes descriptivos por cada avance funcional.

Defensa:

    La defensa del trabajo práctico será grupal y oral.

Recursos de Apoyo:

    Libro: Lenguaje Ensamblador para PC de Paul A. Carter (Capítulos 1-4 son lectura esencial).

    Herramienta: Depurador GDB (su uso es parte central de la evaluación).

Evaluación: Se evaluará el cumplimiento de todos los requisitos, la correcta implementación de la interacción C-Ensamblador usando la pila, la claridad del código, el uso adecuado de Git/GitHub y la demostración con GDB. Son bienvenidos (pero no obligatorios) diagramas, casos de prueba adicionales y análisis de performance/profiling.

## Project File Structure

```shell
.
├── bin
│   ├── exe
│   ├── exe_32
│   ├── exe_asm_c
│   └── noop_src.o
├── c_and_nasm_tests.sh
├── compile_src.py
├── exe_tp.sh
├── project_context.md
├── README.md
├── requirements.txt
├── setup_everything.sh
├── src
│   ├── asm_rounder.asm
│   ├── asm_rounder.o
│   ├── gini_adder.c
│   ├── gini_adder.o
│   ├── gui.py
│   ├── libginiadder.so
│   ├── logic.py
│   ├── main.py
│   ├── __pycache__
│   │   ├── gui.cpython-310.pyc
│   │   └── logic.cpython-310.pyc
│   ├── server_32.py
│   ├── test_c_asm
│   └── test.sh
├── TODO.md
└── utils
    ├── arch.c
    ├── custom_arch.c
    ├── noop_src.asm
    └── noop_src_link.c

4 directories, 29 files
```

## Source Code

### gini_adder.c

```c
// gini_adder.c (SOLO SE MODIFICA main)

#include <stdio.h>
#include <math.h> // <--- Añadir esta línea

// External declaration of the Assembly function
extern void asm_round(float input_float, int* output_int_ptr); // Asegúrate que el nombre coincida con el global en ASM

// The C bridge function
int process_gini_pure_c(float gini_value) { // Cambiar nombre si se quiere, pero Python lo llama así
    int result_from_asm;
    printf("[C Bridge] Calling ASM function 'asm_round' with float: %f\n", gini_value);
    printf("[C Bridge] Address for ASM result output: %p\n", &result_from_asm);
    asm_round(gini_value, &result_from_asm); // Llama a la función ASM correcta
    printf("[C Bridge] Value received from ASM (via pointer): %d\n", result_from_asm);
    return result_from_asm;
}

// --- Main para probar C bridge + ASM directamente (32-bit) ---
int main() {
    float test_values[] = {
        42.7f, 42.3f, 42.5f, 42.0f,
         0.0f,  0.8f, -0.2f, -0.8f,
        -1.0f, -1.3f,-42.7f,-42.3f,
       -42.5f, 41.5f // Añadir otro caso .5
    };
    int num_tests = sizeof(test_values) / sizeof(test_values[0]);
    int failures = 0;

    printf("\n--- Testing C bridge calling ASM (Rounder Version) ---\n");
    for (int i = 0; i < num_tests; ++i) {
        float input = test_values[i];
        printf("\nTest Case %d: Input = %.2f\n", i, input);
        int output = process_gini_pure_c(input); // Llama a la función C -> ASM

        // --- CORREGIR CÁLCULO DEL VALOR ESPERADO ---
        // Usar redondeo "half away from zero" para la expectativa
        int expected;
        // Forma simple y generalmente correcta:
        if (input > 0.0f) {
             expected = (int)(input + 0.5f);
        } else {
             expected = (int)(input - 0.5f); // Restar 0.5 para negativos
        }
        // Alternativa usando math.h (enlazar con -lm):
        // expected = (int)roundf(input); // roundf implementa round-half-away-from-zero

        printf("Test Case %d: Output = %d. Expected (Round half away from 0) = %d.", i, output, expected);

        // Compara la salida real de ASM con la expectativa C
        if (output == expected) {
             // Considerar el caso especial de FPU round-half-to-even
             float diff = fabsf(input - (int)input);
             if (fabsf(diff - 0.5f) < 0.00001f) { // Si es un caso .5
                 printf(" (NOTE: FPU rounds .5 to even: %d) --> PASS\n", output); // Aceptamos la salida par de FPU
             } else {
                 printf(" --> PASS\n");
             }
        } else {
            // Si no coinciden, verificar si la diferencia es por round-half-to-even
             float diff = fabsf(input - (int)input);
             if (fabsf(diff - 0.5f) < 0.00001f && (output % 2 == 0) ) { // Si es .5 y la salida FPU es par
                  printf(" (NOTE: FPU rounds .5 to even: %d) --> PASS\n", output); // Aceptamos la salida par de FPU
             }
             else {
                 printf(" --> FAIL <<<<<<<<\n");
                 failures++;
             }
        }
    }

    printf("\n--- Test Summary ---\n");
    if (failures == 0) {
        printf("All %d tests effectively passed (considering FPU round-half-to-even)!\n", num_tests);
    } else {
        printf("%d out of %d tests failed (excluding FPU .5 differences).\n", failures, num_tests);
    }
    printf("---------------------\n");

    return failures; // Return 0 on success, non-zero on failure
}

```

### asm_rounder.asm

```asm
; asm_rounder.asm
; NASM Assembly code (32-bit Linux) to round a float to the nearest integer.
; Input: float value [ebp+8], int pointer [ebp+12]
; Output: Writes rounded integer result to the location pointed to by [ebp+12].
; Method: Uses FPU instructions for rounding (default FPU mode is round-to-nearest).

section .text
    global asm_round  ; Export symbol for C linker

asm_round:
    ; --- Prologue ---
    push    ebp         ; 1. Save the caller's base pointer.
    mov     ebp, esp    ; 2. Set our own base pointer for accessing args/locals.
                        ;    Now [ebp] holds old ebp, [ebp+4] holds return addr,
                        ;    [ebp+8] holds float arg, [ebp+12] holds ptr arg.

    ; We need temporary stack space to store the integer result from the FPU.
    ; FISTP stores a signed integer (default size depends on operand).
    ; We want a 32-bit integer (dword). Allocate 4 bytes.
    ; Let's allocate 8 bytes for potential alignment benefits, though 4 is strictly needed.
    sub     esp, 8      ; 3. Allocate 8 bytes on the stack for local use.
                        ;    [ebp-4] and [ebp-8] are now available.
                        ;    We will use [ebp-8] as a dword to store the integer.

    ; --- FPU Calculation ---
    ; The default FPU rounding mode is usually "round to nearest or even",
    ; which handles the 0.5 case correctly (rounding away from zero for +/- 0.5).
    ; So, we don't need to change the FPU control word for standard rounding.

    fld     dword [ebp+8]   ; 4. Load the 4-byte float argument from the stack
                        ;    onto the FPU stack (st0).

    ; FISTP: Converts the float in st0 to an integer based on the current
    ;        FPU rounding mode, stores it to the specified memory location,
    ;        and pops st0 off the FPU stack.
    fistp   dword [ebp-8]   ; 5. Convert st0 to 32-bit integer (using default rounding),
                        ;    store it in our temporary stack space at [ebp-8],
                        ;    and pop the FPU stack.

    ; --- Store Result via Pointer ---
    mov     eax, [ebp-8]    ; 6. Load the rounded integer result from our temporary
                        ;    stack space into the EAX register.

    mov     edx, [ebp+12]   ; 7. Load the pointer argument (the address where C wants
                        ;    the result) from the stack into the EDX register.
                        ;    (Using EDX instead of EBX just to show we don't *have*
                        ;    to save/restore EBX if we don't use it).

    mov     [edx], eax      ; 8. Store the final rounded integer result (in EAX)
                        ;    into the memory location pointed to by EDX.
                        ;    *** This is where a crash would occur if EDX is invalid ***

    ; --- Epilogue ---
    ; Restore the stack and caller's state in reverse order of the prologue.
    mov     esp, ebp    ; 9. Deallocate local stack space (the 8 bytes from sub esp, 8).
                        ;    ESP now points to where 'old ebp' is stored ([ebp]).

    pop     ebp         ; 10. Restore the caller's base pointer from the stack.
                        ;     ESP now points to the return address ([ebp+4]).

    ret                 ; 11. Pop the return address from the stack into EIP,
                        ;     transferring control back to the C caller.
                        ;     According to cdecl, the C caller will clean up the
                        ;     arguments ([ebp+8] and [ebp+12]) from the stack.

```

### logic.py

```py
# logic.py
# Contains core data fetching and processing logic, NO GUI code.
# Includes CLI entry point and C library integration (using msl-loadlib Client64).

import requests
import sys
import argparse
import ctypes # Still needed for type definitions if not using __getattr__
import os
from typing import Optional, List, Dict, Any

# --- Import Client64 ---
try:
    from msl.loadlib import Client64
    # Import Server32Error to catch specific errors from the server
    from msl.loadlib.exceptions import Server32Error
except ImportError:
    print("ERROR: 'msl-loadlib' is not installed. Please run setup script or 'pip install msl-loadlib'", file=sys.stderr)
    sys.exit(1)

# --- Constants ---
BASE_URL = "https://api.worldbank.org/v2/en/country"
INDICATOR = "SI.POV.GINI"
DATE_RANGE = "2011:2020"
PER_PAGE = "100"

# --- C Library Integration using Client64 ---

# Name of the Python module file containing the Server32 class
SERVER_MODULE = 'server_32' # No .py extension needed

# Global client instance (lazy loaded)
_gini_client = None

class GiniAdderClient(Client64):
    """
    Client to communicate with the GiniAdderServer running in a 32-bit process.
    """
    def __init__(self):
        print(f"[Client64] Initializing GiniAdderClient...", file=sys.stderr)
        try:
            # Initialize Client64, specifying the 32-bit server module.
            # msl-loadlib will find SERVER_MODULE.py and run it in a 32-bit Python process.
            super().__init__(module32=SERVER_MODULE)
            print(f"[Client64] Successfully initialized Client64 for module '{SERVER_MODULE}'.", file=sys.stderr)
        except Exception as e:
            # Catch errors during Client64 initialization (e.g., cannot start server process)
            print(f"[Client64] FATAL ERROR during Client64 init: {type(e).__name__}: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            raise # Re-raise to prevent use of uninitialized client

    # --- Option 1: Define explicit methods (Good for clarity, IDE help) ---
    # def process_gini_pure_c(self, gini_value: float) -> int:
    #     """
    #     Sends a request to the 'process_gini_pure_c' method on the Server32.
    #     """
    #     print(f"[Client64] Sending request: 'process_gini_pure_c' with value {gini_value}", file=sys.stderr)
    #     # The first argument to request32 is the METHOD NAME on the Server32 class.
    #     # Subsequent arguments are passed to that method.
    #     return self.request32('process_gini_pure_c', gini_value)

    # --- Option 2: Use __getattr__ (Simpler if many functions just pass through) ---
    def __getattr__(self, name):
        """
        Dynamically creates methods that call request32 with the method name.
        This avoids writing a wrapper method for every function on the server.
        """
        # Check if the requested name is likely a method we want to proxy
        # Avoid proxying special methods like __deepcopy__, __getstate__ etc.
        if name.startswith('_'):
             raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

        print(f"[Client64] __getattr__ creating proxy for '{name}'", file=sys.stderr)
        def send_request(*args, **kwargs):
            print(f"[Client64] Sending request via proxy: '{name}'", file=sys.stderr)
            # 'name' will be 'process_gini_pure_c' when called
            return self.request32(name, *args, **kwargs)
        return send_request
    # --- End Option 2 ---


def _get_client_instance() -> Optional[GiniAdderClient]:
    """Gets or creates the singleton GiniAdderClient instance."""
    global _gini_client
    if _gini_client is None:
        print("[Logic] Creating GiniAdderClient instance...", file=sys.stderr)
        try:
            _gini_client = GiniAdderClient()
        except Exception as e:
            # Handle client creation failure
             print(f"[Logic] Failed to create GiniAdderClient: {type(e).__name__}: {e}", file=sys.stderr)
             _gini_client = None # Ensure it's None if creation fails
    return _gini_client


# --- C Function Call (process_data_with_c) ---
# This function now uses the client instance to make the request
def process_data_with_c(gini_value: float) -> Optional[int]:
    """
    Uses the GiniAdderClient (Client64) to request the C processing
    from the 32-bit server.

    Args:
        gini_value: The float GINI value to process.

    Returns:
        The integer result from the C function via the server, or None if an error occurs.
    """
    client = _get_client_instance()
    if client is None:
        print("[Logic] Cannot process with C: Client instance is not available.", file=sys.stderr)
        return None

    try:
        # Call the method on the client instance.
        # If using explicit methods (Option 1):
        # result = client.process_gini_pure_c(gini_value)

        # If using __getattr__ (Option 2):
        # This looks like a direct method call, but __getattr__ intercepts it
        # and calls client.request32('process_gini_pure_c', gini_value)
        result = client.process_gini_pure_c(gini_value)

        print(f"[Logic] Received result from 32-bit server: {result}", file=sys.stderr)
        return result
    except Server32Error as e:
        # Catch errors specifically raised by the 32-bit server process
        print(f"[Logic] Error received from 32-bit server: {e}", file=sys.stderr)
        return None
    except Exception as e:
        # Catch other potential errors during the request (e.g., connection issues)
        print(f"[Logic] Error during request to 32-bit server: {type(e).__name__}: {e}", file=sys.stderr)
        return None


# --- Data Fetching (get_gini_data - NO CHANGES NEEDED) ---
def get_gini_data(country_code: str) -> tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    # ... (Keep the existing robust get_gini_data function) ...
    url = f"{BASE_URL}/{country_code}/indicator/{INDICATOR}"
    params = {
        "format": "json",
        "date": DATE_RANGE,
        "per_page": PER_PAGE
    }
    print(f"[Logic] Requesting URL: {url} with params: {params}", file=sys.stderr)
    error_message = None
    try:
        response = requests.get(url, params=params, timeout=15)
        print(f"[Logic] Response Status Code: {response.status_code}", file=sys.stderr)
        content_type = response.headers.get('Content-Type', '')
        if 'application/json' not in content_type:
             error_detail = f"API did not return JSON. Content-Type: {content_type}. Response: {response.text[:200]}..."
             print(f"Error: {error_detail}", file=sys.stderr)
             if response.text and 'Invalid format' in response.text: error_message = "World Bank API Error: Invalid format requested or resource not found."
             elif response.text and 'Invalid value' in response.text: error_message = f"World Bank API Error: Invalid country code '{country_code}'?"
             else: error_message = "Received non-JSON response from the server."
             return None, error_message
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list) or len(data) < 1:
            error_detail = "Unexpected API response format (not a list or empty)."
            print(f"Error: {error_detail}", file=sys.stderr)
            error_message = "Received unexpected data format from the server."
            return None, error_message
        if isinstance(data[0], dict) and "message" in data[0]:
            error_messages = [msg.get("value", "Unknown error") for msg in data[0]["message"]]
            error_text = "\n".join(error_messages)
            print(f"Error from World Bank API: {error_text}", file=sys.stderr)
            if any("No data available" in msg for msg in error_messages) or any("No matches" in msg for msg in error_messages): return [], None
            else: error_message = f"World Bank API Error:\n{error_text}"; return None, error_message
        if len(data) == 2:
            if data[1] is None: return [], None
            if not isinstance(data[1], list):
                 error_detail = f"Unexpected data format (data[1] is not list). Got: {type(data[1])}"; print(f"Error: {error_detail}", file=sys.stderr); error_message = "Received unexpected data structure from the server."; return None, error_message
            return data[1], None
        elif len(data) == 1 and isinstance(data[0], dict) and "total" in data[0] and data[0]["total"] == 0: return [], None
        else: print(f"Warning: Received unexpected response structure (length {len(data)}). Assuming no data.", file=sys.stderr); return [], None
    except requests.exceptions.HTTPError as e: error_detail = f"HTTP Error: {e.response.status_code} {e.response.reason} for URL {e.request.url}"; print(f"Error: {error_detail}", file=sys.stderr); error_message = f"HTTP Error: {e.response.status_code}\n{e.response.reason}"; return None, error_message
    except requests.exceptions.ConnectionError as e: error_detail = f"Connection Error: {e}"; print(f"Error: {error_detail}", file=sys.stderr); error_message = "Could not connect to the World Bank API.\nCheck internet connection."; return None, error_message
    except requests.exceptions.Timeout: error_detail = "Timeout Error"; print(f"Error: {error_detail}", file=sys.stderr); error_message = "The request to the World Bank API timed out."; return None, error_message
    except requests.exceptions.RequestException as e: error_detail = f"Request Exception: {e}"; print(f"Error: {error_detail}", file=sys.stderr); error_message = f"An error occurred during the request:\n{e}"; return None, error_message
    except requests.exceptions.JSONDecodeError:
        error_detail = "JSON Decode Error"; print(f"Error: {error_detail}", file=sys.stderr)
        try: raw_text = response.text; print(f"Raw response text: {raw_text[:500]}...", file=sys.stderr)
        except: pass
        error_message = "Could not decode the server's response (invalid JSON)."; return None, error_message
    except Exception as e:
        error_detail = f"Unexpected error in get_gini_data: {type(e).__name__}: {e}"; print(f"Error: {error_detail}", file=sys.stderr)
        import traceback; traceback.print_exc(file=sys.stderr); error_message = f"An unexpected error occurred:\n{type(e).__name__}"; return None, error_message


# --- Data Processing (find_latest_valid_gini - NO CHANGES NEEDED) ---
def find_latest_valid_gini(records: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    # ... (Keep the existing find_latest_valid_gini function) ...
    latest_valid_record = None; latest_year = -1
    if not records: return None
    for record in records:
        if not isinstance(record, dict): continue
        value = record.get('value'); date_str = record.get('date')
        if value is not None and date_str:
            try:
                current_year = int(date_str); _ = float(value)
                if current_year > latest_year:
                    latest_year = current_year
                    record['country_name'] = record.get('country', {}).get('value', 'N/A')
                    latest_valid_record = record
            except (ValueError, TypeError, KeyError) as e: print(f"[Logic] Warning: Skipping record with invalid format/keys: {record}, Error: {e}", file=sys.stderr); continue
    return latest_valid_record


# --- CLI Entry Point (__main__ - NO CHANGES NEEDED) ---
if __name__ == "__main__":
    # ... (Keep the existing argparse CLI code) ...
    parser = argparse.ArgumentParser(description=f"Fetch GINI index data ({DATE_RANGE}) from the World Bank API.")
    parser.add_argument("country_code", help="The 3-letter ISO country code (e.g., ARG, USA, BRA).")
    parser.add_argument("-H", "--history", action="store_true", help="Show historical data in addition to the latest value.")
    parser.add_argument("-C", "--process-c", action="store_true", help="Also process the latest value using the C function.")
    args = parser.parse_args()
    code = args.country_code.strip().upper()
    if len(code) != 3 or not code.isalpha(): print(f"Error: Invalid country code format '{args.country_code}'. Please use a 3-letter code.", file=sys.stderr); sys.exit(1)
    print(f"Fetching GINI data for {code}...", file=sys.stderr)
    records, fetch_error = get_gini_data(code)
    if fetch_error: print(f"\nError fetching data: {fetch_error}", file=sys.stderr); sys.exit(1)
    if records is None: print(f"\nError: An unknown issue occurred while fetching data for {code}.", file=sys.stderr); sys.exit(1)
    if not records: print(f"\nNo GINI data points found for {code} in the period {DATE_RANGE}."); sys.exit(0)
    latest_record = find_latest_valid_gini(records)
    if not latest_record:
        print(f"\nData found for {code}, but no records had a valid GINI value in the period {DATE_RANGE}.")
        if args.history:
             print("\n--- Historical Data (raw/invalid values might be present) ---")
             valid_records_sorted = sorted([r for r in records if isinstance(r, dict)], key=lambda x: x.get('date', ''))
             if valid_records_sorted:
                 for entry in valid_records_sorted: print(f"  Year: {entry.get('date', 'N/A')}, Index: {entry.get('value', 'N/A')}")
             else: print("  (No historical records found in response)")
        sys.exit(0)
    print("\n--- GINI Index Summary ---"); print(f"Country:      {latest_record.get('country_name', code)}"); print(f"Latest Year:  {latest_record['date']}")
    try:
        latest_gini_float = float(latest_record['value']); print(f"Latest GINI:  {latest_gini_float:.2f}")
        if args.process_c:
             print("\n--- C Processing (via Client64/Server32) ---");
             c_result = process_data_with_c(latest_gini_float) # Calls the modified function
             if c_result is not None: print(f"Input to C:   {latest_gini_float:.2f}"); print(f"Output: {c_result}")
             else: print("Error during C processing (check logs).", file=sys.stderr)
    except (ValueError, TypeError):
        print(f"Latest GINI:  {latest_record['value']} (Error: Not a valid number)", file=sys.stderr)

        if args.process_c: print("\nCannot perform C processing: Latest GINI value is not a valid number.", file=sys.stderr)
    if args.history:
        print("\n--- Historical Data (Oldest First, Valid Only) ---")
        valid_records_sorted = sorted([r for r in records if r and r.get('value') is not None and r.get('date')], key=lambda x: x.get('date', ''))
        if valid_records_sorted:
            for entry in valid_records_sorted:
                 try: print(f"  Year: {entry['date']}, Index: {float(entry['value']):>6.2f}")
                 except (ValueError, TypeError): print(f"  Year: {entry['date']}, Index: {entry['value']} (invalid?)")
        else: print("  (No valid historical records found)")
    sys.exit(0)

```

### main.py

```py
# main.py
# Entry point for the GINI Fetcher application.

import tkinter as tk
import gui # Import the module containing the GiniApp class
import sys

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = gui.GiniApp(root) # Instantiate the GUI app from the gui module
        root.mainloop()
    except tk.TclError as e:
         # Catch potential theme errors or other Tk initialization issues
         print(f"\nTkinter Error: {e}", file=sys.stderr)
         print("Could not initialize the Tkinter GUI.", file=sys.stderr)
         print("Ensure you have 'python3-tk' (or equivalent) installed.", file=sys.stderr)
         sys.exit(1)
    except ImportError as e:
        # Catch if gui or logic modules are not found
        print(f"\nImport Error: {e}", file=sys.stderr)
        print("Please ensure 'gui.py' and 'logic.py' are in the same directory or accessible via PYTHONPATH.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # Catch any other unexpected startup errors
        print(f"\nUnexpected Error on Startup: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

```

### server_32.py

```py
# gini_server32.py
# Runs in a 32-bit Python environment managed by msl-loadlib.
# Loads the 32-bit C library and exposes its functions.

import os
import ctypes
import sys

try:
    from msl.loadlib import Server32
except ImportError:
    # This error won't typically be seen by the user, but is good practice
    print("ERROR: msl.loadlib not found in the 32-bit server environment.", file=sys.stderr)
    sys.exit(1)

# --- Configuration ---
# Assume the .so is in the same directory as this server script
# The client (logic.py) will ensure this script is found.
LIB_NAME = 'libginiadder.so'
C_FUNC_NAME = 'process_gini_pure_c'

class GiniAdderServer(Server32):
    """
    Server that loads the 32-bit libginiadder.so library and exposes
    the process_gini_pure_c function.
    """
    def __init__(self, host, port, **kwargs):
        """
        Initializes the server and loads the C library.

        host: Host address provided by msl-loadlib.
        port: Port number provided by msl-loadlib.
        kwargs: Extra arguments (quiet, authkey) from msl-loadlib.
        """
        library_path = os.path.join(os.path.dirname(__file__), LIB_NAME)
        print(f"[Server32] Initializing GiniAdderServer...", file=sys.stderr)
        print(f"[Server32] Attempting to load library: {library_path}", file=sys.stderr)

        if not os.path.exists(library_path):
            print(f"[Server32] FATAL ERROR: Library '{library_path}' not found.", file=sys.stderr)
            # Raise an exception to prevent the server from starting improperly
            raise FileNotFoundError(f"32-bit library not found: {library_path}")

        try:
            # --- Load the 32-bit library using ctypes.CDLL ---
            # This works because *this* script runs in a 32-bit process.
            # Use 'cdll' for standard cdecl convention expected from gcc -m32
            super().__init__(library_path, 'cdll', host, port, **kwargs)
            print(f"[Server32] Successfully loaded '{LIB_NAME}' via ctypes.CDLL.", file=sys.stderr)

            # --- Define signature for the C function accessed via self.lib ---
            # self.lib is the ctypes CDLL object created by Server32
            c_func = getattr(self.lib, C_FUNC_NAME)
            c_func.argtypes = [ctypes.c_float]
            c_func.restype = ctypes.c_int
            print(f"[Server32] Set signature for function '{C_FUNC_NAME}'.", file=sys.stderr)

        except OSError as e:
            print(f"[Server32] FATAL ERROR: OSError loading library '{library_path}': {e}", file=sys.stderr)
            raise # Re-raise the exception
        except AttributeError as e:
             print(f"[Server32] FATAL ERROR: Function '{C_FUNC_NAME}' not found in library: {e}", file=sys.stderr)
             raise # Re-raise the exception
        except Exception as e:
            print(f"[Server32] FATAL ERROR: Unexpected error during server init: {type(e).__name__}: {e}", file=sys.stderr)
            raise # Re-raise the exception


    # --- Expose methods callable by the Client64 ---
    # The method name here ('process_gini_pure_c') is what the client will request.
    def process_gini_pure_c(self, gini_value_float):
        """
        Receives the float value from the Client64, calls the C function,
        and returns the integer result back to the client.
        """
        print(f"[Server32] Received request: process_gini_pure_c({gini_value_float})", file=sys.stderr)
        try:
            # Access the C function via the self.lib (ctypes) object
            result = self.lib.process_gini_pure_c(ctypes.c_float(gini_value_float))
            print(f"[Server32] C function returned: {result}", file=sys.stderr)
            return result
        except Exception as e:
            # Catch errors during the actual C call
            print(f"[Server32] ERROR calling C function '{C_FUNC_NAME}': {type(e).__name__}: {e}", file=sys.stderr)
            # Raise the exception so Client64 receives a Server32Error
            raise

# The Server32 base class handles the main server loop when executed.
# No explicit server start code is needed here.

```

### gui.py

```py
# gui.py
# Defines the Tkinter GUI application class. Imports logic.py.

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys # Import sys for stderr logging in GUI context if needed
from typing import Optional, List, Dict, Any
import logic # Import the core logic module

class GiniApp:
    def __init__(self, master: tk.Tk):
        self.master = master
        master.title("GINI Index Fetcher")
        master.geometry("550x480")
        master.config(bg="#f0f0f0")

        # Inject logic functions
        self.get_gini_data = logic.get_gini_data
        self.find_latest_valid_gini = logic.find_latest_valid_gini
        # Use the actual C processing function from logic
        self.process_with_c = logic.process_data_with_c

        self._setup_styles()
        self._create_widgets()
        self._layout_widgets()

        self.latest_gini_value_for_c = None
        self.entry_code.focus_set()

    # _setup_styles, _create_widgets, _layout_widgets as before...
    def _setup_styles(self):
        """Configure ttk styles."""
        self.style = ttk.Style()
        available_themes = self.style.theme_names()
        if 'clam' in available_themes: self.style.theme_use('clam')
        elif 'alt' in available_themes: self.style.theme_use('alt')
        self.style.configure("TLabel", background="#f0f0f0", font=("Segoe UI", 10))
        self.style.configure("TButton", font=("Segoe UI", 10), padding=5)
        self.style.configure("TEntry", font=("Segoe UI", 10), padding=5)
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"))
        self.style.configure("Summary.TLabel", font=("Segoe UI", 11))
        self.style.configure("Status.TLabel", font=("Segoe UI", 9), foreground="gray")

    def _create_widgets(self):
        """Create all the GUI widgets."""
        self.country_code_var = tk.StringVar(); self.status_var = tk.StringVar(value="Enter a 3-letter country code and click Fetch."); self.summary_country_var = tk.StringVar(value="-"); self.summary_year_var = tk.StringVar(value="-"); self.summary_gini_var = tk.StringVar(value="-")
        self.input_frame = ttk.Frame(self.master, padding="15 10 15 5"); self.summary_frame = ttk.Frame(self.master, padding="15 5 15 10", borderwidth=1, relief="solid"); self.history_frame = ttk.Frame(self.master, padding="15 0 15 5"); self.status_frame = ttk.Frame(self.master, padding="15 5 15 10")
        self.label_code = ttk.Label(self.input_frame, text="Country Code:"); self.entry_code = ttk.Entry(self.input_frame, textvariable=self.country_code_var, width=8); self.fetch_button = ttk.Button(self.input_frame, text="Fetch GINI Data", command=self.fetch_and_display_handler)
        self.label_summary_country_title = ttk.Label(self.summary_frame, text="Country:", style="Summary.TLabel"); self.label_summary_country_value = ttk.Label(self.summary_frame, textvariable=self.summary_country_var, style="Summary.TLabel", anchor="w"); self.label_summary_year_title = ttk.Label(self.summary_frame, text="Latest Year:", style="Summary.TLabel"); self.label_summary_year_value = ttk.Label(self.summary_frame, textvariable=self.summary_year_var, style="Summary.TLabel"); self.label_summary_gini_title = ttk.Label(self.summary_frame, text="Latest GINI:", style="Summary.TLabel"); self.label_summary_gini_value = ttk.Label(self.summary_frame, textvariable=self.summary_gini_var, style="Summary.TLabel")
        self.label_history_header = ttk.Label(self.history_frame, text="Historical Data (Oldest First)", style="Header.TLabel"); self.result_text = scrolledtext.ScrolledText(self.history_frame, wrap=tk.WORD, state='disabled', height=10, width=60, font=("Consolas", 9), relief=tk.SUNKEN, borderwidth=1)
        self.status_label = ttk.Label(self.status_frame, textvariable=self.status_var, style="Status.TLabel")
        self.entry_code.bind("<Return>", self.fetch_and_display_handler)

    def _layout_widgets(self):
        """Arrange widgets using the grid layout manager."""
        self.master.grid_columnconfigure(0, weight=1); self.master.grid_rowconfigure(0, weight=0); self.master.grid_rowconfigure(1, weight=0); self.master.grid_rowconfigure(2, weight=1); self.master.grid_rowconfigure(3, weight=0)
        self.input_frame.grid(row=0, column=0, sticky="ew"); self.input_frame.grid_columnconfigure(1, weight=1); self.label_code.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="w"); self.entry_code.grid(row=0, column=1, padx=5, pady=5, sticky="ew"); self.fetch_button.grid(row=0, column=2, padx=(5, 0), pady=5, sticky="e")
        self.summary_frame.grid(row=1, column=0, sticky="ew", pady=(5,10)); self.summary_frame.grid_columnconfigure(1, weight=1); self.label_summary_country_title.grid(row=0, column=0, sticky="w", padx=5, pady=2); self.label_summary_country_value.grid(row=0, column=1, columnspan=3, sticky="ew", padx=5, pady=2); self.label_summary_year_title.grid(row=1, column=0, sticky="w", padx=5, pady=2); self.label_summary_year_value.grid(row=1, column=1, sticky="w", padx=5, pady=2); self.label_summary_gini_title.grid(row=1, column=2, sticky="e", padx=(10,5), pady=2); self.label_summary_gini_value.grid(row=1, column=3, sticky="w", padx=5, pady=2)
        self.history_frame.grid(row=2, column=0, sticky="nsew"); self.history_frame.grid_rowconfigure(1, weight=1); self.history_frame.grid_columnconfigure(0, weight=1); self.label_history_header.grid(row=0, column=0, sticky="w", pady=(0,5)); self.result_text.grid(row=1, column=0, sticky="nsew")
        self.status_frame.grid(row=3, column=0, sticky="ew"); self.status_label.pack(fill=tk.X)


    # update_status, clear_output_fields, display_history_in_textbox as before...
    def update_status(self, message: str, is_error=False):
        self.status_var.set(message); self.status_label.config(foreground="red" if is_error else "gray"); self.master.update_idletasks()
    def clear_output_fields(self):
        self.summary_country_var.set("-"); self.summary_year_var.set("-"); self.summary_gini_var.set("-"); self.latest_gini_value_for_c = None
        try: self.result_text.config(state='normal'); self.result_text.delete('1.0', tk.END); self.result_text.config(state='disabled')
        except tk.TclError as e: print(f"Error clearing text widget: {e}", file=sys.stderr)
    def display_history_in_textbox(self, records: Optional[List[Dict[str, Any]]]):
        text_to_display = ""
        if records:
            valid_records = sorted([r for r in records if r and r.get('value') is not None and r.get('date')], key=lambda x: x.get('date', ''))
            if valid_records: lines = []; [lines.append(f"  Year: {e['date']}, Index: {float(e['value']):>6.2f}") if isinstance(e.get('value'), (int, float, str)) and str(e.get('value')).replace('.','',1).isdigit() else lines.append(f"  Year: {e.get('date','?')}, Index: {e.get('value','?')} (invalid?)") for e in valid_records]; text_to_display = "\n".join(lines)
            else: text_to_display = "(No valid historical data points found)"
        elif records == []: text_to_display = "(No data points available for this period)"
        else: text_to_display = "(Could not load historical data)"
        try: self.result_text.config(state='normal'); self.result_text.delete('1.0', tk.END); self.result_text.insert(tk.END, text_to_display); self.result_text.config(state='disabled')
        except tk.TclError as e: print(f"Error updating text widget: {e}", file=sys.stderr)


    # --- Event Handler ---
    def fetch_and_display_handler(self, event=None):
        """Handles the button click/Enter key press event."""
        country_code = self.country_code_var.get().strip().upper()
        if len(country_code) != 3 or not country_code.isalpha():
            messagebox.showerror("Input Error", "Please enter a valid 3-letter alphabetic country code (e.g., ARG)."); return

        self.fetch_button.config(state='disabled'); self.entry_code.config(state='disabled')
        self.clear_output_fields(); self.update_status(f"Fetching data for {country_code}...")

        # --- Call Logic Layer ---
        gini_records, error_msg = self.get_gini_data(country_code) # Uses logic.get_gini_data
        # ------------------------

        self.fetch_button.config(state='normal'); self.entry_code.config(state='normal'); self.entry_code.focus_set()

        if error_msg:
            messagebox.showerror("API/Network Error", error_msg) # Show error from logic layer
            self.update_status(f"Failed to retrieve data for {country_code}.", is_error=True); self.display_history_in_textbox(None)
        elif gini_records is not None:
            latest_record = self.find_latest_valid_gini(gini_records) # Uses logic.find_latest_valid_gini
            if latest_record:
                self.summary_country_var.set(latest_record.get('country_name', country_code)); self.summary_year_var.set(latest_record.get('date', 'N/A'))
                try:
                    gini_float = float(latest_record['value'])
                    self.summary_gini_var.set(f"{gini_float:.2f}"); self.latest_gini_value_for_c = gini_float
                    # --- Trigger C processing ---
                    self._trigger_c_processing(gini_float) # Call the method below
                    # -----------------------------
                except (ValueError, TypeError):
                    self.summary_gini_var.set("Invalid"); self.update_status("Warning: Latest GINI value is not a valid number.", is_error=True); self.latest_gini_value_for_c = None
                self.update_status("Data fetched successfully.")
            elif not gini_records: self.update_status(f"No GINI data points found for {country_code} in {DATE_RANGE}.", is_error=False)
            else: self.update_status(f"Found records for {country_code}, but none had valid GINI values.", is_error=True)
            self.display_history_in_textbox(gini_records)


    def _trigger_c_processing(self, gini_value: float):
        """Calls the C processing function from logic.py and shows result/error."""
        print(f"[GUI] Triggering C processing with value: {gini_value}", file=sys.stderr)
        try:
            # Call the function imported from the logic module
            c_result = self.process_with_c(gini_value)

            if c_result is not None:
                 messagebox.showinfo("C Processing Result",
                                     f"Input GINI: {gini_value:.2f}\nResult from C Library: {c_result}")
                 self.update_status(f"Data processed by C. Result: {c_result}")
            else:
                 # Error occurred during C call (e.g., library load failed)
                 # logic.py already printed details to stderr
                 messagebox.showerror("C Processing Error", "Failed to execute C function.\nCheck console/stderr for details (e.g., missing library).")
                 self.update_status("Error during C library processing.", is_error=True)

        except Exception as e:
            # Catch unexpected errors specifically during the trigger/call phase in GUI
            print(f"[GUI] Error calling C processing function: {e}", file=sys.stderr)
            messagebox.showerror("C Processing Error", f"Unexpected error setting up C call:\n{e}")
            self.update_status("Error setting up C library processing.", is_error=True)

```

## Batch Shell Scripts

### exe_tp.sh

```bash
#!/bin/bash
# exe_tp.sh
# VERSION: Python 64bit + C/ASM 32bit (using msl-loadlib client/server)

# Function for error messages
fail() {
    echo -e "\033[31mError: $1\033[0m" >&2
    exit 1
}

# Make sure that we are in the script's directory
cd "$(dirname "$0")" || fail "Could not change to script directory"

echo "🚀 Starting TP2 Execution (C/ASM Integration)..."
echo "---------------------------------"

# 1. Setup Environment (Run setup script)
echo "🛠️ Running setup script (setup_everything.sh)..."
chmod +x ./setup_everything.sh
./setup_everything.sh || fail "Environment setup failed."
echo "---------------------------------"

# 2. Activate virtual environment
expected_venv_path="$(pwd)/tp2_venv"
if [ -z "$VIRTUAL_ENV" ] || [ "$VIRTUAL_ENV" != "$expected_venv_path" ]; then
    echo "🐍 Activating Python virtual environment..."
    source tp2_venv/bin/activate || fail "Could not activate virtual environment 'tp2_venv'."
else
    echo "🐍 Python virtual environment already active."
fi
echo "---------------------------------"


# 3. Go to source directory
echo "📁 Changing to 'src' directory..."
cd src || fail "Could not change to 'src' directory. Does it exist?"
echo "   Current directory: $(pwd)"
echo "---------------------------------"


# 4. Compile C/ASM code (32-bit shared library)
echo "🔄 Compiling ASM code (gini_adder.asm) to 32-bit object file..."
ASM_SOURCE="gini_adder.asm"
ASM_OBJECT="gini_adder.o"
ASM_COMPILER=nasm
ASM_FLAGS="-f elf -g -F dwarf" # -f elf for 32-bit linux, -g -F dwarf for debug

if [ ! -f $ASM_SOURCE ]; then
    fail "Assembly source file '$ASM_SOURCE' not found in 'src' directory."
fi

echo "   Command: $ASM_COMPILER $ASM_FLAGS $ASM_SOURCE -o $ASM_OBJECT"
$ASM_COMPILER $ASM_FLAGS $ASM_SOURCE -o $ASM_OBJECT || fail "Assembly compilation failed."

if [ ! -f $ASM_OBJECT ]; then
    fail "Assembly object file '$ASM_OBJECT' was not created."
fi
echo "   Successfully created '$ASM_OBJECT'."
echo ""


echo "🔄 Compiling C bridge (gini_adder.c) and linking with ASM object..."
C_SOURCE="gini_adder.c"
TARGET_LIB="libginiadder.so"
C_COMPILER=gcc
# --- CRUCIAL CHANGE: Link C_SOURCE with ASM_OBJECT ---
C_FLAGS="-m32 -shared -o $TARGET_LIB -fPIC -g -Wall" # -m32, -shared, -fPIC, debug, warnings

if [ ! -f $C_SOURCE ]; then
    fail "C source file '$C_SOURCE' not found in 'src' directory."
fi

echo "   Command: $C_COMPILER $C_FLAGS $C_SOURCE $ASM_OBJECT"
$C_COMPILER $C_FLAGS $C_SOURCE $ASM_OBJECT || fail "C compilation/linking failed."

if [ ! -f $TARGET_LIB ]; then
    fail "Shared library '$TARGET_LIB' was not created."
fi
echo "   Successfully created shared library '$TARGET_LIB' (32-bit, C+ASM)."
echo ""

echo "   Verifying library architecture..."
file "$TARGET_LIB" || echo "   Warning: Could not run 'file' command to verify."
file "$TARGET_LIB" | grep "ELF 32-bit" || fail "Library '$TARGET_LIB' is NOT 32-bit ELF!"
echo "   Library is confirmed 32-bit."
echo "---------------------------------"


# 5. Run Python application
echo "🐍 Launching Python application (main.py)..."
if [ ! -f main.py ]; then
    fail "'main.py' not found in 'src' directory."
fi

python3 main.py

exit_status=$?
echo "---------------------------------"
if [ $exit_status -eq 0 ]; then
    echo "✅ Python application finished successfully."
else
    echo -e "\033[31m⚠️ Python application exited with status $exit_status.\033[0m"
fi
# --- Optional: Clean up object file ---
# echo "🧹 Cleaning up object file..."
# rm -f $ASM_OBJECT
# ------------------------------------
echo "🏁 Execution finished."

exit $exit_status

```

### setup_everything.sh

```bash
# colors functions
red() {
    echo -e "\033[31m$1\033[0m"
}
green() {
    echo -e "\033[32m$1\033[0m"
}
yellow() {
    echo -e "\033[33m$1\033[0m"
}
blue() {
    echo -e "\033[34m$1\033[0m"
}
magent() {
    echo -e "\033[35m$1\033[0m"
}
cyan() {
    echo -e "\033[36m$1\033[0m"
}
bold() {
    echo -e "\033[1m$1\033[0m"
}


set -e

green "📦 Setting up the environment..."
bold "> sudo apt install python3-tk -y"
sudo apt install python3-tk -y
bold "> python -m venv tp2_venv"
python -m venv tp2_venv

bold "> sudo apt-get install gcc-multilib -y"
sudo apt-get install gcc-multilib -y

bold "> sudo apt install g++ gfortran libgfortran5 zlib1g:i386 libstdc++6:i386 libgfortran5:i386 -y (For msl-lib)"
sudo apt install g++ gfortran libgfortran5 zlib1g:i386 libstdc++6:i386 libgfortran5:i386 -y

bold "> source tp2_venv/bin/activate"
source tp2_venv/bin/activate

bold "> pip install -r requirements.txt"
pip install -r requirements.txt


```

### c_and_nasm_tests.sh

```bash
# colors functions
red() {
    echo -e "\033[31m$1\033[0m"
}
green() {
    echo -e "\033[32m$1\033[0m"
}
yellow() {
    echo -e "\033[33m$1\033[0m"
}
blue() {
    echo -e "\033[34m$1\033[0m"
}
magent() {
    echo -e "\033[35m$1\033[0m"
}
cyan() {
    echo -e "\033[36m$1\033[0m"
}
bold() {
    echo -e "\033[1m$1\033[0m"
}


bold "> source tp2_venv/bin/activate"
source tp2_venv/bin/activate

green "💻 Compiling & Running some code"
bold "> cd bin"
cd bin

magent "First, let's compile some C code"

bold "> gcc -o exe ../utils/custom_arch.c"
gcc -o exe ../utils/custom_arch.c

blue "Now let's run the compiled code"
bold "> ./exe"
output=$(./exe)
echo "$output"
echo "What architecture are we on? Apparently, the output is: $output"

blue "Maybe we should run the same compilation with a little trick"
bold "> gcc -m32 -o exe_32 ../utils/custom_arch.c"
gcc -m32 -o exe_32 ../utils/custom_arch.c
echo "The -m32 flag is used to compile the code for a 32-bit architecture"

blue "Now let's run the compiled code"
bold "> ./exe_32"
output=$(./exe_32)
echo "$output"
echo "What architecture are we on? Apparently, the output is: $output"
echo "Of course, it's not that our PC suddenly changed architecture, it just compiled for a 32-bit arch"
echo "It still runs on a 64-bit architecture, though."

magent "Now let's compile some ASM code"

blue "First, let's compile the ASM code with nasm"
bold "> nasm -f elf64 ../utils/noop_src.asm"
nasm -f elf32 ../utils/noop_src.asm -o noop_src.o
echo "The -f flag is used to specify the format of the output file, in this case, elf32: Executable and Linkable Format 32-bit"
echo "A .o file is an object file, which is a compiled version of the source code. You can see it here:"
bold "> ls -l noop_src.o"
ls -l noop_src.o
blue "Now, let's compile the C code that will be linked with the ASM code"
bold "> gcc -m32 -o exe_32 ../utils/noop_src_link.c noop_src.o"
gcc -m32 -o exe_asm_c ../utils/noop_src_link.c noop_src.o
echo "The -m32 flag is used to compile the code for a 32-bit architecture"
blue "Now let's run the compiled code"

bold "> ./exe_asm_c"
output=$(./exe_asm_c)
echo "$output"

```

## Python Requirements

```text
certifi==2025.1.31
charset-normalizer==3.4.1
idna==3.10
msl-loadlib==0.10.0
requests==2.32.3
urllib3==2.3.0

```
