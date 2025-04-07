#include <stdio.h>
#include <unistd.h> // Para verificar si es 32 o 64 bits (opcional)



int main() {
    // Calculate the system architecture in bits
    long architecture_bits = sizeof(void*) * 8;

    // Print the system architecture
    printf("HI THERE! YOUR SYSTEM ARCHITECTURE USES %ld BITS!\n", architecture_bits);

    // Provide a brief explanation
    printf("The size of a pointer determines the architecture:\n");
    printf("- 4 bytes (32 bits) for 32-bit systems\n");
    printf("- 8 bytes (64 bits) for 64-bit systems\n");
    printf("This is because a pointer must be able to address all memory locations.\n");
    printf("And in this case, the pointer size is %ld bytes.\n", sizeof(void*));
    printf("This means that the architecture is %ld bits (%ldx8).\n", architecture_bits, sizeof(void*));
    printf("There are %lu number of addresses in the system.\n", (unsigned long)1 << (architecture_bits - 1));
    return 0;
}
