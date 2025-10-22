OUTPUT_ARCH("riscv")
ENTRY(_start)

/* Memória do sistema */
MEMORY
{
  CODE_DATA (rwx)  : ORIGIN = 0x00000000, LENGTH = 0x20000   /* 128 KiB para código e dados */
  STACK     (rw)   : ORIGIN = 0x20000, LENGTH = 0x10000     /* 64 KiB pilha */
  STDOUT_BUF(rw)   : ORIGIN = 0x30000, LENGTH = 0x2000      /* 8 KiB buffer stdout */
  TIMER     (rw)   : ORIGIN = 0xFFFFFFF8, LENGTH = 0x4      /* timer 32-bit */
}

/* Seções */
SECTIONS
{
  /* Código */
  .text :
  {
    *(.text*)       /* todas as seções de texto */
  } > CODE_DATA

  /* Dados iniciais */
  .data :
  {
    *(.data*)       /* todas as seções de dados */
  } > CODE_DATA

  /* Variáveis não inicializadas */
  .bss :
  {
    *(.bss*)        /* todas as variáveis BSS */
  } > CODE_DATA

  /* Pilha */
  _stack_top = ORIGIN(STACK) + LENGTH(STACK);
  .stack (NOLOAD) :
  {
    /* Seção reservada apenas para a pilha */
  } > STACK

  /* Buffer de stdout */
  _stdout_base = ORIGIN(STDOUT_BUF);
  _stdout_top  = ORIGIN(STDOUT_BUF) + LENGTH(STDOUT_BUF);
  .stdout (NOLOAD) :
  {
    /* Seção reservada apenas para stdout em memória */
  } > STDOUT_BUF

  /* Timer */
  TIMER_REG = ORIGIN(TIMER);
  .timer (NOLOAD) :
  {
    /* Seção do timer mapeada no endereço fixo */
  } > TIMER
}
