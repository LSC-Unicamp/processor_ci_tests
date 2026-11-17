.include "user_define.h"
.globl _start
.section .text
.option norvc;
_start:           
                  .include "user_init.s"
                  csrr x5, 0xf14
                  li x6, 0
                  beq x5, x6, 0f

0: la x2, h0_start
jalr x0, x2, 0
h0_start:
init:             
                  li x0, 0x80000000
                  li x1, 0xfd32be9f
                  li x2, 0x80000000
                  li x3, 0x0
                  li x4, 0xe6d0bcb9
                  li x5, 0x0
                  li x6, 0xf
                  li x7, 0xf
                  li x8, 0x0
                  li x9, 0x1
                  li x10, 0x9
                  li x11, 0xf799adf9
                  li x13, 0x3
                  li x14, 0x0
                  li x15, 0x33902ad5
                  li x16, 0x0
                  li x17, 0x5837ec53
                  li x18, 0xffa4b3d8
                  li x19, 0xf06da708
                  li x20, 0x80000000
                  li x21, 0x80000000
                  li x22, 0x80000000
                  li x23, 0x34f7fef9
                  li x24, 0x0
                  li x25, 0x7c62977b
                  li x26, 0x6
                  li x28, 0xf9abe9a2
                  li x29, 0x80000000
                  li x30, 0x0
                  li x31, 0x0
                  la x27, user_stack_end
main:             auipc       t3, 636713
                  sltiu       s7, tp, -1080
                  and         zero, s11, sp
                  srl         s9, s0, s7
                  sra         t1, s1, tp
                  xor         s7, sp, ra
                  lui         s1, 27715
                  li         a4, 0x0 #start riscv_int_numeric_corner_stream_0
                  li         t6, 0xa33c3cd
                  li         a5, 0x0
                  li         s8, 0x0
                  li         t4, 0x0
                  li         t5, 0x0
                  li         t0, 0x0
                  li         s0, 0x1
                  li         gp, 0x56b3f54f
                  li         t2, 0x1
                  addi        tp, s2, -787
                  sub         zero, a6, s3
                  addi        s5, tp, 1200
                  sub         zero, a4, s8
                  nop
                  add         t3, t5, gp
                  lui         gp, 602142
                  nop
                  add         zero, s4, a5
                  lui         s1, 554855
                  sub         s9, a7, ra
                  nop
                  addi        a1, s6, 1726
                  add         zero, tp, s5
                  sub         t5, t4, s9
                  addi        a5, s0, 540
                  nop
                  nop
                  addi        a7, a3, 1110
                  addi        s6, ra, 1356
                  sub         a1, t2, t3
                  addi        s5, a7, -837
                  addi        t5, t0, -1837
                  lui         ra, 599727
                  lui         zero, 760007 #end riscv_int_numeric_corner_stream_0
                  addi        s2, sp, 184
                  sll         zero, s8, t2
                  srai        t5, a5, 5
                  sra         s1, a6, t4
                  xori        gp, t5, 1634
                  auipc       s3, 351067
                  addi        t4, t0, 937
                  la x2, test_done
                  jalr x0, x2, 0
test_done:        
                  li gp, 1
                  j write_tohost
write_tohost:     
                  sw gp, tohost, t5

_exit:            
                  j write_tohost

.section .data
.align 6; .global tohost; tohost: .dword 0;
.align 6; .global fromhost; fromhost: .dword 0;
.section .user_stack,"aw",@progbits;
.align 2
user_stack_start:
.rept 4999
.4byte 0x0
.endr
user_stack_end:
.4byte 0x0
