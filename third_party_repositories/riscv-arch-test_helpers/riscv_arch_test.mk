############
# DEFAULTS #
############

RISCV_ARCH_TEST_PATH    := /eda/processor_ci_tests/third_party_repositories/riscv-arch-test
RV32I_TESTS_PATH        := $(RISCV_ARCH_TEST_PATH)/riscv-test-suite/rv32i_m/I/src
SINGLE_TEST_NAME        := add-01.S

ROOT_BUILD_DIR          := $(RISCV_ARCH_TEST_PATH)/riscof-plugins/rv32/riscof_work
TARGET_DIR              := $(ROOT_BUILD_DIR)/$(SINGLE_TEST_NAME)/dut
TARGET                  := $(TARGET_DIR)/$(patsubst %.S,%.elf,$(SINGLE_TEST_NAME))
DUMP_TARGET 			:= $(TARGET_DIR)/$(patsubst %.S,%.dump,$(SINGLE_TEST_NAME))

#########
# RULES #
#########

all: dirs compile dump

dirs:
	mkdir -p $(TARGET_DIR)

# build elf and dump the assembly
# default Linker: -T $(RISCV_ARCH_TEST_PATH)/riscof-plugins/rv32/spike_simple/env/link.ld
# new linker    : -T /eda/processor_ci_tests/third_party_repositories/helpers_riscv-arch-test/linkText0x0.ld
compile: $(RV32I_TESTS_PATH)/$(SINGLE_TEST_NAME)
	riscv32-unknown-elf-gcc -march=rv32i -static -mcmodel=medany -fvisibility=hidden -nostdlib -nostartfiles -g \
		-T /eda/processor_ci_tests/third_party_repositories/helpers_riscv-arch-test/linkText0x0.ld \
		-I $(RISCV_ARCH_TEST_PATH)/riscof-plugins/rv32/spike_simple/env/ \
		-I $(RISCV_ARCH_TEST_PATH)/riscv-test-suite/env \
		$(RV32I_TESTS_PATH)/$(SINGLE_TEST_NAME) -o $(TARGET) \
		-DTEST_CASE_1=True -DXLEN=32 -mabi=ilp32

dump: $(TARGET)
	riscv32-unknown-elf-objdump -D $(TARGET) > $(DUMP_TARGET)

clean:
	rm -rf $(ROOT_BUILD_DIR)/*


############################################

.PHONY: compile-folder

# Discover all .S sources and corresponding per-test ELF targets
ALL_SRCS := $(wildcard $(RV32I_TESTS_PATH)/*.S)
ALL_ELF_TARGETS := $(patsubst $(RV32I_TESTS_PATH)/%.S,$(COMPILE_FOLDER_TARGET_DIR)/%.elf,$(ALL_SRCS))


COMPILE_FOLDER_TARGET_DIR ?= $(RISCV_ARCH_TEST_PATH)/build_tests
compile-folder: $(ALL_ELF_TARGETS)
# Pattern rule: build each source into its own work folder
$(COMPILE_FOLDER_TARGET_DIR)/%.elf: $(RV32I_TESTS_PATH)/%.S
	@mkdir -p $(dir $@)
	riscv32-unknown-elf-gcc -march=rv32i -static -mcmodel=medany -fvisibility=hidden -nostdlib -nostartfiles -g \
		-T /eda/processor_ci_tests/third_party_repositories/helpers_riscv-arch-test/linkText0x0.ld \
		-I $(RISCV_ARCH_TEST_PATH)/riscof-plugins/rv32/spike_simple/env/ \
		-I $(RISCV_ARCH_TEST_PATH)/riscv-test-suite/env \
		$< -o $@ \
		-DTEST_CASE_1=True -DXLEN=32 -mabi=ilp32