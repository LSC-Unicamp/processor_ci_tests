
coremark.bare.riscv:     file format elf32-littleriscv


Disassembly of section .text.init:

80000000 <_start>:
80000000:	4081                	li	ra,0
80000002:	4101                	li	sp,0
80000004:	4181                	li	gp,0
80000006:	4201                	li	tp,0
80000008:	4281                	li	t0,0
8000000a:	4301                	li	t1,0
8000000c:	4381                	li	t2,0
8000000e:	4401                	li	s0,0
80000010:	4481                	li	s1,0
80000012:	4501                	li	a0,0
80000014:	4581                	li	a1,0
80000016:	4601                	li	a2,0
80000018:	4681                	li	a3,0
8000001a:	4701                	li	a4,0
8000001c:	4781                	li	a5,0
8000001e:	4801                	li	a6,0
80000020:	4881                	li	a7,0
80000022:	4901                	li	s2,0
80000024:	4981                	li	s3,0
80000026:	4a01                	li	s4,0
80000028:	4a81                	li	s5,0
8000002a:	4b01                	li	s6,0
8000002c:	4b81                	li	s7,0
8000002e:	4c01                	li	s8,0
80000030:	4c81                	li	s9,0
80000032:	4d01                	li	s10,0
80000034:	4d81                	li	s11,0
80000036:	4e01                	li	t3,0
80000038:	4e81                	li	t4,0
8000003a:	4f01                	li	t5,0
8000003c:	4f81                	li	t6,0
8000003e:	62f9                	lui	t0,0x1e
80000040:	3002a073          	csrs	mstatus,t0
80000044:	4285                	li	t0,1
80000046:	02fe                	slli	t0,t0,0x1f
80000048:	0002c863          	bltz	t0,80000058 <_start+0x58>
8000004c:	4505                	li	a0,1
8000004e:	00001297          	auipc	t0,0x1
80000052:	faa2a923          	sw	a0,-78(t0) # 80001000 <tohost>
80000056:	bfdd                	j	8000004c <_start+0x4c>
80000058:	00000297          	auipc	t0,0x0
8000005c:	09028293          	addi	t0,t0,144 # 800000e8 <_start+0xe8>
80000060:	30529073          	csrw	mtvec,t0
80000064:	00301073          	fscsr	zero
80000068:	f0000053          	fmv.w.x	ft0,zero
8000006c:	f00000d3          	fmv.w.x	ft1,zero
80000070:	f0000153          	fmv.w.x	ft2,zero
80000074:	f00001d3          	fmv.w.x	ft3,zero
80000078:	f0000253          	fmv.w.x	ft4,zero
8000007c:	f00002d3          	fmv.w.x	ft5,zero
80000080:	f0000353          	fmv.w.x	ft6,zero
80000084:	f00003d3          	fmv.w.x	ft7,zero
80000088:	f0000453          	fmv.w.x	fs0,zero
8000008c:	f00004d3          	fmv.w.x	fs1,zero
80000090:	f0000553          	fmv.w.x	fa0,zero
80000094:	f00005d3          	fmv.w.x	fa1,zero
80000098:	f0000653          	fmv.w.x	fa2,zero
8000009c:	f00006d3          	fmv.w.x	fa3,zero
800000a0:	f0000753          	fmv.w.x	fa4,zero
800000a4:	f00007d3          	fmv.w.x	fa5,zero
800000a8:	f0000853          	fmv.w.x	fa6,zero
800000ac:	f00008d3          	fmv.w.x	fa7,zero
800000b0:	f0000953          	fmv.w.x	fs2,zero
800000b4:	f00009d3          	fmv.w.x	fs3,zero
800000b8:	f0000a53          	fmv.w.x	fs4,zero
800000bc:	f0000ad3          	fmv.w.x	fs5,zero
800000c0:	f0000b53          	fmv.w.x	fs6,zero
800000c4:	f0000bd3          	fmv.w.x	fs7,zero
800000c8:	f0000c53          	fmv.w.x	fs8,zero
800000cc:	f0000cd3          	fmv.w.x	fs9,zero
800000d0:	f0000d53          	fmv.w.x	fs10,zero
800000d4:	f0000dd3          	fmv.w.x	fs11,zero
800000d8:	f0000e53          	fmv.w.x	ft8,zero
800000dc:	f0000ed3          	fmv.w.x	ft9,zero
800000e0:	f0000f53          	fmv.w.x	ft10,zero
800000e4:	f0000fd3          	fmv.w.x	ft11,zero
800000e8:	00000297          	auipc	t0,0x0
800000ec:	03828293          	addi	t0,t0,56 # 80000120 <trap_entry>
800000f0:	30529073          	csrw	mtvec,t0
800000f4:	00004197          	auipc	gp,0x4
800000f8:	7ec18193          	addi	gp,gp,2028 # 800048e0 <__global_pointer$>
800000fc:	05f18213          	addi	tp,gp,95 # 8000493f <_end+0x3f>
80000100:	fc027213          	andi	tp,tp,-64
80000104:	f1402573          	csrr	a0,mhartid
80000108:	4585                	li	a1,1
8000010a:	00b57063          	bgeu	a0,a1,8000010a <_start+0x10a>
8000010e:	01151613          	slli	a2,a0,0x11
80000112:	9232                	add	tp,tp,a2
80000114:	00150113          	addi	sp,a0,1
80000118:	0146                	slli	sp,sp,0x11
8000011a:	9112                	add	sp,sp,tp
8000011c:	06f0206f          	j	8000298a <_init>

80000120 <trap_entry>:
80000120:	716d                	addi	sp,sp,-272
80000122:	c206                	sw	ra,4(sp)
80000124:	c40a                	sw	sp,8(sp)
80000126:	c60e                	sw	gp,12(sp)
80000128:	c812                	sw	tp,16(sp)
8000012a:	ca16                	sw	t0,20(sp)
8000012c:	cc1a                	sw	t1,24(sp)
8000012e:	ce1e                	sw	t2,28(sp)
80000130:	d022                	sw	s0,32(sp)
80000132:	d226                	sw	s1,36(sp)
80000134:	d42a                	sw	a0,40(sp)
80000136:	d62e                	sw	a1,44(sp)
80000138:	d832                	sw	a2,48(sp)
8000013a:	da36                	sw	a3,52(sp)
8000013c:	dc3a                	sw	a4,56(sp)
8000013e:	de3e                	sw	a5,60(sp)
80000140:	c0c2                	sw	a6,64(sp)
80000142:	c2c6                	sw	a7,68(sp)
80000144:	c4ca                	sw	s2,72(sp)
80000146:	c6ce                	sw	s3,76(sp)
80000148:	c8d2                	sw	s4,80(sp)
8000014a:	cad6                	sw	s5,84(sp)
8000014c:	ccda                	sw	s6,88(sp)
8000014e:	cede                	sw	s7,92(sp)
80000150:	d0e2                	sw	s8,96(sp)
80000152:	d2e6                	sw	s9,100(sp)
80000154:	d4ea                	sw	s10,104(sp)
80000156:	d6ee                	sw	s11,108(sp)
80000158:	d8f2                	sw	t3,112(sp)
8000015a:	daf6                	sw	t4,116(sp)
8000015c:	dcfa                	sw	t5,120(sp)
8000015e:	defe                	sw	t6,124(sp)
80000160:	34202573          	csrr	a0,mcause
80000164:	341025f3          	csrr	a1,mepc
80000168:	860a                	mv	a2,sp
8000016a:	614020ef          	jal	8000277e <handle_trap>
8000016e:	34151073          	csrw	mepc,a0
80000172:	6289                	lui	t0,0x2
80000174:	80028293          	addi	t0,t0,-2048 # 1800 <_tbss_end+0x17bc>
80000178:	3002a073          	csrs	mstatus,t0
8000017c:	4092                	lw	ra,4(sp)
8000017e:	4122                	lw	sp,8(sp)
80000180:	41b2                	lw	gp,12(sp)
80000182:	4242                	lw	tp,16(sp)
80000184:	42d2                	lw	t0,20(sp)
80000186:	4362                	lw	t1,24(sp)
80000188:	43f2                	lw	t2,28(sp)
8000018a:	5402                	lw	s0,32(sp)
8000018c:	5492                	lw	s1,36(sp)
8000018e:	5522                	lw	a0,40(sp)
80000190:	55b2                	lw	a1,44(sp)
80000192:	5642                	lw	a2,48(sp)
80000194:	56d2                	lw	a3,52(sp)
80000196:	5762                	lw	a4,56(sp)
80000198:	57f2                	lw	a5,60(sp)
8000019a:	4806                	lw	a6,64(sp)
8000019c:	4896                	lw	a7,68(sp)
8000019e:	4926                	lw	s2,72(sp)
800001a0:	49b6                	lw	s3,76(sp)
800001a2:	4a46                	lw	s4,80(sp)
800001a4:	4ad6                	lw	s5,84(sp)
800001a6:	4b66                	lw	s6,88(sp)
800001a8:	4bf6                	lw	s7,92(sp)
800001aa:	5c06                	lw	s8,96(sp)
800001ac:	5c96                	lw	s9,100(sp)
800001ae:	5d26                	lw	s10,104(sp)
800001b0:	5db6                	lw	s11,108(sp)
800001b2:	5e46                	lw	t3,112(sp)
800001b4:	5ed6                	lw	t4,116(sp)
800001b6:	5f66                	lw	t5,120(sp)
800001b8:	5ff6                	lw	t6,124(sp)
800001ba:	6151                	addi	sp,sp,272
800001bc:	30200073          	mret
	...

Disassembly of section .text:

80001048 <cmp_idx>:
80001048:	c619                	beqz	a2,80001056 <cmp_idx+0xe>
8000104a:	00251503          	lh	a0,2(a0)
8000104e:	00259783          	lh	a5,2(a1)
80001052:	8d1d                	sub	a0,a0,a5
80001054:	8082                	ret
80001056:	00051783          	lh	a5,0(a0)
8000105a:	01079713          	slli	a4,a5,0x10
8000105e:	8341                	srli	a4,a4,0x10
80001060:	8321                	srli	a4,a4,0x8
80001062:	f007f793          	andi	a5,a5,-256
80001066:	8fd9                	or	a5,a5,a4
80001068:	00f51023          	sh	a5,0(a0)
8000106c:	00059783          	lh	a5,0(a1)
80001070:	00251503          	lh	a0,2(a0)
80001074:	01079713          	slli	a4,a5,0x10
80001078:	8341                	srli	a4,a4,0x10
8000107a:	8321                	srli	a4,a4,0x8
8000107c:	f007f793          	andi	a5,a5,-256
80001080:	8fd9                	or	a5,a5,a4
80001082:	00f59023          	sh	a5,0(a1)
80001086:	00259783          	lh	a5,2(a1)
8000108a:	8d1d                	sub	a0,a0,a5
8000108c:	8082                	ret

8000108e <calc_func>:
8000108e:	1101                	addi	sp,sp,-32
80001090:	cc22                	sw	s0,24(sp)
80001092:	00051403          	lh	s0,0(a0)
80001096:	ce06                	sw	ra,28(sp)
80001098:	40745793          	srai	a5,s0,0x7
8000109c:	8b85                	andi	a5,a5,1
8000109e:	c799                	beqz	a5,800010ac <calc_func+0x1e>
800010a0:	40f2                	lw	ra,28(sp)
800010a2:	07f47513          	andi	a0,s0,127
800010a6:	4462                	lw	s0,24(sp)
800010a8:	6105                	addi	sp,sp,32
800010aa:	8082                	ret
800010ac:	40345713          	srai	a4,s0,0x3
800010b0:	8b3d                	andi	a4,a4,15
800010b2:	00471793          	slli	a5,a4,0x4
800010b6:	00f70633          	add	a2,a4,a5
800010ba:	ca26                	sw	s1,20(sp)
800010bc:	c64e                	sw	s3,12(sp)
800010be:	c84a                	sw	s2,16(sp)
800010c0:	00747693          	andi	a3,s0,7
800010c4:	0385d783          	lhu	a5,56(a1)
800010c8:	89aa                	mv	s3,a0
800010ca:	84ae                	mv	s1,a1
800010cc:	8732                	mv	a4,a2
800010ce:	c2a5                	beqz	a3,8000112e <calc_func+0xa0>
800010d0:	4605                	li	a2,1
800010d2:	04c69963          	bne	a3,a2,80001124 <calc_func+0x96>
800010d6:	863e                	mv	a2,a5
800010d8:	85ba                	mv	a1,a4
800010da:	02848513          	addi	a0,s1,40
800010de:	3d1000ef          	jal	80001cae <core_bench_matrix>
800010e2:	03c4d783          	lhu	a5,60(s1)
800010e6:	01051913          	slli	s2,a0,0x10
800010ea:	41095913          	srai	s2,s2,0x10
800010ee:	e7bd                	bnez	a5,8000115c <calc_func+0xce>
800010f0:	0384d783          	lhu	a5,56(s1)
800010f4:	02a49e23          	sh	a0,60(s1)
800010f8:	85be                	mv	a1,a5
800010fa:	03a010ef          	jal	80002134 <crcu16>
800010fe:	87aa                	mv	a5,a0
80001100:	f0047413          	andi	s0,s0,-256
80001104:	07f97513          	andi	a0,s2,127
80001108:	8c49                	or	s0,s0,a0
8000110a:	02f49c23          	sh	a5,56(s1)
8000110e:	08046413          	ori	s0,s0,128
80001112:	00899023          	sh	s0,0(s3)
80001116:	40f2                	lw	ra,28(sp)
80001118:	4462                	lw	s0,24(sp)
8000111a:	44d2                	lw	s1,20(sp)
8000111c:	4942                	lw	s2,16(sp)
8000111e:	49b2                	lw	s3,12(sp)
80001120:	6105                	addi	sp,sp,32
80001122:	8082                	ret
80001124:	01041513          	slli	a0,s0,0x10
80001128:	8141                	srli	a0,a0,0x10
8000112a:	8922                	mv	s2,s0
8000112c:	b7f1                	j	800010f8 <calc_func+0x6a>
8000112e:	02100693          	li	a3,33
80001132:	00c6e463          	bltu	a3,a2,8000113a <calc_func+0xac>
80001136:	02200713          	li	a4,34
8000113a:	00249683          	lh	a3,2(s1)
8000113e:	00049603          	lh	a2,0(s1)
80001142:	48cc                	lw	a1,20(s1)
80001144:	4c88                	lw	a0,24(s1)
80001146:	667000ef          	jal	80001fac <core_bench_state>
8000114a:	03e4d783          	lhu	a5,62(s1)
8000114e:	01051913          	slli	s2,a0,0x10
80001152:	41095913          	srai	s2,s2,0x10
80001156:	e399                	bnez	a5,8000115c <calc_func+0xce>
80001158:	02a49f23          	sh	a0,62(s1)
8000115c:	0384d783          	lhu	a5,56(s1)
80001160:	bf61                	j	800010f8 <calc_func+0x6a>

80001162 <cmp_complex>:
80001162:	1141                	addi	sp,sp,-16
80001164:	c226                	sw	s1,4(sp)
80001166:	84ae                	mv	s1,a1
80001168:	85b2                	mv	a1,a2
8000116a:	c606                	sw	ra,12(sp)
8000116c:	c422                	sw	s0,8(sp)
8000116e:	8432                	mv	s0,a2
80001170:	3f39                	jal	8000108e <calc_func>
80001172:	87aa                	mv	a5,a0
80001174:	85a2                	mv	a1,s0
80001176:	8526                	mv	a0,s1
80001178:	843e                	mv	s0,a5
8000117a:	3f11                	jal	8000108e <calc_func>
8000117c:	40b2                	lw	ra,12(sp)
8000117e:	40a40533          	sub	a0,s0,a0
80001182:	4422                	lw	s0,8(sp)
80001184:	4492                	lw	s1,4(sp)
80001186:	0141                	addi	sp,sp,16
80001188:	8082                	ret

8000118a <copy_info>:
8000118a:	00059703          	lh	a4,0(a1)
8000118e:	00259783          	lh	a5,2(a1)
80001192:	00e51023          	sh	a4,0(a0)
80001196:	00f51123          	sh	a5,2(a0)
8000119a:	8082                	ret

8000119c <core_list_insert_new>:
8000119c:	00062803          	lw	a6,0(a2)
800011a0:	00880893          	addi	a7,a6,8
800011a4:	02e8ff63          	bgeu	a7,a4,800011e2 <core_list_insert_new+0x46>
800011a8:	4298                	lw	a4,0(a3)
800011aa:	00470313          	addi	t1,a4,4
800011ae:	02f37a63          	bgeu	t1,a5,800011e2 <core_list_insert_new+0x46>
800011b2:	01162023          	sw	a7,0(a2)
800011b6:	411c                	lw	a5,0(a0)
800011b8:	00059883          	lh	a7,0(a1)
800011bc:	00259603          	lh	a2,2(a1)
800011c0:	00f82023          	sw	a5,0(a6)
800011c4:	01052023          	sw	a6,0(a0)
800011c8:	00e82223          	sw	a4,4(a6)
800011cc:	429c                	lw	a5,0(a3)
800011ce:	8542                	mv	a0,a6
800011d0:	0791                	addi	a5,a5,4
800011d2:	c29c                	sw	a5,0(a3)
800011d4:	00482783          	lw	a5,4(a6)
800011d8:	01179023          	sh	a7,0(a5)
800011dc:	00c79123          	sh	a2,2(a5)
800011e0:	8082                	ret
800011e2:	4801                	li	a6,0
800011e4:	8542                	mv	a0,a6
800011e6:	8082                	ret

800011e8 <core_list_remove>:
800011e8:	87aa                	mv	a5,a0
800011ea:	4108                	lw	a0,0(a0)
800011ec:	43d4                	lw	a3,4(a5)
800011ee:	4150                	lw	a2,4(a0)
800011f0:	4118                	lw	a4,0(a0)
800011f2:	c3d0                	sw	a2,4(a5)
800011f4:	c154                	sw	a3,4(a0)
800011f6:	c398                	sw	a4,0(a5)
800011f8:	00052023          	sw	zero,0(a0)
800011fc:	8082                	ret

800011fe <core_list_undo_remove>:
800011fe:	41d0                	lw	a2,4(a1)
80001200:	4154                	lw	a3,4(a0)
80001202:	4198                	lw	a4,0(a1)
80001204:	c150                	sw	a2,4(a0)
80001206:	c1d4                	sw	a3,4(a1)
80001208:	c118                	sw	a4,0(a0)
8000120a:	c188                	sw	a0,0(a1)
8000120c:	8082                	ret

8000120e <core_list_find>:
8000120e:	00259703          	lh	a4,2(a1)
80001212:	00074c63          	bltz	a4,8000122a <core_list_find+0x1c>
80001216:	e501                	bnez	a0,8000121e <core_list_find+0x10>
80001218:	8082                	ret
8000121a:	4108                	lw	a0,0(a0)
8000121c:	c11d                	beqz	a0,80001242 <core_list_find+0x34>
8000121e:	415c                	lw	a5,4(a0)
80001220:	00279783          	lh	a5,2(a5)
80001224:	fee79be3          	bne	a5,a4,8000121a <core_list_find+0xc>
80001228:	8082                	ret
8000122a:	cd01                	beqz	a0,80001242 <core_list_find+0x34>
8000122c:	00059703          	lh	a4,0(a1)
80001230:	a019                	j	80001236 <core_list_find+0x28>
80001232:	4108                	lw	a0,0(a0)
80001234:	c901                	beqz	a0,80001244 <core_list_find+0x36>
80001236:	415c                	lw	a5,4(a0)
80001238:	0007c783          	lbu	a5,0(a5)
8000123c:	fee79be3          	bne	a5,a4,80001232 <core_list_find+0x24>
80001240:	8082                	ret
80001242:	4501                	li	a0,0
80001244:	8082                	ret

80001246 <core_list_reverse>:
80001246:	c901                	beqz	a0,80001256 <core_list_reverse+0x10>
80001248:	4701                	li	a4,0
8000124a:	a011                	j	8000124e <core_list_reverse+0x8>
8000124c:	853e                	mv	a0,a5
8000124e:	411c                	lw	a5,0(a0)
80001250:	c118                	sw	a4,0(a0)
80001252:	872a                	mv	a4,a0
80001254:	ffe5                	bnez	a5,8000124c <core_list_reverse+0x6>
80001256:	8082                	ret

80001258 <core_list_mergesort>:
80001258:	7179                	addi	sp,sp,-48
8000125a:	ce4e                	sw	s3,28(sp)
8000125c:	ca56                	sw	s5,20(sp)
8000125e:	c65e                	sw	s7,12(sp)
80001260:	c462                	sw	s8,8(sp)
80001262:	c06a                	sw	s10,0(sp)
80001264:	4a85                	li	s5,1
80001266:	d606                	sw	ra,44(sp)
80001268:	d422                	sw	s0,40(sp)
8000126a:	d226                	sw	s1,36(sp)
8000126c:	d04a                	sw	s2,32(sp)
8000126e:	cc52                	sw	s4,24(sp)
80001270:	c85a                	sw	s6,16(sp)
80001272:	c266                	sw	s9,4(sp)
80001274:	89aa                	mv	s3,a0
80001276:	8c2e                	mv	s8,a1
80001278:	8bb2                	mv	s7,a2
8000127a:	8d56                	mv	s10,s5
8000127c:	08098f63          	beqz	s3,8000131a <core_list_mergesort+0xc2>
80001280:	4c81                	li	s9,0
80001282:	4901                	li	s2,0
80001284:	4b01                	li	s6,0
80001286:	0c85                	addi	s9,s9,1
80001288:	87ce                	mv	a5,s3
8000128a:	4401                	li	s0,0
8000128c:	01545563          	bge	s0,s5,80001296 <core_list_mergesort+0x3e>
80001290:	439c                	lw	a5,0(a5)
80001292:	0405                	addi	s0,s0,1
80001294:	ffe5                	bnez	a5,8000128c <core_list_mergesort+0x34>
80001296:	84ca                	mv	s1,s2
80001298:	8a56                	mv	s4,s5
8000129a:	894e                	mv	s2,s3
8000129c:	89be                	mv	s3,a5
8000129e:	00805f63          	blez	s0,800012bc <core_list_mergesort+0x64>
800012a2:	040a0263          	beqz	s4,800012e6 <core_list_mergesort+0x8e>
800012a6:	02099063          	bnez	s3,800012c6 <core_list_mergesort+0x6e>
800012aa:	87ca                	mv	a5,s2
800012ac:	147d                	addi	s0,s0,-1
800012ae:	00092903          	lw	s2,0(s2)
800012b2:	c49d                	beqz	s1,800012e0 <core_list_mergesort+0x88>
800012b4:	c09c                	sw	a5,0(s1)
800012b6:	84be                	mv	s1,a5
800012b8:	fe8045e3          	bgtz	s0,800012a2 <core_list_mergesort+0x4a>
800012bc:	0b405463          	blez	s4,80001364 <core_list_mergesort+0x10c>
800012c0:	04098563          	beqz	s3,8000130a <core_list_mergesort+0xb2>
800012c4:	c425                	beqz	s0,8000132c <core_list_mergesort+0xd4>
800012c6:	0049a583          	lw	a1,4(s3)
800012ca:	00492503          	lw	a0,4(s2)
800012ce:	865e                	mv	a2,s7
800012d0:	9c02                	jalr	s8
800012d2:	fca05ce3          	blez	a0,800012aa <core_list_mergesort+0x52>
800012d6:	87ce                	mv	a5,s3
800012d8:	1a7d                	addi	s4,s4,-1
800012da:	0009a983          	lw	s3,0(s3)
800012de:	f8f9                	bnez	s1,800012b4 <core_list_mergesort+0x5c>
800012e0:	8b3e                	mv	s6,a5
800012e2:	84be                	mv	s1,a5
800012e4:	bfd1                	j	800012b8 <core_list_mergesort+0x60>
800012e6:	00092783          	lw	a5,0(s2)
800012ea:	147d                	addi	s0,s0,-1
800012ec:	c891                	beqz	s1,80001300 <core_list_mergesort+0xa8>
800012ee:	0124a023          	sw	s2,0(s1)
800012f2:	c809                	beqz	s0,80001304 <core_list_mergesort+0xac>
800012f4:	84ca                	mv	s1,s2
800012f6:	893e                	mv	s2,a5
800012f8:	00092783          	lw	a5,0(s2)
800012fc:	147d                	addi	s0,s0,-1
800012fe:	f8e5                	bnez	s1,800012ee <core_list_mergesort+0x96>
80001300:	8b4a                	mv	s6,s2
80001302:	f86d                	bnez	s0,800012f4 <core_list_mergesort+0x9c>
80001304:	f80991e3          	bnez	s3,80001286 <core_list_mergesort+0x2e>
80001308:	84ca                	mv	s1,s2
8000130a:	0004a023          	sw	zero,0(s1)
8000130e:	03ac8c63          	beq	s9,s10,80001346 <core_list_mergesort+0xee>
80001312:	89da                	mv	s3,s6
80001314:	0a86                	slli	s5,s5,0x1
80001316:	f60995e3          	bnez	s3,80001280 <core_list_mergesort+0x28>
8000131a:	00002023          	sw	zero,0(zero) # 0 <_tdata_begin>
8000131e:	9002                	ebreak
80001320:	8b4e                	mv	s6,s3
80001322:	000a0d63          	beqz	s4,8000133c <core_list_mergesort+0xe4>
80001326:	84ce                	mv	s1,s3
80001328:	d3ed                	beqz	a5,8000130a <core_list_mergesort+0xb2>
8000132a:	89be                	mv	s3,a5
8000132c:	0009a783          	lw	a5,0(s3)
80001330:	1a7d                	addi	s4,s4,-1
80001332:	d4fd                	beqz	s1,80001320 <core_list_mergesort+0xc8>
80001334:	0134a023          	sw	s3,0(s1)
80001338:	fe0a17e3          	bnez	s4,80001326 <core_list_mergesort+0xce>
8000133c:	894e                	mv	s2,s3
8000133e:	89be                	mv	s3,a5
80001340:	f40993e3          	bnez	s3,80001286 <core_list_mergesort+0x2e>
80001344:	b7d1                	j	80001308 <core_list_mergesort+0xb0>
80001346:	50b2                	lw	ra,44(sp)
80001348:	5422                	lw	s0,40(sp)
8000134a:	5492                	lw	s1,36(sp)
8000134c:	5902                	lw	s2,32(sp)
8000134e:	49f2                	lw	s3,28(sp)
80001350:	4a62                	lw	s4,24(sp)
80001352:	4ad2                	lw	s5,20(sp)
80001354:	4bb2                	lw	s7,12(sp)
80001356:	4c22                	lw	s8,8(sp)
80001358:	4c92                	lw	s9,4(sp)
8000135a:	4d02                	lw	s10,0(sp)
8000135c:	855a                	mv	a0,s6
8000135e:	4b42                	lw	s6,16(sp)
80001360:	6145                	addi	sp,sp,48
80001362:	8082                	ret
80001364:	8926                	mv	s2,s1
80001366:	f20990e3          	bnez	s3,80001286 <core_list_mergesort+0x2e>
8000136a:	bf79                	j	80001308 <core_list_mergesort+0xb0>

