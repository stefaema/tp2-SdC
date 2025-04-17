# Step 1: Assemble the NASM code into a 32-bit object file
# -f elf: Output format for 32-bit Linux ELF
# -g -F dwarf: Include debugging information in DWARF format for GDB
echo "Compiling ASM..."
nasm -f elf -g -F dwarf asm_rounder.asm -o asm_rounder.o

# Check if compilation succeeded
if [ $? -ne 0 ]; then
    echo "Assembly compilation failed!"
    exit 1
fi
echo "ASM compilation successful: asm_rounder.o created."

# Step 2: Compile the C code and link it with the ASM object file
# -m32: Compile for 32-bit architecture
# -g: Include debugging information for the C code
# -Wall: Enable all standard warnings
# -o test_c_asm: Specify the output executable name
# asm_rounder.c: The C source file (containing main now)
# asm_rounder.o: The Assembly object file to link with
echo "Compiling C and linking with ASM object..."
gcc -m32 -g -Wall -o test_c_asm gini_adder.c asm_rounder.o

# Check if compilation/linking succeeded
if [ $? -ne 0 ]; then
    echo "C compilation or linking failed!"
    exit 1
fi
echo "C/ASM linking successful: test_c_asm created."

# Step 3: Run the executable
echo "Running the test executable..."
./test_c_asm

# Step 4 (Optional): Debug with GDB if it crashes or gives wrong results
# echo "To debug, run: gdb ./test_c_asm"
# Inside GDB:
#   (gdb) break main  # Stop at the beginning of main
#   (gdb) run         # Start execution
#   (gdb) layout src  # Show source code
#   (gdb) layout asm  # Show assembly code
#   (gdb) layout regs # Show registers
#   (gdb) step        # Step one C source line
#   (gdb) stepi       # Step one assembly instruction
#   (gdb) next        # Step over function calls in C
#   (gdb) nexti       # Step over function calls in ASM
#   (gdb) info locals # Show local variables in C
#   (gdb) x/d &result_from_asm # Examine the integer result in memory
#   (gdb) info frame  # Show stack frame info
#   (gdb) x/20xw $esp # Examine words on the stack
#   (gdb) break gini_asm_adder # Stop at the beginning of ASM function
#   (gdb) continue    # Continue execution until next breakpoint
#   (gdb) quit        # Exit GDB
