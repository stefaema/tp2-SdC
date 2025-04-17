#!/bin/bash
# setup.sh: Instala dependencias del sistema y de Python. Ejecutar una sola vez.

# --- Funciones de color ---
red() { echo -e "\033[31m$1\033[0m"; }
green() { echo -e "\033[32m$1\033[0m"; }
yellow() { echo -e "\033[33m$1\033[0m"; }
bold() { echo -e "\033[1m$1\033[0m"; }

# --- Salir si cualquier comando falla ---
set -e

green "--- Iniciando Configuración del Entorno para TP2 ---"

# --- 1. Instalar Dependencias del Sistema (Debian/Ubuntu) ---
bold "Paso 1: Instalando paquetes del sistema con APT (requiere sudo)..."
echo "Se instalarán: python3-tk, build-essential, nasm, gcc-multilib, g++, gfortran, y librerías 32-bit para msl-loadlib."

# Lista de paquetes a instalar
packages="python3-tk build-essential nasm gcc-multilib g++ gfortran libgfortran5 zlib1g:i386 libstdc++6:i386 libgfortran5:i386 git"

# Intenta instalar sin preguntar, pero muestra el comando
echo "Comando: sudo apt-get update && sudo apt-get install -y $packages"
if sudo apt-get update && sudo apt-get install -y $packages; then
    green "Paquetes del sistema instalados correctamente."
else
    red "Error instalando paquetes del sistema. Revisa los mensajes de APT."
    exit 1
fi
echo # Línea en blanco

# --- 2. Crear Entorno Virtual Python ---
VENV_DIR="venv"
bold "Paso 2: Creando entorno virtual Python en './${VENV_DIR}'..."
if [ -d "$VENV_DIR" ]; then
    yellow "Directorio '$VENV_DIR' ya existe. Saltando creación."
else
    # Usar python3 explícitamente
    if python3 -m venv "$VENV_DIR"; then
        green "Entorno virtual '$VENV_DIR' creado."
    else
        red "Error creando el entorno virtual. ¿Está 'python3-venv' instalado?"
        exit 1
    fi
fi
echo

# --- 3. Activar Entorno Virtual e Instalar Dependencias Python ---
bold "Paso 3: Activando entorno virtual e instalando requisitos de 'requirements.txt'..."
# Activa el entorno virtual
source "${VENV_DIR}/bin/activate" || { red "Error activando el entorno virtual."; exit 1; }
green "Entorno virtual activado. (Python: $(which python))"

# Actualiza pip e instala requerimientos
echo "Comando: pip install --upgrade pip"
pip install --upgrade pip
echo "Comando: pip install -r requirements.txt"
if pip install -r requirements.txt; then
    green "Dependencias Python instaladas correctamente."
else
    red "Error instalando dependencias Python desde requirements.txt."
    # Desactivar venv antes de salir en error
    deactivate
    exit 1
fi
echo

# --- Finalización ---
green "--- Configuración del Entorno Completada ---"
yellow "Recuerda:"
yellow " - Ejecuta './build.sh' para compilar el código C/ASM."
yellow " - Ejecuta './run.sh' para iniciar la aplicación (activará el venv automáticamente)."
# Desactivar el venv al final del setup es opcional, run.sh lo activará
deactivate
echo "(Entorno virtual desactivado)"

exit 0
