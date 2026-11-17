`timescale 1ns/1ps

module riscv_dv_ibex_controller_tb;
    logic clk = 0;
    always #5 clk = ~clk;
    logic rst_n = 1;
    wire tx, miso, intr;
    processorci_top ptop (
        .sys_clk(clk), .rst_n(rst_n), .rx(1'b1), .tx(tx),
        .sck(1'b0), .cs(1'b1), .mosi(1'b0), .miso(miso),
        .rw(1'b0), .intr(intr)
    );

    integer cycle = 0;
    logic [31:0] status_address;
    initial begin
        if (!$value$plusargs("status=%h", status_address))
            $fatal(1, "status plusarg is required");
        force ptop.clk_core = clk;
        force ptop.rst_core = 1'b1;
        force ptop.u_Controller.memory_mux_selector = 1'b1;
        force ptop.u_Controller.reset_bus = 1'b0;
        force ptop.u_Controller.bus_mode = 1'b0;
        force ptop.u_Controller.end_position = status_address;
        #1 rst_n = 0;
        repeat (10) @(negedge clk);
        rst_n = 1;
        force ptop.rst_core = 1'b0;
        while (cycle < 250000) begin
            @(negedge clk);
            cycle++;
            if (ptop.u_Controller.finish_execution) begin
                $display("IBEX_CONTROLLER_STATUS %08h CYCLE %0d",
                         ptop.u_Controller.Shared_Memory_Bank.Core_Shared_Memory.memory[status_address >> 2],
                         cycle);
                $finish;
            end
        end
        $fatal(1, "Ibex Controller timeout at PC %08h, status %08h",
               ptop.Processor.u_ibex_core.pc_if,
               ptop.u_Controller.Shared_Memory_Bank.Core_Shared_Memory.memory[status_address >> 2]);
    end
endmodule
