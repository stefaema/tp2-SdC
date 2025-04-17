#!/bin/bash
# exe_tp.sh
# VERSION: Python 64bit + C/ASM 32bit (using msl-loadlib client/server)

# Function for error messages
fail() {
    echo -e "\033[31mError: $1\033[0m" >&2
    exit 1
}

# Make sure that we are in the script's directory
cd "$(dirname "$0")" || fail "Could not change to script directory"

echo "🚀 Starting TP2 Execution (C/ASM Integration)..."
echo "---------------------------------"

# 1. Setup Environment (Run setup script)
echo "🛠️ Running setup script (setup_everything.sh)..."
chmod +x ./setup_everything.sh
./setup_everything.sh || fail "Environment setup failed."
echo "---------------------------------"

# 2. Activate virtual environment
expected_venv_path="$(pwd)/tp2_venv"
if [ -z "$VIRTUAL_ENV" ] || [ "$VIRTUAL_ENV" != "$expected_venv_path" ]; then
    echo "🐍 Activating Python virtual environment..."
    source tp2_venv/bin/activate || fail "Could not activate virtual environment 'tp2_venv'."
else
    echo "🐍 Python virtual environment already active."
fi
echo "---------------------------------"


# 3. Go to source directory
echo "📁 Changing to 'src' directory..."
cd src || fail "Could not change to 'src' directory. Does it exist?"
echo "   Current directory: $(pwd)"
echo "---------------------------------"


# 4. Compile C/ASM code (32-bit shared library)
echo "🔄 Compiling ASM code (gini_adder.asm) to 32-bit object file..."
ASM_SOURCE="gini_adder.asm"
ASM_OBJECT="gini_adder.o"
ASM_COMPILER=nasm
ASM_FLAGS="-f elf -g -F dwarf" # -f elf for 32-bit linux, -g -F dwarf for debug

if [ ! -f $ASM_SOURCE ]; then
    fail "Assembly source file '$ASM_SOURCE' not found in 'src' directory."
fi

echo "   Command: $ASM_COMPILER $ASM_FLAGS $ASM_SOURCE -o $ASM_OBJECT"
$ASM_COMPILER $ASM_FLAGS $ASM_SOURCE -o $ASM_OBJECT || fail "Assembly compilation failed."

if [ ! -f $ASM_OBJECT ]; then
    fail "Assembly object file '$ASM_OBJECT' was not created."
fi
echo "   Successfully created '$ASM_OBJECT'."
echo ""


echo "🔄 Compiling C bridge (gini_adder.c) and linking with ASM object..."
C_SOURCE="gini_adder.c"
TARGET_LIB="libginiadder.so"
C_COMPILER=gcc
# --- CRUCIAL CHANGE: Link C_SOURCE with ASM_OBJECT ---
C_FLAGS="-m32 -shared -o $TARGET_LIB -fPIC -g -Wall" # -m32, -shared, -fPIC, debug, warnings

if [ ! -f $C_SOURCE ]; then
    fail "C source file '$C_SOURCE' not found in 'src' directory."
fi

echo "   Command: $C_COMPILER $C_FLAGS $C_SOURCE $ASM_OBJECT"
$C_COMPILER $C_FLAGS $C_SOURCE $ASM_OBJECT || fail "C compilation/linking failed."

if [ ! -f $TARGET_LIB ]; then
    fail "Shared library '$TARGET_LIB' was not created."
fi
echo "   Successfully created shared library '$TARGET_LIB' (32-bit, C+ASM)."
echo ""

echo "   Verifying library architecture..."
file "$TARGET_LIB" || echo "   Warning: Could not run 'file' command to verify."
file "$TARGET_LIB" | grep "ELF 32-bit" || fail "Library '$TARGET_LIB' is NOT 32-bit ELF!"
echo "   Library is confirmed 32-bit."
echo "---------------------------------"


# 5. Run Python application
echo "🐍 Launching Python application (main.py)..."
if [ ! -f main.py ]; then
    fail "'main.py' not found in 'src' directory."
fi

python3 main.py

exit_status=$?
echo "---------------------------------"
if [ $exit_status -eq 0 ]; then
    echo "✅ Python application finished successfully."
else
    echo -e "\033[31m⚠️ Python application exited with status $exit_status.\033[0m"
fi
# --- Optional: Clean up object file ---
# echo "🧹 Cleaning up object file..."
# rm -f $ASM_OBJECT
# ------------------------------------
echo "🏁 Execution finished."

exit $exit_status