8000136c <core_bench_list>:
8000136c:	862a                	mv	a2,a0
8000136e:	00451503          	lh	a0,4(a0)
80001372:	1101                	addi	sp,sp,-32
80001374:	cc22                	sw	s0,24(sp)
80001376:	c64e                	sw	s3,12(sp)
80001378:	ce06                	sw	ra,28(sp)
8000137a:	ca26                	sw	s1,20(sp)
8000137c:	c84a                	sw	s2,16(sp)
8000137e:	c452                	sw	s4,8(sp)
80001380:	c256                	sw	s5,4(sp)
80001382:	5240                	lw	s0,36(a2)
80001384:	4981                	li	s3,0
80001386:	1ea05d63          	blez	a0,80001580 <core_bench_list+0x214>
8000138a:	1e05ce63          	bltz	a1,80001586 <core_bench_list+0x21a>
8000138e:	20040563          	beqz	s0,80001598 <core_bench_list+0x22c>
80001392:	892e                	mv	s2,a1
80001394:	4301                	li	t1,0
80001396:	4e81                	li	t4,0
80001398:	4e01                	li	t3,0
8000139a:	4881                	li	a7,0
8000139c:	87a2                	mv	a5,s0
8000139e:	a019                	j	800013a4 <core_bench_list+0x38>
800013a0:	439c                	lw	a5,0(a5)
800013a2:	cfc5                	beqz	a5,8000145a <core_bench_list+0xee>
800013a4:	43d8                	lw	a4,4(a5)
800013a6:	00271803          	lh	a6,2(a4)
800013aa:	ff281be3          	bne	a6,s2,800013a0 <core_bench_list+0x34>
800013ae:	4681                	li	a3,0
800013b0:	a011                	j	800013b4 <core_bench_list+0x48>
800013b2:	843a                	mv	s0,a4
800013b4:	4018                	lw	a4,0(s0)
800013b6:	c014                	sw	a3,0(s0)
800013b8:	86a2                	mv	a3,s0
800013ba:	ff65                	bnez	a4,800013b2 <core_bench_list+0x46>
800013bc:	c3cd                	beqz	a5,8000145e <core_bench_list+0xf2>
800013be:	43d8                	lw	a4,4(a5)
800013c0:	00071703          	lh	a4,0(a4)
800013c4:	00177693          	andi	a3,a4,1
800013c8:	ca81                	beqz	a3,800013d8 <core_bench_list+0x6c>
800013ca:	8725                	srai	a4,a4,0x9
800013cc:	8b05                	andi	a4,a4,1
800013ce:	9746                	add	a4,a4,a7
800013d0:	01071893          	slli	a7,a4,0x10
800013d4:	0108d893          	srli	a7,a7,0x10
800013d8:	4398                	lw	a4,0(a5)
800013da:	c711                	beqz	a4,800013e6 <core_bench_list+0x7a>
800013dc:	4314                	lw	a3,0(a4)
800013de:	c394                	sw	a3,0(a5)
800013e0:	401c                	lw	a5,0(s0)
800013e2:	c31c                	sw	a5,0(a4)
800013e4:	c018                	sw	a4,0(s0)
800013e6:	0e05                	addi	t3,t3,1
800013e8:	0e42                	slli	t3,t3,0x10
800013ea:	010e5e13          	srli	t3,t3,0x10
800013ee:	04084863          	bltz	a6,8000143e <core_bench_list+0xd2>
800013f2:	00130793          	addi	a5,t1,1
800013f6:	01079313          	slli	t1,a5,0x10
800013fa:	00180913          	addi	s2,a6,1
800013fe:	0942                	slli	s2,s2,0x10
80001400:	07c2                	slli	a5,a5,0x10
80001402:	41035313          	srai	t1,t1,0x10
80001406:	41095913          	srai	s2,s2,0x10
8000140a:	83c1                	srli	a5,a5,0x10
8000140c:	06650963          	beq	a0,t1,8000147e <core_bench_list+0x112>
80001410:	0ff7f993          	zext.b	s3,a5
80001414:	86ce                	mv	a3,s3
80001416:	87a2                	mv	a5,s0
80001418:	7861                	lui	a6,0xffff8
8000141a:	f80951e3          	bgez	s2,8000139c <core_bench_list+0x30>
8000141e:	43d8                	lw	a4,4(a5)
80001420:	00074983          	lbu	s3,0(a4)
80001424:	f8d985e3          	beq	s3,a3,800013ae <core_bench_list+0x42>
80001428:	439c                	lw	a5,0(a5)
8000142a:	cb81                	beqz	a5,8000143a <core_bench_list+0xce>
8000142c:	43d8                	lw	a4,4(a5)
8000142e:	00074983          	lbu	s3,0(a4)
80001432:	f6d98ee3          	beq	s3,a3,800013ae <core_bench_list+0x42>
80001436:	439c                	lw	a5,0(a5)
80001438:	fbf5                	bnez	a5,8000142c <core_bench_list+0xc0>
8000143a:	89b6                	mv	s3,a3
8000143c:	bf8d                	j	800013ae <core_bench_list+0x42>
8000143e:	00130693          	addi	a3,t1,1
80001442:	01069313          	slli	t1,a3,0x10
80001446:	41035313          	srai	t1,t1,0x10
8000144a:	06c2                	slli	a3,a3,0x10
8000144c:	82c1                	srli	a3,a3,0x10
8000144e:	02650763          	beq	a0,t1,8000147c <core_bench_list+0x110>
80001452:	0ff6f693          	zext.b	a3,a3
80001456:	87a2                	mv	a5,s0
80001458:	bfd1                	j	8000142c <core_bench_list+0xc0>
8000145a:	884a                	mv	a6,s2
8000145c:	bf89                	j	800013ae <core_bench_list+0x42>
8000145e:	401c                	lw	a5,0(s0)
80001460:	0e85                	addi	t4,t4,1
80001462:	0ec2                	slli	t4,t4,0x10
80001464:	43dc                	lw	a5,4(a5)
80001466:	010ede93          	srli	t4,t4,0x10
8000146a:	00178783          	lb	a5,1(a5)
8000146e:	8b85                	andi	a5,a5,1
80001470:	97c6                	add	a5,a5,a7
80001472:	01079893          	slli	a7,a5,0x10
80001476:	0108d893          	srli	a7,a7,0x10
8000147a:	bf95                	j	800013ee <core_bench_list+0x82>
8000147c:	8942                	mv	s2,a6
8000147e:	002e1793          	slli	a5,t3,0x2
80001482:	41d787b3          	sub	a5,a5,t4
80001486:	98be                	add	a7,a7,a5
80001488:	01089493          	slli	s1,a7,0x10
8000148c:	80c1                	srli	s1,s1,0x10
8000148e:	00b05963          	blez	a1,800014a0 <core_bench_list+0x134>
80001492:	8522                	mv	a0,s0
80001494:	00000597          	auipc	a1,0x0
80001498:	cce58593          	addi	a1,a1,-818 # 80001162 <cmp_complex>
8000149c:	3b75                	jal	80001258 <core_list_mergesort>
8000149e:	842a                	mv	s0,a0
800014a0:	401c                	lw	a5,0(s0)
800014a2:	8a22                	mv	s4,s0
800014a4:	0007aa83          	lw	s5,0(a5)
800014a8:	43d8                	lw	a4,4(a5)
800014aa:	004aa603          	lw	a2,4(s5)
800014ae:	000aa683          	lw	a3,0(s5)
800014b2:	c3d0                	sw	a2,4(a5)
800014b4:	00eaa223          	sw	a4,4(s5)
800014b8:	c394                	sw	a3,0(a5)
800014ba:	000aa023          	sw	zero,0(s5)
800014be:	00095763          	bgez	s2,800014cc <core_bench_list+0x160>
800014c2:	a841                	j	80001552 <core_bench_list+0x1e6>
800014c4:	000a2a03          	lw	s4,0(s4)
800014c8:	080a0c63          	beqz	s4,80001560 <core_bench_list+0x1f4>
800014cc:	004a2783          	lw	a5,4(s4)
800014d0:	00279783          	lh	a5,2(a5)
800014d4:	ff2798e3          	bne	a5,s2,800014c4 <core_bench_list+0x158>
800014d8:	405c                	lw	a5,4(s0)
800014da:	85a6                	mv	a1,s1
800014dc:	00079503          	lh	a0,0(a5)
800014e0:	55d000ef          	jal	8000223c <crc16>
800014e4:	000a2a03          	lw	s4,0(s4)
800014e8:	84aa                	mv	s1,a0
800014ea:	fe0a17e3          	bnez	s4,800014d8 <core_bench_list+0x16c>
800014ee:	00042a03          	lw	s4,0(s0)
800014f2:	004aa703          	lw	a4,4(s5)
800014f6:	004a2683          	lw	a3,4(s4)
800014fa:	000a2783          	lw	a5,0(s4)
800014fe:	8522                	mv	a0,s0
80001500:	00daa223          	sw	a3,4(s5)
80001504:	00ea2223          	sw	a4,4(s4)
80001508:	00faa023          	sw	a5,0(s5)
8000150c:	015a2023          	sw	s5,0(s4)
80001510:	4601                	li	a2,0
80001512:	00000597          	auipc	a1,0x0
80001516:	b3658593          	addi	a1,a1,-1226 # 80001048 <cmp_idx>
8000151a:	3b3d                	jal	80001258 <core_list_mergesort>
8000151c:	4100                	lw	s0,0(a0)
8000151e:	892a                	mv	s2,a0
80001520:	c819                	beqz	s0,80001536 <core_bench_list+0x1ca>
80001522:	00492783          	lw	a5,4(s2)
80001526:	85a6                	mv	a1,s1
80001528:	00079503          	lh	a0,0(a5)
8000152c:	511000ef          	jal	8000223c <crc16>
80001530:	4000                	lw	s0,0(s0)
80001532:	84aa                	mv	s1,a0
80001534:	f47d                	bnez	s0,80001522 <core_bench_list+0x1b6>
80001536:	40f2                	lw	ra,28(sp)
80001538:	4462                	lw	s0,24(sp)
8000153a:	4942                	lw	s2,16(sp)
8000153c:	49b2                	lw	s3,12(sp)
8000153e:	4a22                	lw	s4,8(sp)
80001540:	4a92                	lw	s5,4(sp)
80001542:	8526                	mv	a0,s1
80001544:	44d2                	lw	s1,20(sp)
80001546:	6105                	addi	sp,sp,32
80001548:	8082                	ret
8000154a:	000a2a03          	lw	s4,0(s4)
8000154e:	000a0963          	beqz	s4,80001560 <core_bench_list+0x1f4>
80001552:	004a2783          	lw	a5,4(s4)
80001556:	0007c783          	lbu	a5,0(a5)
8000155a:	fef998e3          	bne	s3,a5,8000154a <core_bench_list+0x1de>
8000155e:	bfad                	j	800014d8 <core_bench_list+0x16c>
80001560:	00042a03          	lw	s4,0(s0)
80001564:	f80a09e3          	beqz	s4,800014f6 <core_bench_list+0x18a>
80001568:	405c                	lw	a5,4(s0)
8000156a:	85a6                	mv	a1,s1
8000156c:	00079503          	lh	a0,0(a5)
80001570:	4cd000ef          	jal	8000223c <crc16>
80001574:	000a2a03          	lw	s4,0(s4)
80001578:	84aa                	mv	s1,a0
8000157a:	f40a1fe3          	bnez	s4,800014d8 <core_bench_list+0x16c>
8000157e:	bf85                	j	800014ee <core_bench_list+0x182>
80001580:	892e                	mv	s2,a1
80001582:	4481                	li	s1,0
80001584:	b729                	j	8000148e <core_bench_list+0x122>
80001586:	c809                	beqz	s0,80001598 <core_bench_list+0x22c>
80001588:	882e                	mv	a6,a1
8000158a:	87a2                	mv	a5,s0
8000158c:	4881                	li	a7,0
8000158e:	4301                	li	t1,0
80001590:	4681                	li	a3,0
80001592:	4e81                	li	t4,0
80001594:	4e01                	li	t3,0
80001596:	bd59                	j	8000142c <core_bench_list+0xc0>
80001598:	4781                	li	a5,0
8000159a:	439c                	lw	a5,0(a5)
8000159c:	9002                	ebreak

8000159e <core_list_init>:
8000159e:	ccccd7b7          	lui	a5,0xccccd
800015a2:	ccd78793          	addi	a5,a5,-819 # cccccccd <_end+0x4ccc83cd>
800015a6:	02f53333          	mulhu	t1,a0,a5
800015aa:	77e1                	lui	a5,0xffff8
800015ac:	0005a023          	sw	zero,0(a1)
800015b0:	08078793          	addi	a5,a5,128 # ffff8080 <_end+0x7fff3780>
800015b4:	01058693          	addi	a3,a1,16
800015b8:	852e                	mv	a0,a1
800015ba:	00858e13          	addi	t3,a1,8
800015be:	00435313          	srli	t1,t1,0x4
800015c2:	1379                	addi	t1,t1,-2
800015c4:	00331e93          	slli	t4,t1,0x3
800015c8:	9eae                	add	t4,t4,a1
800015ca:	01d5a223          	sw	t4,4(a1)
800015ce:	00fe9023          	sh	a5,0(t4)
800015d2:	00231f93          	slli	t6,t1,0x2
800015d6:	000e9123          	sh	zero,2(t4)
800015da:	9ff6                	add	t6,t6,t4
800015dc:	004e8713          	addi	a4,t4,4
800015e0:	77e1                	lui	a5,0xffff8
800015e2:	0fd6f563          	bgeu	a3,t4,800016cc <core_list_init+0x12e>
800015e6:	008e8893          	addi	a7,t4,8
800015ea:	0ff8f163          	bgeu	a7,t6,800016cc <core_list_init+0x12e>
800015ee:	c5d8                	sw	a4,12(a1)
800015f0:	0005a423          	sw	zero,8(a1)
800015f4:	01c5a023          	sw	t3,0(a1)
800015f8:	fff7c793          	not	a5,a5
800015fc:	577d                	li	a4,-1
800015fe:	00fe9323          	sh	a5,6(t4)
80001602:	00ee9223          	sh	a4,4(t4)
80001606:	04030e63          	beqz	t1,80001662 <core_list_init+0xc4>
8000160a:	01061293          	slli	t0,a2,0x10
8000160e:	73e1                	lui	t2,0xffff8
80001610:	0102d293          	srli	t0,t0,0x10
80001614:	fff3c393          	not	t2,t2
80001618:	4801                	li	a6,0
8000161a:	01081713          	slli	a4,a6,0x10
8000161e:	8341                	srli	a4,a4,0x10
80001620:	005747b3          	xor	a5,a4,t0
80001624:	078e                	slli	a5,a5,0x3
80001626:	8b1d                	andi	a4,a4,7
80001628:	0787f793          	andi	a5,a5,120
8000162c:	8fd9                	or	a5,a5,a4
8000162e:	00879f13          	slli	t5,a5,0x8
80001632:	00868593          	addi	a1,a3,8
80001636:	0805                	addi	a6,a6,1 # ffff8001 <_end+0x7fff3701>
80001638:	00488713          	addi	a4,a7,4
8000163c:	97fa                	add	a5,a5,t5
8000163e:	03d5f063          	bgeu	a1,t4,8000165e <core_list_init+0xc0>
80001642:	01f77e63          	bgeu	a4,t6,8000165e <core_list_init+0xc0>
80001646:	01c6a023          	sw	t3,0(a3)
8000164a:	c114                	sw	a3,0(a0)
8000164c:	0116a223          	sw	a7,4(a3)
80001650:	00f89023          	sh	a5,0(a7)
80001654:	00789123          	sh	t2,2(a7)
80001658:	8e36                	mv	t3,a3
8000165a:	88ba                	mv	a7,a4
8000165c:	86ae                	mv	a3,a1
8000165e:	fb031ee3          	bne	t1,a6,8000161a <core_list_init+0x7c>
80001662:	000e2803          	lw	a6,0(t3)
80001666:	04080d63          	beqz	a6,800016c0 <core_list_init+0x122>
8000166a:	ccccd7b7          	lui	a5,0xccccd
8000166e:	ccd78793          	addi	a5,a5,-819 # cccccccd <_end+0x4ccc83cd>
80001672:	02f33333          	mulhu	t1,t1,a5
80001676:	6e91                	lui	t4,0x4
80001678:	1efd                	addi	t4,t4,-1 # 3fff <_tbss_end+0x3fbb>
8000167a:	20000713          	li	a4,512
8000167e:	4685                	li	a3,1
80001680:	00235313          	srli	t1,t1,0x2
80001684:	a011                	j	80001688 <core_list_init+0xea>
80001686:	8846                	mv	a6,a7
80001688:	00d645b3          	xor	a1,a2,a3
8000168c:	70077793          	andi	a5,a4,1792
80001690:	8fcd                	or	a5,a5,a1
80001692:	01d7f7b3          	and	a5,a5,t4
80001696:	07c2                	slli	a5,a5,0x10
80001698:	004e2583          	lw	a1,4(t3)
8000169c:	87c1                	srai	a5,a5,0x10
8000169e:	0066f563          	bgeu	a3,t1,800016a8 <core_list_init+0x10a>
800016a2:	01069793          	slli	a5,a3,0x10
800016a6:	87c1                	srai	a5,a5,0x10
800016a8:	00082883          	lw	a7,0(a6)
800016ac:	10070713          	addi	a4,a4,256
800016b0:	0742                	slli	a4,a4,0x10
800016b2:	00f59123          	sh	a5,2(a1)
800016b6:	8341                	srli	a4,a4,0x10
800016b8:	0685                	addi	a3,a3,1
800016ba:	8e42                	mv	t3,a6
800016bc:	fc0895e3          	bnez	a7,80001686 <core_list_init+0xe8>
800016c0:	4601                	li	a2,0
800016c2:	00000597          	auipc	a1,0x0
800016c6:	98658593          	addi	a1,a1,-1658 # 80001048 <cmp_idx>
800016ca:	b679                	j	80001258 <core_list_mergesort>
800016cc:	86f2                	mv	a3,t3
800016ce:	88ba                	mv	a7,a4
800016d0:	4e01                	li	t3,0
800016d2:	bf15                	j	80001606 <core_list_init+0x68>

800016d4 <iterate>:
800016d4:	1141                	addi	sp,sp,-16
800016d6:	c04a                	sw	s2,0(sp)
800016d8:	01c52903          	lw	s2,28(a0)
800016dc:	c606                	sw	ra,12(sp)
800016de:	02052c23          	sw	zero,56(a0)
800016e2:	02052e23          	sw	zero,60(a0)
800016e6:	04090063          	beqz	s2,80001726 <iterate+0x52>
800016ea:	c422                	sw	s0,8(sp)
800016ec:	c226                	sw	s1,4(sp)
800016ee:	842a                	mv	s0,a0
800016f0:	4481                	li	s1,0
800016f2:	4585                	li	a1,1
800016f4:	8522                	mv	a0,s0
800016f6:	399d                	jal	8000136c <core_bench_list>
800016f8:	03845583          	lhu	a1,56(s0)
800016fc:	239000ef          	jal	80002134 <crcu16>
80001700:	02a41c23          	sh	a0,56(s0)
80001704:	55fd                	li	a1,-1
80001706:	8522                	mv	a0,s0
80001708:	3195                	jal	8000136c <core_bench_list>
8000170a:	03845583          	lhu	a1,56(s0)
8000170e:	227000ef          	jal	80002134 <crcu16>
80001712:	02a41c23          	sh	a0,56(s0)
80001716:	e099                	bnez	s1,8000171c <iterate+0x48>
80001718:	02a41d23          	sh	a0,58(s0)
8000171c:	0485                	addi	s1,s1,1
8000171e:	fc991ae3          	bne	s2,s1,800016f2 <iterate+0x1e>
80001722:	4422                	lw	s0,8(sp)
80001724:	4492                	lw	s1,4(sp)
80001726:	40b2                	lw	ra,12(sp)
80001728:	4902                	lw	s2,0(sp)
8000172a:	4501                	li	a0,0
8000172c:	0141                	addi	sp,sp,16
8000172e:	8082                	ret

80001730 <core_init_matrix>:
80001730:	1141                	addi	sp,sp,-16
80001732:	c622                	sw	s0,12(sp)
80001734:	c426                	sw	s1,8(sp)
80001736:	882a                	mv	a6,a0
80001738:	e211                	bnez	a2,8000173c <core_init_matrix+0xc>
8000173a:	4605                	li	a2,1
8000173c:	15fd                	addi	a1,a1,-1
8000173e:	ffc5f293          	andi	t0,a1,-4
80001742:	00428413          	addi	s0,t0,4
80001746:	4781                	li	a5,0
80001748:	08080f63          	beqz	a6,800017e6 <core_init_matrix+0xb6>
8000174c:	853e                	mv	a0,a5
8000174e:	0785                	addi	a5,a5,1
80001750:	02f78733          	mul	a4,a5,a5
80001754:	070e                	slli	a4,a4,0x3
80001756:	ff076be3          	bltu	a4,a6,8000174c <core_init_matrix+0x1c>
8000175a:	02a503b3          	mul	t2,a0,a0
8000175e:	0386                	slli	t2,t2,0x1
80001760:	007402b3          	add	t0,s0,t2
80001764:	c559                	beqz	a0,800017f2 <core_init_matrix+0xc2>
80001766:	c24a                	sw	s2,4(sp)
80001768:	84aa                	mv	s1,a0
8000176a:	00150313          	addi	t1,a0,1
8000176e:	00151913          	slli	s2,a0,0x1
80001772:	8f16                	mv	t5,t0
80001774:	4e81                	li	t4,0
80001776:	4705                	li	a4,1
80001778:	40540e33          	sub	t3,s0,t0
8000177c:	8fba                	mv	t6,a4
8000177e:	887a                	mv	a6,t5
80001780:	02e60633          	mul	a2,a2,a4
80001784:	01071793          	slli	a5,a4,0x10
80001788:	83c1                	srli	a5,a5,0x10
8000178a:	010e08b3          	add	a7,t3,a6
8000178e:	0705                	addi	a4,a4,1
80001790:	0809                	addi	a6,a6,2
80001792:	41f65593          	srai	a1,a2,0x1f
80001796:	81c1                	srli	a1,a1,0x10
80001798:	962e                	add	a2,a2,a1
8000179a:	0642                	slli	a2,a2,0x10
8000179c:	8241                	srli	a2,a2,0x10
8000179e:	8e0d                	sub	a2,a2,a1
800017a0:	00c785b3          	add	a1,a5,a2
800017a4:	05c2                	slli	a1,a1,0x10
800017a6:	81c1                	srli	a1,a1,0x10
800017a8:	97ae                	add	a5,a5,a1
800017aa:	feb81f23          	sh	a1,-2(a6)
800017ae:	0ff7f793          	zext.b	a5,a5
800017b2:	00f89023          	sh	a5,0(a7)
800017b6:	fc6715e3          	bne	a4,t1,80001780 <core_init_matrix+0x50>
800017ba:	0e85                	addi	t4,t4,1
800017bc:	01f50733          	add	a4,a0,t6
800017c0:	932a                	add	t1,t1,a0
800017c2:	9f4a                	add	t5,t5,s2
800017c4:	faae9ce3          	bne	t4,a0,8000177c <core_init_matrix+0x4c>
800017c8:	4912                	lw	s2,4(sp)
800017ca:	007287b3          	add	a5,t0,t2
800017ce:	17fd                	addi	a5,a5,-1
800017d0:	c2c0                	sw	s0,4(a3)
800017d2:	9bf1                	andi	a5,a5,-4
800017d4:	4432                	lw	s0,12(sp)
800017d6:	0791                	addi	a5,a5,4
800017d8:	c284                	sw	s1,0(a3)
800017da:	c6dc                	sw	a5,12(a3)
800017dc:	0056a423          	sw	t0,8(a3)
800017e0:	44a2                	lw	s1,8(sp)
800017e2:	0141                	addi	sp,sp,16
800017e4:	8082                	ret
800017e6:	54fd                	li	s1,-1
800017e8:	c24a                	sw	s2,4(sp)
800017ea:	0299                	addi	t0,t0,6
800017ec:	8526                	mv	a0,s1
800017ee:	4389                	li	t2,2
800017f0:	bfad                	j	8000176a <core_init_matrix+0x3a>
800017f2:	4381                	li	t2,0
800017f4:	4481                	li	s1,0
800017f6:	bfd1                	j	800017ca <core_init_matrix+0x9a>

800017f8 <matrix_sum>:
800017f8:	8eaa                	mv	t4,a0
800017fa:	cd39                	beqz	a0,80001858 <matrix_sum+0x60>
800017fc:	00251f93          	slli	t6,a0,0x2
80001800:	40a00f33          	neg	t5,a0
80001804:	01f588b3          	add	a7,a1,t6
80001808:	0f0e                	slli	t5,t5,0x3
8000180a:	4301                	li	t1,0
8000180c:	4501                	li	a0,0
8000180e:	4681                	li	a3,0
80001810:	4801                	li	a6,0
80001812:	41f88e33          	sub	t3,a7,t6
80001816:	8772                	mv	a4,t3
80001818:	a039                	j	80001826 <matrix_sum+0x2e>
8000181a:	01079513          	slli	a0,a5,0x10
8000181e:	0711                	addi	a4,a4,4
80001820:	8541                	srai	a0,a0,0x10
80001822:	02e88563          	beq	a7,a4,8000184c <matrix_sum+0x54>
80001826:	85b6                	mv	a1,a3
80001828:	01051793          	slli	a5,a0,0x10
8000182c:	4314                	lw	a3,0(a4)
8000182e:	83c1                	srli	a5,a5,0x10
80001830:	00a78513          	addi	a0,a5,10
80001834:	00d5a5b3          	slt	a1,a1,a3
80001838:	0542                	slli	a0,a0,0x10
8000183a:	9836                	add	a6,a6,a3
8000183c:	8541                	srai	a0,a0,0x10
8000183e:	97ae                	add	a5,a5,a1
80001840:	fd065de3          	bge	a2,a6,8000181a <matrix_sum+0x22>
80001844:	0711                	addi	a4,a4,4
80001846:	4801                	li	a6,0
80001848:	fce89fe3          	bne	a7,a4,80001826 <matrix_sum+0x2e>
8000184c:	0305                	addi	t1,t1,1
8000184e:	41ee08b3          	sub	a7,t3,t5
80001852:	fc6e90e3          	bne	t4,t1,80001812 <matrix_sum+0x1a>
80001856:	8082                	ret
80001858:	4501                	li	a0,0
8000185a:	8082                	ret

8000185c <matrix_mul_const>:
8000185c:	c121                	beqz	a0,8000189c <matrix_mul_const+0x40>
8000185e:	00151f13          	slli	t5,a0,0x1
80001862:	40a00eb3          	neg	t4,a0
80001866:	01e60833          	add	a6,a2,t5
8000186a:	0e8a                	slli	t4,t4,0x2
8000186c:	4301                	li	t1,0
8000186e:	4881                	li	a7,0
80001870:	41e80e33          	sub	t3,a6,t5
80001874:	00231613          	slli	a2,t1,0x2
80001878:	87f2                	mv	a5,t3
8000187a:	962e                	add	a2,a2,a1
8000187c:	00079703          	lh	a4,0(a5)
80001880:	0789                	addi	a5,a5,2
80001882:	0611                	addi	a2,a2,4
80001884:	02d70733          	mul	a4,a4,a3
80001888:	fee62e23          	sw	a4,-4(a2)
8000188c:	ff0798e3          	bne	a5,a6,8000187c <matrix_mul_const+0x20>
80001890:	0885                	addi	a7,a7,1
80001892:	932a                	add	t1,t1,a0
80001894:	41de0833          	sub	a6,t3,t4
80001898:	fd151ce3          	bne	a0,a7,80001870 <matrix_mul_const+0x14>
8000189c:	8082                	ret

8000189e <matrix_add_const>:
8000189e:	c91d                	beqz	a0,800018d4 <matrix_add_const+0x36>
800018a0:	00151313          	slli	t1,a0,0x1
800018a4:	40a008b3          	neg	a7,a0
800018a8:	0642                	slli	a2,a2,0x10
800018aa:	006586b3          	add	a3,a1,t1
800018ae:	8241                	srli	a2,a2,0x10
800018b0:	088a                	slli	a7,a7,0x2
800018b2:	4581                	li	a1,0
800018b4:	40668833          	sub	a6,a3,t1
800018b8:	87c2                	mv	a5,a6
800018ba:	0007d703          	lhu	a4,0(a5)
800018be:	0789                	addi	a5,a5,2
800018c0:	9732                	add	a4,a4,a2
800018c2:	fee79f23          	sh	a4,-2(a5)
800018c6:	fef69ae3          	bne	a3,a5,800018ba <matrix_add_const+0x1c>
800018ca:	0585                	addi	a1,a1,1
800018cc:	411806b3          	sub	a3,a6,a7
800018d0:	feb512e3          	bne	a0,a1,800018b4 <matrix_add_const+0x16>
800018d4:	8082                	ret

