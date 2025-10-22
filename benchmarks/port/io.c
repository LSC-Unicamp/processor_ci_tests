#include <unistd.h>
#include <stdint.h>

#define OUT_BUFFER_BASE 0x30000
#define OUT_BUFFER_SIZE 0x00002000

volatile char *stdout_ptr = (volatile char *)OUT_BUFFER_BASE;
volatile char *stdout_init = (volatile char *)OUT_BUFFER_BASE;
volatile char *stdout_end = (char *)(OUT_BUFFER_BASE + OUT_BUFFER_SIZE);

int _write(int file, char *ptr, int len){
    for(int i=0; i<len; i++){
        if(stdout_ptr < stdout_end){
            *stdout_ptr++ = *ptr++;
        } else {
            break;
        }
    }

    return len;
}

int _sbrk(int incr){
    return 0;
}

int _close(int file){
    return -1;
}

int _read(int file, char *ptr, int len){
    return 0;
}


int _lseek(int file, int ptr, int dir){
    return 0;
}