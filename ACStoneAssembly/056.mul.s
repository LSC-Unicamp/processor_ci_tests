	.file	"056.mul.c"
	.option nopic
	.attribute arch, "rv32i2p1_m2p0_a2p1_f2p2_d2p2_zicsr2p0"
	.attribute unaligned_access, 0
	.attribute stack_align, 16
	.text
	.align	2
	.globl	main
	.type	main, @function
main:
	addi	sp,sp,-288
	sw	s0,284(sp)
	sw	s2,280(sp)
	sw	s3,276(sp)
	sw	s4,272(sp)
	sw	s5,268(sp)
	sw	s6,264(sp)
	sw	s7,260(sp)
	sw	s8,256(sp)
	sw	s9,252(sp)
	sw	s10,248(sp)
	sw	s11,244(sp)
	addi	s0,sp,288
	li	a5,2
	sw	a5,-52(s0)
	li	a5,4
	sw	a5,-56(s0)
	lw	a5,-52(s0)
	mv	a0,a5
	li	a1,0
	lw	a5,-56(s0)
	mv	a2,a5
	li	a3,0
	mul	a4,a1,a2
	mul	a5,a3,a0
	add	a4,a4,a5
	mul	a5,a0,a2
	mulhu	a7,a0,a2
	mv	a6,a5
	add	a5,a4,a7
	mv	a7,a5
	sw	a6,-64(s0)
	sw	a7,-60(s0)
	sw	a6,-64(s0)
	sw	a7,-60(s0)
	li	a2,0
	li	a3,0
	sw	a2,-64(s0)
	sw	a3,-60(s0)
	li	a5,-1
	sw	a5,-52(s0)
	li	a5,-1
	sw	a5,-56(s0)
	lw	a5,-52(s0)
	mv	t3,a5
	li	t4,0
	lw	a5,-56(s0)
	mv	t1,a5
	li	t2,0
	mul	a4,t4,t1
	mul	a5,t2,t3
	add	a4,a4,a5
	mul	a5,t3,t1
	mulhu	t6,t3,t1
	mv	t5,a5
	add	a5,a4,t6
	mv	t6,a5
	sw	t5,-64(s0)
	sw	t6,-60(s0)
	sw	t5,-64(s0)
	sw	t6,-60(s0)
	sw	a2,-64(s0)
	sw	a3,-60(s0)
	li	a5,-1
	sw	a5,-52(s0)
	li	a5,1
	sw	a5,-56(s0)
	lw	a5,-52(s0)
	mv	s4,a5
	li	s5,0
	lw	a5,-56(s0)
	mv	s2,a5
	li	s3,0
	mul	a4,s5,s2
	mul	a5,s3,s4
	add	a4,a4,a5
	mul	a5,s4,s2
	mulhu	s7,s4,s2
	mv	s6,a5
	add	a5,a4,s7
	mv	s7,a5
	sw	s6,-64(s0)
	sw	s7,-60(s0)
	sw	s6,-64(s0)
	sw	s7,-60(s0)
	sw	a2,-64(s0)
	sw	a3,-60(s0)
	li	a5,-1
	sw	a5,-52(s0)
	li	a5,10
	sw	a5,-56(s0)
	lw	a5,-52(s0)
	mv	s10,a5
	li	s11,0
	lw	a5,-56(s0)
	mv	s8,a5
	li	s9,0
	mul	a4,s11,s8
	mul	a5,s9,s10
	add	a4,a4,a5
	mul	a5,s10,s8
	mulhu	a1,s10,s8
	sw	a1,-68(s0)
	sw	a5,-72(s0)
	lw	a5,-68(s0)
	add	a5,a4,a5
	sw	a5,-68(s0)
	lw	a5,-72(s0)
	lw	a6,-68(s0)
	sw	a5,-64(s0)
	sw	a6,-60(s0)
	sw	a5,-64(s0)
	sw	a6,-60(s0)
	sw	a2,-64(s0)
	sw	a3,-60(s0)
	li	a5,-2
	sw	a5,-52(s0)
	li	a5,-4
	sw	a5,-56(s0)
	lw	a5,-52(s0)
	sw	a5,-152(s0)
	sw	zero,-148(s0)
	lw	a5,-56(s0)
	sw	a5,-160(s0)
	sw	zero,-156(s0)
	lw	a5,-152(s0)
	lw	a6,-148(s0)
	mv	a4,a6
	lw	a0,-160(s0)
	lw	a1,-156(s0)
	mv	a7,a0
	mul	a4,a4,a7
	mv	t1,a1
	mv	a7,a6
	mv	a6,a5
	mv	a5,a6
	mul	a5,t1,a5
	add	a4,a4,a5
	mv	a5,a6
	mv	t1,a0
	mul	a5,a5,t1
	mv	a1,a0
	mulhu	a1,a6,a1
	sw	a1,-76(s0)
	sw	a5,-80(s0)
	lw	a5,-76(s0)
	add	a5,a4,a5
	sw	a5,-76(s0)
	lw	a5,-80(s0)
	lw	a6,-76(s0)
	sw	a5,-64(s0)
	sw	a6,-60(s0)
	sw	a5,-64(s0)
	sw	a6,-60(s0)
	sw	a2,-64(s0)
	sw	a3,-60(s0)
	li	a5,10
	sw	a5,-52(s0)
	li	a5,11
	sw	a5,-56(s0)
	lw	a5,-52(s0)
	sw	a5,-168(s0)
	sw	zero,-164(s0)
	lw	a5,-56(s0)
	sw	a5,-176(s0)
	sw	zero,-172(s0)
	lw	a5,-168(s0)
	lw	a6,-164(s0)
	mv	a4,a6
	lw	a0,-176(s0)
	lw	a1,-172(s0)
	mv	a7,a0
	mul	a4,a4,a7
	mv	t1,a1
	mv	a7,a6
	mv	a6,a5
	mv	a5,a6
	mul	a5,t1,a5
	add	a4,a4,a5
	mv	a5,a6
	mv	t1,a0
	mul	a5,a5,t1
	mv	a1,a0
	mulhu	a1,a6,a1
	sw	a1,-84(s0)
	sw	a5,-88(s0)
	lw	a5,-84(s0)
	add	a5,a4,a5
	sw	a5,-84(s0)
	lw	a5,-88(s0)
	lw	a6,-84(s0)
	sw	a5,-64(s0)
	sw	a6,-60(s0)
	sw	a5,-64(s0)
	sw	a6,-60(s0)
	sw	a2,-64(s0)
	sw	a3,-60(s0)
	li	a5,-10
	sw	a5,-52(s0)
	li	a5,11
	sw	a5,-56(s0)
	lw	a5,-52(s0)
	sw	a5,-184(s0)
	sw	zero,-180(s0)
	lw	a5,-56(s0)
	sw	a5,-192(s0)
	sw	zero,-188(s0)
	lw	a5,-184(s0)
	lw	a6,-180(s0)
	mv	a4,a6
	lw	a0,-192(s0)
	lw	a1,-188(s0)
	mv	a7,a0
	mul	a4,a4,a7
	mv	t1,a1
	mv	a7,a6
	mv	a6,a5
	mv	a5,a6
	mul	a5,t1,a5
	add	a4,a4,a5
	mv	a5,a6
	mv	t1,a0
	mul	a5,a5,t1
	mv	a1,a0
	mulhu	a1,a6,a1
	sw	a1,-92(s0)
	sw	a5,-96(s0)
	lw	a5,-92(s0)
	add	a5,a4,a5
	sw	a5,-92(s0)
	lw	a5,-96(s0)
	lw	a6,-92(s0)
	sw	a5,-64(s0)
	sw	a6,-60(s0)
	sw	a5,-64(s0)
	sw	a6,-60(s0)
	sw	a2,-64(s0)
	sw	a3,-60(s0)
	li	a5,61440
	sw	a5,-52(s0)
	li	a5,61440
	addi	a5,a5,1
	sw	a5,-56(s0)
	lw	a5,-52(s0)
	sw	a5,-200(s0)
	sw	zero,-196(s0)
	lw	a5,-56(s0)
	sw	a5,-208(s0)
	sw	zero,-204(s0)
	lw	a5,-200(s0)
	lw	a6,-196(s0)
	mv	a4,a6
	lw	a0,-208(s0)
	lw	a1,-204(s0)
	mv	a7,a0
	mul	a4,a4,a7
	mv	t1,a1
	mv	a7,a6
	mv	a6,a5
	mv	a5,a6
	mul	a5,t1,a5
	add	a4,a4,a5
	mv	a5,a6
	mv	t1,a0
	mul	a5,a5,t1
	mv	a1,a0
	mulhu	a1,a6,a1
	sw	a1,-100(s0)
	sw	a5,-104(s0)
	lw	a5,-100(s0)
	add	a5,a4,a5
	sw	a5,-100(s0)
	lw	a5,-104(s0)
	lw	a6,-100(s0)
	sw	a5,-64(s0)
	sw	a6,-60(s0)
	sw	a5,-64(s0)
	sw	a6,-60(s0)
	sw	a2,-64(s0)
	sw	a3,-60(s0)
	li	a5,1431654400
	addi	a5,a5,1365
	sw	a5,-52(s0)
	li	a5,858992640
	addi	a5,a5,819
	sw	a5,-56(s0)
	lw	a5,-52(s0)
	sw	a5,-216(s0)
	sw	zero,-212(s0)
	lw	a5,-56(s0)
	sw	a5,-224(s0)
	sw	zero,-220(s0)
	lw	a5,-216(s0)
	lw	a6,-212(s0)
	mv	a4,a6
	lw	a0,-224(s0)
	lw	a1,-220(s0)
	mv	a7,a0
	mul	a4,a4,a7
	mv	t1,a1
	mv	a7,a6
	mv	a6,a5
	mv	a5,a6
	mul	a5,t1,a5
	add	a4,a4,a5
	mv	a5,a6
	mv	t1,a0
	mul	a5,a5,t1
	mv	a1,a0
	mulhu	a1,a6,a1
	sw	a1,-108(s0)
	sw	a5,-112(s0)
	lw	a5,-108(s0)
	add	a5,a4,a5
	sw	a5,-108(s0)
	lw	a5,-112(s0)
	lw	a6,-108(s0)
	sw	a5,-64(s0)
	sw	a6,-60(s0)
	sw	a5,-64(s0)
	sw	a6,-60(s0)
	sw	a2,-64(s0)
	sw	a3,-60(s0)
	li	a5,20480
	addi	a5,a5,851
	sw	a5,-52(s0)
	li	a5,32768
	sw	a5,-56(s0)
	lw	a5,-52(s0)
	sw	a5,-232(s0)
	sw	zero,-228(s0)
	lw	a5,-56(s0)
	sw	a5,-240(s0)
	sw	zero,-236(s0)
	lw	a5,-232(s0)
	lw	a6,-228(s0)
	mv	a4,a6
	lw	a0,-240(s0)
	lw	a1,-236(s0)
	mv	a7,a0
	mul	a4,a4,a7
	mv	t1,a1
	mv	a7,a6
	mv	a6,a5
	mv	a5,a6
	mul	a5,t1,a5
	add	a5,a4,a5
	mv	a4,a6
	mv	t1,a0
	mul	a4,a4,t1
	mv	a1,a0
	mulhu	a1,a6,a1
	sw	a1,-116(s0)
	sw	a4,-120(s0)
	lw	a4,-116(s0)
	add	a5,a5,a4
	sw	a5,-116(s0)
	lw	a5,-120(s0)
	lw	a6,-116(s0)
	sw	a5,-64(s0)
	sw	a6,-60(s0)
	sw	a5,-64(s0)
	sw	a6,-60(s0)
	sw	a2,-64(s0)
	sw	a3,-60(s0)
	li	a5,-4096
	sw	a5,-52(s0)
	li	a5,-4096
	addi	a5,a5,1
	sw	a5,-56(s0)
	lw	a5,-52(s0)
	sw	a5,-248(s0)
	sw	zero,-244(s0)
	lw	a5,-56(s0)
	sw	a5,-256(s0)
	sw	zero,-252(s0)
	lw	a5,-248(s0)
	lw	a6,-244(s0)
	mv	a4,a6
	lw	a0,-256(s0)
	lw	a1,-252(s0)
	mv	a7,a0
	mul	a4,a4,a7
	mv	t1,a1
	mv	a7,a6
	mv	a6,a5
	mv	a5,a6
	mul	a5,t1,a5
	add	a5,a4,a5
	mv	a4,a6
	mv	t1,a0
	mul	a4,a4,t1
	mv	a1,a0
	mulhu	a1,a6,a1
	sw	a1,-124(s0)
	sw	a4,-128(s0)
	lw	a4,-124(s0)
	add	a5,a5,a4
	sw	a5,-124(s0)
	lw	a5,-128(s0)
	lw	a6,-124(s0)
	sw	a5,-64(s0)
	sw	a6,-60(s0)
	sw	a5,-64(s0)
	sw	a6,-60(s0)
	sw	a2,-64(s0)
	sw	a3,-60(s0)
	li	a5,20480
	addi	a5,a5,1365
	sw	a5,-52(s0)
	li	a5,858980352
	sw	a5,-56(s0)
	lw	a5,-52(s0)
	sw	a5,-264(s0)
	sw	zero,-260(s0)
	lw	a5,-56(s0)
	sw	a5,-272(s0)
	sw	zero,-268(s0)
	lw	a5,-264(s0)
	lw	a6,-260(s0)
	mv	a4,a6
	lw	a0,-272(s0)
	lw	a1,-268(s0)
	mv	a7,a0
	mul	a4,a4,a7
	mv	t1,a1
	mv	a7,a6
	mv	a6,a5
	mv	a5,a6
	mul	a5,t1,a5
	add	a5,a4,a5
	mv	a4,a6
	mv	t1,a0
	mul	a4,a4,t1
	mv	a1,a0
	mulhu	a1,a6,a1
	sw	a1,-132(s0)
	sw	a4,-136(s0)
	lw	a4,-132(s0)
	add	a5,a5,a4
	sw	a5,-132(s0)
	lw	a5,-136(s0)
	lw	a6,-132(s0)
	sw	a5,-64(s0)
	sw	a6,-60(s0)
	sw	a5,-64(s0)
	sw	a6,-60(s0)
	sw	a2,-64(s0)
	sw	a3,-60(s0)
	li	a5,1397968896
	addi	a5,a5,851
	sw	a5,-52(s0)
	li	a5,-2147450880
	sw	a5,-56(s0)
	lw	a5,-52(s0)
	sw	a5,-280(s0)
	sw	zero,-276(s0)
	lw	a5,-56(s0)
	sw	a5,-288(s0)
	sw	zero,-284(s0)
	lw	a5,-280(s0)
	lw	a6,-276(s0)
	mv	a4,a6
	lw	a0,-288(s0)
	lw	a1,-284(s0)
	mv	a7,a0
	mul	a4,a4,a7
	mv	t1,a1
	mv	a7,a6
	mv	a6,a5
	mv	a5,a6
	mul	a5,t1,a5
	add	a5,a4,a5
	mv	a4,a6
	mv	t1,a0
	mul	a4,a4,t1
	mv	a1,a0
	mulhu	a1,a6,a1
	sw	a1,-140(s0)
	sw	a4,-144(s0)
	lw	a4,-140(s0)
	add	a5,a5,a4
	sw	a5,-140(s0)
	lw	a5,-144(s0)
	lw	a6,-140(s0)
	sw	a5,-64(s0)
	sw	a6,-60(s0)
	sw	a5,-64(s0)
	sw	a6,-60(s0)
	sw	a2,-64(s0)
	sw	a3,-60(s0)
	li	a5,0
	mv	a0,a5
	lw	s0,284(sp)
	lw	s2,280(sp)
	lw	s3,276(sp)
	lw	s4,272(sp)
	lw	s5,268(sp)
	lw	s6,264(sp)
	lw	s7,260(sp)
	lw	s8,256(sp)
	lw	s9,252(sp)
	lw	s10,248(sp)
	lw	s11,244(sp)
	addi	sp,sp,288
	jr	ra
	.size	main, .-main
	.ident	"GCC: () 13.2.0"