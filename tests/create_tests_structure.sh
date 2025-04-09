#!/bin/bash

# Define extensões e suas instruções completas
declare -A EXTENSIONS
EXTENSIONS=(
    ["RV32I"]="addi sw slti sltiu xori ori andi slli srli srai lui auipc jal jalr beq bne blt bge bltu bgeu lb lh lw lbu lhu sb sh add sub sll slt sltu xor srl sra or and fence ecall ebreak"
    ["RV64I"]="addiw slliw srliw sraiw addw subw sllw srlw sraw lwu ld sd"
    ["RV32M"]="mul mulh mulhsu mulhu div divu rem remu"
    ["RV64M"]="mulw divw divuw remw remuw"
    ["RV32F"]="flw fsw fadds fsubs fmuls fdivs fsqrts fsgnj fsgnjn fsgnjx fmins fmaxs fcvtws fcvtwus fmvxw fmvwx feqs flts fles fclasss"
    ["RV64F"]="fcvt.l.s fcvt.lu.s fcvt.s.l fcvt.s.lu"
    ["RV32D"]="fld fsd faddd fsubd fmuld fdivd fsqrtd fsgnjd fsgnjnd fsgnjxd fmind fmaxd fcvtwd fcvtwud fmvxd fmvwx feqd fltd fled fclassd"
    ["RV64D"]="fcvt.l.d fcvt.lu.d fmv.x.d fcvt.d.l fcvt.d.lu fmv.d.x"
    ["RV32A"]="lr.w sc.w amoswap.w amoadd.w amoxor.w amoand.w amoor.w amomin.w amomax.w amominu.w amomaxu.w"
    ["RV64A"]="lr.d sc.d amoswap.d amoadd.d amoxor.d amoand.d amoor.d amomin.d amomax.d amominu.d amomaxu.d"
    ["RV32C"]="caddi caddiw clw csw cj cjjal cjr cjalr cand cor candi cmv csub cadd"
    ["RV32V"]="vadd.vv vsub.vv vmul.vv vreduce.vv vdot.vv vmin.vv vmax.vv vslideup.vx vslidedown.vx vredsum.vs vpopc.m vfirst.m vcompress.m"
    ["RV32P"]="pmulw paddw psubw pmulh paddh psubh pmulb paddb psubb"
    ["RV32B"]="andn orn xnor clz ctz pcnt sextb sexth zexth min max rol ror rori andc slo sro sbset sbclr sbinv sbext gorc grev pack packh shuffle unshuffle bdep bext clmul clmulh clmulr"
    ["RV32Zicsr"]="csrrw csrrs csrrc csrrwi csrrsi csrrci"
)

# Função para criar estrutura de pastas e arquivos
create_structure() {
    local extension=$1
    local instructions=($2)

    # Cria as pastas básicas, avançadas e inválidas para a extensão
    for level in basic advanced invalid; do
        mkdir -p "${extension}/${level}/src" "${extension}/${level}/memory" "${extension}/${level}/reference"
    done

    # Cria arquivos na pasta src e reference para as estruturas básica e avançada
    for level in basic advanced; do
        local counter=0
        for instruction in "${instructions[@]}"; do
            printf -v file_number "%03d" $counter
            echo "# $instruction implementation" > "${extension}/${level}/src/${file_number}-${instruction}.s"
            echo "# Reference data for $instruction" > "${extension}/${level}/reference/${file_number}-${instruction}.hex"
            counter=$((counter + 1))
        done
    done

    # Cria arquivos placeholders na pasta invalid
    counter=0
    for invalid_index in {1..5}; do  # Adiciona 5 placeholders como exemplo
        printf -v file_number "%03d" $counter
        echo "# Invalid instruction placeholder ${invalid_index}" > "${extension}/invalid/src/${file_number}-invalid${invalid_index}.s"
        echo "# Invalid reference placeholder ${invalid_index}" > "${extension}/invalid/reference/${file_number}-invalid${invalid_index}.hex"
        counter=$((counter + 1))
    done
}

# Itera sobre todas as extensões e cria suas estruturas
for extension in "${!EXTENSIONS[@]}"; do
    create_structure "$extension" "${EXTENSIONS[$extension]}"
done

echo "Estrutura de pastas e arquivos criada com sucesso!"
