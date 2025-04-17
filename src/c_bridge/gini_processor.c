// src/c_bridge/gini_processor.c
// Recibe el valor GINI float desde Python (via Server32) y llama a la rutina ASM.

#include <stdio.h> // Para printf

// --- Macros de Logging Simplificado ---
// Define el prefijo constante para los mensajes
#define LOG_PREFIX "INFO [C Bridge]"
// Define la macro INFO usando __VA_ARGS__ (estándar C99/C11)
// format: La cadena de formato para printf
// ...: Los argumentos variables para la cadena de formato
// ##__VA_ARGS__: Concatena la coma solo si hay argumentos variables (extensión GNU común)
#define INFO(format, ...) printf(LOG_PREFIX " " format "\n", ##__VA_ARGS__)

// --- Declaración de la Función Ensamblador ---
// Especifica que la función 'asm_float_round' está definida externamente
// y sigue la convención de llamada cdecl (implícita para GCC 32-bit).
// Parámetros pasados por la pila:
//   1. (input_float): El valor float a procesar.
//   2. (output_int_ptr): Un puntero a la ubicación int donde se debe escribir el resultado.
extern void asm_float_round(float input_float, int* output_int_ptr);

// --- Función C Puente (Llamada desde Python/Server32) ---
// Esta función actúa como intermediaria. Recibe un float y devuelve un int.
int process_gini_float(float gini_value) {
    // Variable local para almacenar el resultado que escribirá la rutina ASM.
    // Se inicializa a un valor por defecto para seguridad/depuración.
    int result_from_asm = -999; // Valor inicial por si ASM falla

    // Mensaje de log: Valor recibido y dirección de memoria para el resultado.
    INFO("Recibido de Python/Server32: float = %f", gini_value);
    INFO("Dirección para resultado ASM (&result_from_asm): %p", &result_from_asm);

    // --- Llamada a la Rutina Ensamblador ---
    // Se pasan los argumentos por la pila según la convención cdecl:
    // 1. Se empuja &result_from_asm (el puntero int*).
    // 2. Se empuja gini_value (el float).
    // 3. Se ejecuta la instrucción CALL asm_float_round.
    INFO("Llamando a asm_float_round...");
    asm_float_round(gini_value, &result_from_asm);
    INFO("Retorno de asm_float_round.");

    // Mensaje de log: Valor que ASM (esperadamente) escribió en la memoria.
    INFO("Valor escrito por ASM en &result_from_asm: %d", result_from_asm);

    // --- Devolución del Resultado a Python ---
    // La convención cdecl dicta que el valor de retorno entero se coloque
    // en el registro EAX. El compilador C se encarga de esto con la
    // instrucción 'return'.
    return result_from_asm;
}
