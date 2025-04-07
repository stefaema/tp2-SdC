# Plan de Proyecto: TP#2 - Integración C/Ensamblador con API REST

**Objetivo Principal:** Desarrollar una aplicación multicapa que consume datos de una API REST (Índice GINI del Banco Mundial), los procesa mediante una rutina en ensamblador (invocada desde C) para convertir de float a entero y sumar uno, y muestra el resultado final. El pasaje de parámetros y retorno entre C y Ensamblador debe realizarse exclusivamente a través del stack, siguiendo convenciones de llamada estándar.

**Fase 0: Preparación y Configuración del Entorno (Individual/Grupal)**
*   [ ] **Configurar Repositorio GitHub:**
    *   [ ] Crear repositorio privado en GitHub.
    *   [ ] Añadir colaboradores (los demás miembros del grupo).
    *   [ ] Cada miembro (excepto el dueño) debe hacer un fork del repositorio principal.
    *   [ ] Establecer flujo de trabajo: desarrollo en forks -> Pull Requests -> revisión -> merge en el principal. Commit por cada funcionalidad/mejora significativa con mensaje descriptivo.
*   [ ] **Instalar Software Requerido (Linux - ej. Ubuntu 22.04):**
    *   [x] `sudo apt update && sudo apt upgrade -y`
    *   [x] `sudo apt install build-essential nasm gcc-multilib g++-multilib gdb python3 python3-pip git -y`
    *   [x] `pip install requests` (para Python)
    *   - (Opcional, si se usa C para API) `sudo apt install libcurl4-openssl-dev`
    *   - (Opcional, si hay problemas 32/64 bits con Python) Investigar/instalar `msl-loadlib` o verificar compatibilidad de `ctypes`.
*   [x] **Verificar Entorno:** Compilar y ejecutar programas de ejemplo C y NASM (ej., del libro de Paul Carter) para asegurar que el toolchain funciona (incluyendo enlace 32-bit: `gcc -m32 ...`, `nasm -f elf32 ...`).
*   [ ] **Lectura Obligatoria:** Leer Capítulos 1-4 del libro de Paul A. Carter ("Lenguaje Ensamblador para PC"). Compilar y depurar ejemplos del Cap. 4.

**Fase 1: Iteración Inicial - Funcionalidad Base (Python + C)**

*   [ ] **Capa Superior (Python): Consumo de API REST**
    *   [x] Crear script Python (`main.py` o similar).
    *   [x] Usar `requests` para llamar a la API del Banco Mundial: `https://api.worldbank.org/v2/en/country/all/indicator/SI.POV.GINI?format=json&date=2011:2020&per_page=32500&page=1&country=%22Argentina%22` (o país elegido).
    *   [x] Implementar manejo de errores básicos (conexión, respuesta no exitosa).
    *   [x] Parsear la respuesta JSON.
    *   [x] Extraer el valor más reciente del índice GINI (float) para el país seleccionado. Manejar casos donde el dato no exista o sea `null`.
*   [ ] **Capa Intermedia (C): Procesamiento Simulado**
    *   [ ] Crear archivo C (`process.c` o similar).
    *   [ ] Definir una función C, ej: `int process_gini_c_version(float gini_float)`.
    *   [ ] *Implementar* dentro de esta función C la lógica de conversión float a entero y la suma de 1. (Ej: `return (int)gini_float + 1;`).
    *   [ ] Compilar `process.c` como una librería compartida (`.so`) para 32 bits: `gcc -m32 -shared -o libprocess.so process.c -fPIC`.
*   [ ] **Integración Python -> C (ctypes)**
    *   [ ] En el script Python, usar `ctypes` para cargar `libprocess.so`.
    *   [ ] Definir `argtypes` (float -> `ctypes.c_float`) y `restype` (int -> `ctypes.c_int`) para la función C importada.
    *   [ ] Llamar a la función C desde Python, pasando el valor GINI obtenido de la API.
