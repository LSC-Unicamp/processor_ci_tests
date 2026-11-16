`timescale 1ns/1ps

module controller_shared_memory_tb;
    logic clk = 0;
    always #5 clk = ~clk;
    logic rst_n = 0;
    logic core_cyc = 0, core_stb = 0, core_we = 0;
    logic [3:0] core_sel = 4'hf;
    logic [31:0] core_addr = 0, core_write = 0;
    wire [31:0] core_read;
    wire core_ack, tx, intr, clk_core, rst_core;
    logic data_cyc = 0, data_stb = 0, data_we = 0;
    logic [3:0] data_sel = 4'hf;
    logic [31:0] data_addr = 0, data_write = 0;
    wire [31:0] data_read;
    wire data_ack;

    Controller #(.MEMORY_SIZE(524288), .SHARED_MEMORY(1)) dut (
        .clk(clk), .rst_n(rst_n), .sck_i(1'b0), .cs_i(1'b1),
        .mosi_i(1'b0), .miso_o(1'b0), .rw_i(1'b0), .intr_o(intr),
        .rx(1'b1), .tx(tx), .clk_core_o(clk_core), .rst_core_o(rst_core),
        .core_cyc_i(core_cyc), .core_stb_i(core_stb), .core_we_i(core_we),
        .core_sel_i(core_sel), .core_addr_i(core_addr), .core_data_i(core_write),
        .core_data_o(core_read), .core_ack_o(core_ack),
        .data_mem_cyc_i(data_cyc), .data_mem_stb_i(data_stb),
        .data_mem_we_i(data_we), .data_mem_sel_i(data_sel),
        .data_mem_addr_i(data_addr), .data_mem_data_i(data_write),
        .data_mem_data_o(data_read), .data_mem_ack_o(data_ack)
    );

    initial begin
        repeat (4) @(negedge clk);
        rst_n = 1;
        force dut.reset_bus = 1'b0;
        force dut.bus_mode = 1'b0;
        force dut.end_position = 32'h20020;
        force dut.memory_mux_selector = 1'b0;
        force dut.interpreter_memory_address = 32'h20020;
        force dut.interpreter_memory_write_data = 32'h11223344;
        force dut.interpreter_memory_write = 1'b1;
        force dut.interpreter_memory_read = 1'b0;
        repeat (2) @(negedge clk);
        if (!dut.interpreter_memory_response) $fatal(1, "serial load was not acknowledged");
        release dut.interpreter_memory_write;
        release dut.interpreter_memory_read;
        release dut.interpreter_memory_address;
        release dut.interpreter_memory_write_data;

        force dut.memory_mux_selector = 1'b1;
        data_cyc = 1; data_stb = 1; data_addr = 32'h20020;
        repeat (2) @(negedge clk);
        if (!data_ack || data_read !== 32'h11223344)
            $fatal(1, "core data port cannot see serial-loaded word");
        if (dut.finish_execution !== 1'b0) $fatal(1, "read stopped execution");

        data_we = 1; data_sel = 4'b0010; data_write = 32'h0000aa00;
        repeat (2) @(negedge clk);
        data_we = 0;
        #1;
        if (data_read !== 32'h1122aa44) $fatal(1, "byte enable lost: %h", data_read);
        data_we = 1; data_sel = 4'b1100; data_write = 32'hbeef0000;
        repeat (2) @(negedge clk);
        data_we = 0;
        #1;
        if (data_read !== 32'hbeefaa44) $fatal(1, "halfword enables lost: %h", data_read);
        if (dut.finish_execution !== 1'b1) $fatal(1, "status write did not stop execution");

        core_cyc = 1; core_stb = 1; core_addr = 32'h20020;
        repeat (2) @(negedge clk);
        if (!core_ack || core_read !== 32'hbeefaa44)
            $fatal(1, "instruction port cannot see data-port writes");
        core_addr = 32'h7f000;
        data_addr = 32'h7f000;
        repeat (2) @(negedge clk);
        if (core_ack || data_ack || core_read !== 0 || data_read !== 0)
            $fatal(1, "out-of-range access aliased into RAM");
        data_addr = 32'h10000000;
        data_we = 1; data_sel = 4'hf; data_write = 32'h00000041;
        repeat (2) @(negedge clk);
        if (!data_ack) $fatal(1, "ACT virtual printer did not acknowledge");
        data_cyc = 0; data_stb = 0; data_we = 0;
        force dut.memory_mux_selector = 1'b0;
        force dut.interpreter_memory_read = 1'b1;
        force dut.interpreter_memory_write = 1'b0;
        force dut.interpreter_memory_address = 32'h0007f000;
        #1;
        if (!dut.interpreter_memory_response || dut.interpreter_memory_read_data !== 2)
            $fatal(1, "diagnostic count not readable");
        force dut.interpreter_memory_address = 32'h0007f100;
        #1;
        if (dut.interpreter_memory_read_data[7:0] !== 8'h41)
            $fatal(1, "diagnostic text not readable");
        $display("RTL_SHARED_MEMORY_PASS");
        $finish;
    end
endmodule
