# VERSION: Python + C 64bits

# make sure that you are in the same directory as this script
cd "$(dirname "$0")"

# Execution of setup_everything.sh
./setup_everything.sh

# Goes to src directory
cd src

echo "🔄 Compiling the C code that will be used in Python..."
# compiles the C code as a shared library (64bit for now)
gcc -m64 -shared -o libginiadder.so -fPIC gini_adder.c

echo "🐍 Opening python script"
python3 main.py



