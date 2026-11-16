OUTPUT_ARCH(riscv)
ENTRY(_start)

MEMORY {
  ram (rwx) : ORIGIN = 0, LENGTH = 8192
}

SECTIONS {
  .text : { *(.text .text.*) } > ram
  . = ALIGN(8);
  .rodata : { *(.rodata .rodata.*) } > ram
  .data : { *(.data .data.*) } > ram
  . = ALIGN(8);
  .tohost : { *(.tohost) } > ram
  .bss (NOLOAD) : { *(.bss .bss.*) *(COMMON) } > ram
  _end = .;
  ASSERT(_end <= ORIGIN(ram) + LENGTH(ram), "smoke ELF exceeds 8 KiB controller RAM")
}
