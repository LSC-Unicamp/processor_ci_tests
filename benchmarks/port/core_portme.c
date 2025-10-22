#include <stdio.h>
#include <stdlib.h>
#include "coremark.h"

#define CPU_FREQ_HZ 25000000 // 25 MHz
#define ITERATIONS 10000

volatile ee_s32 seed1_volatile=0x0;
volatile ee_s32 seed2_volatile=0x0;
volatile ee_s32 seed3_volatile=0x66;


volatile ee_s32 seed4_volatile=ITERATIONS;
volatile ee_s32 seed5_volatile=0;

volatile uint32_t t0_low, t0_high;
volatile uint32_t t1_low, t1_high;
static CORE_TICKS t0, t1;

static inline uint64_t read_timer64(void)
{
    uint32_t lo, hi;

    __asm__ volatile (
        "lw %0, 0xFFFFFFF8(zero)\n"
        "lw %1, 0xFFFFFFFC(zero)\n"
        : "=r"(lo), "=r"(hi)
    );

    return ((uint64_t)hi << 32) | lo;
}

void start_time(void)
{
    t0 = read_timer64();
}

void stop_time(void)
{
    t1 = read_timer64();
}

CORE_TICKS get_time(void)
{
  return t1 - t0;
}

secs_ret time_in_secs(CORE_TICKS ticks)
{
    // retorna tempo em milissegundos (inteiro)
    uint64_t ms = ((uint64_t)ticks * 1000ULL) / CPU_FREQ_HZ;
    return (secs_ret)ms;
}

void portable_init(core_portable *p, int *argc, char *argv[])
{
    
}

void portable_fini(core_portable *p){

}