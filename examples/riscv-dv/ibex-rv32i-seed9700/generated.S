.include "user_define.h"
.globl _start
.section .text
.option norvc;
_start:           
                  .include "user_init.s"
                  csrr x5, 0xf14
                  li x6, 0
                  beq x5, x6, 0f

0: la x31, h0_start
jalr x0, x31, 0
h0_start:
init:             
                  li x0, 0x80000000
                  li x1, 0xf02c3f3d
                  li x2, 0xe0c8bdb
                  li x3, 0x80000000
                  li x4, 0x80000000
                  li x5, 0x0
                  li x6, 0xe
                  li x7, 0x0
                  li x8, 0xf
                  li x9, 0x80000000
                  li x10, 0x80000000
                  li x11, 0x0
                  li x12, 0x9c502617
                  li x13, 0x0
                  li x14, 0xfaf87cc5
                  li x15, 0xbbb38004
                  li x16, 0x0
                  li x17, 0x0
                  li x18, 0xf758bfe6
                  li x20, 0x80000000
                  li x21, 0x0
                  li x22, 0x80000000
                  li x23, 0xe
                  li x24, 0x33355f65
                  li x25, 0xa
                  li x26, 0xffcc4b14
                  li x27, 0x80000000
                  li x28, 0x4a971332
                  li x29, 0x7
                  li x31, 0x33479c09
                  la x19, user_stack_end
main:             srli        s8, tp, 4
                  srai        s10, t2, 4
                  li         s5, 0x211fa009 #start riscv_int_numeric_corner_stream_0
                  li         t3, 0x1
                  li         a2, 0x0
                  li         s4, 0x2f96b4f8
                  li         s9, 0x6697420b
                  li         s10, 0x1
                  li         s8, 0x7af703c6
                  li         t4, 0x659839fd
                  li         a3, 0x0
                  li         s7, 0x1
                  nop
                  nop
                  add         a0, t5, s9
                  nop
                  addi        s11, ra, -547
                  add         s4, t0, zero
                  nop
                  add         s11, gp, a7
                  nop
                  nop
                  sub         zero, s0, s4
                  lui         sp, 239114
                  nop
                  add         a3, a7, sp
                  lui         zero, 1033997
                  sub         s8, t6, a3
                  addi        s9, ra, -655
                  lui         s2, 920683
                  lui         s8, 820452
                  sub         s1, t4, ra
                  addi        zero, a5, 216 #end riscv_int_numeric_corner_stream_0
                  slli        s2, s7, 27
                  ori         s8, sp, -12
                  srai        ra, s8, 13
                  xori        s10, a7, 1209
                  sltiu       s9, a3, -1592
                  auipc       s2, 395349
                  slti        gp, s10, -580
                  srai        a5, t0, 2
                  sltiu       a6, zero, 899
                  srl         t4, a5, t2
                  slt         s10, s8, a4
                  sltiu       s9, s9, -1033
                  slli        a3, a7, 1
                  sra         s6, a5, a2
                  sltu        s6, s10, sp
                  srli        a3, t0, 3
                  add         a1, a3, s10
                  nop
                  andi        s7, s1, 882
                  and         zero, t6, a3
                  addi        s11, a5, -895
                  addi        s8, sp, -1176
                  addi        s10, s0, -292
                  add         s11, t1, gp
                  slt         s2, t2, zero
                  sltu        s6, t6, t4
                  sltu        a1, s4, t0
                  sra         a3, s8, gp
                  xor         s1, s6, sp
                  xori        a2, s4, -866
                  lui         s2, 314307
                  la x31, test_done
                  jalr x0, x31, 0
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
