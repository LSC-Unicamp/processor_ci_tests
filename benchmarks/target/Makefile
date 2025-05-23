# Makefile for libtarg on RISC-V RV32IMC

# RISC-V GCC toolchain prefix
RISCV_PREFIX = riscv32-unknown-elf

# Compiler and Arch Flags
CC = $(RISCV_PREFIX)-gcc
AR = $(RISCV_PREFIX)-ar
CFLAGS = -Wall -march=rv32imc -mabi=ilp32 -nostdlib -ffreestanding -static -mstrict-align

# Source files
SRC = libtarg.c
OBJ = libtarg.o
LIB = libtarg.a

# Default target
all: $(LIB)

# Compile object file
$(OBJ): $(SRC) libtarg.h
	$(CC) $(CFLAGS) -c $(SRC) -o $(OBJ)

# Create static library
$(LIB): $(OBJ)
	$(AR) rcs $(LIB) $(OBJ)

# Clean
clean:
	rm -f $(OBJ) $(LIB)
