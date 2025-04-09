#!/bin/bash

# Caminho base onde estão as extensões
base_dir="."
march="rv32imafdb_zicsr"  # Arquitetura padrão, pode ser ajustada conforme necessário

# Loop por todas as extensões
for extension_dir in "$base_dir"/*/; do
    extension=$(basename "$extension_dir")

    # Loop pelos níveis (basic, advanced, invalid)
    for level_dir in "$extension_dir"*/; do
        level=$(basename "$level_dir")

        # Diretório de origem dos arquivos .s
        src_dir="${level_dir}src"
        # Diretório de destino dos arquivos .hex
        memory_dir="${level_dir}memory"
        # Diretório para arquivos ELF para Spike
        spike_dir="${level_dir}spike"

        # Verifica se o diretório src existe
        if [ -d "$src_dir" ]; then
            echo "Compilando arquivos em ${src_dir}..."

            # Cria os diretórios de destino, se não existirem
            mkdir -p "$memory_dir"
            mkdir -p "$spike_dir"

            # Loop pelos arquivos .s no diretório src
            for arquivo in "$src_dir"/*.s; do
                if [ -f "$arquivo" ]; then
                    # Obtém o nome do arquivo sem extensão
                    nome_sem_extensao=$(basename "$arquivo" | sed 's/\.[^.]*$//')

                    # Diretório temporário para build intermediário
                    build_dir="${level_dir}build"
                    mkdir -p "$build_dir"

                    echo "Compilando $arquivo..."

                    # Arquivos intermediários
                    obj_file="$build_dir/$nome_sem_extensao.o"
                    elf_file="$build_dir/$nome_sem_extensao.elf"
                    bin_file="$build_dir/$nome_sem_extensao.bin"
                    hex_file="$memory_dir/$nome_sem_extensao.hex"
                    spike_elf="$spike_dir/$nome_sem_extensao.elf"

                    # Compila e gera binário
                    riscv32-unknown-elf-as -march=$march "$arquivo" -o "$obj_file"
                    riscv32-unknown-elf-ld "$obj_file" -Ttext=0x80000000 -o "$elf_file"
                    cp "$elf_file" "$spike_elf"

                    riscv32-unknown-elf-objcopy -O binary "$elf_file" "$bin_file"
                    hexdump -v -e '1/4 "%08x" "\n"' "$bin_file" > "$hex_file"

                    echo "$arquivo compilado:"
                    echo "  - .hex salvo em $hex_file"
                    echo "  - ELF para Spike salvo em $spike_elf"
                fi
            done
        else
            echo "Nenhum diretório src encontrado em $level_dir."
        fi
    done
done

echo "Processo de compilação concluído."
