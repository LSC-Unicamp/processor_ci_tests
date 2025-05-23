#!/bin/bash

# Variáveis do toolchain
RISCV_PREFIX="riscv32-unknown-elf"
CC="${RISCV_PREFIX}-gcc"
AR="${RISCV_PREFIX}-ar"
CFLAGS="-Wall -march=rv32imc -mabi=ilp32 -nostdlib -ffreestanding -static -mstrict-align -I./target"

SRC_DIR="common"
OBJ_DIR="common"

# Cria diretório de objetos, se não existir
mkdir -p $OBJ_DIR

# Compila todos os arquivos .c da pasta common
for src_file in $SRC_DIR/*.c; do
    # Extrai nome base (ex: libmin_abs.c -> libmin_abs.o)
    base_name=$(basename "$src_file" .c)
    obj_file="$OBJ_DIR/${base_name}.o"
    
    echo "Compilando $src_file -> $obj_file"
    $CC $CFLAGS -c "$src_file" -o "$obj_file"
done

# Cria a biblioteca estática libcommon.a com todos os .o
echo "Criando biblioteca estática libcommon.a"
$AR rcs libcommon.a $OBJ_DIR/*.o

echo "Compilação concluída."
