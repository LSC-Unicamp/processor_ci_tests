#!/bin/bash

# Caminho base onde estão as extensões
base_dir="."
march_base="rv32imafdbv_zicsr"  # Arquitetura base, sem 'c'

# Função para inserir 'c' após 'a', se ainda não estiver presente
adiciona_c_na_ordem_canonica() {
    echo "$1" | sed -E 's/^(rv32i[m]*a)([^cfdqjlbtpvnxyz]*)/\1c\2/'
}

# Loop por todas as extensões
for extension_dir in "$base_dir"/*/; do
    extension=$(basename "$extension_dir")

    # Define march com ou sem 'c' dependendo do nome da pasta
    if [ "$extension" = "RV32C" ]; then
        march=$(adiciona_c_na_ordem_canonica "$march_base")
    else
        march="$march_base"
    fi

    # Loop pelos níveis (basic, advanced, invalid)
    for level_dir in "$extension_dir"*/; do
        level=$(basename "$level_dir")

        src_dir="${level_dir}src"
        memory_dir="${level_dir}memory"

        if [ -d "$src_dir" ]; then
            echo "Compilando arquivos em ${src_dir} com -march=$march..."
            mkdir -p "$memory_dir"

            for arquivo in "$src_dir"/*.s; do
                if [ -f "$arquivo" ]; then
                    nome_sem_extensao=$(basename "$arquivo" | sed 's/\.[^.]*$//')
                    build_dir="${level_dir}build"
                    mkdir -p "$build_dir"

                    echo "Compilando $arquivo..."

                    riscv32-unknown-elf-as -march=$march "$arquivo" -o "$build_dir/$nome_sem_extensao.o"
                    riscv32-unknown-elf-ld "$build_dir/$nome_sem_extensao.o" -o "$build_dir/$nome_sem_extensao.elf"
                    riscv32-unknown-elf-objcopy -O binary "$build_dir/$nome_sem_extensao.elf" "$build_dir/$nome_sem_extensao.bin"
                    hexdump -v -e '1/4 "%08x" "\n"' "$build_dir/$nome_sem_extensao.bin" > "$memory_dir/$nome_sem_extensao.hex"

                    echo "$arquivo compilado e salvo como $memory_dir/$nome_sem_extensao.hex"
                fi
            done
        else
            echo "Nenhum diretório src encontrado em $level_dir."
        fi
    done
done

echo "Processo de compilação concluído."
