#include "libtarg.h"

#define END_ADDRESS 0x140000 - 4 // 13FFFC
#define REG_CTRL (*(volatile unsigned int *) (END_ADDRESS))

#define CHAR_ADDRESS 0x140000 - 4096 // 13F000

#define HEAP_ADDRESS 0x140000 - 65536 // 130000

static volatile unsigned int *char_ptr = (volatile unsigned int *) CHAR_ADDRESS;
static volatile unsigned int *heap_ptr = (volatile unsigned int *) HEAP_ADDRESS;

/* benchmark completed successfully */
void libtarg_success(void){
    REG_CTRL = 0x474F4F44; // GOOD
}

/* benchmark completed with error CODE */
void libtarg_fail(int code){
    REG_CTRL = code; // error
}

/* output a single character, to whereever the target wants to send it... */
void libtarg_putc(char c){
    *char_ptr = (int) c;
    char_ptr++;
}

/* get some memory */
void *libtarg_sbrk(size_t inc){
    void *ptr = (void *) heap_ptr;
    heap_ptr += inc;
    if (heap_ptr > (volatile unsigned int *) END_ADDRESS) {
        libtarg_fail(0xDEAD);
    }
    return ptr;
}