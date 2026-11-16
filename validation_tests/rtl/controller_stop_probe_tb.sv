`timescale 1ns/1ps

// Only UART transport is stubbed. Controller, Interpreter, Memory, Timer, and
// ClkDivider are compiled from the neighboring RTL repository.
module UART #(
    parameter CLK_FREQ=25000000, BIT_RATE=9600, PAYLOAD_BITS=8,
    BUFFER_SIZE=8, WORD_SIZE_BY=4
) (
    input logic clk, rst_n, rx, read, write,
    input logic [31:0] write_data,
    output logic tx, uart_rx_empty, uart_tx_empty, read_response, write_response,
    output logic [31:0] read_data
);
    assign tx = 1'b1;
    assign uart_rx_empty = 1'b1;
    assign uart_tx_empty = 1'b1;
    assign read_response = 1'b0;
    assign write_response = 1'b0;
    assign read_data = 32'b0;
endmodule

module controller_stop_probe_tb;
    logic clk = 0;
    always #5 clk = ~clk;
    logic rst_n = 0;
    logic core_cyc = 0, core_stb = 0, core_we = 0;
    logic [31:0] core_addr = 0, core_data = 0;
    wire [31:0] core_read;
    wire core_ack, tx, intr, clk_core, rst_core;
`ifdef ENABLE_SECOND_MEMORY
    logic data_cyc = 0, data_stb = 0, data_we = 0;
    logic [31:0] data_addr = 0, data_write = 0;
    wire [31:0] data_read;
    wire data_ack;
`endif

    Controller #(.MEMORY_SIZE(8192)) dut (
        .clk(clk), .rst_n(rst_n), .sck_i(1'b0), .cs_i(1'b1),
        .mosi_i(1'b0), .miso_o(1'b0), .rw_i(1'b0), .intr_o(intr),
        .rx(1'b1), .tx(tx), .clk_core_o(clk_core), .rst_core_o(rst_core),
        .core_cyc_i(core_cyc), .core_stb_i(core_stb), .core_we_i(core_we),
        .core_addr_i(core_addr), .core_data_i(core_data),
        .core_data_o(core_read), .core_ack_o(core_ack)
`ifdef ENABLE_SECOND_MEMORY
        , .data_mem_cyc_i(data_cyc), .data_mem_stb_i(data_stb),
        .data_mem_we_i(data_we), .data_mem_addr_i(data_addr),
        .data_mem_data_i(data_write), .data_mem_data_o(data_read),
        .data_mem_ack_o(data_ack)
`endif
    );

    initial begin
        repeat (4) @(negedge clk);
        rst_n = 1;
        force dut.memory_mux_selector = 1'b1;
        force dut.reset_bus = 1'b0;
        force dut.bus_mode = 1'b0;
        force dut.end_position = 32'h100;
        repeat (2) @(negedge clk);
        if (dut.finish_execution !== 1'b0) $fatal(1, "unexpected initial finish");

        // Idle and read address matches must not stop execution.
        core_addr = 32'h100;
        repeat (2) @(negedge clk);
        if (dut.finish_execution !== 1'b0) $fatal(1, "idle address match stopped execution");
        core_cyc = 1;
        core_stb = 1;
        repeat (2) @(negedge clk);
        if (dut.finish_execution !== 1'b0) $fatal(1, "read address match stopped execution");
        core_we = 1;
        repeat (2) @(negedge clk);
        if (dut.finish_execution !== 1'b1) $fatal(1, "acknowledged primary write did not stop execution");
        $display("RTL_PRIMARY_WRITE_QUALIFIED_FINISH");

        force dut.reset_bus = 1'b1;
        repeat (2) @(negedge clk);
        if (dut.finish_execution !== 1'b0) $fatal(1, "reset did not clear finish");
        core_cyc = 0;
        core_stb = 0;
        core_we = 0;
`ifdef ENABLE_SECOND_MEMORY
        data_addr = 32'h100;
        repeat (2) @(negedge clk);
        if (dut.finish_execution !== 1'b0) $fatal(1, "idle data address match stopped execution");
        data_cyc = 1;
        data_stb = 1;
        repeat (2) @(negedge clk);
        if (dut.finish_execution !== 1'b0) $fatal(1, "data read address match stopped execution");
        data_we = 1;
        repeat (2) @(negedge clk);
        if (dut.finish_execution !== 1'b0) $fatal(1, "reset_bus did not hold finish clear");
        release dut.reset_bus;
        repeat (2) @(negedge clk);
        if (dut.finish_execution !== 1'b1) $fatal(1, "acknowledged data write did not stop execution");
        $display("RTL_DATA_WRITE_QUALIFIED_FINISH");
`else
        release dut.reset_bus;
`endif
        $finish;
    end
endmodule