800018d6 <matrix_mul_vect>:
800018d6:	cd15                	beqz	a0,80001912 <matrix_mul_vect+0x3c>
800018d8:	00251f13          	slli	t5,a0,0x2
800018dc:	00151e13          	slli	t3,a0,0x1
800018e0:	9f2e                	add	t5,t5,a1
800018e2:	9e36                	add	t3,t3,a3
800018e4:	4e81                	li	t4,0
800018e6:	001e9813          	slli	a6,t4,0x1
800018ea:	9832                	add	a6,a6,a2
800018ec:	87b6                	mv	a5,a3
800018ee:	4881                	li	a7,0
800018f0:	00081703          	lh	a4,0(a6)
800018f4:	00079303          	lh	t1,0(a5)
800018f8:	0789                	addi	a5,a5,2
800018fa:	0809                	addi	a6,a6,2
800018fc:	02670733          	mul	a4,a4,t1
80001900:	98ba                	add	a7,a7,a4
80001902:	fefe17e3          	bne	t3,a5,800018f0 <matrix_mul_vect+0x1a>
80001906:	0115a023          	sw	a7,0(a1)
8000190a:	0591                	addi	a1,a1,4
8000190c:	9eaa                	add	t4,t4,a0
8000190e:	fcbf1ce3          	bne	t5,a1,800018e6 <matrix_mul_vect+0x10>
80001912:	8082                	ret

80001914 <matrix_mul_matrix>:
80001914:	c52d                	beqz	a0,8000197e <matrix_mul_matrix+0x6a>
80001916:	1141                	addi	sp,sp,-16
80001918:	8f2a                	mv	t5,a0
8000191a:	0506                	slli	a0,a0,0x1
8000191c:	c622                	sw	s0,12(sp)
8000191e:	83ae                	mv	t2,a1
80001920:	8436                	mv	s0,a3
80001922:	8eb2                	mv	t4,a2
80001924:	00a60833          	add	a6,a2,a0
80001928:	4f81                	li	t6,0
8000192a:	4281                	li	t0,0
8000192c:	002f9893          	slli	a7,t6,0x2
80001930:	989e                	add	a7,a7,t2
80001932:	8322                	mv	t1,s0
80001934:	4e01                	li	t3,0
80001936:	869a                	mv	a3,t1
80001938:	87f6                	mv	a5,t4
8000193a:	4601                	li	a2,0
8000193c:	00079703          	lh	a4,0(a5)
80001940:	00069583          	lh	a1,0(a3)
80001944:	0789                	addi	a5,a5,2
80001946:	96aa                	add	a3,a3,a0
80001948:	02b70733          	mul	a4,a4,a1
8000194c:	963a                	add	a2,a2,a4
8000194e:	fef817e3          	bne	a6,a5,8000193c <matrix_mul_matrix+0x28>
80001952:	00c8a023          	sw	a2,0(a7)
80001956:	001e0793          	addi	a5,t3,1
8000195a:	0891                	addi	a7,a7,4
8000195c:	0309                	addi	t1,t1,2
8000195e:	00ff0463          	beq	t5,a5,80001966 <matrix_mul_matrix+0x52>
80001962:	8e3e                	mv	t3,a5
80001964:	bfc9                	j	80001936 <matrix_mul_matrix+0x22>
80001966:	9eaa                	add	t4,t4,a0
80001968:	9ffa                	add	t6,t6,t5
8000196a:	982a                	add	a6,a6,a0
8000196c:	00128793          	addi	a5,t0,1
80001970:	01c28463          	beq	t0,t3,80001978 <matrix_mul_matrix+0x64>
80001974:	82be                	mv	t0,a5
80001976:	bf5d                	j	8000192c <matrix_mul_matrix+0x18>
80001978:	4432                	lw	s0,12(sp)
8000197a:	0141                	addi	sp,sp,16
8000197c:	8082                	ret
8000197e:	8082                	ret

80001980 <matrix_mul_matrix_bitextract>:
80001980:	cd2d                	beqz	a0,800019fa <matrix_mul_matrix_bitextract+0x7a>
80001982:	1141                	addi	sp,sp,-16
80001984:	8f2a                	mv	t5,a0
80001986:	0506                	slli	a0,a0,0x1
80001988:	c622                	sw	s0,12(sp)
8000198a:	83ae                	mv	t2,a1
8000198c:	8436                	mv	s0,a3
8000198e:	8eb2                	mv	t4,a2
80001990:	00a60833          	add	a6,a2,a0
80001994:	4f81                	li	t6,0
80001996:	4281                	li	t0,0
80001998:	002f9893          	slli	a7,t6,0x2
8000199c:	989e                	add	a7,a7,t2
8000199e:	8322                	mv	t1,s0
800019a0:	4e01                	li	t3,0
800019a2:	861a                	mv	a2,t1
800019a4:	86f6                	mv	a3,t4
800019a6:	4581                	li	a1,0
800019a8:	00061703          	lh	a4,0(a2)
800019ac:	00069783          	lh	a5,0(a3)
800019b0:	0689                	addi	a3,a3,2
800019b2:	962a                	add	a2,a2,a0
800019b4:	02e787b3          	mul	a5,a5,a4
800019b8:	4027d713          	srai	a4,a5,0x2
800019bc:	8795                	srai	a5,a5,0x5
800019be:	8b3d                	andi	a4,a4,15
800019c0:	07f7f793          	andi	a5,a5,127
800019c4:	02f707b3          	mul	a5,a4,a5
800019c8:	95be                	add	a1,a1,a5
800019ca:	fcd81fe3          	bne	a6,a3,800019a8 <matrix_mul_matrix_bitextract+0x28>
800019ce:	00b8a023          	sw	a1,0(a7)
800019d2:	001e0793          	addi	a5,t3,1
800019d6:	0891                	addi	a7,a7,4
800019d8:	0309                	addi	t1,t1,2
800019da:	00ff0463          	beq	t5,a5,800019e2 <matrix_mul_matrix_bitextract+0x62>
800019de:	8e3e                	mv	t3,a5
800019e0:	b7c9                	j	800019a2 <matrix_mul_matrix_bitextract+0x22>
800019e2:	9eaa                	add	t4,t4,a0
800019e4:	9ffa                	add	t6,t6,t5
800019e6:	982a                	add	a6,a6,a0
800019e8:	00128793          	addi	a5,t0,1
800019ec:	01c28463          	beq	t0,t3,800019f4 <matrix_mul_matrix_bitextract+0x74>
800019f0:	82be                	mv	t0,a5
800019f2:	b75d                	j	80001998 <matrix_mul_matrix_bitextract+0x18>
800019f4:	4432                	lw	s0,12(sp)
800019f6:	0141                	addi	sp,sp,16
800019f8:	8082                	ret
800019fa:	8082                	ret

800019fc <matrix_test>:
800019fc:	7179                	addi	sp,sp,-48
800019fe:	d422                	sw	s0,40(sp)
80001a00:	d226                	sw	s1,36(sp)
80001a02:	cc52                	sw	s4,24(sp)
80001a04:	ca56                	sw	s5,20(sp)
80001a06:	7a7d                	lui	s4,0xfffff
80001a08:	d606                	sw	ra,44(sp)
80001a0a:	d04a                	sw	s2,32(sp)
80001a0c:	8aae                	mv	s5,a1
80001a0e:	8432                	mv	s0,a2
80001a10:	84b6                	mv	s1,a3
80001a12:	01476a33          	or	s4,a4,s4
80001a16:	24050d63          	beqz	a0,80001c70 <matrix_test+0x274>
80001a1a:	00151313          	slli	t1,a0,0x1
80001a1e:	ce4e                	sw	s3,28(sp)
80001a20:	c462                	sw	s8,8(sp)
80001a22:	006605b3          	add	a1,a2,t1
80001a26:	40a00c33          	neg	s8,a0
80001a2a:	01071993          	slli	s3,a4,0x10
80001a2e:	c65e                	sw	s7,12(sp)
80001a30:	c85a                	sw	s6,16(sp)
80001a32:	c266                	sw	s9,4(sp)
80001a34:	c06a                	sw	s10,0(sp)
80001a36:	88aa                	mv	a7,a0
80001a38:	862e                	mv	a2,a1
80001a3a:	0c0a                	slli	s8,s8,0x2
80001a3c:	0109d993          	srli	s3,s3,0x10
80001a40:	4b81                	li	s7,0
80001a42:	40660833          	sub	a6,a2,t1
80001a46:	87c2                	mv	a5,a6
80001a48:	0007d683          	lhu	a3,0(a5)
80001a4c:	0789                	addi	a5,a5,2
80001a4e:	96ce                	add	a3,a3,s3
80001a50:	fed79f23          	sh	a3,-2(a5)
80001a54:	fec79ae3          	bne	a5,a2,80001a48 <matrix_test+0x4c>
80001a58:	001b8913          	addi	s2,s7,1
80001a5c:	41880633          	sub	a2,a6,s8
80001a60:	01288463          	beq	a7,s2,80001a68 <matrix_test+0x6c>
80001a64:	8bca                	mv	s7,s2
80001a66:	bff1                	j	80001a42 <matrix_test+0x46>
80001a68:	4501                	li	a0,0
80001a6a:	4881                	li	a7,0
80001a6c:	40658833          	sub	a6,a1,t1
80001a70:	00251613          	slli	a2,a0,0x2
80001a74:	87c2                	mv	a5,a6
80001a76:	9656                	add	a2,a2,s5
80001a78:	00079683          	lh	a3,0(a5)
80001a7c:	0789                	addi	a5,a5,2
80001a7e:	0611                	addi	a2,a2,4
80001a80:	02e686b3          	mul	a3,a3,a4
80001a84:	fed62e23          	sw	a3,-4(a2)
80001a88:	fef598e3          	bne	a1,a5,80001a78 <matrix_test+0x7c>
80001a8c:	954a                	add	a0,a0,s2
80001a8e:	418805b3          	sub	a1,a6,s8
80001a92:	00188793          	addi	a5,a7,1
80001a96:	01788463          	beq	a7,s7,80001a9e <matrix_test+0xa2>
80001a9a:	88be                	mv	a7,a5
80001a9c:	bfc1                	j	80001a6c <matrix_test+0x70>
80001a9e:	418a8cb3          	sub	s9,s5,s8
80001aa2:	41200d33          	neg	s10,s2
80001aa6:	8866                	mv	a6,s9
80001aa8:	0d0e                	slli	s10,s10,0x3
80001aaa:	4681                	li	a3,0
80001aac:	4581                	li	a1,0
80001aae:	4501                	li	a0,0
80001ab0:	4301                	li	t1,0
80001ab2:	018808b3          	add	a7,a6,s8
80001ab6:	8746                	mv	a4,a7
80001ab8:	a039                	j	80001ac6 <matrix_test+0xca>
80001aba:	01079513          	slli	a0,a5,0x10
80001abe:	0711                	addi	a4,a4,4
80001ac0:	8541                	srai	a0,a0,0x10
80001ac2:	02e80563          	beq	a6,a4,80001aec <matrix_test+0xf0>
80001ac6:	8636                	mv	a2,a3
80001ac8:	01051793          	slli	a5,a0,0x10
80001acc:	4314                	lw	a3,0(a4)
80001ace:	83c1                	srli	a5,a5,0x10
80001ad0:	00a78513          	addi	a0,a5,10
80001ad4:	00d62633          	slt	a2,a2,a3
80001ad8:	0542                	slli	a0,a0,0x10
80001ada:	95b6                	add	a1,a1,a3
80001adc:	8541                	srai	a0,a0,0x10
80001ade:	97b2                	add	a5,a5,a2
80001ae0:	fcba5de3          	bge	s4,a1,80001aba <matrix_test+0xbe>
80001ae4:	0711                	addi	a4,a4,4
80001ae6:	4581                	li	a1,0
80001ae8:	fce81fe3          	bne	a6,a4,80001ac6 <matrix_test+0xca>
80001aec:	41a88833          	sub	a6,a7,s10
80001af0:	00130793          	addi	a5,t1,1
80001af4:	006b8463          	beq	s7,t1,80001afc <matrix_test+0x100>
80001af8:	833e                	mv	t1,a5
80001afa:	bf65                	j	80001ab2 <matrix_test+0xb6>
80001afc:	4581                	li	a1,0
80001afe:	2f3d                	jal	8000223c <crc16>
80001b00:	86a6                	mv	a3,s1
80001b02:	85d6                	mv	a1,s5
80001b04:	8b2a                	mv	s6,a0
80001b06:	8622                	mv	a2,s0
80001b08:	854a                	mv	a0,s2
80001b0a:	33f1                	jal	800018d6 <matrix_mul_vect>
80001b0c:	4681                	li	a3,0
80001b0e:	4581                	li	a1,0
80001b10:	4501                	li	a0,0
80001b12:	4881                	li	a7,0
80001b14:	019c0833          	add	a6,s8,s9
80001b18:	8742                	mv	a4,a6
80001b1a:	a039                	j	80001b28 <matrix_test+0x12c>
80001b1c:	01079513          	slli	a0,a5,0x10
80001b20:	0711                	addi	a4,a4,4
80001b22:	8541                	srai	a0,a0,0x10
80001b24:	03970563          	beq	a4,s9,80001b4e <matrix_test+0x152>
80001b28:	8636                	mv	a2,a3
80001b2a:	01051793          	slli	a5,a0,0x10
80001b2e:	4314                	lw	a3,0(a4)
80001b30:	83c1                	srli	a5,a5,0x10
80001b32:	00a78513          	addi	a0,a5,10
80001b36:	00d62633          	slt	a2,a2,a3
80001b3a:	0542                	slli	a0,a0,0x10
80001b3c:	95b6                	add	a1,a1,a3
80001b3e:	8541                	srai	a0,a0,0x10
80001b40:	97b2                	add	a5,a5,a2
80001b42:	fcba5de3          	bge	s4,a1,80001b1c <matrix_test+0x120>
80001b46:	0711                	addi	a4,a4,4
80001b48:	4581                	li	a1,0
80001b4a:	fd971fe3          	bne	a4,s9,80001b28 <matrix_test+0x12c>
80001b4e:	41a80cb3          	sub	s9,a6,s10
80001b52:	00188793          	addi	a5,a7,1
80001b56:	01788463          	beq	a7,s7,80001b5e <matrix_test+0x162>
80001b5a:	88be                	mv	a7,a5
80001b5c:	bf65                	j	80001b14 <matrix_test+0x118>
80001b5e:	85da                	mv	a1,s6
80001b60:	2df1                	jal	8000223c <crc16>
80001b62:	8622                	mv	a2,s0
80001b64:	8b2a                	mv	s6,a0
80001b66:	86a6                	mv	a3,s1
80001b68:	854a                	mv	a0,s2
80001b6a:	85d6                	mv	a1,s5
80001b6c:	3365                	jal	80001914 <matrix_mul_matrix>
80001b6e:	4301                	li	t1,0
80001b70:	4701                	li	a4,0
80001b72:	4601                	li	a2,0
80001b74:	4501                	li	a0,0
80001b76:	4881                	li	a7,0
80001b78:	00231593          	slli	a1,t1,0x2
80001b7c:	95d6                	add	a1,a1,s5
80001b7e:	4801                	li	a6,0
80001b80:	a801                	j	80001b90 <matrix_test+0x194>
80001b82:	01079513          	slli	a0,a5,0x10
80001b86:	0805                	addi	a6,a6,1
80001b88:	8541                	srai	a0,a0,0x10
80001b8a:	0591                	addi	a1,a1,4
80001b8c:	03287663          	bgeu	a6,s2,80001bb8 <matrix_test+0x1bc>
80001b90:	86ba                	mv	a3,a4
80001b92:	01051793          	slli	a5,a0,0x10
80001b96:	4198                	lw	a4,0(a1)
80001b98:	83c1                	srli	a5,a5,0x10
80001b9a:	00a78513          	addi	a0,a5,10
80001b9e:	00e6a6b3          	slt	a3,a3,a4
80001ba2:	0542                	slli	a0,a0,0x10
80001ba4:	963a                	add	a2,a2,a4
80001ba6:	8541                	srai	a0,a0,0x10
80001ba8:	97b6                	add	a5,a5,a3
80001baa:	fcca5ce3          	bge	s4,a2,80001b82 <matrix_test+0x186>
80001bae:	0805                	addi	a6,a6,1
80001bb0:	4601                	li	a2,0
80001bb2:	0591                	addi	a1,a1,4
80001bb4:	fd286ee3          	bltu	a6,s2,80001b90 <matrix_test+0x194>
80001bb8:	0885                	addi	a7,a7,1
80001bba:	934a                	add	t1,t1,s2
80001bbc:	fb28eee3          	bltu	a7,s2,80001b78 <matrix_test+0x17c>
80001bc0:	85da                	mv	a1,s6
80001bc2:	2dad                	jal	8000223c <crc16>
80001bc4:	87aa                	mv	a5,a0
80001bc6:	86a6                	mv	a3,s1
80001bc8:	8622                	mv	a2,s0
80001bca:	854a                	mv	a0,s2
80001bcc:	85d6                	mv	a1,s5
80001bce:	84be                	mv	s1,a5
80001bd0:	3b45                	jal	80001980 <matrix_mul_matrix_bitextract>
80001bd2:	4301                	li	t1,0
80001bd4:	4701                	li	a4,0
80001bd6:	4601                	li	a2,0
80001bd8:	4501                	li	a0,0
80001bda:	4881                	li	a7,0
80001bdc:	00231593          	slli	a1,t1,0x2
80001be0:	95d6                	add	a1,a1,s5
80001be2:	4801                	li	a6,0
80001be4:	a801                	j	80001bf4 <matrix_test+0x1f8>
80001be6:	01079513          	slli	a0,a5,0x10
80001bea:	0805                	addi	a6,a6,1
80001bec:	8541                	srai	a0,a0,0x10
80001bee:	0591                	addi	a1,a1,4
80001bf0:	03287663          	bgeu	a6,s2,80001c1c <matrix_test+0x220>
80001bf4:	86ba                	mv	a3,a4
80001bf6:	01051793          	slli	a5,a0,0x10
80001bfa:	4198                	lw	a4,0(a1)
80001bfc:	83c1                	srli	a5,a5,0x10
80001bfe:	00a78513          	addi	a0,a5,10
80001c02:	00e6a6b3          	slt	a3,a3,a4
80001c06:	0542                	slli	a0,a0,0x10
80001c08:	963a                	add	a2,a2,a4
80001c0a:	8541                	srai	a0,a0,0x10
80001c0c:	97b6                	add	a5,a5,a3
80001c0e:	fcca5ce3          	bge	s4,a2,80001be6 <matrix_test+0x1ea>
80001c12:	0805                	addi	a6,a6,1
80001c14:	4601                	li	a2,0
80001c16:	0591                	addi	a1,a1,4
80001c18:	fd286ee3          	bltu	a6,s2,80001bf4 <matrix_test+0x1f8>
80001c1c:	0885                	addi	a7,a7,1
80001c1e:	934a                	add	t1,t1,s2
80001c20:	fb28eee3          	bltu	a7,s2,80001bdc <matrix_test+0x1e0>
80001c24:	85a6                	mv	a1,s1
80001c26:	2d19                	jal	8000223c <crc16>
80001c28:	4581                	li	a1,0
80001c2a:	4601                	li	a2,0
80001c2c:	00159793          	slli	a5,a1,0x1
80001c30:	97a2                	add	a5,a5,s0
80001c32:	4681                	li	a3,0
80001c34:	0007d703          	lhu	a4,0(a5)
80001c38:	0685                	addi	a3,a3,1
80001c3a:	0789                	addi	a5,a5,2
80001c3c:	41370733          	sub	a4,a4,s3
80001c40:	fee79f23          	sh	a4,-2(a5)
80001c44:	ff26e8e3          	bltu	a3,s2,80001c34 <matrix_test+0x238>
80001c48:	0605                	addi	a2,a2,1
80001c4a:	95ca                	add	a1,a1,s2
80001c4c:	ff2660e3          	bltu	a2,s2,80001c2c <matrix_test+0x230>
80001c50:	49f2                	lw	s3,28(sp)
80001c52:	4b42                	lw	s6,16(sp)
80001c54:	4bb2                	lw	s7,12(sp)
80001c56:	4c22                	lw	s8,8(sp)
80001c58:	4c92                	lw	s9,4(sp)
80001c5a:	4d02                	lw	s10,0(sp)
80001c5c:	50b2                	lw	ra,44(sp)
80001c5e:	5422                	lw	s0,40(sp)
80001c60:	0542                	slli	a0,a0,0x10
80001c62:	5492                	lw	s1,36(sp)
80001c64:	5902                	lw	s2,32(sp)
80001c66:	4a62                	lw	s4,24(sp)
80001c68:	4ad2                	lw	s5,20(sp)
80001c6a:	8541                	srai	a0,a0,0x10
80001c6c:	6145                	addi	sp,sp,48
80001c6e:	8082                	ret
80001c70:	4581                	li	a1,0
80001c72:	23e9                	jal	8000223c <crc16>
80001c74:	86a6                	mv	a3,s1
80001c76:	8622                	mv	a2,s0
80001c78:	892a                	mv	s2,a0
80001c7a:	85d6                	mv	a1,s5
80001c7c:	4501                	li	a0,0
80001c7e:	39a1                	jal	800018d6 <matrix_mul_vect>
80001c80:	85ca                	mv	a1,s2
80001c82:	4501                	li	a0,0
80001c84:	2b65                	jal	8000223c <crc16>
80001c86:	86a6                	mv	a3,s1
80001c88:	8622                	mv	a2,s0
80001c8a:	892a                	mv	s2,a0
80001c8c:	85d6                	mv	a1,s5
80001c8e:	4501                	li	a0,0
80001c90:	3151                	jal	80001914 <matrix_mul_matrix>
80001c92:	85ca                	mv	a1,s2
80001c94:	4501                	li	a0,0
80001c96:	235d                	jal	8000223c <crc16>
80001c98:	87aa                	mv	a5,a0
80001c9a:	8622                	mv	a2,s0
80001c9c:	85d6                	mv	a1,s5
80001c9e:	86a6                	mv	a3,s1
80001ca0:	4501                	li	a0,0
80001ca2:	843e                	mv	s0,a5
80001ca4:	39f1                	jal	80001980 <matrix_mul_matrix_bitextract>
80001ca6:	85a2                	mv	a1,s0
80001ca8:	4501                	li	a0,0
80001caa:	2b49                	jal	8000223c <crc16>
80001cac:	bf45                	j	80001c5c <matrix_test+0x260>

80001cae <core_bench_matrix>:
80001cae:	1141                	addi	sp,sp,-16
80001cb0:	c422                	sw	s0,8(sp)
80001cb2:	4514                	lw	a3,8(a0)
80001cb4:	8432                	mv	s0,a2
80001cb6:	872e                	mv	a4,a1
80001cb8:	4150                	lw	a2,4(a0)
80001cba:	454c                	lw	a1,12(a0)
80001cbc:	4108                	lw	a0,0(a0)
80001cbe:	c606                	sw	ra,12(sp)
80001cc0:	3b35                	jal	800019fc <matrix_test>
80001cc2:	85a2                	mv	a1,s0
80001cc4:	4422                	lw	s0,8(sp)
80001cc6:	40b2                	lw	ra,12(sp)
80001cc8:	0141                	addi	sp,sp,16
80001cca:	ab8d                	j	8000223c <crc16>

80001ccc <core_init_state>:
80001ccc:	fff50813          	addi	a6,a0,-1
80001cd0:	4e05                	li	t3,1
80001cd2:	0d0e7163          	bgeu	t3,a6,80001d94 <core_init_state+0xc8>
80001cd6:	95f2                	add	a1,a1,t3
80001cd8:	05c2                	slli	a1,a1,0x10
80001cda:	81c1                	srli	a1,a1,0x10
80001cdc:	1141                	addi	sp,sp,-16
80001cde:	0035d793          	srli	a5,a1,0x3
80001ce2:	c622                	sw	s0,12(sp)
80001ce4:	489d                	li	a7,7
80001ce6:	0075f693          	andi	a3,a1,7
80001cea:	4701                	li	a4,0
80001cec:	00002317          	auipc	t1,0x2
80001cf0:	0e430313          	addi	t1,t1,228 # 80003dd0 <intpat>
80001cf4:	4e91                	li	t4,4
80001cf6:	02c00f13          	li	t5,44
80001cfa:	8b8d                	andi	a5,a5,3
80001cfc:	05168d63          	beq	a3,a7,80001d56 <core_init_state+0x8a>
80001d00:	08dee563          	bltu	t4,a3,80001d8a <core_init_state+0xbe>
80001d04:	16f5                	addi	a3,a3,-3
80001d06:	06c2                	slli	a3,a3,0x10
80001d08:	078a                	slli	a5,a5,0x2
80001d0a:	82c1                	srli	a3,a3,0x10
80001d0c:	979a                	add	a5,a5,t1
80001d0e:	06de6b63          	bltu	t3,a3,80001d84 <core_init_state+0xb8>
80001d12:	4b9c                	lw	a5,16(a5)
80001d14:	42a1                	li	t0,8
80001d16:	00170693          	addi	a3,a4,1
80001d1a:	00568433          	add	s0,a3,t0
80001d1e:	05047663          	bgeu	s0,a6,80001d6a <core_init_state+0x9e>
80001d22:	9732                	add	a4,a4,a2
80001d24:	86ba                	mv	a3,a4
80001d26:	005783b3          	add	t2,a5,t0
80001d2a:	0007cf83          	lbu	t6,0(a5)
80001d2e:	0785                	addi	a5,a5,1
80001d30:	0685                	addi	a3,a3,1
80001d32:	fff68fa3          	sb	t6,-1(a3)
80001d36:	fef39ae3          	bne	t2,a5,80001d2a <core_init_state+0x5e>
80001d3a:	0585                	addi	a1,a1,1
80001d3c:	05c2                	slli	a1,a1,0x10
80001d3e:	81c1                	srli	a1,a1,0x10
80001d40:	9716                	add	a4,a4,t0
80001d42:	01e70023          	sb	t5,0(a4)
80001d46:	0035d793          	srli	a5,a1,0x3
80001d4a:	0075f693          	andi	a3,a1,7
80001d4e:	8722                	mv	a4,s0
80001d50:	8b8d                	andi	a5,a5,3
80001d52:	fb1697e3          	bne	a3,a7,80001d00 <core_init_state+0x34>
80001d56:	078a                	slli	a5,a5,0x2
80001d58:	42a1                	li	t0,8
80001d5a:	00170693          	addi	a3,a4,1
80001d5e:	979a                	add	a5,a5,t1
80001d60:	00568433          	add	s0,a3,t0
80001d64:	5b9c                	lw	a5,48(a5)
80001d66:	fb046ee3          	bltu	s0,a6,80001d22 <core_init_state+0x56>
80001d6a:	00a76463          	bltu	a4,a0,80001d72 <core_init_state+0xa6>
80001d6e:	a801                	j	80001d7e <core_init_state+0xb2>
80001d70:	0685                	addi	a3,a3,1
80001d72:	9732                	add	a4,a4,a2
80001d74:	00070023          	sb	zero,0(a4)
80001d78:	8736                	mv	a4,a3
80001d7a:	fea6ebe3          	bltu	a3,a0,80001d70 <core_init_state+0xa4>
80001d7e:	4432                	lw	s0,12(sp)
80001d80:	0141                	addi	sp,sp,16
80001d82:	8082                	ret
80001d84:	439c                	lw	a5,0(a5)
80001d86:	4291                	li	t0,4
80001d88:	b779                	j	80001d16 <core_init_state+0x4a>
80001d8a:	078a                	slli	a5,a5,0x2
80001d8c:	979a                	add	a5,a5,t1
80001d8e:	539c                	lw	a5,32(a5)
80001d90:	42a1                	li	t0,8
80001d92:	b751                	j	80001d16 <core_init_state+0x4a>
80001d94:	86f2                	mv	a3,t3
80001d96:	4701                	li	a4,0
80001d98:	a011                	j	80001d9c <core_init_state+0xd0>
80001d9a:	0685                	addi	a3,a3,1
80001d9c:	9732                	add	a4,a4,a2
80001d9e:	00070023          	sb	zero,0(a4)
80001da2:	8736                	mv	a4,a3
80001da4:	fea6ebe3          	bltu	a3,a0,80001d9a <core_init_state+0xce>
80001da8:	8082                	ret

