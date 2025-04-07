# colors functions
red() {
    echo -e "\033[31m$1\033[0m"
}
green() {
    echo -e "\033[32m$1\033[0m"
}
yellow() {
    echo -e "\033[33m$1\033[0m"
}
blue() {
    echo -e "\033[34m$1\033[0m"
}
magent() {
    echo -e "\033[35m$1\033[0m"
}
cyan() {
    echo -e "\033[36m$1\033[0m"
}
bold() {
    echo -e "\033[1m$1\033[0m"
}


bold "> source tp2_venv/bin/activate"
source tp2_venv/bin/activate

green "💻 Compiling & Running some code"
bold "> cd bin"
cd bin

magent "First, let's compile some C code"

bold "> gcc -o exe ../utils/custom_arch.c"
gcc -o exe ../utils/custom_arch.c

blue "Now let's run the compiled code"
bold "> ./exe"
output=$(./exe)
echo "$output"
echo "What architecture are we on? Apparently, the output is: $output"

blue "Maybe we should run the same compilation with a little trick"
bold "> gcc -m32 -o exe_32 ../utils/custom_arch.c"
gcc -m32 -o exe_32 ../utils/custom_arch.c
echo "The -m32 flag is used to compile the code for a 32-bit architecture"

blue "Now let's run the compiled code"
bold "> ./exe_32"
output=$(./exe_32)
echo "$output"
echo "What architecture are we on? Apparently, the output is: $output"
echo "Of course, it's not that our PC suddenly changed architecture, it just compiled for a 32-bit arch"
echo "It still runs on a 64-bit architecture, though."

magent "Now let's compile some ASM code"

blue "First, let's compile the ASM code with nasm"
bold "> nasm -f elf64 ../utils/noop_src.asm"
nasm -f elf32 ../utils/noop_src.asm -o noop_src.o
echo "The -f flag is used to specify the format of the output file, in this case, elf32: Executable and Linkable Format 32-bit"
echo "A .o file is an object file, which is a compiled version of the source code. You can see it here:"
bold "> ls -l noop_src.o"
ls -l noop_src.o
blue "Now, let's compile the C code that will be linked with the ASM code"
bold "> gcc -m32 -o exe_32 ../utils/noop_src_link.c noop_src.o"
gcc -m32 -o exe_asm_c ../utils/noop_src_link.c noop_src.o
echo "The -m32 flag is used to compile the code for a 32-bit architecture"
blue "Now let's run the compiled code"

bold "> ./exe_asm_c"
output=$(./exe_asm_c)
echo "$output"
