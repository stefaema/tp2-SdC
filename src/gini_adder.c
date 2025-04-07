// gini_adder.c
// Contains C implementations for GINI processing.

#include <stdio.h> // Include for potential printf debugging
#include <math.h>  // Include for potential standard math functions (though not strictly needed for this manual implementation)

/*
 * Function: process_gini_pure_c
 * -----------------------------
 * Takes a float GINI value, rounds it to the nearest integer using
 * standard rounding rules (>= .5 rounds away from zero), and returns the result.
 * Specifically, it adds 1 to the truncated integer part only if the
 * fractional part's magnitude warrants rounding away from zero.
 *
 * Example:
 *   42.7 -> rounds to 43
 *   42.3 -> rounds to 42
 *   42.5 -> rounds to 43
 *  -42.7 -> rounds to -43
 *  -42.3 -> rounds to -42
 *  -42.5 -> rounds to -43
 *
 * gini_value: The input float value.
 *
 * returns: The rounded integer value.
 */
int process_gini_pure_c(float gini_value) {
    int result;

    // Standard rounding logic: add/subtract 0.5 before casting to int.
    // This handles the "add 1 if fractional >= 0.5" rule correctly for both
    // positive and negative numbers (rounding away from zero).
    if (gini_value >= 0.0f) {
        // For positive numbers or zero
        result = (int)(gini_value + 0.5f);
    } else {
        // For negative numbers
        result = (int)(gini_value - 0.5f);
    }


    printf("[C - process_gini_pure_c] Input: %f, Rounded Output: %d\n", gini_value, result);


    return result;
}


// --- Placeholder for the future ASM linked function ---
// This declaration tells the C compiler that a function named 'process_gini_asm'
// exists elsewhere (defined in assembly and linked later). It expects a float
// and returns an int, matching the C calling convention.
//
// extern int process_gini_asm(float value);
//
// int process_data(float gini_float) {
//      // This C function would eventually call the ASM version
//      return process_gini_asm(gini_float);
// }
// --- End Placeholder ---

/*
// --- Optional main for testing gini_adder.c directly ---
// Compile with: gcc -m32 gini_adder.c -o test_c -lm (if using math.h functions)
int main() {
    float test_values[] = {42.7f, 42.3f, 42.5f, 0.0f, -0.2f, -0.8f, -42.7f, -42.3f, -42.5f};
    int num_tests = sizeof(test_values) / sizeof(test_values[0]);

    printf("Testing process_gini_pure_c:\n");
    for (int i = 0; i < num_tests; ++i) {
        float input = test_values[i];
        int output = process_gini_pure_c(input);
        printf("  Input: %f -> Output: %d. (Expected %d)\n", input, output,
               (int)(input >= 0.0f ? input + 0.5f : input - 0.5f));
    }
    return 0;
}
*/