80001daa <core_state_transition>:
80001daa:	4114                	lw	a3,0(a0)
80001dac:	862a                	mv	a2,a0
80001dae:	0006c783          	lbu	a5,0(a3)
80001db2:	1c078563          	beqz	a5,80001f7c <core_state_transition+0x1d2>
80001db6:	02c00713          	li	a4,44
80001dba:	4501                	li	a0,0
80001dbc:	16e78a63          	beq	a5,a4,80001f30 <core_state_transition+0x186>
80001dc0:	02e00813          	li	a6,46
80001dc4:	19078b63          	beq	a5,a6,80001f5a <core_state_transition+0x1b0>
80001dc8:	16f86663          	bltu	a6,a5,80001f34 <core_state_transition+0x18a>
80001dcc:	fd578793          	addi	a5,a5,-43
80001dd0:	0fd7f793          	andi	a5,a5,253
80001dd4:	cb99                	beqz	a5,80001dea <core_state_transition+0x40>
80001dd6:	41d8                	lw	a4,4(a1)
80001dd8:	419c                	lw	a5,0(a1)
80001dda:	0685                	addi	a3,a3,1
80001ddc:	0705                	addi	a4,a4,1
80001dde:	0785                	addi	a5,a5,1
80001de0:	c1d8                	sw	a4,4(a1)
80001de2:	c19c                	sw	a5,0(a1)
80001de4:	4505                	li	a0,1
80001de6:	c214                	sw	a3,0(a2)
80001de8:	8082                	ret
80001dea:	4188                	lw	a0,0(a1)
80001dec:	00168793          	addi	a5,a3,1
80001df0:	0505                	addi	a0,a0,1
80001df2:	c188                	sw	a0,0(a1)
80001df4:	0016c883          	lbu	a7,1(a3)
80001df8:	1a088763          	beqz	a7,80001fa6 <core_state_transition+0x1fc>
80001dfc:	16e88c63          	beq	a7,a4,80001f74 <core_state_transition+0x1ca>
80001e00:	4588                	lw	a0,8(a1)
80001e02:	fd088713          	addi	a4,a7,-48
80001e06:	0ff77713          	zext.b	a4,a4
80001e0a:	4325                	li	t1,9
80001e0c:	0505                	addi	a0,a0,1
80001e0e:	00e37963          	bgeu	t1,a4,80001e20 <core_state_transition+0x76>
80001e12:	15088f63          	beq	a7,a6,80001f70 <core_state_transition+0x1c6>
80001e16:	c588                	sw	a0,8(a1)
80001e18:	0689                	addi	a3,a3,2
80001e1a:	4505                	li	a0,1
80001e1c:	c214                	sw	a3,0(a2)
80001e1e:	8082                	ret
80001e20:	c588                	sw	a0,8(a1)
80001e22:	0017c683          	lbu	a3,1(a5)
80001e26:	0785                	addi	a5,a5,1
80001e28:	12068663          	beqz	a3,80001f54 <core_state_transition+0x1aa>
80001e2c:	02c00713          	li	a4,44
80001e30:	16e68263          	beq	a3,a4,80001f94 <core_state_transition+0x1ea>
80001e34:	02e00713          	li	a4,46
80001e38:	02e68263          	beq	a3,a4,80001e5c <core_state_transition+0xb2>
80001e3c:	fd068693          	addi	a3,a3,-48
80001e40:	0ff6f693          	zext.b	a3,a3
80001e44:	4725                	li	a4,9
80001e46:	fcd77ee3          	bgeu	a4,a3,80001e22 <core_state_transition+0x78>
80001e4a:	4998                	lw	a4,16(a1)
80001e4c:	4505                	li	a0,1
80001e4e:	00178693          	addi	a3,a5,1
80001e52:	00a707b3          	add	a5,a4,a0
80001e56:	c99c                	sw	a5,16(a1)
80001e58:	c214                	sw	a3,0(a2)
80001e5a:	8082                	ret
80001e5c:	4998                	lw	a4,16(a1)
80001e5e:	0705                	addi	a4,a4,1
80001e60:	c998                	sw	a4,16(a1)
80001e62:	0017c683          	lbu	a3,1(a5)
80001e66:	0785                	addi	a5,a5,1
80001e68:	10068163          	beqz	a3,80001f6a <core_state_transition+0x1c0>
80001e6c:	02c00713          	li	a4,44
80001e70:	0ae68e63          	beq	a3,a4,80001f2c <core_state_transition+0x182>
80001e74:	0df6f713          	andi	a4,a3,223
80001e78:	04500513          	li	a0,69
80001e7c:	02a70263          	beq	a4,a0,80001ea0 <core_state_transition+0xf6>
80001e80:	fd068693          	addi	a3,a3,-48
80001e84:	0ff6f693          	zext.b	a3,a3
80001e88:	4725                	li	a4,9
80001e8a:	fcd77ce3          	bgeu	a4,a3,80001e62 <core_state_transition+0xb8>
80001e8e:	49d8                	lw	a4,20(a1)
80001e90:	4505                	li	a0,1
80001e92:	00178693          	addi	a3,a5,1
80001e96:	00a707b3          	add	a5,a4,a0
80001e9a:	c9dc                	sw	a5,20(a1)
80001e9c:	c214                	sw	a3,0(a2)
80001e9e:	8082                	ret
80001ea0:	49d8                	lw	a4,20(a1)
80001ea2:	00178693          	addi	a3,a5,1
80001ea6:	0705                	addi	a4,a4,1
80001ea8:	c9d8                	sw	a4,20(a1)
80001eaa:	0017c703          	lbu	a4,1(a5)
80001eae:	cb79                	beqz	a4,80001f84 <core_state_transition+0x1da>
80001eb0:	02c00513          	li	a0,44
80001eb4:	0ca70d63          	beq	a4,a0,80001f8e <core_state_transition+0x1e4>
80001eb8:	45d4                	lw	a3,12(a1)
80001eba:	fd570713          	addi	a4,a4,-43
80001ebe:	0fd77713          	andi	a4,a4,253
80001ec2:	0685                	addi	a3,a3,1
80001ec4:	c5d4                	sw	a3,12(a1)
80001ec6:	c711                	beqz	a4,80001ed2 <core_state_transition+0x128>
80001ec8:	00278693          	addi	a3,a5,2
80001ecc:	4505                	li	a0,1
80001ece:	c214                	sw	a3,0(a2)
80001ed0:	8082                	ret
80001ed2:	0027c703          	lbu	a4,2(a5)
80001ed6:	00278693          	addi	a3,a5,2
80001eda:	c35d                	beqz	a4,80001f80 <core_state_transition+0x1d6>
80001edc:	0aa70663          	beq	a4,a0,80001f88 <core_state_transition+0x1de>
80001ee0:	0185a803          	lw	a6,24(a1)
80001ee4:	fd070713          	addi	a4,a4,-48
80001ee8:	0ff77713          	zext.b	a4,a4
80001eec:	0805                	addi	a6,a6,1
80001eee:	4525                	li	a0,9
80001ef0:	0105ac23          	sw	a6,24(a1)
80001ef4:	00e57663          	bgeu	a0,a4,80001f00 <core_state_transition+0x156>
80001ef8:	00378693          	addi	a3,a5,3
80001efc:	4505                	li	a0,1
80001efe:	b5e5                	j	80001de6 <core_state_transition+0x3c>
80001f00:	8836                	mv	a6,a3
80001f02:	0016c703          	lbu	a4,1(a3)
80001f06:	0685                	addi	a3,a3,1
80001f08:	02c00893          	li	a7,44
80001f0c:	fd070793          	addi	a5,a4,-48
80001f10:	0ff7f793          	zext.b	a5,a5
80001f14:	c759                	beqz	a4,80001fa2 <core_state_transition+0x1f8>
80001f16:	09170363          	beq	a4,a7,80001f9c <core_state_transition+0x1f2>
80001f1a:	fef573e3          	bgeu	a0,a5,80001f00 <core_state_transition+0x156>
80001f1e:	41dc                	lw	a5,4(a1)
80001f20:	4505                	li	a0,1
80001f22:	00280693          	addi	a3,a6,2
80001f26:	97aa                	add	a5,a5,a0
80001f28:	c1dc                	sw	a5,4(a1)
80001f2a:	bd75                	j	80001de6 <core_state_transition+0x3c>
80001f2c:	86be                	mv	a3,a5
80001f2e:	4515                	li	a0,5
80001f30:	0685                	addi	a3,a3,1
80001f32:	bd55                	j	80001de6 <core_state_transition+0x3c>
80001f34:	fd078793          	addi	a5,a5,-48
80001f38:	0ff7f793          	zext.b	a5,a5
80001f3c:	4525                	li	a0,9
80001f3e:	e8f56ce3          	bltu	a0,a5,80001dd6 <core_state_transition+0x2c>
80001f42:	4188                	lw	a0,0(a1)
80001f44:	00168793          	addi	a5,a3,1
80001f48:	0505                	addi	a0,a0,1
80001f4a:	c188                	sw	a0,0(a1)
80001f4c:	0016c683          	lbu	a3,1(a3)
80001f50:	ee0690e3          	bnez	a3,80001e30 <core_state_transition+0x86>
80001f54:	86be                	mv	a3,a5
80001f56:	4511                	li	a0,4
80001f58:	b579                	j	80001de6 <core_state_transition+0x3c>
80001f5a:	4188                	lw	a0,0(a1)
80001f5c:	00168793          	addi	a5,a3,1
80001f60:	0505                	addi	a0,a0,1
80001f62:	c188                	sw	a0,0(a1)
80001f64:	0016c683          	lbu	a3,1(a3)
80001f68:	f681                	bnez	a3,80001e70 <core_state_transition+0xc6>
80001f6a:	86be                	mv	a3,a5
80001f6c:	4515                	li	a0,5
80001f6e:	bda5                	j	80001de6 <core_state_transition+0x3c>
80001f70:	c588                	sw	a0,8(a1)
80001f72:	bdc5                	j	80001e62 <core_state_transition+0xb8>
80001f74:	86be                	mv	a3,a5
80001f76:	4509                	li	a0,2
80001f78:	0685                	addi	a3,a3,1
80001f7a:	b5b5                	j	80001de6 <core_state_transition+0x3c>
80001f7c:	4501                	li	a0,0
80001f7e:	b5a5                	j	80001de6 <core_state_transition+0x3c>
80001f80:	4519                	li	a0,6
80001f82:	b595                	j	80001de6 <core_state_transition+0x3c>
80001f84:	450d                	li	a0,3
80001f86:	b585                	j	80001de6 <core_state_transition+0x3c>
80001f88:	4519                	li	a0,6
80001f8a:	0685                	addi	a3,a3,1
80001f8c:	bda9                	j	80001de6 <core_state_transition+0x3c>
80001f8e:	450d                	li	a0,3
80001f90:	0685                	addi	a3,a3,1
80001f92:	bd91                	j	80001de6 <core_state_transition+0x3c>
80001f94:	86be                	mv	a3,a5
80001f96:	4511                	li	a0,4
80001f98:	0685                	addi	a3,a3,1
80001f9a:	b5b1                	j	80001de6 <core_state_transition+0x3c>
80001f9c:	451d                	li	a0,7
80001f9e:	0685                	addi	a3,a3,1
80001fa0:	b599                	j	80001de6 <core_state_transition+0x3c>
80001fa2:	451d                	li	a0,7
80001fa4:	b589                	j	80001de6 <core_state_transition+0x3c>
80001fa6:	86be                	mv	a3,a5
80001fa8:	4509                	li	a0,2
80001faa:	bd35                	j	80001de6 <core_state_transition+0x3c>

80001fac <core_bench_state>:
80001fac:	7119                	addi	sp,sp,-128
80001fae:	d6ce                	sw	s3,108(sp)
80001fb0:	d4d2                	sw	s4,104(sp)
80001fb2:	01010993          	addi	s3,sp,16
80001fb6:	03010a13          	addi	s4,sp,48
80001fba:	dca2                	sw	s0,120(sp)
80001fbc:	daa6                	sw	s1,116(sp)
80001fbe:	d8ca                	sw	s2,112(sp)
80001fc0:	d2d6                	sw	s5,100(sp)
80001fc2:	cede                	sw	s7,92(sp)
80001fc4:	cce2                	sw	s8,88(sp)
80001fc6:	cae6                	sw	s9,84(sp)
80001fc8:	8aba                	mv	s5,a4
80001fca:	84be                	mv	s1,a5
80001fcc:	de86                	sw	ra,124(sp)
80001fce:	d0da                	sw	s6,96(sp)
80001fd0:	842e                	mv	s0,a1
80001fd2:	c62e                	sw	a1,12(sp)
80001fd4:	8c2a                	mv	s8,a0
80001fd6:	8cb2                	mv	s9,a2
80001fd8:	8bb6                	mv	s7,a3
80001fda:	87d2                	mv	a5,s4
80001fdc:	894e                	mv	s2,s3
80001fde:	874e                	mv	a4,s3
80001fe0:	0007a023          	sw	zero,0(a5)
80001fe4:	00072023          	sw	zero,0(a4)
80001fe8:	0791                	addi	a5,a5,4
80001fea:	0894                	addi	a3,sp,80
80001fec:	0711                	addi	a4,a4,4
80001fee:	fed799e3          	bne	a5,a3,80001fe0 <core_bench_state+0x34>
80001ff2:	00044783          	lbu	a5,0(s0)
80001ff6:	00c10b13          	addi	s6,sp,12
80001ffa:	c3e1                	beqz	a5,800020ba <core_bench_state+0x10e>
80001ffc:	180c                	addi	a1,sp,48
80001ffe:	855a                	mv	a0,s6
80002000:	336d                	jal	80001daa <core_state_transition>
80002002:	00251813          	slli	a6,a0,0x2
80002006:	984e                	add	a6,a6,s3
80002008:	4732                	lw	a4,12(sp)
8000200a:	00082783          	lw	a5,0(a6)
8000200e:	00074703          	lbu	a4,0(a4)
80002012:	0785                	addi	a5,a5,1
80002014:	00f82023          	sw	a5,0(a6)
80002018:	f375                	bnez	a4,80001ffc <core_bench_state+0x50>
8000201a:	c622                	sw	s0,12(sp)
8000201c:	9c22                	add	s8,s8,s0
8000201e:	03847563          	bgeu	s0,s8,80002048 <core_bench_state+0x9c>
80002022:	87a2                	mv	a5,s0
80002024:	02c00613          	li	a2,44
80002028:	0007c703          	lbu	a4,0(a5)
8000202c:	019746b3          	xor	a3,a4,s9
80002030:	00c70463          	beq	a4,a2,80002038 <core_bench_state+0x8c>
80002034:	00d78023          	sb	a3,0(a5)
80002038:	97d6                	add	a5,a5,s5
8000203a:	ff87e7e3          	bltu	a5,s8,80002028 <core_bench_state+0x7c>
8000203e:	00044783          	lbu	a5,0(s0)
80002042:	00c10b13          	addi	s6,sp,12
80002046:	cf91                	beqz	a5,80002062 <core_bench_state+0xb6>
80002048:	180c                	addi	a1,sp,48
8000204a:	855a                	mv	a0,s6
8000204c:	3bb9                	jal	80001daa <core_state_transition>
8000204e:	00251613          	slli	a2,a0,0x2
80002052:	964e                	add	a2,a2,s3
80002054:	4732                	lw	a4,12(sp)
80002056:	421c                	lw	a5,0(a2)
80002058:	00074703          	lbu	a4,0(a4)
8000205c:	0785                	addi	a5,a5,1
8000205e:	c21c                	sw	a5,0(a2)
80002060:	f765                	bnez	a4,80002048 <core_bench_state+0x9c>
80002062:	c622                	sw	s0,12(sp)
80002064:	02c00693          	li	a3,44
80002068:	01847d63          	bgeu	s0,s8,80002082 <core_bench_state+0xd6>
8000206c:	00044783          	lbu	a5,0(s0)
80002070:	0177c733          	xor	a4,a5,s7
80002074:	00d78463          	beq	a5,a3,8000207c <core_bench_state+0xd0>
80002078:	00e40023          	sb	a4,0(s0)
8000207c:	9456                	add	s0,s0,s5
8000207e:	ff8467e3          	bltu	s0,s8,8000206c <core_bench_state+0xc0>
80002082:	02098993          	addi	s3,s3,32
80002086:	00092503          	lw	a0,0(s2)
8000208a:	85a6                	mv	a1,s1
8000208c:	0911                	addi	s2,s2,4
8000208e:	28fd                	jal	8000218c <crcu32>
80002090:	85aa                	mv	a1,a0
80002092:	000a2503          	lw	a0,0(s4) # fffff000 <_end+0x7fffa700>
80002096:	0a11                	addi	s4,s4,4
80002098:	28d5                	jal	8000218c <crcu32>
8000209a:	84aa                	mv	s1,a0
8000209c:	ff2995e3          	bne	s3,s2,80002086 <core_bench_state+0xda>
800020a0:	50f6                	lw	ra,124(sp)
800020a2:	5466                	lw	s0,120(sp)
800020a4:	54d6                	lw	s1,116(sp)
800020a6:	5946                	lw	s2,112(sp)
800020a8:	59b6                	lw	s3,108(sp)
800020aa:	5a26                	lw	s4,104(sp)
800020ac:	5a96                	lw	s5,100(sp)
800020ae:	5b06                	lw	s6,96(sp)
800020b0:	4bf6                	lw	s7,92(sp)
800020b2:	4c66                	lw	s8,88(sp)
800020b4:	4cd6                	lw	s9,84(sp)
800020b6:	6109                	addi	sp,sp,128
800020b8:	8082                	ret
800020ba:	9c22                	add	s8,s8,s0
800020bc:	f78463e3          	bltu	s0,s8,80002022 <core_bench_state+0x76>
800020c0:	b7c9                	j	80002082 <core_bench_state+0xd6>

800020c2 <get_seed_32>:
800020c2:	4795                	li	a5,5
800020c4:	04a7e063          	bltu	a5,a0,80002104 <get_seed_32+0x42>
800020c8:	00002717          	auipc	a4,0x2
800020cc:	d4870713          	addi	a4,a4,-696 # 80003e10 <errpat+0x10>
800020d0:	050a                	slli	a0,a0,0x2
800020d2:	953a                	add	a0,a0,a4
800020d4:	411c                	lw	a5,0(a0)
800020d6:	97ba                	add	a5,a5,a4
800020d8:	8782                	jr	a5
800020da:	00002517          	auipc	a0,0x2
800020de:	03252503          	lw	a0,50(a0) # 8000410c <seed5_volatile>
800020e2:	8082                	ret
800020e4:	00002517          	auipc	a0,0x2
800020e8:	03052503          	lw	a0,48(a0) # 80004114 <seed1_volatile>
800020ec:	8082                	ret
800020ee:	00002517          	auipc	a0,0x2
800020f2:	02252503          	lw	a0,34(a0) # 80004110 <seed2_volatile>
800020f6:	8082                	ret
800020f8:	8201a503          	lw	a0,-2016(gp) # 80004100 <seed3_volatile>
800020fc:	8082                	ret
800020fe:	81c1a503          	lw	a0,-2020(gp) # 800040fc <seed4_volatile>
80002102:	8082                	ret
80002104:	4501                	li	a0,0
80002106:	8082                	ret

80002108 <crcu8>:
80002108:	7669                	lui	a2,0xffffa
8000210a:	86aa                	mv	a3,a0
8000210c:	0605                	addi	a2,a2,1 # ffffa001 <_end+0x7fff5701>
8000210e:	852e                	mv	a0,a1
80002110:	4721                	li	a4,8
80002112:	00a6c7b3          	xor	a5,a3,a0
80002116:	8b85                	andi	a5,a5,1
80002118:	40f007b3          	neg	a5,a5
8000211c:	8105                	srli	a0,a0,0x1
8000211e:	8ff1                	and	a5,a5,a2
80002120:	177d                	addi	a4,a4,-1
80002122:	8fa9                	xor	a5,a5,a0
80002124:	01079513          	slli	a0,a5,0x10
80002128:	0ff77713          	zext.b	a4,a4
8000212c:	8141                	srli	a0,a0,0x10
8000212e:	8285                	srli	a3,a3,0x1
80002130:	f36d                	bnez	a4,80002112 <crcu8+0xa>
80002132:	8082                	ret

80002134 <crcu16>:
80002134:	86aa                	mv	a3,a0
80002136:	77e9                	lui	a5,0xffffa
80002138:	852e                	mv	a0,a1
8000213a:	0ff6f613          	zext.b	a2,a3
8000213e:	00178593          	addi	a1,a5,1 # ffffa001 <_end+0x7fff5701>
80002142:	4721                	li	a4,8
80002144:	00a647b3          	xor	a5,a2,a0
80002148:	8b85                	andi	a5,a5,1
8000214a:	40f007b3          	neg	a5,a5
8000214e:	8fed                	and	a5,a5,a1
80002150:	8105                	srli	a0,a0,0x1
80002152:	177d                	addi	a4,a4,-1
80002154:	8d3d                	xor	a0,a0,a5
80002156:	0542                	slli	a0,a0,0x10
80002158:	0ff77713          	zext.b	a4,a4
8000215c:	8141                	srli	a0,a0,0x10
8000215e:	8205                	srli	a2,a2,0x1
80002160:	f375                	bnez	a4,80002144 <crcu16+0x10>
80002162:	7669                	lui	a2,0xffffa
80002164:	82a1                	srli	a3,a3,0x8
80002166:	0605                	addi	a2,a2,1 # ffffa001 <_end+0x7fff5701>
80002168:	4721                	li	a4,8
8000216a:	00a6c7b3          	xor	a5,a3,a0
8000216e:	8b85                	andi	a5,a5,1
80002170:	40f007b3          	neg	a5,a5
80002174:	8105                	srli	a0,a0,0x1
80002176:	8ff1                	and	a5,a5,a2
80002178:	177d                	addi	a4,a4,-1
8000217a:	8fa9                	xor	a5,a5,a0
8000217c:	01079513          	slli	a0,a5,0x10
80002180:	0ff77713          	zext.b	a4,a4
80002184:	8141                	srli	a0,a0,0x10
80002186:	8285                	srli	a3,a3,0x1
80002188:	f36d                	bnez	a4,8000216a <crcu16+0x36>
8000218a:	8082                	ret

8000218c <crcu32>:
8000218c:	86aa                	mv	a3,a0
8000218e:	01051613          	slli	a2,a0,0x10
80002192:	7869                	lui	a6,0xffffa
80002194:	852e                	mv	a0,a1
80002196:	8241                	srli	a2,a2,0x10
80002198:	0ff6f593          	zext.b	a1,a3
8000219c:	0805                	addi	a6,a6,1 # ffffa001 <_end+0x7fff5701>
8000219e:	4721                	li	a4,8
800021a0:	00a5c7b3          	xor	a5,a1,a0
800021a4:	8b85                	andi	a5,a5,1
800021a6:	40f007b3          	neg	a5,a5
800021aa:	8105                	srli	a0,a0,0x1
800021ac:	0107f7b3          	and	a5,a5,a6
800021b0:	177d                	addi	a4,a4,-1
800021b2:	8fa9                	xor	a5,a5,a0
800021b4:	01079513          	slli	a0,a5,0x10
800021b8:	0ff77713          	zext.b	a4,a4
800021bc:	8141                	srli	a0,a0,0x10
800021be:	8185                	srli	a1,a1,0x1
800021c0:	f365                	bnez	a4,800021a0 <crcu32+0x14>
800021c2:	75e9                	lui	a1,0xffffa
800021c4:	8221                	srli	a2,a2,0x8
800021c6:	0585                	addi	a1,a1,1 # ffffa001 <_end+0x7fff5701>
800021c8:	4721                	li	a4,8
800021ca:	00a647b3          	xor	a5,a2,a0
800021ce:	8b85                	andi	a5,a5,1
800021d0:	40f007b3          	neg	a5,a5
800021d4:	8105                	srli	a0,a0,0x1
800021d6:	8fed                	and	a5,a5,a1
800021d8:	177d                	addi	a4,a4,-1
800021da:	8fa9                	xor	a5,a5,a0
800021dc:	01079513          	slli	a0,a5,0x10
800021e0:	0ff77713          	zext.b	a4,a4
800021e4:	8141                	srli	a0,a0,0x10
800021e6:	8205                	srli	a2,a2,0x1
800021e8:	f36d                	bnez	a4,800021ca <crcu32+0x3e>
800021ea:	82c1                	srli	a3,a3,0x10
800021ec:	75e9                	lui	a1,0xffffa
800021ee:	0ff6f613          	zext.b	a2,a3
800021f2:	0585                	addi	a1,a1,1 # ffffa001 <_end+0x7fff5701>
800021f4:	4721                	li	a4,8
800021f6:	00a647b3          	xor	a5,a2,a0
800021fa:	8b85                	andi	a5,a5,1
800021fc:	40f007b3          	neg	a5,a5
80002200:	8fed                	and	a5,a5,a1
80002202:	8105                	srli	a0,a0,0x1
80002204:	177d                	addi	a4,a4,-1
80002206:	8d3d                	xor	a0,a0,a5
80002208:	0542                	slli	a0,a0,0x10
8000220a:	0ff77713          	zext.b	a4,a4
8000220e:	8141                	srli	a0,a0,0x10
80002210:	8205                	srli	a2,a2,0x1
80002212:	f375                	bnez	a4,800021f6 <crcu32+0x6a>
80002214:	7669                	lui	a2,0xffffa
80002216:	82a1                	srli	a3,a3,0x8
80002218:	0605                	addi	a2,a2,1 # ffffa001 <_end+0x7fff5701>
8000221a:	4721                	li	a4,8
8000221c:	00a6c7b3          	xor	a5,a3,a0
80002220:	8b85                	andi	a5,a5,1
80002222:	40f007b3          	neg	a5,a5
80002226:	8ff1                	and	a5,a5,a2
80002228:	8105                	srli	a0,a0,0x1
8000222a:	177d                	addi	a4,a4,-1
8000222c:	8d3d                	xor	a0,a0,a5
8000222e:	0542                	slli	a0,a0,0x10
80002230:	0ff77713          	zext.b	a4,a4
80002234:	8141                	srli	a0,a0,0x10
80002236:	8285                	srli	a3,a3,0x1
80002238:	f375                	bnez	a4,8000221c <crcu32+0x90>
8000223a:	8082                	ret

8000223c <crc16>:
8000223c:	86aa                	mv	a3,a0
8000223e:	01051613          	slli	a2,a0,0x10
80002242:	77e9                	lui	a5,0xffffa
80002244:	852e                	mv	a0,a1
80002246:	8241                	srli	a2,a2,0x10
80002248:	0ff6f693          	zext.b	a3,a3
8000224c:	00178593          	addi	a1,a5,1 # ffffa001 <_end+0x7fff5701>
80002250:	4721                	li	a4,8
80002252:	00a6c7b3          	xor	a5,a3,a0
80002256:	8b85                	andi	a5,a5,1
80002258:	40f007b3          	neg	a5,a5
8000225c:	8fed                	and	a5,a5,a1
8000225e:	8105                	srli	a0,a0,0x1
80002260:	177d                	addi	a4,a4,-1
80002262:	8d3d                	xor	a0,a0,a5
80002264:	0542                	slli	a0,a0,0x10
80002266:	0ff77713          	zext.b	a4,a4
8000226a:	8141                	srli	a0,a0,0x10
8000226c:	8285                	srli	a3,a3,0x1
8000226e:	f375                	bnez	a4,80002252 <crc16+0x16>
80002270:	77e9                	lui	a5,0xffffa
80002272:	00865693          	srli	a3,a2,0x8
80002276:	4721                	li	a4,8
80002278:	00178613          	addi	a2,a5,1 # ffffa001 <_end+0x7fff5701>
8000227c:	00a6c7b3          	xor	a5,a3,a0
80002280:	8b85                	andi	a5,a5,1
80002282:	40f007b3          	neg	a5,a5
80002286:	8105                	srli	a0,a0,0x1
80002288:	8ff1                	and	a5,a5,a2
8000228a:	177d                	addi	a4,a4,-1
8000228c:	8fa9                	xor	a5,a5,a0
8000228e:	01079513          	slli	a0,a5,0x10
80002292:	0ff77713          	zext.b	a4,a4
80002296:	8141                	srli	a0,a0,0x10
80002298:	8285                	srli	a3,a3,0x1
8000229a:	f36d                	bnez	a4,8000227c <crc16+0x40>
8000229c:	8082                	ret