*   [ ] **Salida:** Mostrar el resultado devuelto por la función C en la consola desde Python.
*   [ ] **Pruebas Iniciales:** Verificar que el flujo completo (API -> Python -> C -> Python -> Consola) funciona y el cálculo (simulado en C) es correcto.
*   [ ] **Commit:** Realizar commit con mensaje "Iteración 1 completa: Flujo Python-C con cálculo en C".

**Fase 2: Iteración Final - Integración con Ensamblador**

*   [ ] **Capa Baja (Ensamblador - NASM): Rutina de Cálculo**
    *   [ ] Crear archivo NASM (`gini_asm.asm` o similar).
    *   [ ] Definir una sección de código (`section .text`).
    *   [ ] Declarar la función como global (ej: `global process_gini_asm`).
    *   [ ] Implementar la rutina `process_gini_asm`:
        *   [ ] Establecer el stack frame (`push ebp; mov ebp, esp`).
        *   [ ] Acceder al parámetro `float` desde el stack (ubicación relativa a `ebp`, ej: `[ebp+8]`). Considerar convención `cdecl`.
        *   [ ] Usar instrucciones FPU (x87) para cargar el float (`fld dword [ebp+8]`).
        *   [ ] Convertir el float a entero truncado y almacenarlo en memoria (`fistp dword [temp_int]`, necesitará definir `temp_int` en `.bss` o en stack).
        *   [ ] Mover el entero de memoria a un registro (ej: `mov eax, [temp_int]`).
        *   [ ] Incrementar el registro entero (`inc eax`).
        *   [ ] El resultado queda en `EAX` (convención `cdecl` para retorno de enteros).
        *   [ ] Restaurar el stack frame (`mov esp, ebp; pop ebp`).
        *   [ ] Retornar (`ret`).
    *   [ ] Ensamblar el archivo NASM a un objeto 32 bits con información de debug: `nasm -f elf32 gini_asm.asm -o gini_asm.o -g -F dwarf`.
*   [ ] **Modificación Capa Intermedia (C): Llamada a Ensamblador**
    *   [ ] Modificar `process.c`.
    *   [ ] Declarar la función ensambladora como externa: `extern int process_gini_asm(float value);`.
    *   [ ] Crear (o modificar) la función C que será llamada por Python (ej: `int process_data(float gini_float)`).
    *   [ ] Dentro de `process_data`, *llamar* a la función de ensamblador: `return process_gini_asm(gini_float);`. Eliminar la implementación C del cálculo.
    *   [ ] Compilar `process.c` a objeto 32 bits: `gcc -m32 -c process.c -o process.o -g3`.
*   [ ] **Enlace Final:**
    *   [ ] Crear la librería compartida (`.so`) final enlazando los objetos C y ASM: `gcc -m32 -shared -o libprocess.so process.o gini_asm.o -g3`.
*   [ ] **Pruebas de Integración:**
    *   [ ] Ejecutar el script Python (`main.py`).
    *   [ ] Verificar que el flujo completo ahora usa la rutina de ensamblador y el resultado sigue siendo correcto.
*   [ ] **Commit:** Realizar commit con mensaje "Iteración 2 completa: Integración de rutina ASM para cálculo GINI".

**Fase 3: Depuración y Verificación con GDB**

*   [ ] **Crear Programa de Prueba C Puro:**
    *   [ ] Crear un archivo C simple (`test_asm.c`).
    *   [ ] Incluir un `main`.
    *   [ ] Declarar la función ASM externa (`extern int process_gini_asm(float value);`).
    *   [ ] En `main`, llamar a `process_gini_asm` con un valor float de prueba (ej: `float test_val = 45.6; int result = process_gini_asm(test_val);`).
    *   [ ] Imprimir el resultado usando `printf`.
*   [ ] **Compilar y Enlazar para Debug:**
    *   [ ] Compilar `test_asm.c`: `gcc -m32 -c test_asm.c -o test_asm.o -g3`.
    *   [ ] Enlazar con el objeto ASM para crear un ejecutable: `gcc -m32 test_asm.o gini_asm.o -o test_asm_exec -g3`.
