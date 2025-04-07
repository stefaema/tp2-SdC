section .text
    global asm_function  ; Hacer la función visible para el enlazador

asm_function:
    ; Función simple: solo devuelve un valor fijo en EAX
    mov eax, 55         ; Colocar el valor de retorno 55 en EAX
    ret                 ; Retornar al código llamador (C)
