	.file	"134.call.c"
	.option nopic
	.attribute arch, "rv32i2p1_m2p0_a2p1_f2p2_d2p2_zicsr2p0"
	.attribute unaligned_access, 0
	.attribute stack_align, 16
	.text
	.align	2
	.globl	main
	.type	main, @function
main:
	addi	sp,sp,-32
	sw	ra,28(sp)
	sw	s0,24(sp)
	sw	s2,20(sp)
	sw	s3,16(sp)
	addi	s0,sp,32
	li	a0,13
	li	a1,0
	call	ulifibonacci
	sw	a0,-24(s0)
	sw	a1,-20(s0)
	li	a5,0
	li	a6,0
	mv	s2,a5
	mv	s3,a6
	sw	a5,-24(s0)
	sw	a6,-20(s0)
	li	a0,13
	li	a1,0
	call	slifibonacci
	sw	a0,-32(s0)
	sw	a1,-28(s0)
	mv	a5,s2
	mv	a6,s3
	sw	a5,-32(s0)
	sw	a6,-28(s0)
	li	a5,0
	mv	a0,a5
	lw	ra,28(sp)
	lw	s0,24(sp)
	lw	s2,20(sp)
	lw	s3,16(sp)
	addi	sp,sp,32
	jr	ra
	.size	main, .-main
	.align	2
	.globl	ulifibonacci
	.type	ulifibonacci, @function
ulifibonacci:
	addi	sp,sp,-32
	sw	ra,28(sp)
	sw	s0,24(sp)
	sw	s2,20(sp)
	sw	s3,16(sp)
	addi	s0,sp,32
	sw	a0,-24(s0)
	sw	a1,-20(s0)
	lw	a5,-20(s0)
	bne	a5,zero,.L4
	lw	a5,-20(s0)
	bne	a5,zero,.L7
	lw	a4,-24(s0)
	li	a5,2
	bgtu	a4,a5,.L4
.L7:
	li	a4,1
	li	a5,0
	j	.L6
.L4:
	lw	a4,-24(s0)
	lw	a5,-20(s0)
	li	a0,-1
	li	a1,-1
	add	a2,a4,a0
	mv	a6,a2
	sltu	a6,a6,a4
	add	a3,a5,a1
	add	a5,a6,a3
	mv	a3,a5
	mv	a4,a2
	mv	a5,a3
	mv	a0,a4
	mv	a1,a5
	call	ulifibonacci
	mv	s2,a0
	mv	s3,a1
	lw	a4,-24(s0)
	lw	a5,-20(s0)
	li	a0,-2
	li	a1,-1
	add	a2,a4,a0
	mv	a6,a2
	sltu	a6,a6,a4
	add	a3,a5,a1
	add	a5,a6,a3
	mv	a3,a5
	mv	a4,a2
	mv	a5,a3
	mv	a0,a4
	mv	a1,a5
	call	ulifibonacci
	mv	a2,a0
	mv	a3,a1
	add	a4,s2,a2
	mv	a1,a4
	sltu	a1,a1,s2
	add	a5,s3,a3
	add	a3,a1,a5
	mv	a5,a3
.L6:
	mv	a0,a4
	mv	a1,a5
	lw	ra,28(sp)
	lw	s0,24(sp)
	lw	s2,20(sp)
	lw	s3,16(sp)
	addi	sp,sp,32
	jr	ra
	.size	ulifibonacci, .-ulifibonacci
	.align	2
	.globl	slifibonacci
	.type	slifibonacci, @function
slifibonacci:
	addi	sp,sp,-32
	sw	ra,28(sp)
	sw	s0,24(sp)
	sw	s2,20(sp)
	sw	s3,16(sp)
	addi	s0,sp,32
	sw	a0,-24(s0)
	sw	a1,-20(s0)
	lw	a5,-20(s0)
	bgt	a5,zero,.L9
	lw	a5,-20(s0)
	bne	a5,zero,.L12
	lw	a4,-24(s0)
	li	a5,2
	bgtu	a4,a5,.L9
.L12:
	li	a4,1
	li	a5,0
	j	.L11
.L9:
	lw	a4,-24(s0)
	lw	a5,-20(s0)
	li	a0,-1
	li	a1,-1
	add	a2,a4,a0
	mv	a6,a2
	sltu	a6,a6,a4
	add	a3,a5,a1
	add	a5,a6,a3
	mv	a3,a5
	mv	a4,a2
	mv	a5,a3
	mv	a0,a4
	mv	a1,a5
	call	slifibonacci
	mv	s2,a0
	mv	s3,a1
	lw	a4,-24(s0)
	lw	a5,-20(s0)
	li	a0,-2
	li	a1,-1
	add	a2,a4,a0
	mv	a6,a2
	sltu	a6,a6,a4
	add	a3,a5,a1
	add	a5,a6,a3
	mv	a3,a5
	mv	a4,a2
	mv	a5,a3
	mv	a0,a4
	mv	a1,a5
	call	slifibonacci
	mv	a2,a0
	mv	a3,a1
	add	a4,s2,a2
	mv	a1,a4
	sltu	a1,a1,s2
	add	a5,s3,a3
	add	a3,a1,a5
	mv	a5,a3
.L11:
	mv	a0,a4
	mv	a1,a5
	lw	ra,28(sp)
	lw	s0,24(sp)
	lw	s2,20(sp)
	lw	s3,16(sp)
	addi	sp,sp,32
	jr	ra
	.size	slifibonacci, .-slifibonacci
	.ident	"GCC: () 13.2.0"