*   [ ] **Análisis con GDB:**
    *   [ ] Iniciar GDB: `gdb ./test_asm_exec`.
    *   [ ] Establecer punto de interrupción antes de la llamada a ASM en `test_asm.c`: `break test_asm.c:<linea_del_call>`.
    *   [ ] Ejecutar: `run`.
    *   [ ] **Antes del `call`:** Examinar el stack (`x/16xw $esp`, `info frame`). Identificar dónde se colocará el parámetro float.
    *   [ ] Establecer punto de interrupción al inicio de la función ASM: `break process_gini_asm`.
    *   [ ] Continuar: `continue`.
    *   [ ] **Dentro de ASM (inicio):** Examinar registros (`info registers esp ebp eax`) y el stack (`x/16xw $esp`, `x/xw $ebp+8` para ver el float pasado). Verificar el stack frame.
    *   [ ] Avanzar paso a paso por instrucciones (`stepi` o `si`). Observar la recuperación del parámetro, las operaciones FPU, la conversión a entero, el incremento y la colocación del resultado en EAX.
    *   [ ] Establecer punto de interrupción después del `call` en `test_asm.c`.
    *   [ ] Continuar: `continue`.
    *   [ ] **Después del `call`:** Examinar el valor de retorno en C (variable `result`) y el registro `EAX` (`p $eax`). Verificar que el stack se haya limpiado correctamente (según `cdecl`, el caller C es responsable).
*   [ ] **Documentar Observaciones GDB:** Tomar notas / capturas de pantalla del estado del stack y registros en los puntos clave.
*   [ ] **Commit:** Realizar commit con mensaje "Análisis GDB de la interacción C-ASM y estado del stack".

**Fase 4: Documentación, Extras y Finalización**

*   [ ] **Comentarios en Código:** Asegurar que Python, C y ASM estén adecuadamente comentados.
*   [ ] **README.md:** Crear/completar el archivo `README.md` en el repositorio GitHub con:
    *   [ ] Descripción del proyecto.
    *   [ ] Integrantes del equipo.
    *   [ ] Instrucciones detalladas de compilación y ejecución.
    *   [ ] Explicación de la arquitectura (Python -> C -> ASM).
    *   [ ] Descripción clara del mecanismo de paso de parámetros y retorno por stack entre C y ASM (ilustrar con esquema si es posible).
    *   [ ] Resumen de los hallazgos de la depuración con GDB (o enlace a un documento/sección).
*   [ ] **(Opcional/Bonus) Diagramas:**
    *   [ ] Crear diagrama de bloques de la arquitectura.
    *   [ ] Crear diagrama de secuencia del flujo de llamadas.
*   [ ] **(Opcional/Bonus) Pruebas y Rendimiento:**
    *   [ ] Definir casos de prueba formales.
    *   [ ] Realizar pruebas de performance comparando la versión solo C vs C+ASM (medir tiempo de ejecución de la función de procesamiento).
    *   [ ] Realizar profiling de la parte C/ASM (ej. con `gprof`).
*   [ ] **Revisión Final y Limpieza:**
    *   [ ] Revisar todo el código y la documentación.
    *   [ ] Asegurarse que todos los commits estén en el repositorio principal y los forks sincronizados.
    *   [ ] Verificar que el proyecto cumple todos los requisitos del enunciado.
*   [ ] **Preparación para Defensa:** Preparar una presentación/demostración del proyecto, incluyendo la ejecución, explicación del código y la demostración con GDB.

**Fase 5: Defensa del Proyecto**

*   [ ] **Presentación Grupal:** Exponer el trabajo realizado, la arquitectura, el código, el flujo de datos, la interacción C-ASM vía stack, y la demostración con GDB.
*   [ ] **Responder Preguntas:** Estar preparados para responder preguntas sobre el diseño, implementación y conceptos subyacentes.
