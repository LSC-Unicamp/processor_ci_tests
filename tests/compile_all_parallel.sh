#!/bin/bash

# Número de núcleos a usar
NCORES=${1:-8}  # padrão: 8 núcleos, pode passar como argumento

# Arquitetura base (sem 'c')
march_base="rv32imafdbv_zicsr"

# Função para inserir 'c' na ordem canônica após o 'a', se necessário
adiciona_c_na_ordem_canonica() {
    echo "$1" | sed -E 's/^(rv32i[m]*a)([^cfdqjlbtpvnxyz]*)/\1c\2/'
}

# Função que compila um único arquivo .s
compile_single() {
    local arquivo="$1"
    local src_dir
    local level_dir
    local extension_dir
    local nome_sem_extensao
    local build_dir
    local memory_dir
    local march_final

    src_dir=$(dirname "$arquivo")
    level_dir=$(dirname "$src_dir")
    extension_dir=$(dirname "$level_dir")
    nome_sem_extensao=$(basename "$arquivo" .s)
    build_dir="${level_dir}/build"
    memory_dir="${level_dir}/memory"

    # Define march corretamente
    if [ "$(basename "$extension_dir")" = "RV32C" ]; then
        march_final=$(adiciona_c_na_ordem_canonica "$march_base")
    else
        march_final="$march_base"
    fi

    mkdir -p "$build_dir" "$memory_dir"

    echo "Compilando $arquivo com -march=$march_final..."

    riscv32-unknown-elf-as -march="$march_final" "$arquivo" -o "$build_dir/$nome_sem_extensao.o" &&
    riscv32-unknown-elf-ld "$build_dir/$nome_sem_extensao.o" -o "$build_dir/$nome_sem_extensao.elf" &&
    riscv32-unknown-elf-objcopy -O binary "$build_dir/$nome_sem_extensao.elf" "$build_dir/$nome_sem_extensao.bin" &&
    hexdump -v -e '1/4 "%08x" "\n"' "$build_dir/$nome_sem_extensao.bin" > "$memory_dir/$nome_sem_extensao.hex"

    echo "$arquivo compilado para $memory_dir/$nome_sem_extensao.hex"
}

export -f compile_single
export march_base
export -f adiciona_c_na_ordem_canonica

# Encontra todos os arquivos .s dentro dos diretórios src/
find . -type f -path '*/src/*.s' | parallel -j "$NCORES" compile_single

echo "Compilação paralela finalizada."