8000229e <check_data_types>:
8000229e:	4501                	li	a0,0
800022a0:	8082                	ret

800022a2 <portable_malloc>:
800022a2:	4501                	li	a0,0
800022a4:	8082                	ret

800022a6 <portable_free>:
800022a6:	8082                	ret

800022a8 <start_time>:
800022a8:	c00027f3          	rdcycle	a5
800022ac:	00002717          	auipc	a4,0x2
800022b0:	e4f72e23          	sw	a5,-420(a4) # 80004108 <start_time_val>
800022b4:	8082                	ret

800022b6 <stop_time>:
800022b6:	c00027f3          	rdcycle	a5
800022ba:	00002717          	auipc	a4,0x2
800022be:	e4f72523          	sw	a5,-438(a4) # 80004104 <stop_time_val>
800022c2:	8082                	ret

800022c4 <get_time>:
800022c4:	00002517          	auipc	a0,0x2
800022c8:	e4052503          	lw	a0,-448(a0) # 80004104 <stop_time_val>
800022cc:	00002797          	auipc	a5,0x2
800022d0:	e3c7a783          	lw	a5,-452(a5) # 80004108 <start_time_val>
800022d4:	8d1d                	sub	a0,a0,a5
800022d6:	8082                	ret

800022d8 <time_in_secs>:
800022d8:	d2150553          	fcvt.d.wu	fa0,a0
800022dc:	00002797          	auipc	a5,0x2
800022e0:	e147b787          	fld	fa5,-492(a5) # 800040f0 <.got.plt+0x18>
800022e4:	1af57553          	fdiv.d	fa0,fa0,fa5
800022e8:	8082                	ret

800022ea <portable_init>:
800022ea:	4785                	li	a5,1
800022ec:	00f50023          	sb	a5,0(a0)
800022f0:	8082                	ret

800022f2 <portable_fini>:
800022f2:	00050023          	sb	zero,0(a0)
800022f6:	8082                	ret

800022f8 <vprintfmt>:
800022f8:	714d                	addi	sp,sp,-336
800022fa:	14812423          	sw	s0,328(sp)
800022fe:	15212023          	sw	s2,320(sp)
80002302:	13312e23          	sw	s3,316(sp)
80002306:	13512a23          	sw	s5,308(sp)
8000230a:	14112623          	sw	ra,332(sp)
8000230e:	14912223          	sw	s1,324(sp)
80002312:	13412c23          	sw	s4,312(sp)
80002316:	13712623          	sw	s7,300(sp)
8000231a:	13812423          	sw	s8,296(sp)
8000231e:	13912223          	sw	s9,292(sp)
80002322:	13a12023          	sw	s10,288(sp)
80002326:	89aa                	mv	s3,a0
80002328:	892e                	mv	s2,a1
8000232a:	8432                	mv	s0,a2
8000232c:	c636                	sw	a3,12(sp)
8000232e:	02500a93          	li	s5,37
80002332:	a029                	j	8000233c <vprintfmt+0x44>
80002334:	c531                	beqz	a0,80002380 <vprintfmt+0x88>
80002336:	85ca                	mv	a1,s2
80002338:	0405                	addi	s0,s0,1
8000233a:	9982                	jalr	s3
8000233c:	00044503          	lbu	a0,0(s0)
80002340:	ff551ae3          	bne	a0,s5,80002334 <vprintfmt+0x3c>
80002344:	00144683          	lbu	a3,1(s0)
80002348:	00140a13          	addi	s4,s0,1
8000234c:	54fd                	li	s1,-1
8000234e:	02000793          	li	a5,32
80002352:	8752                	mv	a4,s4
80002354:	8c26                	mv	s8,s1
80002356:	c43e                	sw	a5,8(sp)
80002358:	4581                	li	a1,0
8000235a:	fdd68793          	addi	a5,a3,-35
8000235e:	0ff7f793          	zext.b	a5,a5
80002362:	05500613          	li	a2,85
80002366:	00170413          	addi	s0,a4,1
8000236a:	06f66163          	bltu	a2,a5,800023cc <vprintfmt+0xd4>
8000236e:	00002617          	auipc	a2,0x2
80002372:	aba60613          	addi	a2,a2,-1350 # 80003e28 <errpat+0x28>
80002376:	078a                	slli	a5,a5,0x2
80002378:	97b2                	add	a5,a5,a2
8000237a:	439c                	lw	a5,0(a5)
8000237c:	97b2                	add	a5,a5,a2
8000237e:	8782                	jr	a5
80002380:	14c12083          	lw	ra,332(sp)
80002384:	14812403          	lw	s0,328(sp)
80002388:	14412483          	lw	s1,324(sp)
8000238c:	14012903          	lw	s2,320(sp)
80002390:	13c12983          	lw	s3,316(sp)
80002394:	13812a03          	lw	s4,312(sp)
80002398:	13412a83          	lw	s5,308(sp)
8000239c:	12c12b83          	lw	s7,300(sp)
800023a0:	12812c03          	lw	s8,296(sp)
800023a4:	12412c83          	lw	s9,292(sp)
800023a8:	12012d03          	lw	s10,288(sp)
800023ac:	6171                	addi	sp,sp,336
800023ae:	8082                	ret
800023b0:	c436                	sw	a3,8(sp)
800023b2:	00174683          	lbu	a3,1(a4)
800023b6:	05500613          	li	a2,85
800023ba:	8722                	mv	a4,s0
800023bc:	fdd68793          	addi	a5,a3,-35
800023c0:	0ff7f793          	zext.b	a5,a5
800023c4:	00170413          	addi	s0,a4,1
800023c8:	faf673e3          	bgeu	a2,a5,8000236e <vprintfmt+0x76>
800023cc:	85ca                	mv	a1,s2
800023ce:	02500513          	li	a0,37
800023d2:	9982                	jalr	s3
800023d4:	8452                	mv	s0,s4
800023d6:	b79d                	j	8000233c <vprintfmt+0x44>
800023d8:	00174603          	lbu	a2,1(a4)
800023dc:	4525                	li	a0,9
800023de:	fd068493          	addi	s1,a3,-48
800023e2:	fd060793          	addi	a5,a2,-48
800023e6:	86b2                	mv	a3,a2
800023e8:	8722                	mv	a4,s0
800023ea:	02f56163          	bltu	a0,a5,8000240c <vprintfmt+0x114>
800023ee:	00249793          	slli	a5,s1,0x2
800023f2:	97a6                	add	a5,a5,s1
800023f4:	0705                	addi	a4,a4,1
800023f6:	0786                	slli	a5,a5,0x1
800023f8:	97b2                	add	a5,a5,a2
800023fa:	00074603          	lbu	a2,0(a4)
800023fe:	fd078493          	addi	s1,a5,-48
80002402:	fd060793          	addi	a5,a2,-48
80002406:	86b2                	mv	a3,a2
80002408:	fef573e3          	bgeu	a0,a5,800023ee <vprintfmt+0xf6>
8000240c:	f40c57e3          	bgez	s8,8000235a <vprintfmt+0x62>
80002410:	8c26                	mv	s8,s1
80002412:	54fd                	li	s1,-1
80002414:	b799                	j	8000235a <vprintfmt+0x62>
80002416:	13612823          	sw	s6,304(sp)
8000241a:	4bc1                	li	s7,16
8000241c:	4d01                	li	s10,0
8000241e:	4785                	li	a5,1
80002420:	1eb7cb63          	blt	a5,a1,80002616 <vprintfmt+0x31e>
80002424:	47b2                	lw	a5,12(sp)
80002426:	00478713          	addi	a4,a5,4
8000242a:	47b2                	lw	a5,12(sp)
8000242c:	4c81                	li	s9,0
8000242e:	4384                	lw	s1,0(a5)
80002430:	c63a                	sw	a4,12(sp)
80002432:	865e                	mv	a2,s7
80002434:	4681                	li	a3,0
80002436:	8526                	mv	a0,s1
80002438:	85e6                	mv	a1,s9
8000243a:	23b000ef          	jal	80002e74 <__umoddi3>
8000243e:	c82a                	sw	a0,16(sp)
80002440:	1f9d0563          	beq	s10,s9,8000262a <vprintfmt+0x332>
80002444:	11b12e23          	sw	s11,284(sp)
80002448:	4b05                	li	s6,1
8000244a:	01410d93          	addi	s11,sp,20
8000244e:	8526                	mv	a0,s1
80002450:	85e6                	mv	a1,s9
80002452:	865e                	mv	a2,s7
80002454:	4681                	li	a3,0
80002456:	25d1                	jal	80002b1a <__udivdi3>
80002458:	865e                	mv	a2,s7
8000245a:	4681                	li	a3,0
8000245c:	84aa                	mv	s1,a0
8000245e:	8cae                	mv	s9,a1
80002460:	215000ef          	jal	80002e74 <__umoddi3>
80002464:	00ada023          	sw	a0,0(s11)
80002468:	8a5a                	mv	s4,s6
8000246a:	0d91                	addi	s11,s11,4
8000246c:	0b05                	addi	s6,s6,1
8000246e:	ff9d10e3          	bne	s10,s9,8000244e <vprintfmt+0x156>
80002472:	fd74fee3          	bgeu	s1,s7,8000244e <vprintfmt+0x156>
80002476:	11c12d83          	lw	s11,284(sp)
8000247a:	fffc0b93          	addi	s7,s8,-1
8000247e:	fffb0493          	addi	s1,s6,-1
80002482:	018b5863          	bge	s6,s8,80002492 <vprintfmt+0x19a>
80002486:	4522                	lw	a0,8(sp)
80002488:	85ca                	mv	a1,s2
8000248a:	1bfd                	addi	s7,s7,-1
8000248c:	9982                	jalr	s3
8000248e:	fe9b9ce3          	bne	s7,s1,80002486 <vprintfmt+0x18e>
80002492:	0a0a                	slli	s4,s4,0x2
80002494:	0804                	addi	s1,sp,16
80002496:	9a26                	add	s4,s4,s1
80002498:	4b25                	li	s6,9
8000249a:	a011                	j	8000249e <vprintfmt+0x1a6>
8000249c:	8a3e                	mv	s4,a5
8000249e:	000a2783          	lw	a5,0(s4)
800024a2:	03000513          	li	a0,48
800024a6:	00fb7463          	bgeu	s6,a5,800024ae <vprintfmt+0x1b6>
800024aa:	05700513          	li	a0,87
800024ae:	953e                	add	a0,a0,a5
800024b0:	85ca                	mv	a1,s2
800024b2:	9982                	jalr	s3
800024b4:	ffca0793          	addi	a5,s4,-4
800024b8:	ff4492e3          	bne	s1,s4,8000249c <vprintfmt+0x1a4>
800024bc:	13012b03          	lw	s6,304(sp)
800024c0:	bdb5                	j	8000233c <vprintfmt+0x44>
800024c2:	47b2                	lw	a5,12(sp)
800024c4:	0007aa03          	lw	s4,0(a5)
800024c8:	040a0a63          	beqz	s4,8000251c <vprintfmt+0x224>
800024cc:	09805c63          	blez	s8,80002564 <vprintfmt+0x26c>
800024d0:	4722                	lw	a4,8(sp)
800024d2:	02d00793          	li	a5,45
800024d6:	06f71063          	bne	a4,a5,80002536 <vprintfmt+0x23e>
800024da:	000a4503          	lbu	a0,0(s4)
800024de:	c505                	beqz	a0,80002506 <vprintfmt+0x20e>
800024e0:	13612823          	sw	s6,304(sp)
800024e4:	5b7d                	li	s6,-1
800024e6:	0004c563          	bltz	s1,800024f0 <vprintfmt+0x1f8>
800024ea:	14fd                	addi	s1,s1,-1
800024ec:	01648963          	beq	s1,s6,800024fe <vprintfmt+0x206>
800024f0:	85ca                	mv	a1,s2
800024f2:	9982                	jalr	s3
800024f4:	001a4503          	lbu	a0,1(s4)
800024f8:	0a05                	addi	s4,s4,1
800024fa:	1c7d                	addi	s8,s8,-1
800024fc:	f56d                	bnez	a0,800024e6 <vprintfmt+0x1ee>
800024fe:	13012b03          	lw	s6,304(sp)
80002502:	01805963          	blez	s8,80002514 <vprintfmt+0x21c>
80002506:	85ca                	mv	a1,s2
80002508:	02000513          	li	a0,32
8000250c:	1c7d                	addi	s8,s8,-1
8000250e:	9982                	jalr	s3
80002510:	fe0c1be3          	bnez	s8,80002506 <vprintfmt+0x20e>
80002514:	47b2                	lw	a5,12(sp)
80002516:	0791                	addi	a5,a5,4
80002518:	c63e                	sw	a5,12(sp)
8000251a:	b50d                	j	8000233c <vprintfmt+0x44>
8000251c:	15805063          	blez	s8,8000265c <vprintfmt+0x364>
80002520:	4722                	lw	a4,8(sp)
80002522:	02d00793          	li	a5,45
80002526:	00002a17          	auipc	s4,0x2
8000252a:	846a0a13          	addi	s4,s4,-1978 # 80003d6c <main+0xbd6>
8000252e:	02800513          	li	a0,40
80002532:	faf707e3          	beq	a4,a5,800024e0 <vprintfmt+0x1e8>
80002536:	87d2                	mv	a5,s4
80002538:	009a06b3          	add	a3,s4,s1
8000253c:	e489                	bnez	s1,80002546 <vprintfmt+0x24e>
8000253e:	a829                	j	80002558 <vprintfmt+0x260>
80002540:	0785                	addi	a5,a5,1
80002542:	00d78563          	beq	a5,a3,8000254c <vprintfmt+0x254>
80002546:	0007c703          	lbu	a4,0(a5)
8000254a:	fb7d                	bnez	a4,80002540 <vprintfmt+0x248>
8000254c:	414787b3          	sub	a5,a5,s4
80002550:	40fc0c33          	sub	s8,s8,a5
80002554:	01805863          	blez	s8,80002564 <vprintfmt+0x26c>
80002558:	4522                	lw	a0,8(sp)
8000255a:	85ca                	mv	a1,s2
8000255c:	1c7d                	addi	s8,s8,-1
8000255e:	9982                	jalr	s3
80002560:	fe0c1ce3          	bnez	s8,80002558 <vprintfmt+0x260>
80002564:	000a4503          	lbu	a0,0(s4)
80002568:	d555                	beqz	a0,80002514 <vprintfmt+0x21c>
8000256a:	13612823          	sw	s6,304(sp)
8000256e:	bf9d                	j	800024e4 <vprintfmt+0x1ec>
80002570:	fffc4793          	not	a5,s8
80002574:	87fd                	srai	a5,a5,0x1f
80002576:	00174683          	lbu	a3,1(a4)
8000257a:	00fc7c33          	and	s8,s8,a5
8000257e:	8722                	mv	a4,s0
80002580:	bbe9                	j	8000235a <vprintfmt+0x62>
80002582:	00174683          	lbu	a3,1(a4)
80002586:	8722                	mv	a4,s0
80002588:	bbc9                	j	8000235a <vprintfmt+0x62>
8000258a:	85ca                	mv	a1,s2
8000258c:	02500513          	li	a0,37
80002590:	9982                	jalr	s3
80002592:	b36d                	j	8000233c <vprintfmt+0x44>
80002594:	47b2                	lw	a5,12(sp)
80002596:	00174683          	lbu	a3,1(a4)
8000259a:	8722                	mv	a4,s0
8000259c:	4384                	lw	s1,0(a5)
8000259e:	0791                	addi	a5,a5,4
800025a0:	c63e                	sw	a5,12(sp)
800025a2:	b5ad                	j	8000240c <vprintfmt+0x114>
800025a4:	47b2                	lw	a5,12(sp)
800025a6:	85ca                	mv	a1,s2
800025a8:	4388                	lw	a0,0(a5)
800025aa:	00478493          	addi	s1,a5,4
800025ae:	9982                	jalr	s3
800025b0:	c626                	sw	s1,12(sp)
800025b2:	b369                	j	8000233c <vprintfmt+0x44>
800025b4:	13612823          	sw	s6,304(sp)
800025b8:	4785                	li	a5,1
800025ba:	06b7cd63          	blt	a5,a1,80002634 <vprintfmt+0x33c>
800025be:	47b2                	lw	a5,12(sp)
800025c0:	4384                	lw	s1,0(a5)
800025c2:	0791                	addi	a5,a5,4
800025c4:	c63e                	sw	a5,12(sp)
800025c6:	41f4dc93          	srai	s9,s1,0x1f
800025ca:	000cde63          	bgez	s9,800025e6 <vprintfmt+0x2ee>
800025ce:	85ca                	mv	a1,s2
800025d0:	02d00513          	li	a0,45
800025d4:	9982                	jalr	s3
800025d6:	00903733          	snez	a4,s1
800025da:	419007b3          	neg	a5,s9
800025de:	40e78cb3          	sub	s9,a5,a4
800025e2:	409004b3          	neg	s1,s1
800025e6:	4ba9                	li	s7,10
800025e8:	4d01                	li	s10,0
800025ea:	b5a1                	j	80002432 <vprintfmt+0x13a>
800025ec:	00174683          	lbu	a3,1(a4)
800025f0:	0585                	addi	a1,a1,1
800025f2:	8722                	mv	a4,s0
800025f4:	b39d                	j	8000235a <vprintfmt+0x62>
800025f6:	85ca                	mv	a1,s2
800025f8:	03000513          	li	a0,48
800025fc:	13612823          	sw	s6,304(sp)
80002600:	9982                	jalr	s3
80002602:	85ca                	mv	a1,s2
80002604:	07800513          	li	a0,120
80002608:	9982                	jalr	s3
8000260a:	47b2                	lw	a5,12(sp)
8000260c:	4bc1                	li	s7,16
8000260e:	4d01                	li	s10,0
80002610:	00478713          	addi	a4,a5,4
80002614:	bd19                	j	8000242a <vprintfmt+0x132>
80002616:	47b2                	lw	a5,12(sp)
80002618:	079d                	addi	a5,a5,7
8000261a:	9be1                	andi	a5,a5,-8
8000261c:	00878713          	addi	a4,a5,8
80002620:	4384                	lw	s1,0(a5)
80002622:	0047ac83          	lw	s9,4(a5)
80002626:	c63a                	sw	a4,12(sp)
80002628:	b529                	j	80002432 <vprintfmt+0x13a>
8000262a:	e174fde3          	bgeu	s1,s7,80002444 <vprintfmt+0x14c>
8000262e:	4a01                	li	s4,0
80002630:	4b05                	li	s6,1
80002632:	b5a1                	j	8000247a <vprintfmt+0x182>
80002634:	47b2                	lw	a5,12(sp)
80002636:	079d                	addi	a5,a5,7
80002638:	9be1                	andi	a5,a5,-8
8000263a:	00878713          	addi	a4,a5,8
8000263e:	4384                	lw	s1,0(a5)
80002640:	0047ac83          	lw	s9,4(a5)
80002644:	c63a                	sw	a4,12(sp)
80002646:	b751                	j	800025ca <vprintfmt+0x2d2>
80002648:	13612823          	sw	s6,304(sp)
8000264c:	4ba9                	li	s7,10
8000264e:	4d01                	li	s10,0
80002650:	b3f9                	j	8000241e <vprintfmt+0x126>
80002652:	13612823          	sw	s6,304(sp)
80002656:	4ba1                	li	s7,8
80002658:	4d01                	li	s10,0
8000265a:	b3d1                	j	8000241e <vprintfmt+0x126>
8000265c:	13612823          	sw	s6,304(sp)
80002660:	00001a17          	auipc	s4,0x1
80002664:	70ca0a13          	addi	s4,s4,1804 # 80003d6c <main+0xbd6>
80002668:	02800513          	li	a0,40
8000266c:	5b7d                	li	s6,-1
8000266e:	bda5                	j	800024e6 <vprintfmt+0x1ee>

80002670 <sprintf_putch.0>:
80002670:	419c                	lw	a5,0(a1)
80002672:	00a78023          	sb	a0,0(a5)
80002676:	419c                	lw	a5,0(a1)
80002678:	0785                	addi	a5,a5,1
8000267a:	c19c                	sw	a5,0(a1)
8000267c:	8082                	ret

8000267e <putchar>:
8000267e:	04022783          	lw	a5,64(tp) # 40 <buflen.1>
80002682:	00020713          	mv	a4,tp
80002686:	7119                	addi	sp,sp,-128
80002688:	973e                	add	a4,a4,a5
8000268a:	0785                	addi	a5,a5,1
8000268c:	00a70023          	sb	a0,0(a4)
80002690:	04f22023          	sw	a5,64(tp) # 40 <buflen.1>
80002694:	4729                	li	a4,10
80002696:	03f10693          	addi	a3,sp,63
8000269a:	fc06f693          	andi	a3,a3,-64
8000269e:	00e50963          	beq	a0,a4,800026b0 <putchar+0x32>
800026a2:	04000713          	li	a4,64
800026a6:	00e78563          	beq	a5,a4,800026b0 <putchar+0x32>
800026aa:	4501                	li	a0,0
800026ac:	6109                	addi	sp,sp,128
800026ae:	8082                	ret
800026b0:	04000813          	li	a6,64
800026b4:	0106a023          	sw	a6,0(a3)
800026b8:	4881                	li	a7,0
800026ba:	0116a223          	sw	a7,4(a3)
800026be:	4e05                	li	t3,1
800026c0:	01c6a423          	sw	t3,8(a3)
800026c4:	4e81                	li	t4,0
800026c6:	01d6a623          	sw	t4,12(a3)
800026ca:	00020313          	mv	t1,tp
800026ce:	0066a823          	sw	t1,16(a3)
800026d2:	4381                	li	t2,0
800026d4:	0076aa23          	sw	t2,20(a3)
800026d8:	ce9c                	sw	a5,24(a3)
800026da:	41f7d893          	srai	a7,a5,0x1f
800026de:	0116ae23          	sw	a7,28(a3)
800026e2:	0330000f          	fence	rw,rw
800026e6:	fffff617          	auipc	a2,0xfffff
800026ea:	91a60613          	addi	a2,a2,-1766 # 80001000 <tohost>
800026ee:	c214                	sw	a3,0(a2)
800026f0:	4781                	li	a5,0
800026f2:	c25c                	sw	a5,4(a2)
800026f4:	fffff617          	auipc	a2,0xfffff
800026f8:	94c60613          	addi	a2,a2,-1716 # 80001040 <fromhost>
800026fc:	4218                	lw	a4,0(a2)
800026fe:	425c                	lw	a5,4(a2)
80002700:	8f5d                	or	a4,a4,a5
80002702:	df6d                	beqz	a4,800026fc <putchar+0x7e>
80002704:	4781                	li	a5,0
80002706:	c21c                	sw	a5,0(a2)
80002708:	4801                	li	a6,0
8000270a:	01062223          	sw	a6,4(a2)
8000270e:	0330000f          	fence	rw,rw
80002712:	04022023          	sw	zero,64(tp) # 40 <buflen.1>
80002716:	4298                	lw	a4,0(a3)
80002718:	4501                	li	a0,0
8000271a:	42dc                	lw	a5,4(a3)
8000271c:	6109                	addi	sp,sp,128
8000271e:	8082                	ret

80002720 <setStats>:
80002720:	b0002773          	csrr	a4,mcycle
80002724:	00002797          	auipc	a5,0x2
80002728:	9fc78793          	addi	a5,a5,-1540 # 80004120 <counters>
8000272c:	c511                	beqz	a0,80002738 <setStats+0x18>
8000272e:	c398                	sw	a4,0(a5)
80002730:	b0202773          	csrr	a4,minstret
80002734:	c3d8                	sw	a4,4(a5)
80002736:	8082                	ret
80002738:	438c                	lw	a1,0(a5)
8000273a:	00002697          	auipc	a3,0x2
8000273e:	9de68693          	addi	a3,a3,-1570 # 80004118 <counter_names>
80002742:	00001617          	auipc	a2,0x1
80002746:	63260613          	addi	a2,a2,1586 # 80003d74 <main+0xbde>
8000274a:	8f0d                	sub	a4,a4,a1
8000274c:	c398                	sw	a4,0(a5)
8000274e:	c290                	sw	a2,0(a3)
80002750:	b0202773          	csrr	a4,minstret
80002754:	43d0                	lw	a2,4(a5)
80002756:	00001597          	auipc	a1,0x1
8000275a:	62658593          	addi	a1,a1,1574 # 80003d7c <main+0xbe6>
8000275e:	c2cc                	sw	a1,4(a3)
80002760:	8f11                	sub	a4,a4,a2
80002762:	c3d8                	sw	a4,4(a5)
80002764:	8082                	ret

80002766 <tohost_exit>:
80002766:	00151693          	slli	a3,a0,0x1
8000276a:	0016e713          	ori	a4,a3,1
8000276e:	fffff697          	auipc	a3,0xfffff
80002772:	89268693          	addi	a3,a3,-1902 # 80001000 <tohost>
80002776:	4781                	li	a5,0
80002778:	c298                	sw	a4,0(a3)
8000277a:	c2dc                	sw	a5,4(a3)
8000277c:	a001                	j	8000277c <tohost_exit+0x16>

8000277e <handle_trap>:
8000277e:	6605                	lui	a2,0x1
80002780:	fffff797          	auipc	a5,0xfffff
80002784:	88078793          	addi	a5,a5,-1920 # 80001000 <tohost>
80002788:	a7360613          	addi	a2,a2,-1421 # a73 <_tbss_end+0xa2f>
8000278c:	4681                	li	a3,0
8000278e:	c390                	sw	a2,0(a5)
80002790:	c3d4                	sw	a3,4(a5)
80002792:	a001                	j	80002792 <handle_trap+0x14>

80002794 <exit>:
80002794:	1141                	addi	sp,sp,-16
80002796:	c606                	sw	ra,12(sp)
80002798:	37f9                	jal	80002766 <tohost_exit>

8000279a <abort>:
8000279a:	fffff797          	auipc	a5,0xfffff
8000279e:	86678793          	addi	a5,a5,-1946 # 80001000 <tohost>
800027a2:	10d00613          	li	a2,269
800027a6:	4681                	li	a3,0
800027a8:	c390                	sw	a2,0(a5)
800027aa:	c3d4                	sw	a3,4(a5)
800027ac:	a001                	j	800027ac <abort+0x12>

