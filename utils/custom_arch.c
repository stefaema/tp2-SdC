#include <stdio.h>
#include <stddef.h>

int main(){
    printf("Using %zu bits architecture\n", sizeof(void*) * 8);
}
