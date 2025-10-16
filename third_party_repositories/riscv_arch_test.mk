RISCV_ARCH_TEST_PATH    := /eda/processor_ci_tests/third_party_repositories/riscv-arch-test
RV32I_TESTS_PATH        := $(RISCV_ARCH_TEST_PATH)/riscv-test-suite/rv32i_m/I/src
SINGLE_TEST_NAME        := add-01.S

ROOT_BUILD_DIR          := $(RISCV_ARCH_TEST_PATH)/riscof-plugins/rv32/riscof_work
TARGET_DIR              := $(ROOT_BUILD_DIR)/$(SINGLE_TEST_NAME)/dut
TARGET                  := $(TARGET_DIR)/$(patsubst %.S,%.elf,$(SINGLE_TEST_NAME))

all: dirs $(TARGET)

dirs:
	mkdir -p $(TARGET_DIR)

# build elf and dump the assembly
$(TARGET): $(RV32I_TESTS_PATH)/$(SINGLE_TEST_NAME)
	riscv32-unknown-elf-gcc -march=rv32i -static -mcmodel=medany -fvisibility=hidden -nostdlib -nostartfiles -g \
		-T $(RISCV_ARCH_TEST_PATH)/riscof-plugins/rv32/spike_simple/env/link.ld \
		-I $(RISCV_ARCH_TEST_PATH)/riscof-plugins/rv32/spike_simple/env/ \
		-I $(RISCV_ARCH_TEST_PATH)/riscv-test-suite/env \
		$(RV32I_TESTS_PATH)/$(SINGLE_TEST_NAME) -o $(TARGET) \
		-DTEST_CASE_1=True -DXLEN=32 -mabi=ilp32
	riscv32-unknown-elf-objdump -D $(TARGET) > $(TARGET_DIR)/$(patsubst %.S,%.dump,$(SINGLE_TEST_NAME))

clean:
	rm -rf $(ROOT_BUILD_DIR)/*