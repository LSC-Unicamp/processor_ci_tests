#!/bin/bash

# Número de núcleos a usar
NCORES=${1:-8}  # padrão: 4 núcleos, pode passar como argumento

# Arquitetura padrão
march="rv32imafdb_zicsr"

# Função que compila um único arquivo .s
compile_single() {
    local arquivo="$1"
    local march="$2"
    local src_dir
    local level_dir
    local nome_sem_extensao
    local build_dir
    local memory_dir

    src_dir=$(dirname "$arquivo")
    level_dir=$(dirname "$src_dir")
    nome_sem_extensao=$(basename "$arquivo" .s)
    build_dir="${level_dir}/build"
    memory_dir="${level_dir}/memory"

    mkdir -p "$build_dir" "$memory_dir"

    echo "Compilando $arquivo..."

    riscv32-unknown-elf-as -march="$march" "$arquivo" -o "$build_dir/$nome_sem_extensao.o" &&
    riscv32-unknown-elf-ld "$build_dir/$nome_sem_extensao.o" -o "$build_dir/$nome_sem_extensao.elf" &&
    riscv32-unknown-elf-objcopy -O binary "$build_dir/$nome_sem_extensao.elf" "$build_dir/$nome_sem_extensao.bin" &&
    hexdump -v -e '1/4 "%08x" "\n"' "$build_dir/$nome_sem_extensao.bin" > "$memory_dir/$nome_sem_extensao.hex"

    echo "$arquivo compilado para $memory_dir/$nome_sem_extensao.hex"
}

export -f compile_single

# Encontra todos os arquivos .s dentro dos diretórios src/
find . -type f -path '*/src/*.s' | parallel -j "$NCORES" compile_single {} "$march"

echo "Compilação paralela finalizada."