800027ae <printstr>:
800027ae:	00054783          	lbu	a5,0(a0)
800027b2:	7119                	addi	sp,sp,-128
800027b4:	03f10613          	addi	a2,sp,63
800027b8:	882a                	mv	a6,a0
800027ba:	4881                	li	a7,0
800027bc:	fc067613          	andi	a2,a2,-64
800027c0:	c7b5                	beqz	a5,8000282c <printstr+0x7e>
800027c2:	87aa                	mv	a5,a0
800027c4:	0017c703          	lbu	a4,1(a5)
800027c8:	0785                	addi	a5,a5,1
800027ca:	ff6d                	bnez	a4,800027c4 <printstr+0x16>
800027cc:	40a78333          	sub	t1,a5,a0
800027d0:	4381                	li	t2,0
800027d2:	04000713          	li	a4,64
800027d6:	c218                	sw	a4,0(a2)
800027d8:	4781                	li	a5,0
800027da:	c25c                	sw	a5,4(a2)
800027dc:	4705                	li	a4,1
800027de:	c618                	sw	a4,8(a2)
800027e0:	4781                	li	a5,0
800027e2:	c65c                	sw	a5,12(a2)
800027e4:	01062823          	sw	a6,16(a2)
800027e8:	01162a23          	sw	a7,20(a2)
800027ec:	00662c23          	sw	t1,24(a2)
800027f0:	00762e23          	sw	t2,28(a2)
800027f4:	0330000f          	fence	rw,rw
800027f8:	fffff697          	auipc	a3,0xfffff
800027fc:	80868693          	addi	a3,a3,-2040 # 80001000 <tohost>
80002800:	c290                	sw	a2,0(a3)
80002802:	4781                	li	a5,0
80002804:	c2dc                	sw	a5,4(a3)
80002806:	fffff697          	auipc	a3,0xfffff
8000280a:	83a68693          	addi	a3,a3,-1990 # 80001040 <fromhost>
8000280e:	4298                	lw	a4,0(a3)
80002810:	42dc                	lw	a5,4(a3)
80002812:	8f5d                	or	a4,a4,a5
80002814:	df6d                	beqz	a4,8000280e <printstr+0x60>
80002816:	4781                	li	a5,0
80002818:	c29c                	sw	a5,0(a3)
8000281a:	4801                	li	a6,0
8000281c:	0106a223          	sw	a6,4(a3)
80002820:	0330000f          	fence	rw,rw
80002824:	4218                	lw	a4,0(a2)
80002826:	425c                	lw	a5,4(a2)
80002828:	6109                	addi	sp,sp,128
8000282a:	8082                	ret
8000282c:	4301                	li	t1,0
8000282e:	4381                	li	t2,0
80002830:	b74d                	j	800027d2 <printstr+0x24>

80002832 <thread_entry>:
80002832:	e111                	bnez	a0,80002836 <thread_entry+0x4>
80002834:	8082                	ret
80002836:	a001                	j	80002836 <thread_entry+0x4>

80002838 <printhex>:
80002838:	7179                	addi	sp,sp,-48
8000283a:	872a                	mv	a4,a0
8000283c:	d606                	sw	ra,44(sp)
8000283e:	0068                	addi	a0,sp,12
80002840:	01b10613          	addi	a2,sp,27
80002844:	4825                	li	a6,9
80002846:	a011                	j	8000284a <printhex+0x12>
80002848:	863e                	mv	a2,a5
8000284a:	00f77793          	andi	a5,a4,15
8000284e:	00f837b3          	sltu	a5,a6,a5
80002852:	40f007b3          	neg	a5,a5
80002856:	0277f793          	andi	a5,a5,39
8000285a:	00f77693          	andi	a3,a4,15
8000285e:	03078793          	addi	a5,a5,48
80002862:	97b6                	add	a5,a5,a3
80002864:	00f60023          	sb	a5,0(a2)
80002868:	8311                	srli	a4,a4,0x4
8000286a:	01c59793          	slli	a5,a1,0x1c
8000286e:	8f5d                	or	a4,a4,a5
80002870:	8191                	srli	a1,a1,0x4
80002872:	fff60793          	addi	a5,a2,-1
80002876:	fcc519e3          	bne	a0,a2,80002848 <printhex+0x10>
8000287a:	00010e23          	sb	zero,28(sp)
8000287e:	3f05                	jal	800027ae <printstr>
80002880:	50b2                	lw	ra,44(sp)
80002882:	6145                	addi	sp,sp,48
80002884:	8082                	ret

80002886 <printf>:
80002886:	7139                	addi	sp,sp,-64
80002888:	02410313          	addi	t1,sp,36
8000288c:	d22e                	sw	a1,36(sp)
8000288e:	d432                	sw	a2,40(sp)
80002890:	d636                	sw	a3,44(sp)
80002892:	862a                	mv	a2,a0
80002894:	869a                	mv	a3,t1
80002896:	00000517          	auipc	a0,0x0
8000289a:	de850513          	addi	a0,a0,-536 # 8000267e <putchar>
8000289e:	4581                	li	a1,0
800028a0:	ce06                	sw	ra,28(sp)
800028a2:	d83a                	sw	a4,48(sp)
800028a4:	da3e                	sw	a5,52(sp)
800028a6:	dc42                	sw	a6,56(sp)
800028a8:	de46                	sw	a7,60(sp)
800028aa:	c61a                	sw	t1,12(sp)
800028ac:	34b1                	jal	800022f8 <vprintfmt>
800028ae:	40f2                	lw	ra,28(sp)
800028b0:	4501                	li	a0,0
800028b2:	6121                	addi	sp,sp,64
800028b4:	8082                	ret

800028b6 <puts>:
800028b6:	1141                	addi	sp,sp,-16
800028b8:	c606                	sw	ra,12(sp)
800028ba:	37f1                	jal	80002886 <printf>
800028bc:	4529                	li	a0,10
800028be:	33c1                	jal	8000267e <putchar>
800028c0:	40b2                	lw	ra,12(sp)
800028c2:	4501                	li	a0,0
800028c4:	0141                	addi	sp,sp,16
800028c6:	8082                	ret

800028c8 <sprintf>:
800028c8:	715d                	addi	sp,sp,-80
800028ca:	03810313          	addi	t1,sp,56
800028ce:	d422                	sw	s0,40(sp)
800028d0:	c62a                	sw	a0,12(sp)
800028d2:	dc32                	sw	a2,56(sp)
800028d4:	de36                	sw	a3,60(sp)
800028d6:	842a                	mv	s0,a0
800028d8:	862e                	mv	a2,a1
800028da:	00000517          	auipc	a0,0x0
800028de:	d9650513          	addi	a0,a0,-618 # 80002670 <sprintf_putch.0>
800028e2:	006c                	addi	a1,sp,12
800028e4:	869a                	mv	a3,t1
800028e6:	d606                	sw	ra,44(sp)
800028e8:	c2be                	sw	a5,68(sp)
800028ea:	c0ba                	sw	a4,64(sp)
800028ec:	c4c2                	sw	a6,72(sp)
800028ee:	c6c6                	sw	a7,76(sp)
800028f0:	ce1a                	sw	t1,28(sp)
800028f2:	3419                	jal	800022f8 <vprintfmt>
800028f4:	47b2                	lw	a5,12(sp)
800028f6:	00078023          	sb	zero,0(a5)
800028fa:	4532                	lw	a0,12(sp)
800028fc:	50b2                	lw	ra,44(sp)
800028fe:	8d01                	sub	a0,a0,s0
80002900:	5422                	lw	s0,40(sp)
80002902:	6161                	addi	sp,sp,80
80002904:	8082                	ret

80002906 <memcpy>:
80002906:	00c5e7b3          	or	a5,a1,a2
8000290a:	8fc9                	or	a5,a5,a0
8000290c:	8b8d                	andi	a5,a5,3
8000290e:	00c506b3          	add	a3,a0,a2
80002912:	cf91                	beqz	a5,8000292e <memcpy+0x28>
80002914:	962e                	add	a2,a2,a1
80002916:	87aa                	mv	a5,a0
80002918:	02d57663          	bgeu	a0,a3,80002944 <memcpy+0x3e>
8000291c:	0005c703          	lbu	a4,0(a1)
80002920:	0585                	addi	a1,a1,1
80002922:	0785                	addi	a5,a5,1
80002924:	fee78fa3          	sb	a4,-1(a5)
80002928:	feb61ae3          	bne	a2,a1,8000291c <memcpy+0x16>
8000292c:	8082                	ret
8000292e:	fed57fe3          	bgeu	a0,a3,8000292c <memcpy+0x26>
80002932:	87aa                	mv	a5,a0
80002934:	4198                	lw	a4,0(a1)
80002936:	0791                	addi	a5,a5,4
80002938:	0591                	addi	a1,a1,4
8000293a:	fee7ae23          	sw	a4,-4(a5)
8000293e:	fed7ebe3          	bltu	a5,a3,80002934 <memcpy+0x2e>
80002942:	8082                	ret
80002944:	8082                	ret

80002946 <memset>:
80002946:	00c567b3          	or	a5,a0,a2
8000294a:	8b8d                	andi	a5,a5,3
8000294c:	962a                	add	a2,a2,a0
8000294e:	cf81                	beqz	a5,80002966 <memset+0x20>
80002950:	0ff5f593          	zext.b	a1,a1
80002954:	87aa                	mv	a5,a0
80002956:	02c57963          	bgeu	a0,a2,80002988 <memset+0x42>
8000295a:	0785                	addi	a5,a5,1
8000295c:	feb78fa3          	sb	a1,-1(a5)
80002960:	fef61de3          	bne	a2,a5,8000295a <memset+0x14>
80002964:	8082                	ret
80002966:	0ff5f593          	zext.b	a1,a1
8000296a:	00859713          	slli	a4,a1,0x8
8000296e:	972e                	add	a4,a4,a1
80002970:	01071793          	slli	a5,a4,0x10
80002974:	973e                	add	a4,a4,a5
80002976:	fec577e3          	bgeu	a0,a2,80002964 <memset+0x1e>
8000297a:	87aa                	mv	a5,a0
8000297c:	0791                	addi	a5,a5,4
8000297e:	fee7ae23          	sw	a4,-4(a5)
80002982:	fec7ede3          	bltu	a5,a2,8000297c <memset+0x36>
80002986:	8082                	ret
80002988:	8082                	ret

8000298a <_init>:
8000298a:	7135                	addi	sp,sp,-160
8000298c:	cd22                	sw	s0,152(sp)
8000298e:	cb26                	sw	s1,148(sp)
80002990:	00001417          	auipc	s0,0x1
80002994:	74042403          	lw	s0,1856(s0) # 800040d0 <_GLOBAL_OFFSET_TABLE_+0x8>
80002998:	00001497          	auipc	s1,0x1
8000299c:	7344a483          	lw	s1,1844(s1) # 800040cc <_GLOBAL_OFFSET_TABLE_+0x4>
800029a0:	c74e                	sw	s3,140(sp)
800029a2:	c552                	sw	s4,136(sp)
800029a4:	40848433          	sub	s0,s1,s0
800029a8:	8622                	mv	a2,s0
800029aa:	89aa                	mv	s3,a0
800029ac:	8a2e                	mv	s4,a1
800029ae:	8512                	mv	a0,tp
800029b0:	02018593          	addi	a1,gp,32 # 80004900 <_end>
800029b4:	cf06                	sw	ra,156(sp)
800029b6:	c94a                	sw	s2,144(sp)
800029b8:	c356                	sw	s5,132(sp)
800029ba:	8a92                	mv	s5,tp
800029bc:	37a9                	jal	80002906 <memcpy>
800029be:	00001617          	auipc	a2,0x1
800029c2:	71662603          	lw	a2,1814(a2) # 800040d4 <_GLOBAL_OFFSET_TABLE_+0xc>
800029c6:	008a8533          	add	a0,s5,s0
800029ca:	4581                	li	a1,0
800029cc:	8e05                	sub	a2,a2,s1
800029ce:	3fa5                	jal	80002946 <memset>
800029d0:	85d2                	mv	a1,s4
800029d2:	854e                	mv	a0,s3
800029d4:	3db9                	jal	80002832 <thread_entry>
800029d6:	4581                	li	a1,0
800029d8:	4501                	li	a0,0
800029da:	7bc000ef          	jal	80003196 <main>
800029de:	00001497          	auipc	s1,0x1
800029e2:	74248493          	addi	s1,s1,1858 # 80004120 <counters>
800029e6:	4094                	lw	a3,0(s1)
800029e8:	03f10913          	addi	s2,sp,63
800029ec:	fc097913          	andi	s2,s2,-64
800029f0:	842a                	mv	s0,a0
800029f2:	ea85                	bnez	a3,80002a22 <_init+0x98>
800029f4:	40d4                	lw	a3,4(s1)
800029f6:	e299                	bnez	a3,800029fc <_init+0x72>
800029f8:	8522                	mv	a0,s0
800029fa:	33b5                	jal	80002766 <tohost_exit>
800029fc:	84ca                	mv	s1,s2
800029fe:	00001997          	auipc	s3,0x1
80002a02:	71a98993          	addi	s3,s3,1818 # 80004118 <counter_names>
80002a06:	0049a603          	lw	a2,4(s3)
80002a0a:	8526                	mv	a0,s1
80002a0c:	00001597          	auipc	a1,0x1
80002a10:	39458593          	addi	a1,a1,916 # 80003da0 <main+0xc0a>
80002a14:	3d55                	jal	800028c8 <sprintf>
80002a16:	94aa                	add	s1,s1,a0
80002a18:	fe9900e3          	beq	s2,s1,800029f8 <_init+0x6e>
80002a1c:	854a                	mv	a0,s2
80002a1e:	3b41                	jal	800027ae <printstr>
80002a20:	bfe1                	j	800029f8 <_init+0x6e>
80002a22:	00001997          	auipc	s3,0x1
80002a26:	6f698993          	addi	s3,s3,1782 # 80004118 <counter_names>
80002a2a:	0009a603          	lw	a2,0(s3)
80002a2e:	00001597          	auipc	a1,0x1
80002a32:	37258593          	addi	a1,a1,882 # 80003da0 <main+0xc0a>
80002a36:	854a                	mv	a0,s2
80002a38:	3d41                	jal	800028c8 <sprintf>
80002a3a:	40d4                	lw	a3,4(s1)
80002a3c:	00a904b3          	add	s1,s2,a0
80002a40:	dee1                	beqz	a3,80002a18 <_init+0x8e>
80002a42:	b7d1                	j	80002a06 <_init+0x7c>

80002a44 <strlen>:
80002a44:	00054783          	lbu	a5,0(a0)
80002a48:	cb89                	beqz	a5,80002a5a <strlen+0x16>
80002a4a:	87aa                	mv	a5,a0
80002a4c:	0017c703          	lbu	a4,1(a5)
80002a50:	0785                	addi	a5,a5,1
80002a52:	ff6d                	bnez	a4,80002a4c <strlen+0x8>
80002a54:	40a78533          	sub	a0,a5,a0
80002a58:	8082                	ret
80002a5a:	4501                	li	a0,0
80002a5c:	8082                	ret

80002a5e <strnlen>:
80002a5e:	00b506b3          	add	a3,a0,a1
80002a62:	87aa                	mv	a5,a0
80002a64:	e589                	bnez	a1,80002a6e <strnlen+0x10>
80002a66:	a811                	j	80002a7a <strnlen+0x1c>
80002a68:	0785                	addi	a5,a5,1
80002a6a:	00d78563          	beq	a5,a3,80002a74 <strnlen+0x16>
80002a6e:	0007c703          	lbu	a4,0(a5)
80002a72:	fb7d                	bnez	a4,80002a68 <strnlen+0xa>
80002a74:	40a78533          	sub	a0,a5,a0
80002a78:	8082                	ret
80002a7a:	4501                	li	a0,0
80002a7c:	8082                	ret

80002a7e <strcmp>:
80002a7e:	00054783          	lbu	a5,0(a0)
80002a82:	0505                	addi	a0,a0,1
80002a84:	0585                	addi	a1,a1,1
80002a86:	fff5c703          	lbu	a4,-1(a1)
80002a8a:	c791                	beqz	a5,80002a96 <strcmp+0x18>
80002a8c:	fee789e3          	beq	a5,a4,80002a7e <strcmp>
80002a90:	40e78533          	sub	a0,a5,a4
80002a94:	8082                	ret
80002a96:	4781                	li	a5,0
80002a98:	bfe5                	j	80002a90 <strcmp+0x12>

80002a9a <strcpy>:
80002a9a:	87aa                	mv	a5,a0
80002a9c:	0005c703          	lbu	a4,0(a1)
80002aa0:	0585                	addi	a1,a1,1
80002aa2:	0785                	addi	a5,a5,1
80002aa4:	fee78fa3          	sb	a4,-1(a5)
80002aa8:	fb75                	bnez	a4,80002a9c <strcpy+0x2>
80002aaa:	8082                	ret

80002aac <atol>:
80002aac:	00054703          	lbu	a4,0(a0)
80002ab0:	02000693          	li	a3,32
80002ab4:	87aa                	mv	a5,a0
80002ab6:	00d71863          	bne	a4,a3,80002ac6 <atol+0x1a>
80002aba:	86ba                	mv	a3,a4
80002abc:	0017c703          	lbu	a4,1(a5)
80002ac0:	0785                	addi	a5,a5,1
80002ac2:	fed70de3          	beq	a4,a3,80002abc <atol+0x10>
80002ac6:	02d00693          	li	a3,45
80002aca:	04d70163          	beq	a4,a3,80002b0c <atol+0x60>
80002ace:	02b00693          	li	a3,43
80002ad2:	02d70763          	beq	a4,a3,80002b00 <atol+0x54>
80002ad6:	0007c683          	lbu	a3,0(a5)
80002ada:	4581                	li	a1,0
80002adc:	ce8d                	beqz	a3,80002b16 <atol+0x6a>
80002ade:	4501                	li	a0,0
80002ae0:	0785                	addi	a5,a5,1
80002ae2:	fd068613          	addi	a2,a3,-48
80002ae6:	00251713          	slli	a4,a0,0x2
80002aea:	0007c683          	lbu	a3,0(a5)
80002aee:	972a                	add	a4,a4,a0
80002af0:	0706                	slli	a4,a4,0x1
80002af2:	00e60533          	add	a0,a2,a4
80002af6:	f6ed                	bnez	a3,80002ae0 <atol+0x34>
80002af8:	c185                	beqz	a1,80002b18 <atol+0x6c>
80002afa:	40a00533          	neg	a0,a0
80002afe:	8082                	ret
80002b00:	0017c683          	lbu	a3,1(a5)
80002b04:	0785                	addi	a5,a5,1
80002b06:	ca81                	beqz	a3,80002b16 <atol+0x6a>
80002b08:	4581                	li	a1,0
80002b0a:	bfd1                	j	80002ade <atol+0x32>
80002b0c:	0017c683          	lbu	a3,1(a5)
80002b10:	4585                	li	a1,1
80002b12:	97ae                	add	a5,a5,a1
80002b14:	f6e9                	bnez	a3,80002ade <atol+0x32>
80002b16:	4501                	li	a0,0
80002b18:	8082                	ret

80002b1a <__udivdi3>:
80002b1a:	88aa                	mv	a7,a0
80002b1c:	832e                	mv	t1,a1
80002b1e:	8732                	mv	a4,a2
80002b20:	882a                	mv	a6,a0
80002b22:	87ae                	mv	a5,a1
80002b24:	20069663          	bnez	a3,80002d30 <__udivdi3+0x216>
80002b28:	800045b7          	lui	a1,0x80004
80002b2c:	f8058593          	addi	a1,a1,-128 # 80003f80 <__clz_tab>
80002b30:	0cc37163          	bgeu	t1,a2,80002bf2 <__udivdi3+0xd8>
80002b34:	66c1                	lui	a3,0x10
80002b36:	0ad67763          	bgeu	a2,a3,80002be4 <__udivdi3+0xca>
80002b3a:	10063693          	sltiu	a3,a2,256
80002b3e:	0016b693          	seqz	a3,a3
80002b42:	068e                	slli	a3,a3,0x3
80002b44:	00d65533          	srl	a0,a2,a3
80002b48:	95aa                	add	a1,a1,a0
80002b4a:	0005c583          	lbu	a1,0(a1)
80002b4e:	02000513          	li	a0,32
80002b52:	96ae                	add	a3,a3,a1
80002b54:	40d505b3          	sub	a1,a0,a3
80002b58:	00d50b63          	beq	a0,a3,80002b6e <__udivdi3+0x54>
80002b5c:	00b317b3          	sll	a5,t1,a1
80002b60:	00d8d6b3          	srl	a3,a7,a3
80002b64:	00b61733          	sll	a4,a2,a1
80002b68:	8fd5                	or	a5,a5,a3
80002b6a:	00b89833          	sll	a6,a7,a1
80002b6e:	01075593          	srli	a1,a4,0x10
80002b72:	02b7d333          	divu	t1,a5,a1
80002b76:	01071613          	slli	a2,a4,0x10
80002b7a:	8241                	srli	a2,a2,0x10
80002b7c:	02b7f7b3          	remu	a5,a5,a1
80002b80:	851a                	mv	a0,t1
80002b82:	026608b3          	mul	a7,a2,t1
80002b86:	01079693          	slli	a3,a5,0x10
80002b8a:	01085793          	srli	a5,a6,0x10
80002b8e:	8fd5                	or	a5,a5,a3
80002b90:	0117fc63          	bgeu	a5,a7,80002ba8 <__udivdi3+0x8e>
80002b94:	97ba                	add	a5,a5,a4
80002b96:	fff30513          	addi	a0,t1,-1
80002b9a:	00e7e763          	bltu	a5,a4,80002ba8 <__udivdi3+0x8e>
80002b9e:	0117f563          	bgeu	a5,a7,80002ba8 <__udivdi3+0x8e>
80002ba2:	ffe30513          	addi	a0,t1,-2
80002ba6:	97ba                	add	a5,a5,a4
80002ba8:	411787b3          	sub	a5,a5,a7
80002bac:	02b7d8b3          	divu	a7,a5,a1
80002bb0:	0842                	slli	a6,a6,0x10
80002bb2:	01085813          	srli	a6,a6,0x10
80002bb6:	02b7f7b3          	remu	a5,a5,a1
80002bba:	031606b3          	mul	a3,a2,a7
80002bbe:	07c2                	slli	a5,a5,0x10
80002bc0:	00f86833          	or	a6,a6,a5
80002bc4:	87c6                	mv	a5,a7
80002bc6:	00d87b63          	bgeu	a6,a3,80002bdc <__udivdi3+0xc2>
80002bca:	983a                	add	a6,a6,a4
80002bcc:	fff88793          	addi	a5,a7,-1
80002bd0:	00e86663          	bltu	a6,a4,80002bdc <__udivdi3+0xc2>
80002bd4:	00d87463          	bgeu	a6,a3,80002bdc <__udivdi3+0xc2>
80002bd8:	ffe88793          	addi	a5,a7,-2
80002bdc:	0542                	slli	a0,a0,0x10
80002bde:	8d5d                	or	a0,a0,a5
80002be0:	4581                	li	a1,0
80002be2:	8082                	ret
80002be4:	01000537          	lui	a0,0x1000
80002be8:	46e1                	li	a3,24
80002bea:	f4a67de3          	bgeu	a2,a0,80002b44 <__udivdi3+0x2a>
80002bee:	46c1                	li	a3,16
80002bf0:	bf91                	j	80002b44 <__udivdi3+0x2a>
80002bf2:	4681                	li	a3,0
80002bf4:	ca09                	beqz	a2,80002c06 <__udivdi3+0xec>
80002bf6:	67c1                	lui	a5,0x10
80002bf8:	08f67f63          	bgeu	a2,a5,80002c96 <__udivdi3+0x17c>
80002bfc:	10063693          	sltiu	a3,a2,256
80002c00:	0016b693          	seqz	a3,a3
80002c04:	068e                	slli	a3,a3,0x3
80002c06:	00d657b3          	srl	a5,a2,a3
80002c0a:	95be                	add	a1,a1,a5
80002c0c:	0005c783          	lbu	a5,0(a1)
80002c10:	97b6                	add	a5,a5,a3
80002c12:	02000693          	li	a3,32
80002c16:	40f685b3          	sub	a1,a3,a5
80002c1a:	08f69563          	bne	a3,a5,80002ca4 <__udivdi3+0x18a>
80002c1e:	40c307b3          	sub	a5,t1,a2
80002c22:	4585                	li	a1,1
80002c24:	01075893          	srli	a7,a4,0x10
80002c28:	0317de33          	divu	t3,a5,a7
80002c2c:	01071613          	slli	a2,a4,0x10
80002c30:	8241                	srli	a2,a2,0x10
80002c32:	01085693          	srli	a3,a6,0x10
80002c36:	0317f7b3          	remu	a5,a5,a7
80002c3a:	8572                	mv	a0,t3
80002c3c:	03c60333          	mul	t1,a2,t3
80002c40:	07c2                	slli	a5,a5,0x10
80002c42:	8fd5                	or	a5,a5,a3
80002c44:	0067fc63          	bgeu	a5,t1,80002c5c <__udivdi3+0x142>
80002c48:	97ba                	add	a5,a5,a4
80002c4a:	fffe0513          	addi	a0,t3,-1
80002c4e:	00e7e763          	bltu	a5,a4,80002c5c <__udivdi3+0x142>
80002c52:	0067f563          	bgeu	a5,t1,80002c5c <__udivdi3+0x142>
80002c56:	ffee0513          	addi	a0,t3,-2
80002c5a:	97ba                	add	a5,a5,a4
80002c5c:	406787b3          	sub	a5,a5,t1
80002c60:	0317d333          	divu	t1,a5,a7
80002c64:	0842                	slli	a6,a6,0x10
80002c66:	01085813          	srli	a6,a6,0x10
80002c6a:	0317f7b3          	remu	a5,a5,a7
80002c6e:	026606b3          	mul	a3,a2,t1
80002c72:	07c2                	slli	a5,a5,0x10
80002c74:	00f86833          	or	a6,a6,a5
80002c78:	879a                	mv	a5,t1
80002c7a:	00d87b63          	bgeu	a6,a3,80002c90 <__udivdi3+0x176>
80002c7e:	983a                	add	a6,a6,a4
80002c80:	fff30793          	addi	a5,t1,-1
80002c84:	00e86663          	bltu	a6,a4,80002c90 <__udivdi3+0x176>
80002c88:	00d87463          	bgeu	a6,a3,80002c90 <__udivdi3+0x176>
80002c8c:	ffe30793          	addi	a5,t1,-2
80002c90:	0542                	slli	a0,a0,0x10
80002c92:	8d5d                	or	a0,a0,a5
80002c94:	8082                	ret
80002c96:	010007b7          	lui	a5,0x1000
80002c9a:	46e1                	li	a3,24
80002c9c:	f6f675e3          	bgeu	a2,a5,80002c06 <__udivdi3+0xec>
80002ca0:	46c1                	li	a3,16
80002ca2:	b795                	j	80002c06 <__udivdi3+0xec>
80002ca4:	00b61733          	sll	a4,a2,a1
80002ca8:	00f356b3          	srl	a3,t1,a5
80002cac:	01075513          	srli	a0,a4,0x10
80002cb0:	00b31333          	sll	t1,t1,a1
80002cb4:	00f8d7b3          	srl	a5,a7,a5
80002cb8:	0067e7b3          	or	a5,a5,t1
80002cbc:	02a6d333          	divu	t1,a3,a0
80002cc0:	01071613          	slli	a2,a4,0x10
80002cc4:	8241                	srli	a2,a2,0x10
80002cc6:	00b89833          	sll	a6,a7,a1
80002cca:	02a6f6b3          	remu	a3,a3,a0
80002cce:	026608b3          	mul	a7,a2,t1
80002cd2:	01069593          	slli	a1,a3,0x10
80002cd6:	0107d693          	srli	a3,a5,0x10
80002cda:	8ecd                	or	a3,a3,a1
80002cdc:	859a                	mv	a1,t1
80002cde:	0116fc63          	bgeu	a3,a7,80002cf6 <__udivdi3+0x1dc>
80002ce2:	96ba                	add	a3,a3,a4
80002ce4:	fff30593          	addi	a1,t1,-1
80002ce8:	00e6e763          	bltu	a3,a4,80002cf6 <__udivdi3+0x1dc>
80002cec:	0116f563          	bgeu	a3,a7,80002cf6 <__udivdi3+0x1dc>
80002cf0:	ffe30593          	addi	a1,t1,-2
80002cf4:	96ba                	add	a3,a3,a4
80002cf6:	411686b3          	sub	a3,a3,a7
80002cfa:	02a6d8b3          	divu	a7,a3,a0
80002cfe:	07c2                	slli	a5,a5,0x10
80002d00:	83c1                	srli	a5,a5,0x10
80002d02:	02a6f6b3          	remu	a3,a3,a0
80002d06:	03160633          	mul	a2,a2,a7
80002d0a:	06c2                	slli	a3,a3,0x10
80002d0c:	8fd5                	or	a5,a5,a3
80002d0e:	86c6                	mv	a3,a7
80002d10:	00c7fc63          	bgeu	a5,a2,80002d28 <__udivdi3+0x20e>
80002d14:	97ba                	add	a5,a5,a4
80002d16:	fff88693          	addi	a3,a7,-1
80002d1a:	00e7e763          	bltu	a5,a4,80002d28 <__udivdi3+0x20e>
80002d1e:	00c7f563          	bgeu	a5,a2,80002d28 <__udivdi3+0x20e>
80002d22:	ffe88693          	addi	a3,a7,-2
80002d26:	97ba                	add	a5,a5,a4
80002d28:	05c2                	slli	a1,a1,0x10
80002d2a:	8f91                	sub	a5,a5,a2
80002d2c:	8dd5                	or	a1,a1,a3
80002d2e:	bddd                	j	80002c24 <__udivdi3+0x10a>
80002d30:	12d5ef63          	bltu	a1,a3,80002e6e <__udivdi3+0x354>
80002d34:	67c1                	lui	a5,0x10
80002d36:	02f6ff63          	bgeu	a3,a5,80002d74 <__udivdi3+0x25a>
80002d3a:	1006b793          	sltiu	a5,a3,256
80002d3e:	0017b793          	seqz	a5,a5
80002d42:	078e                	slli	a5,a5,0x3
80002d44:	80004737          	lui	a4,0x80004
80002d48:	00f6d5b3          	srl	a1,a3,a5
80002d4c:	f8070713          	addi	a4,a4,-128 # 80003f80 <__clz_tab>
80002d50:	972e                	add	a4,a4,a1
80002d52:	00074703          	lbu	a4,0(a4)
80002d56:	973e                	add	a4,a4,a5
80002d58:	02000793          	li	a5,32
80002d5c:	40e785b3          	sub	a1,a5,a4
80002d60:	02e79163          	bne	a5,a4,80002d82 <__udivdi3+0x268>
80002d64:	4505                	li	a0,1
80002d66:	e666eee3          	bltu	a3,t1,80002be2 <__udivdi3+0xc8>
80002d6a:	00c8b533          	sltu	a0,a7,a2
80002d6e:	00153513          	seqz	a0,a0
80002d72:	8082                	ret
80002d74:	01000737          	lui	a4,0x1000
80002d78:	47e1                	li	a5,24
80002d7a:	fce6f5e3          	bgeu	a3,a4,80002d44 <__udivdi3+0x22a>
80002d7e:	47c1                	li	a5,16
80002d80:	b7d1                	j	80002d44 <__udivdi3+0x22a>
80002d82:	00e65533          	srl	a0,a2,a4
80002d86:	00b696b3          	sll	a3,a3,a1
80002d8a:	00e357b3          	srl	a5,t1,a4
80002d8e:	8d55                	or	a0,a0,a3
80002d90:	00b31333          	sll	t1,t1,a1
80002d94:	00e8d733          	srl	a4,a7,a4
80002d98:	00676733          	or	a4,a4,t1
80002d9c:	01055313          	srli	t1,a0,0x10
80002da0:	0267deb3          	divu	t4,a5,t1
80002da4:	01051813          	slli	a6,a0,0x10
80002da8:	01085813          	srli	a6,a6,0x10
80002dac:	01075693          	srli	a3,a4,0x10
80002db0:	00b61633          	sll	a2,a2,a1
80002db4:	0267f7b3          	remu	a5,a5,t1
80002db8:	03d80e33          	mul	t3,a6,t4
80002dbc:	07c2                	slli	a5,a5,0x10
80002dbe:	8edd                	or	a3,a3,a5
80002dc0:	87f6                	mv	a5,t4
80002dc2:	01c6fc63          	bgeu	a3,t3,80002dda <__udivdi3+0x2c0>
80002dc6:	96aa                	add	a3,a3,a0
80002dc8:	fffe8793          	addi	a5,t4,-1
80002dcc:	00a6e763          	bltu	a3,a0,80002dda <__udivdi3+0x2c0>
80002dd0:	01c6f563          	bgeu	a3,t3,80002dda <__udivdi3+0x2c0>
80002dd4:	ffee8793          	addi	a5,t4,-2
80002dd8:	96aa                	add	a3,a3,a0
80002dda:	41c686b3          	sub	a3,a3,t3
80002dde:	0266de33          	divu	t3,a3,t1
80002de2:	0742                	slli	a4,a4,0x10
80002de4:	8341                	srli	a4,a4,0x10
80002de6:	0266f6b3          	remu	a3,a3,t1
80002dea:	03c80833          	mul	a6,a6,t3
80002dee:	06c2                	slli	a3,a3,0x10
80002df0:	8f55                	or	a4,a4,a3
80002df2:	86f2                	mv	a3,t3
80002df4:	01077c63          	bgeu	a4,a6,80002e0c <__udivdi3+0x2f2>
80002df8:	972a                	add	a4,a4,a0
80002dfa:	fffe0693          	addi	a3,t3,-1
80002dfe:	00a76763          	bltu	a4,a0,80002e0c <__udivdi3+0x2f2>
80002e02:	01077563          	bgeu	a4,a6,80002e0c <__udivdi3+0x2f2>
80002e06:	ffee0693          	addi	a3,t3,-2
80002e0a:	972a                	add	a4,a4,a0
80002e0c:	07c2                	slli	a5,a5,0x10
80002e0e:	00d7e533          	or	a0,a5,a3
80002e12:	01061313          	slli	t1,a2,0x10
80002e16:	06c2                	slli	a3,a3,0x10
80002e18:	82c1                	srli	a3,a3,0x10
80002e1a:	01035313          	srli	t1,t1,0x10
80002e1e:	8241                	srli	a2,a2,0x10
80002e20:	41070733          	sub	a4,a4,a6
80002e24:	01055813          	srli	a6,a0,0x10
80002e28:	02668e33          	mul	t3,a3,t1
80002e2c:	02680333          	mul	t1,a6,t1
80002e30:	010e5793          	srli	a5,t3,0x10
80002e34:	02c686b3          	mul	a3,a3,a2
80002e38:	969a                	add	a3,a3,t1
80002e3a:	97b6                	add	a5,a5,a3
80002e3c:	02c80833          	mul	a6,a6,a2
80002e40:	0067f463          	bgeu	a5,t1,80002e48 <__udivdi3+0x32e>
80002e44:	66c1                	lui	a3,0x10
80002e46:	9836                	add	a6,a6,a3
80002e48:	0107d693          	srli	a3,a5,0x10
80002e4c:	96c2                	add	a3,a3,a6
80002e4e:	00d76e63          	bltu	a4,a3,80002e6a <__udivdi3+0x350>
80002e52:	d8d717e3          	bne	a4,a3,80002be0 <__udivdi3+0xc6>
80002e56:	0e42                	slli	t3,t3,0x10
80002e58:	07c2                	slli	a5,a5,0x10
80002e5a:	010e5e13          	srli	t3,t3,0x10
80002e5e:	00b898b3          	sll	a7,a7,a1
80002e62:	97f2                	add	a5,a5,t3
80002e64:	4581                	li	a1,0
80002e66:	d6f8fee3          	bgeu	a7,a5,80002be2 <__udivdi3+0xc8>
80002e6a:	157d                	addi	a0,a0,-1 # ffffff <_tbss_end+0xffffbb>
80002e6c:	bb95                	j	80002be0 <__udivdi3+0xc6>
80002e6e:	4581                	li	a1,0
80002e70:	4501                	li	a0,0
80002e72:	8082                	ret

