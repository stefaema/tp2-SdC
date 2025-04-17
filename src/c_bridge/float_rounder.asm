; src/c_bridge/float_rounder.asm
; Rutina NASM (32-bit Linux, ELF) para redondear un float al entero más cercano.
; Utiliza la pila para recibir parámetros según la convención de llamada cdecl.
;
; Interfaz C <-> ASM (cdecl):
; - Llamada desde C: asm_float_round(float_value, &int_result_var);
; - Pila al entrar a asm_float_round:
;   [ESP+0] : Dirección de retorno (puesta por CALL)
;   [ESP+4] : float_value       (primer argumento en C, último pusheado)
;   [ESP+8] : &int_result_var   (segundo argumento en C, primer pusheado)
; - Tras el prólogo (mov ebp, esp):
;   [EBP+0] : EBP antiguo (guardado por PUSH EBP)
;   [EBP+4] : Dirección de retorno
;   [EBP+8] : float_value       <--- Parámetro 1 (float)
;   [EBP+12]: &int_result_var   <--- Parámetro 2 (int*)
; - Valor de Retorno: Ninguno (void). El resultado se escribe en la dirección [EBP+12].
; - Registros Preservados (Callee-Save): EBX, ESI, EDI, EBP deben restaurarse si se usan.
; - Registros No Preservados (Caller-Save/Scratch): EAX, ECX, EDX pueden modificarse libremente.
; - Limpieza de Pila: El llamante (C) limpia los parámetros de la pila después del retorno.

section .text
    global asm_float_round      ; Exporta el símbolo para el enlazador C 

asm_float_round:
    push    ebp                 ; 1. Guarda EBP del llamante (Preserva EBP)
    mov     ebp, esp            ; 2. Establece el nuevo EBP para este frame

    ; --- Espacio local en la pila ---
    ; Necesario para que FISTP tenga una dirección de memoria donde escribir.
    ; Reservamos 8 bytes (dword alineado) para el entero temporal.
    sub     esp, 8              ; Reserva espacio. Acceso vía [EBP-8].

    ; --- Carga de argumentos desde la pila ---
    ; Acceder a los parámetros usando EBP.
    fld     dword [ebp+8]       ; Carga el float (parámetro 1) de [ebp+8] en st0
    mov     edx, [ebp+12]       ; Carga el puntero int* (parámetro 2) de [ebp+12] a EDX (Caller-Save)

    ; --- Redondeo (FPU) y almacenamiento temporal ---
    ; FISTP redondea st0 (según modo FPU) a entero y lo guarda en memoria.
    fistp   dword [ebp-8]       ; Guarda entero redondeado en variable local [ebp-8], popea st0.

    ; --- Obtener resultado redondeado y escribirlo en la dirección de salida ---
    mov     eax, [ebp-8]        ; Carga el entero redondeado desde [ebp-8] a EAX (Caller-Save)
    ; EDX ya contiene la dirección de salida (&int_result_var)
    mov     [edx], eax          ; Guarda EAX (resultado) en la memoria apuntada por EDX.
                                ; Cumple el contrato de la función (escribir vía puntero).

    ; --- Epílogo estándar cdecl ---
    ; No se coloca nada en EAX como valor de retorno, ya que la función es void.
    ; El C wrapper se encargará de devolver el valor si es necesario.
    mov     esp, ebp            ; 1. Libera el espacio local (deshace SUB ESP)
    pop     ebp                 ; 2. Restaura EBP del llamante (Preserva EBP)
    ret                         ; 3. Retorna al llamante (usa dirección de retorno en pila)
                                ;    El llamante C limpiará los parámetros.

; Fin de la función asm_float_round
