# TP2 - Sistemas de Computación: Interacción Multinivel con Ensamblador

Este proyecto implementa un sistema por capas (Python -> C -> Ensamblador) para obtener el Índice GINI de un país desde una API REST, realizar un cálculo específico en Ensamblador y mostrar el resultado. Demuestra la interacción entre niveles de abstracción y el uso de convenciones de llamada (`cdecl`) y la pila para el pasaje de parámetros entre C y ASM. Utiliza `msl-loadlib` para la comunicación entre Python 64-bit y la biblioteca C/ASM 32-bit.

## Tecnologías Utilizadas

*   **Python 3:** Capa superior (GUI con Tkinter, lógica de API, cliente 64-bit `msl-loadlib`).
*   **C (GCC):** Capa intermedia (puente que recibe datos de Python y llama a ASM). Compilado a 32-bit.
*   **Ensamblador (NASM):** Capa inferior (rutina que realiza el cálculo sobre el float GINI). Sintaxis Intel, 32-bit.
*   **API REST:** Banco Mundial (para obtener el índice GINI).
*   **msl-loadlib:** Biblioteca Python para facilitar la llamada a bibliotecas 32-bit desde un proceso Python 64-bit (y viceversa).
*   **Linux:** Entorno de desarrollo y ejecución (probado en Ubuntu/Debian).

## Instrucciones de Uso

1.  **Clonar el Repositorio:**
    ```bash
    git clone <url-del-repositorio>
    cd <directorio-del-proyecto>
    ```

2.  **Configurar el Entorno (Ejecutar una sola vez):**
    Este script instala paquetes del sistema (`apt`) y dependencias Python (`pip`) en un entorno virtual (`venv`). Requiere `sudo`.
    ```bash
    chmod +x setup.sh
    ./setup.sh
    ```

3.  **Compilar el Código C/ASM (Cada vez que se modifique C o ASM):**
    Este script compila `float_rounder.asm` y `gini_processor.c` para generar la biblioteca compartida `src/lib/libginiprocessor.so` (32-bit).
    ```bash
    chmod +x build.sh
    ./build.sh
    ```

4.  **Ejecutar la Aplicación:**
    Este script activa el entorno virtual y lanza la aplicación Python principal (`src/main.py`).
    ```bash
    chmod +x run.sh
    ./run.sh
    ```
    Se abrirá una ventana gráfica donde podrás introducir un código de país (ej. ARG, USA, BRA) y obtener el índice GINI. Luego, podrás usar el botón "Procesar GINI con C/ASM" para ejecutar el cálculo en la biblioteca 32-bit.

## Flujo de Datos y Procesamiento

1.  **GUI (`gui.py`)**: El usuario introduce un código de país y pulsa "Obtener Datos".
2.  **Lógica (`core_logic.py`)**:
    *   Llama a `get_gini_data` para consultar la API del Banco Mundial.
    *   `find_latest_valid_gini` procesa la respuesta para encontrar el dato más reciente y válido.
    *   Muestra el resultado en la GUI.
3.  **Procesamiento C/ASM (al pulsar el botón)**:
    *   **GUI (`gui.py`)**: Llama a `process_with_c_asm` en `core_logic.py` con el valor GINI (float).
    *   **Lógica (`core_logic.py`)**:
        *   Obtiene la instancia `GiniClient64`.
        *   Llama a `client.process_gini_float_on_server(gini_float)`. Esto envía una solicitud de red al servidor 32-bit.
    *   **Servidor 32-bit (`server32_bridge.py` corriendo en Python 32-bit)**:
        *   Recibe la solicitud y el valor `gini_float`.
        *   Llama a la función `process_gini_float(gini_float)` de la biblioteca `libginiprocessor.so` cargada mediante `ctypes`.
    *   **Puente C (`gini_processor.c` en `libginiprocessor.so`)**:
        *   Recibe el `gini_float`.
        *   Declara una variable local `int result_from_asm`.
        *   Llama a `asm_float_round(gini_float, &result_from_asm)` (pasando argumentos por la pila según `cdecl`).
        *   Devuelve `result_from_asm` (en `EAX`).
    *   **Ensamblador (`float_rounder.asm` en `libginiprocessor.so`)**:
        *   Recibe `float` y `puntero int*` de la pila (`[ebp+8]`, `[ebp+12]`).
        *   Usa la FPU (`fld`, `fistp`) para redondear el float al entero más cercano.
        *   Guarda el resultado entero en la dirección de memoria apuntada por el puntero recibido.
        *   Retorna el control a C (`ret`).
    *   **Servidor 32-bit**: Recibe el `int` devuelto por la función C.
    *   **Lógica (`core_logic.py`)**: Recibe el `int` del servidor 32-bit.
    *   **GUI (`gui.py`)**: Recibe el `int` y lo muestra en un `messagebox`.

## Depuración con GDB

(Instrucciones para depurar la interacción C-ASM usando GDB irían aquí, enfocándose en la inspección de la pila antes/durante/después de la llamada a `asm_float_round` desde `gini_processor.c`. Se necesitaría un pequeño programa C de prueba o depurar directamente `libginiprocessor.so` si se carga desde un ejecutable C de 32 bits).