80002e74 <__umoddi3>:
80002e74:	8832                	mv	a6,a2
80002e76:	87aa                	mv	a5,a0
80002e78:	872e                	mv	a4,a1
80002e7a:	1a069363          	bnez	a3,80003020 <__umoddi3+0x1ac>
80002e7e:	800048b7          	lui	a7,0x80004
80002e82:	f8088893          	addi	a7,a7,-128 # 80003f80 <__clz_tab>
80002e86:	0ac5f663          	bgeu	a1,a2,80002f32 <__umoddi3+0xbe>
80002e8a:	66c1                	lui	a3,0x10
80002e8c:	08d67c63          	bgeu	a2,a3,80002f24 <__umoddi3+0xb0>
80002e90:	10063693          	sltiu	a3,a2,256
80002e94:	0016b693          	seqz	a3,a3
80002e98:	068e                	slli	a3,a3,0x3
80002e9a:	00d65333          	srl	t1,a2,a3
80002e9e:	989a                	add	a7,a7,t1
80002ea0:	0008c883          	lbu	a7,0(a7)
80002ea4:	02000313          	li	t1,32
80002ea8:	96c6                	add	a3,a3,a7
80002eaa:	40d308b3          	sub	a7,t1,a3
80002eae:	00d30b63          	beq	t1,a3,80002ec4 <__umoddi3+0x50>
80002eb2:	01159733          	sll	a4,a1,a7
80002eb6:	00d556b3          	srl	a3,a0,a3
80002eba:	01161833          	sll	a6,a2,a7
80002ebe:	8f55                	or	a4,a4,a3
80002ec0:	011517b3          	sll	a5,a0,a7
80002ec4:	01085613          	srli	a2,a6,0x10
80002ec8:	02c756b3          	divu	a3,a4,a2
80002ecc:	01081513          	slli	a0,a6,0x10
80002ed0:	8141                	srli	a0,a0,0x10
80002ed2:	02c77733          	remu	a4,a4,a2
80002ed6:	02a686b3          	mul	a3,a3,a0
80002eda:	01071593          	slli	a1,a4,0x10
80002ede:	0107d713          	srli	a4,a5,0x10
80002ee2:	8f4d                	or	a4,a4,a1
80002ee4:	00d77863          	bgeu	a4,a3,80002ef4 <__umoddi3+0x80>
80002ee8:	9742                	add	a4,a4,a6
80002eea:	01076563          	bltu	a4,a6,80002ef4 <__umoddi3+0x80>
80002eee:	00d77363          	bgeu	a4,a3,80002ef4 <__umoddi3+0x80>
80002ef2:	9742                	add	a4,a4,a6
80002ef4:	8f15                	sub	a4,a4,a3
80002ef6:	02c756b3          	divu	a3,a4,a2
80002efa:	02c77733          	remu	a4,a4,a2
80002efe:	02a686b3          	mul	a3,a3,a0
80002f02:	07c2                	slli	a5,a5,0x10
80002f04:	0742                	slli	a4,a4,0x10
80002f06:	83c1                	srli	a5,a5,0x10
80002f08:	8fd9                	or	a5,a5,a4
80002f0a:	00d7f863          	bgeu	a5,a3,80002f1a <__umoddi3+0xa6>
80002f0e:	97c2                	add	a5,a5,a6
80002f10:	0107e563          	bltu	a5,a6,80002f1a <__umoddi3+0xa6>
80002f14:	00d7f363          	bgeu	a5,a3,80002f1a <__umoddi3+0xa6>
80002f18:	97c2                	add	a5,a5,a6
80002f1a:	8f95                	sub	a5,a5,a3
80002f1c:	0117d533          	srl	a0,a5,a7
80002f20:	4581                	li	a1,0
80002f22:	8082                	ret
80002f24:	01000337          	lui	t1,0x1000
80002f28:	46e1                	li	a3,24
80002f2a:	f66678e3          	bgeu	a2,t1,80002e9a <__umoddi3+0x26>
80002f2e:	46c1                	li	a3,16
80002f30:	b7ad                	j	80002e9a <__umoddi3+0x26>
80002f32:	4681                	li	a3,0
80002f34:	ca09                	beqz	a2,80002f46 <__umoddi3+0xd2>
80002f36:	6741                	lui	a4,0x10
80002f38:	06e67463          	bgeu	a2,a4,80002fa0 <__umoddi3+0x12c>
80002f3c:	10063693          	sltiu	a3,a2,256
80002f40:	0016b693          	seqz	a3,a3
80002f44:	068e                	slli	a3,a3,0x3
80002f46:	00d65733          	srl	a4,a2,a3
80002f4a:	98ba                	add	a7,a7,a4
80002f4c:	0008c703          	lbu	a4,0(a7)
80002f50:	9736                	add	a4,a4,a3
80002f52:	02000693          	li	a3,32
80002f56:	40e688b3          	sub	a7,a3,a4
80002f5a:	04e69a63          	bne	a3,a4,80002fae <__umoddi3+0x13a>
80002f5e:	40c58733          	sub	a4,a1,a2
80002f62:	01085593          	srli	a1,a6,0x10
80002f66:	02b75633          	divu	a2,a4,a1
80002f6a:	01081513          	slli	a0,a6,0x10
80002f6e:	8141                	srli	a0,a0,0x10
80002f70:	0107d693          	srli	a3,a5,0x10
80002f74:	02b77733          	remu	a4,a4,a1
80002f78:	02a60633          	mul	a2,a2,a0
80002f7c:	0742                	slli	a4,a4,0x10
80002f7e:	8f55                	or	a4,a4,a3
80002f80:	00c77863          	bgeu	a4,a2,80002f90 <__umoddi3+0x11c>
80002f84:	9742                	add	a4,a4,a6
80002f86:	01076563          	bltu	a4,a6,80002f90 <__umoddi3+0x11c>
80002f8a:	00c77363          	bgeu	a4,a2,80002f90 <__umoddi3+0x11c>
80002f8e:	9742                	add	a4,a4,a6
80002f90:	8f11                	sub	a4,a4,a2
80002f92:	02b756b3          	divu	a3,a4,a1
80002f96:	02b77733          	remu	a4,a4,a1
80002f9a:	02a686b3          	mul	a3,a3,a0
80002f9e:	b795                	j	80002f02 <__umoddi3+0x8e>
80002fa0:	01000737          	lui	a4,0x1000
80002fa4:	46e1                	li	a3,24
80002fa6:	fae670e3          	bgeu	a2,a4,80002f46 <__umoddi3+0xd2>
80002faa:	46c1                	li	a3,16
80002fac:	bf69                	j	80002f46 <__umoddi3+0xd2>
80002fae:	01161833          	sll	a6,a2,a7
80002fb2:	00e5d6b3          	srl	a3,a1,a4
80002fb6:	011517b3          	sll	a5,a0,a7
80002fba:	011595b3          	sll	a1,a1,a7
80002fbe:	00e55733          	srl	a4,a0,a4
80002fc2:	01085513          	srli	a0,a6,0x10
80002fc6:	8f4d                	or	a4,a4,a1
80002fc8:	02a6d5b3          	divu	a1,a3,a0
80002fcc:	01081313          	slli	t1,a6,0x10
80002fd0:	01035313          	srli	t1,t1,0x10
80002fd4:	02a6f6b3          	remu	a3,a3,a0
80002fd8:	026585b3          	mul	a1,a1,t1
80002fdc:	01069613          	slli	a2,a3,0x10
80002fe0:	01075693          	srli	a3,a4,0x10
80002fe4:	8ed1                	or	a3,a3,a2
80002fe6:	00b6f863          	bgeu	a3,a1,80002ff6 <__umoddi3+0x182>
80002fea:	96c2                	add	a3,a3,a6
80002fec:	0106e563          	bltu	a3,a6,80002ff6 <__umoddi3+0x182>
80002ff0:	00b6f363          	bgeu	a3,a1,80002ff6 <__umoddi3+0x182>
80002ff4:	96c2                	add	a3,a3,a6
80002ff6:	8e8d                	sub	a3,a3,a1
80002ff8:	02a6d633          	divu	a2,a3,a0
80002ffc:	0742                	slli	a4,a4,0x10
80002ffe:	8341                	srli	a4,a4,0x10
80003000:	02a6f6b3          	remu	a3,a3,a0
80003004:	02660633          	mul	a2,a2,t1
80003008:	06c2                	slli	a3,a3,0x10
8000300a:	8f55                	or	a4,a4,a3
8000300c:	00c77863          	bgeu	a4,a2,8000301c <__umoddi3+0x1a8>
80003010:	9742                	add	a4,a4,a6
80003012:	01076563          	bltu	a4,a6,8000301c <__umoddi3+0x1a8>
80003016:	00c77363          	bgeu	a4,a2,8000301c <__umoddi3+0x1a8>
8000301a:	9742                	add	a4,a4,a6
8000301c:	8f11                	sub	a4,a4,a2
8000301e:	b791                	j	80002f62 <__umoddi3+0xee>
80003020:	16d5ea63          	bltu	a1,a3,80003194 <__umoddi3+0x320>
80003024:	6841                	lui	a6,0x10
80003026:	0506f763          	bgeu	a3,a6,80003074 <__umoddi3+0x200>
8000302a:	1006b813          	sltiu	a6,a3,256
8000302e:	00183813          	seqz	a6,a6
80003032:	080e                	slli	a6,a6,0x3
80003034:	800048b7          	lui	a7,0x80004
80003038:	0106d333          	srl	t1,a3,a6
8000303c:	f8088893          	addi	a7,a7,-128 # 80003f80 <__clz_tab>
80003040:	989a                	add	a7,a7,t1
80003042:	0008c883          	lbu	a7,0(a7)
80003046:	02000313          	li	t1,32
8000304a:	98c2                	add	a7,a7,a6
8000304c:	41130833          	sub	a6,t1,a7
80003050:	03131963          	bne	t1,a7,80003082 <__umoddi3+0x20e>
80003054:	00b6e463          	bltu	a3,a1,8000305c <__umoddi3+0x1e8>
80003058:	00c56b63          	bltu	a0,a2,8000306e <__umoddi3+0x1fa>
8000305c:	40c50633          	sub	a2,a0,a2
80003060:	40d586b3          	sub	a3,a1,a3
80003064:	00c53733          	sltu	a4,a0,a2
80003068:	87b2                	mv	a5,a2
8000306a:	40e68733          	sub	a4,a3,a4
8000306e:	853e                	mv	a0,a5
80003070:	85ba                	mv	a1,a4
80003072:	8082                	ret
80003074:	010008b7          	lui	a7,0x1000
80003078:	4861                	li	a6,24
8000307a:	fb16fde3          	bgeu	a3,a7,80003034 <__umoddi3+0x1c0>
8000307e:	4841                	li	a6,16
80003080:	bf55                	j	80003034 <__umoddi3+0x1c0>
80003082:	011657b3          	srl	a5,a2,a7
80003086:	010696b3          	sll	a3,a3,a6
8000308a:	8edd                	or	a3,a3,a5
8000308c:	0115d733          	srl	a4,a1,a7
80003090:	0106d313          	srli	t1,a3,0x10
80003094:	02675f33          	divu	t5,a4,t1
80003098:	01069e13          	slli	t3,a3,0x10
8000309c:	010e5e13          	srli	t3,t3,0x10
800030a0:	010597b3          	sll	a5,a1,a6
800030a4:	011555b3          	srl	a1,a0,a7
800030a8:	8ddd                	or	a1,a1,a5
800030aa:	0105d793          	srli	a5,a1,0x10
800030ae:	01061633          	sll	a2,a2,a6
800030b2:	01051533          	sll	a0,a0,a6
800030b6:	02677733          	remu	a4,a4,t1
800030ba:	03ee0eb3          	mul	t4,t3,t5
800030be:	0742                	slli	a4,a4,0x10
800030c0:	8fd9                	or	a5,a5,a4
800030c2:	877a                	mv	a4,t5
800030c4:	01d7fc63          	bgeu	a5,t4,800030dc <__umoddi3+0x268>
800030c8:	97b6                	add	a5,a5,a3
800030ca:	ffff0713          	addi	a4,t5,-1
800030ce:	00d7e763          	bltu	a5,a3,800030dc <__umoddi3+0x268>
800030d2:	01d7f563          	bgeu	a5,t4,800030dc <__umoddi3+0x268>
800030d6:	ffef0713          	addi	a4,t5,-2
800030da:	97b6                	add	a5,a5,a3
800030dc:	41d787b3          	sub	a5,a5,t4
800030e0:	0267deb3          	divu	t4,a5,t1
800030e4:	05c2                	slli	a1,a1,0x10
800030e6:	81c1                	srli	a1,a1,0x10
800030e8:	0267f7b3          	remu	a5,a5,t1
800030ec:	8376                	mv	t1,t4
800030ee:	03de0e33          	mul	t3,t3,t4
800030f2:	07c2                	slli	a5,a5,0x10
800030f4:	8ddd                	or	a1,a1,a5
800030f6:	01c5fc63          	bgeu	a1,t3,8000310e <__umoddi3+0x29a>
800030fa:	95b6                	add	a1,a1,a3
800030fc:	fffe8313          	addi	t1,t4,-1
80003100:	00d5e763          	bltu	a1,a3,8000310e <__umoddi3+0x29a>
80003104:	01c5f563          	bgeu	a1,t3,8000310e <__umoddi3+0x29a>
80003108:	ffee8313          	addi	t1,t4,-2
8000310c:	95b6                	add	a1,a1,a3
8000310e:	01071793          	slli	a5,a4,0x10
80003112:	0067e7b3          	or	a5,a5,t1
80003116:	41c585b3          	sub	a1,a1,t3
8000311a:	0342                	slli	t1,t1,0x10
8000311c:	01061e13          	slli	t3,a2,0x10
80003120:	01065713          	srli	a4,a2,0x10
80003124:	01035313          	srli	t1,t1,0x10
80003128:	83c1                	srli	a5,a5,0x10
8000312a:	010e5e13          	srli	t3,t3,0x10
8000312e:	03c30eb3          	mul	t4,t1,t3
80003132:	03c78e33          	mul	t3,a5,t3
80003136:	02e30333          	mul	t1,t1,a4
8000313a:	02e787b3          	mul	a5,a5,a4
8000313e:	9372                	add	t1,t1,t3
80003140:	010ed713          	srli	a4,t4,0x10
80003144:	971a                	add	a4,a4,t1
80003146:	01c77463          	bgeu	a4,t3,8000314e <__umoddi3+0x2da>
8000314a:	6341                	lui	t1,0x10
8000314c:	979a                	add	a5,a5,t1
8000314e:	01075313          	srli	t1,a4,0x10
80003152:	0ec2                	slli	t4,t4,0x10
80003154:	0742                	slli	a4,a4,0x10
80003156:	010ede93          	srli	t4,t4,0x10
8000315a:	979a                	add	a5,a5,t1
8000315c:	9776                	add	a4,a4,t4
8000315e:	00f5e663          	bltu	a1,a5,8000316a <__umoddi3+0x2f6>
80003162:	00f59b63          	bne	a1,a5,80003178 <__umoddi3+0x304>
80003166:	00e57963          	bgeu	a0,a4,80003178 <__umoddi3+0x304>
8000316a:	40c70633          	sub	a2,a4,a2
8000316e:	00c73333          	sltu	t1,a4,a2
80003172:	969a                	add	a3,a3,t1
80003174:	8732                	mv	a4,a2
80003176:	8f95                	sub	a5,a5,a3
80003178:	40e50733          	sub	a4,a0,a4
8000317c:	00e53533          	sltu	a0,a0,a4
80003180:	8d9d                	sub	a1,a1,a5
80003182:	8d89                	sub	a1,a1,a0
80003184:	011598b3          	sll	a7,a1,a7
80003188:	01075733          	srl	a4,a4,a6
8000318c:	00e8e533          	or	a0,a7,a4
80003190:	0105d5b3          	srl	a1,a1,a6
80003194:	8082                	ret

Disassembly of section .text.startup:

