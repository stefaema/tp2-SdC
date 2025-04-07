#include <stdio.h>

// Declaración de la función externa definida en NASM
extern int asm_function();

int main() {
    printf("Llamando a la función ASM desde C...\n");
    int result = asm_function();
    printf("La función ASM devolvió: %d\n", result);
    printf("Verificación: El valor esperado es 55.\n");
    return 0;
}
