#!/bin/bash
set -e  # para abortar se der erro

# ====== Configurações ======
RISCV_PREFIX="riscv32-unknown-elf"
CC="${RISCV_PREFIX}-gcc"
OBJDUMP="${RISCV_PREFIX}-objdump"
OBJCOPY="${RISCV_PREFIX}-objcopy"

CFLAGS="-Wall -O3 -march=rv32im_zicsr -mabi=ilp32 -static -nostartfiles -mstrict-align"
INCLUDES="-I./coremark -I./port"
LDFLAGS="-T link.ld -static"

OUT_DIR=build
OUT_ELF=${OUT_DIR}/coremark.elf
OUT_BIN=${OUT_DIR}/coremark.bin

# ====== Cria diretório de build ======
mkdir -p ${OUT_DIR}

# ====== Compila todos os .c e o boot.S ======
SRC_CORE=$(ls coremark/*.c)
SRC_PORT=$(ls port/*.c)
SRC_BOOT=port/boot.S
SRC_INTERRUPT=port/interrupts.S

echo "[Compilando CoreMark para RISC-V baremetal]"
${CC} ${CFLAGS} ${INCLUDES} ${SRC_CORE} ${SRC_PORT} ${SRC_BOOT} ${SRC_INTERRUPT} -o ${OUT_ELF} ${LDFLAGS}

# ====== Gera binário e dump ======
${OBJCOPY} -O binary ${OUT_ELF} ${OUT_BIN}
${OBJDUMP} -D ${OUT_ELF} > ${OUT_DIR}/coremark.dump
hexdump -v -e '1/4 "%08x" "\n"' ${OUT_BIN} > ${OUT_DIR}/coremark.hex

echo "✅ Build concluído!"
echo "ELF: ${OUT_ELF}"
echo "BIN: ${OUT_BIN}"
echo "Dump: ${OUT_DIR}/coremark.dump"
echo "Hex: ${OUT_DIR}/coremark.hex"