80003196 <main>:
80003196:	7135                	addi	sp,sp,-160
80003198:	0830                	addi	a2,sp,24
8000319a:	084c                	addi	a1,sp,20
8000319c:	05e10513          	addi	a0,sp,94
800031a0:	cf06                	sw	ra,156(sp)
800031a2:	cd22                	sw	s0,152(sp)
800031a4:	cb26                	sw	s1,148(sp)
800031a6:	c94a                	sw	s2,144(sp)
800031a8:	c74e                	sw	s3,140(sp)
800031aa:	c552                	sw	s4,136(sp)
800031ac:	c356                	sw	s5,132(sp)
800031ae:	ca02                	sw	zero,20(sp)
800031b0:	93aff0ef          	jal	800022ea <portable_init>
800031b4:	4505                	li	a0,1
800031b6:	f0dfe0ef          	jal	800020c2 <get_seed_32>
800031ba:	87aa                	mv	a5,a0
800031bc:	4509                	li	a0,2
800031be:	00f11e23          	sh	a5,28(sp)
800031c2:	f01fe0ef          	jal	800020c2 <get_seed_32>
800031c6:	87aa                	mv	a5,a0
800031c8:	450d                	li	a0,3
800031ca:	00f11f23          	sh	a5,30(sp)
800031ce:	ef5fe0ef          	jal	800020c2 <get_seed_32>
800031d2:	87aa                	mv	a5,a0
800031d4:	4511                	li	a0,4
800031d6:	02f11023          	sh	a5,32(sp)
800031da:	ee9fe0ef          	jal	800020c2 <get_seed_32>
800031de:	87aa                	mv	a5,a0
800031e0:	4515                	li	a0,5
800031e2:	dc3e                	sw	a5,56(sp)
800031e4:	edffe0ef          	jal	800020c2 <get_seed_32>
800031e8:	e111                	bnez	a0,800031ec <main+0x56>
800031ea:	451d                	li	a0,7
800031ec:	47f2                	lw	a5,28(sp)
800031ee:	de2a                	sw	a0,60(sp)
800031f0:	18079063          	bnez	a5,80003370 <main+0x1da>
800031f4:	02011783          	lh	a5,32(sp)
800031f8:	2a078c63          	beqz	a5,800034b0 <main+0x31a>
800031fc:	00257793          	andi	a5,a0,2
80003200:	84818313          	addi	t1,gp,-1976 # 80004128 <static_memblk>
80003204:	00f037b3          	snez	a5,a5
80003208:	00157713          	andi	a4,a0,1
8000320c:	04011e23          	sh	zero,92(sp)
80003210:	d21a                	sw	t1,36(sp)
80003212:	00457693          	andi	a3,a0,4
80003216:	973e                	add	a4,a4,a5
80003218:	c681                	beqz	a3,80003220 <main+0x8a>
8000321a:	0705                	addi	a4,a4,1 # 1000001 <_tbss_end+0xffffbd>
8000321c:	0742                	slli	a4,a4,0x10
8000321e:	8341                	srli	a4,a4,0x10
80003220:	7d000593          	li	a1,2000
80003224:	02e5d5b3          	divu	a1,a1,a4
80003228:	0874                	addi	a3,sp,28
8000322a:	4781                	li	a5,0
8000322c:	4601                	li	a2,0
8000322e:	4885                	li	a7,1
80003230:	480d                	li	a6,3
80003232:	da2e                	sw	a1,52(sp)
80003234:	00f89733          	sll	a4,a7,a5
80003238:	8f69                	and	a4,a4,a0
8000323a:	0785                	addi	a5,a5,1 # 10001 <_tbss_end+0xffbd>
8000323c:	12071263          	bnez	a4,80003360 <main+0x1ca>
80003240:	0691                	addi	a3,a3,4 # 10004 <_tbss_end+0xffc0>
80003242:	ff0799e3          	bne	a5,a6,80003234 <main+0x9e>
80003246:	57f2                	lw	a5,60(sp)
80003248:	0017f713          	andi	a4,a5,1
8000324c:	cb09                	beqz	a4,8000325e <main+0xc8>
8000324e:	01c11603          	lh	a2,28(sp)
80003252:	55a2                	lw	a1,40(sp)
80003254:	5552                	lw	a0,52(sp)
80003256:	b48fe0ef          	jal	8000159e <core_list_init>
8000325a:	57f2                	lw	a5,60(sp)
8000325c:	c0aa                	sw	a0,64(sp)
8000325e:	0027f713          	andi	a4,a5,2
80003262:	0e071263          	bnez	a4,80003346 <main+0x1b0>
80003266:	8b91                	andi	a5,a5,4
80003268:	c799                	beqz	a5,80003276 <main+0xe0>
8000326a:	5642                	lw	a2,48(sp)
8000326c:	01c11583          	lh	a1,28(sp)
80003270:	5552                	lw	a0,52(sp)
80003272:	a5bfe0ef          	jal	80001ccc <core_init_state>
80003276:	57e2                	lw	a5,56(sp)
80003278:	efb9                	bnez	a5,800032d6 <main+0x140>
8000327a:	b4a2                	fsd	fs0,104(sp)
8000327c:	00001797          	auipc	a5,0x1
80003280:	e647b407          	fld	fs0,-412(a5) # 800040e0 <.got.plt+0x8>
80003284:	4785                	li	a5,1
80003286:	dc3e                	sw	a5,56(sp)
80003288:	5762                	lw	a4,56(sp)
8000328a:	00271793          	slli	a5,a4,0x2
8000328e:	97ba                	add	a5,a5,a4
80003290:	0786                	slli	a5,a5,0x1
80003292:	dc3e                	sw	a5,56(sp)
80003294:	814ff0ef          	jal	800022a8 <start_time>
80003298:	0868                	addi	a0,sp,28
8000329a:	c3afe0ef          	jal	800016d4 <iterate>
8000329e:	818ff0ef          	jal	800022b6 <stop_time>
800032a2:	822ff0ef          	jal	800022c4 <get_time>
800032a6:	832ff0ef          	jal	800022d8 <time_in_secs>
800032aa:	a02a                	fsd	fa0,0(sp)
800032ac:	4782                	lw	a5,0(sp)
800032ae:	c43e                	sw	a5,8(sp)
800032b0:	4792                	lw	a5,4(sp)
800032b2:	c63e                	sw	a5,12(sp)
800032b4:	27a2                	fld	fa5,8(sp)
800032b6:	a28797d3          	flt.d	a5,fa5,fs0
800032ba:	f7f9                	bnez	a5,80003288 <main+0xf2>
800032bc:	c2179753          	fcvt.wu.d	a4,fa5,rtz
800032c0:	1e070663          	beqz	a4,800034ac <main+0x316>
800032c4:	47a9                	li	a5,10
800032c6:	02e7d7b3          	divu	a5,a5,a4
800032ca:	5762                	lw	a4,56(sp)
800032cc:	3426                	fld	fs0,104(sp)
800032ce:	0785                	addi	a5,a5,1
800032d0:	02f707b3          	mul	a5,a4,a5
800032d4:	dc3e                	sw	a5,56(sp)
800032d6:	fd3fe0ef          	jal	800022a8 <start_time>
800032da:	0868                	addi	a0,sp,28
800032dc:	bf8fe0ef          	jal	800016d4 <iterate>
800032e0:	fd7fe0ef          	jal	800022b6 <stop_time>
800032e4:	fe1fe0ef          	jal	800022c4 <get_time>
800032e8:	892a                	mv	s2,a0
800032ea:	01c11503          	lh	a0,28(sp)
800032ee:	4581                	li	a1,0
800032f0:	f4dfe0ef          	jal	8000223c <crc16>
800032f4:	85aa                	mv	a1,a0
800032f6:	01e11503          	lh	a0,30(sp)
800032fa:	f43fe0ef          	jal	8000223c <crc16>
800032fe:	85aa                	mv	a1,a0
80003300:	02011503          	lh	a0,32(sp)
80003304:	f39fe0ef          	jal	8000223c <crc16>
80003308:	85aa                	mv	a1,a0
8000330a:	03411503          	lh	a0,52(sp)
8000330e:	f2ffe0ef          	jal	8000223c <crc16>
80003312:	67a1                	lui	a5,0x8
80003314:	b0578793          	addi	a5,a5,-1275 # 7b05 <_tbss_end+0x7ac1>
80003318:	8a2a                	mv	s4,a0
8000331a:	46f50963          	beq	a0,a5,8000378c <main+0x5f6>
8000331e:	06a7fa63          	bgeu	a5,a0,80003392 <main+0x1fc>
80003322:	67a5                	lui	a5,0x9
80003324:	a0278793          	addi	a5,a5,-1534 # 8a02 <_tbss_end+0x89be>
80003328:	44f50a63          	beq	a0,a5,8000377c <main+0x5e6>
8000332c:	67bd                	lui	a5,0xf
8000332e:	9f578793          	addi	a5,a5,-1547 # e9f5 <_tbss_end+0xe9b1>
80003332:	18f51463          	bne	a0,a5,800034ba <main+0x324>
80003336:	00000517          	auipc	a0,0x0
8000333a:	52650513          	addi	a0,a0,1318 # 8000385c <main+0x6c6>
8000333e:	d78ff0ef          	jal	800028b6 <puts>
80003342:	498d                	li	s3,3
80003344:	a885                	j	800033b4 <main+0x21e>
80003346:	01e11783          	lh	a5,30(sp)
8000334a:	01c11603          	lh	a2,28(sp)
8000334e:	55b2                	lw	a1,44(sp)
80003350:	5552                	lw	a0,52(sp)
80003352:	07c2                	slli	a5,a5,0x10
80003354:	8e5d                	or	a2,a2,a5
80003356:	00d4                	addi	a3,sp,68
80003358:	bd8fe0ef          	jal	80001730 <core_init_matrix>
8000335c:	57f2                	lw	a5,60(sp)
8000335e:	b721                	j	80003266 <main+0xd0>
80003360:	02b60733          	mul	a4,a2,a1
80003364:	0605                	addi	a2,a2,1
80003366:	0642                	slli	a2,a2,0x10
80003368:	8241                	srli	a2,a2,0x10
8000336a:	971a                	add	a4,a4,t1
8000336c:	c6d8                	sw	a4,12(a3)
8000336e:	bdc9                	j	80003240 <main+0xaa>
80003370:	4705                	li	a4,1
80003372:	e8e795e3          	bne	a5,a4,800031fc <main+0x66>
80003376:	02011783          	lh	a5,32(sp)
8000337a:	e80791e3          	bnez	a5,800031fc <main+0x66>
8000337e:	341537b7          	lui	a5,0x34153
80003382:	41578793          	addi	a5,a5,1045 # 34153415 <_tbss_end+0x341533d1>
80003386:	06600713          	li	a4,102
8000338a:	ce3e                	sw	a5,28(sp)
8000338c:	02e11023          	sh	a4,32(sp)
80003390:	b5b5                	j	800031fc <main+0x66>
80003392:	6789                	lui	a5,0x2
80003394:	8f278793          	addi	a5,a5,-1806 # 18f2 <_tbss_end+0x18ae>
80003398:	40f50263          	beq	a0,a5,8000379c <main+0x606>
8000339c:	6795                	lui	a5,0x5
8000339e:	eaf78793          	addi	a5,a5,-337 # 4eaf <_tbss_end+0x4e6b>
800033a2:	10f51c63          	bne	a0,a5,800034ba <main+0x324>
800033a6:	00000517          	auipc	a0,0x0
800033aa:	48650513          	addi	a0,a0,1158 # 8000382c <main+0x696>
800033ae:	d08ff0ef          	jal	800028b6 <puts>
800033b2:	4989                	li	s3,2
800033b4:	81818a93          	addi	s5,gp,-2024 # 800040f8 <default_num_contexts>
800033b8:	000aa783          	lw	a5,0(s5)
800033bc:	3e078863          	beqz	a5,800037ac <main+0x616>
800033c0:	dede                	sw	s7,124(sp)
800033c2:	00199793          	slli	a5,s3,0x1
800033c6:	00001b97          	auipc	s7,0x1
800033ca:	9e6b8b93          	addi	s7,s7,-1562 # 80003dac <list_known_crc>
800033ce:	c15a                	sw	s6,128(sp)
800033d0:	dce2                	sw	s8,120(sp)
800033d2:	9bbe                	add	s7,s7,a5
800033d4:	4c01                	li	s8,0
800033d6:	4b01                	li	s6,0
800033d8:	a025                	j	80003400 <main+0x26a>
800033da:	940a                	add	s0,s0,sp
800033dc:	05c45783          	lhu	a5,92(s0)
800033e0:	0b05                	addi	s6,s6,1
800033e2:	000aa703          	lw	a4,0(s5)
800033e6:	97e2                	add	a5,a5,s8
800033e8:	0b42                	slli	s6,s6,0x10
800033ea:	01079493          	slli	s1,a5,0x10
800033ee:	01079c13          	slli	s8,a5,0x10
800033f2:	010b5b13          	srli	s6,s6,0x10
800033f6:	80c1                	srli	s1,s1,0x10
800033f8:	410c5c13          	srai	s8,s8,0x10
800033fc:	2eeb7663          	bgeu	s6,a4,800036e8 <main+0x552>
80003400:	004b1413          	slli	s0,s6,0x4
80003404:	016404b3          	add	s1,s0,s6
80003408:	048a                	slli	s1,s1,0x2
8000340a:	05048793          	addi	a5,s1,80
8000340e:	0818                	addi	a4,sp,16
80003410:	00e784b3          	add	s1,a5,a4
80003414:	fdc4a783          	lw	a5,-36(s1)
80003418:	fe049e23          	sh	zero,-4(s1)
8000341c:	0017f713          	andi	a4,a5,1
80003420:	c70d                	beqz	a4,8000344a <main+0x2b4>
80003422:	ff64d603          	lhu	a2,-10(s1)
80003426:	000bd683          	lhu	a3,0(s7)
8000342a:	02d60063          	beq	a2,a3,8000344a <main+0x2b4>
8000342e:	85da                	mv	a1,s6
80003430:	00000517          	auipc	a0,0x0
80003434:	48450513          	addi	a0,a0,1156 # 800038b4 <main+0x71e>
80003438:	c4eff0ef          	jal	80002886 <printf>
8000343c:	ffc4d703          	lhu	a4,-4(s1)
80003440:	fdc4a783          	lw	a5,-36(s1)
80003444:	0705                	addi	a4,a4,1
80003446:	fee49e23          	sh	a4,-4(s1)
8000344a:	0027f713          	andi	a4,a5,2
8000344e:	cf0d                	beqz	a4,80003488 <main+0x2f2>
80003450:	016404b3          	add	s1,s0,s6
80003454:	048a                	slli	s1,s1,0x2
80003456:	0814                	addi	a3,sp,16
80003458:	05048713          	addi	a4,s1,80
8000345c:	00d704b3          	add	s1,a4,a3
80003460:	ff84d603          	lhu	a2,-8(s1)
80003464:	00cbd683          	lhu	a3,12(s7)
80003468:	02d60063          	beq	a2,a3,80003488 <main+0x2f2>
8000346c:	85da                	mv	a1,s6
8000346e:	00000517          	auipc	a0,0x0
80003472:	47650513          	addi	a0,a0,1142 # 800038e4 <main+0x74e>
80003476:	c10ff0ef          	jal	80002886 <printf>
8000347a:	ffc4d703          	lhu	a4,-4(s1)
8000347e:	fdc4a783          	lw	a5,-36(s1)
80003482:	0705                	addi	a4,a4,1
80003484:	fee49e23          	sh	a4,-4(s1)
80003488:	945a                	add	s0,s0,s6
8000348a:	8b91                	andi	a5,a5,4
8000348c:	040a                	slli	s0,s0,0x2
8000348e:	d7b1                	beqz	a5,800033da <main+0x244>
80003490:	05040793          	addi	a5,s0,80
80003494:	0818                	addi	a4,sp,16
80003496:	00e78433          	add	s0,a5,a4
8000349a:	ffa45603          	lhu	a2,-6(s0)
8000349e:	018bd683          	lhu	a3,24(s7)
800034a2:	22d61463          	bne	a2,a3,800036ca <main+0x534>
800034a6:	ffc45783          	lhu	a5,-4(s0)
800034aa:	bf1d                	j	800033e0 <main+0x24a>
800034ac:	4705                	li	a4,1
800034ae:	bd19                	j	800032c4 <main+0x12e>
800034b0:	06600793          	li	a5,102
800034b4:	02f11023          	sh	a5,32(sp)
800034b8:	b391                	j	800031fc <main+0x66>
800034ba:	6441                	lui	s0,0x10
800034bc:	fff40493          	addi	s1,s0,-1 # ffff <_tbss_end+0xffbb>
800034c0:	59fd                	li	s3,-1
800034c2:	81818a93          	addi	s5,gp,-2024 # 800040f8 <default_num_contexts>
800034c6:	dd9fe0ef          	jal	8000229e <check_data_types>
800034ca:	55d2                	lw	a1,52(sp)
800034cc:	94aa                	add	s1,s1,a0
800034ce:	00000517          	auipc	a0,0x0
800034d2:	47a50513          	addi	a0,a0,1146 # 80003948 <main+0x7b2>
800034d6:	bb0ff0ef          	jal	80002886 <printf>
800034da:	85ca                	mv	a1,s2
800034dc:	00000517          	auipc	a0,0x0
800034e0:	48450513          	addi	a0,a0,1156 # 80003960 <main+0x7ca>
800034e4:	ba2ff0ef          	jal	80002886 <printf>
800034e8:	854a                	mv	a0,s2
800034ea:	deffe0ef          	jal	800022d8 <time_in_secs>
800034ee:	a02a                	fsd	fa0,0(sp)
800034f0:	4602                	lw	a2,0(sp)
800034f2:	4692                	lw	a3,4(sp)
800034f4:	00000517          	auipc	a0,0x0
800034f8:	48450513          	addi	a0,a0,1156 # 80003978 <main+0x7e2>
800034fc:	04c2                	slli	s1,s1,0x10
800034fe:	b88ff0ef          	jal	80002886 <printf>
80003502:	854a                	mv	a0,s2
80003504:	dd5fe0ef          	jal	800022d8 <time_in_secs>
80003508:	d20007d3          	fcvt.d.w	fa5,zero
8000350c:	80c1                	srli	s1,s1,0x10
8000350e:	a2a797d3          	flt.d	a5,fa5,fa0
80003512:	cb85                	beqz	a5,80003542 <main+0x3ac>
80003514:	000aa703          	lw	a4,0(s5)
80003518:	57e2                	lw	a5,56(sp)
8000351a:	b4a2                	fsd	fs0,104(sp)
8000351c:	854a                	mv	a0,s2
8000351e:	02e787b3          	mul	a5,a5,a4
80003522:	d2178453          	fcvt.d.wu	fs0,a5
80003526:	db3fe0ef          	jal	800022d8 <time_in_secs>
8000352a:	00000517          	auipc	a0,0x0
8000352e:	46650513          	addi	a0,a0,1126 # 80003990 <main+0x7fa>
80003532:	1aa477d3          	fdiv.d	fa5,fs0,fa0
80003536:	a03e                	fsd	fa5,0(sp)
80003538:	4602                	lw	a2,0(sp)
8000353a:	4692                	lw	a3,4(sp)
8000353c:	b4aff0ef          	jal	80002886 <printf>
80003540:	3426                	fld	fs0,104(sp)
80003542:	854a                	mv	a0,s2
80003544:	d95fe0ef          	jal	800022d8 <time_in_secs>
80003548:	00001797          	auipc	a5,0x1
8000354c:	ba07b787          	fld	fa5,-1120(a5) # 800040e8 <.got.plt+0x10>
80003550:	a2f517d3          	flt.d	a5,fa0,fa5
80003554:	20079c63          	bnez	a5,8000376c <main+0x5d6>
80003558:	000aa783          	lw	a5,0(s5)
8000355c:	55e2                	lw	a1,56(sp)
8000355e:	00000517          	auipc	a0,0x0
80003562:	48a50513          	addi	a0,a0,1162 # 800039e8 <main+0x852>
80003566:	04c2                	slli	s1,s1,0x10
80003568:	02f585b3          	mul	a1,a1,a5
8000356c:	84c1                	srai	s1,s1,0x10
8000356e:	b18ff0ef          	jal	80002886 <printf>
80003572:	00000597          	auipc	a1,0x0
80003576:	48e58593          	addi	a1,a1,1166 # 80003a00 <main+0x86a>
8000357a:	00000517          	auipc	a0,0x0
8000357e:	49250513          	addi	a0,a0,1170 # 80003a0c <main+0x876>
80003582:	b04ff0ef          	jal	80002886 <printf>
80003586:	00000597          	auipc	a1,0x0
8000358a:	49e58593          	addi	a1,a1,1182 # 80003a24 <main+0x88e>
8000358e:	00000517          	auipc	a0,0x0
80003592:	52a50513          	addi	a0,a0,1322 # 80003ab8 <main+0x922>
80003596:	af0ff0ef          	jal	80002886 <printf>
8000359a:	00000597          	auipc	a1,0x0
8000359e:	53658593          	addi	a1,a1,1334 # 80003ad0 <main+0x93a>
800035a2:	00000517          	auipc	a0,0x0
800035a6:	57e50513          	addi	a0,a0,1406 # 80003b20 <main+0x98a>
800035aa:	adcff0ef          	jal	80002886 <printf>
800035ae:	85d2                	mv	a1,s4
800035b0:	00000517          	auipc	a0,0x0
800035b4:	58850513          	addi	a0,a0,1416 # 80003b38 <main+0x9a2>
800035b8:	aceff0ef          	jal	80002886 <printf>
800035bc:	57f2                	lw	a5,60(sp)
800035be:	0017f713          	andi	a4,a5,1
800035c2:	cb1d                	beqz	a4,800035f8 <main+0x462>
800035c4:	000aa703          	lw	a4,0(s5)
800035c8:	cb05                	beqz	a4,800035f8 <main+0x462>
800035ca:	4401                	li	s0,0
800035cc:	00441793          	slli	a5,s0,0x4
800035d0:	97a2                	add	a5,a5,s0
800035d2:	078a                	slli	a5,a5,0x2
800035d4:	978a                	add	a5,a5,sp
800035d6:	0567d603          	lhu	a2,86(a5)
800035da:	85a2                	mv	a1,s0
800035dc:	00000517          	auipc	a0,0x0
800035e0:	57850513          	addi	a0,a0,1400 # 80003b54 <main+0x9be>
800035e4:	aa2ff0ef          	jal	80002886 <printf>
800035e8:	0405                	addi	s0,s0,1
800035ea:	000aa783          	lw	a5,0(s5)
800035ee:	0442                	slli	s0,s0,0x10
800035f0:	8041                	srli	s0,s0,0x10
800035f2:	fcf46de3          	bltu	s0,a5,800035cc <main+0x436>
800035f6:	57f2                	lw	a5,60(sp)
800035f8:	0027f713          	andi	a4,a5,2
800035fc:	cf05                	beqz	a4,80003634 <main+0x49e>
800035fe:	000aa703          	lw	a4,0(s5)
80003602:	1a070763          	beqz	a4,800037b0 <main+0x61a>
80003606:	4401                	li	s0,0
80003608:	00441793          	slli	a5,s0,0x4
8000360c:	97a2                	add	a5,a5,s0
8000360e:	078a                	slli	a5,a5,0x2
80003610:	978a                	add	a5,a5,sp
80003612:	0587d603          	lhu	a2,88(a5)
80003616:	85a2                	mv	a1,s0
80003618:	00000517          	auipc	a0,0x0
8000361c:	55850513          	addi	a0,a0,1368 # 80003b70 <main+0x9da>
80003620:	a66ff0ef          	jal	80002886 <printf>
80003624:	0405                	addi	s0,s0,1
80003626:	000aa783          	lw	a5,0(s5)
8000362a:	0442                	slli	s0,s0,0x10
8000362c:	8041                	srli	s0,s0,0x10
8000362e:	fcf46de3          	bltu	s0,a5,80003608 <main+0x472>
80003632:	57f2                	lw	a5,60(sp)
80003634:	8b91                	andi	a5,a5,4
80003636:	cb95                	beqz	a5,8000366a <main+0x4d4>
80003638:	000aa783          	lw	a5,0(s5)
8000363c:	4401                	li	s0,0
8000363e:	cfb9                	beqz	a5,8000369c <main+0x506>
80003640:	00441793          	slli	a5,s0,0x4
80003644:	97a2                	add	a5,a5,s0
80003646:	078a                	slli	a5,a5,0x2
80003648:	978a                	add	a5,a5,sp
8000364a:	05a7d603          	lhu	a2,90(a5)
8000364e:	85a2                	mv	a1,s0
80003650:	00000517          	auipc	a0,0x0
80003654:	53c50513          	addi	a0,a0,1340 # 80003b8c <main+0x9f6>
80003658:	a2eff0ef          	jal	80002886 <printf>
8000365c:	0405                	addi	s0,s0,1
8000365e:	000aa783          	lw	a5,0(s5)
80003662:	0442                	slli	s0,s0,0x10
80003664:	8041                	srli	s0,s0,0x10
80003666:	fcf46de3          	bltu	s0,a5,80003640 <main+0x4aa>
8000366a:	000aa783          	lw	a5,0(s5)
8000366e:	4401                	li	s0,0
80003670:	c795                	beqz	a5,8000369c <main+0x506>
80003672:	00441793          	slli	a5,s0,0x4
80003676:	97a2                	add	a5,a5,s0
80003678:	078a                	slli	a5,a5,0x2
8000367a:	978a                	add	a5,a5,sp
8000367c:	0547d603          	lhu	a2,84(a5)
80003680:	85a2                	mv	a1,s0
80003682:	00000517          	auipc	a0,0x0
80003686:	52650513          	addi	a0,a0,1318 # 80003ba8 <main+0xa12>
8000368a:	9fcff0ef          	jal	80002886 <printf>
8000368e:	0405                	addi	s0,s0,1
80003690:	000aa783          	lw	a5,0(s5)
80003694:	0442                	slli	s0,s0,0x10
80003696:	8041                	srli	s0,s0,0x10
80003698:	fcf46de3          	bltu	s0,a5,80003672 <main+0x4dc>
8000369c:	c0ad                	beqz	s1,800036fe <main+0x568>
8000369e:	04904963          	bgtz	s1,800036f0 <main+0x55a>
800036a2:	00000517          	auipc	a0,0x0
800036a6:	58e50513          	addi	a0,a0,1422 # 80003c30 <main+0xa9a>
800036aa:	a0cff0ef          	jal	800028b6 <puts>
800036ae:	05e10513          	addi	a0,sp,94
800036b2:	c41fe0ef          	jal	800022f2 <portable_fini>
800036b6:	40fa                	lw	ra,156(sp)
800036b8:	446a                	lw	s0,152(sp)
800036ba:	44da                	lw	s1,148(sp)
800036bc:	494a                	lw	s2,144(sp)
800036be:	49ba                	lw	s3,140(sp)
800036c0:	4a2a                	lw	s4,136(sp)
800036c2:	4a9a                	lw	s5,132(sp)
800036c4:	4501                	li	a0,0
800036c6:	610d                	addi	sp,sp,160
800036c8:	8082                	ret
800036ca:	85da                	mv	a1,s6
800036cc:	00000517          	auipc	a0,0x0
800036d0:	24c50513          	addi	a0,a0,588 # 80003918 <main+0x782>
800036d4:	9b2ff0ef          	jal	80002886 <printf>
800036d8:	ffc45783          	lhu	a5,-4(s0)
800036dc:	0785                	addi	a5,a5,1
800036de:	07c2                	slli	a5,a5,0x10
800036e0:	83c1                	srli	a5,a5,0x10
800036e2:	fef41e23          	sh	a5,-4(s0)
800036e6:	b9ed                	j	800033e0 <main+0x24a>
800036e8:	4b0a                	lw	s6,128(sp)
800036ea:	5bf6                	lw	s7,124(sp)
800036ec:	5c66                	lw	s8,120(sp)
800036ee:	bbe1                	j	800034c6 <main+0x330>
800036f0:	00000517          	auipc	a0,0x0
800036f4:	5a450513          	addi	a0,a0,1444 # 80003c94 <main+0xafe>
800036f8:	9beff0ef          	jal	800028b6 <puts>
800036fc:	bf4d                	j	800036ae <main+0x518>
800036fe:	00000517          	auipc	a0,0x0
80003702:	4c650513          	addi	a0,a0,1222 # 80003bc4 <main+0xa2e>
80003706:	9b0ff0ef          	jal	800028b6 <puts>
8000370a:	478d                	li	a5,3
8000370c:	faf991e3          	bne	s3,a5,800036ae <main+0x518>
80003710:	000aa703          	lw	a4,0(s5)
80003714:	57e2                	lw	a5,56(sp)
80003716:	b4a2                	fsd	fs0,104(sp)
80003718:	854a                	mv	a0,s2
8000371a:	02e787b3          	mul	a5,a5,a4
8000371e:	d2178453          	fcvt.d.wu	fs0,a5
80003722:	bb7fe0ef          	jal	800022d8 <time_in_secs>
80003726:	00000717          	auipc	a4,0x0
8000372a:	2da70713          	addi	a4,a4,730 # 80003a00 <main+0x86a>
8000372e:	1aa477d3          	fdiv.d	fa5,fs0,fa0
80003732:	00000797          	auipc	a5,0x0
80003736:	2f278793          	addi	a5,a5,754 # 80003a24 <main+0x88e>
8000373a:	00000517          	auipc	a0,0x0
8000373e:	4d250513          	addi	a0,a0,1234 # 80003c0c <main+0xa76>
80003742:	a03e                	fsd	fa5,0(sp)
80003744:	4602                	lw	a2,0(sp)
80003746:	4692                	lw	a3,4(sp)
80003748:	93eff0ef          	jal	80002886 <printf>
8000374c:	00001797          	auipc	a5,0x1
80003750:	97078793          	addi	a5,a5,-1680 # 800040bc <mem_name>
80003754:	438c                	lw	a1,0(a5)
80003756:	00000517          	auipc	a0,0x0
8000375a:	4d250513          	addi	a0,a0,1234 # 80003c28 <main+0xa92>
8000375e:	928ff0ef          	jal	80002886 <printf>
80003762:	4529                	li	a0,10
80003764:	f1bfe0ef          	jal	8000267e <putchar>
80003768:	3426                	fld	fs0,104(sp)
8000376a:	b791                	j	800036ae <main+0x518>
8000376c:	00000517          	auipc	a0,0x0
80003770:	23c50513          	addi	a0,a0,572 # 800039a8 <main+0x812>
80003774:	942ff0ef          	jal	800028b6 <puts>
80003778:	0485                	addi	s1,s1,1
8000377a:	bbf9                	j	80003558 <main+0x3c2>
8000377c:	00000517          	auipc	a0,0x0
80003780:	05450513          	addi	a0,a0,84 # 800037d0 <main+0x63a>
80003784:	932ff0ef          	jal	800028b6 <puts>
80003788:	4981                	li	s3,0
8000378a:	b12d                	j	800033b4 <main+0x21e>
8000378c:	00000517          	auipc	a0,0x0
80003790:	07050513          	addi	a0,a0,112 # 800037fc <main+0x666>
80003794:	922ff0ef          	jal	800028b6 <puts>
80003798:	4985                	li	s3,1
8000379a:	b929                	j	800033b4 <main+0x21e>
8000379c:	00000517          	auipc	a0,0x0
800037a0:	0ec50513          	addi	a0,a0,236 # 80003888 <main+0x6f2>
800037a4:	912ff0ef          	jal	800028b6 <puts>
800037a8:	4991                	li	s3,4
800037aa:	b129                	j	800033b4 <main+0x21e>
800037ac:	4481                	li	s1,0
800037ae:	bb21                	j	800034c6 <main+0x330>
800037b0:	8b91                	andi	a5,a5,4
800037b2:	ea078ce3          	beqz	a5,8000366a <main+0x4d4>
800037b6:	b5dd                	j	8000369c <main+0x506>
800037b8:	1141                	addi	sp,sp,-16
800037ba:	00000517          	auipc	a0,0x0
800037be:	5ce50513          	addi	a0,a0,1486 # 80003d88 <main+0xbf2>
800037c2:	c606                	sw	ra,12(sp)
800037c4:	febfe0ef          	jal	800027ae <printstr>
800037c8:	40b2                	lw	ra,12(sp)
800037ca:	557d                	li	a0,-1
800037cc:	0141                	addi	sp,sp,16
800037ce:	8082                	ret
