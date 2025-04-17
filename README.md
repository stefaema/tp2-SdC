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
