`timescale 1ns/1ps

module act4_cv32e40s_controller_tb;
    logic clk = 0;
    always #5 clk = ~clk;
    logic rst_n = 0;
    wire tx, miso, intr;
    processorci_top ptop (
        .sys_clk(clk), .rst_n(rst_n), .rx(1'b1), .tx(tx),
        .sck(1'b0), .cs(1'b1), .mosi(1'b0), .miso(miso),
        .rw(1'b0), .intr(intr)
    );

    integer cycle = 0;
    integer data_transactions = 0;
    logic [31:0] status_address, expected_status;
    initial begin
        if (!$value$plusargs("status=%h", status_address) ||
            !$value$plusargs("expected=%h", expected_status))
            $fatal(1, "status and expected plusargs are required");
        force ptop.clk_core = clk;
        force ptop.rst_core = 1'b1;
        force ptop.u_Controller.memory_mux_selector = 1'b1;
        force ptop.u_Controller.reset_bus = 1'b0;
        force ptop.u_Controller.bus_mode = 1'b0;
        force ptop.u_Controller.end_position = status_address;
        repeat (10) @(negedge clk);
        rst_n = 1;
        force ptop.rst_core = 1'b0;
        while (cycle < 250000) begin
            @(negedge clk);
            cycle++;
            if (ptop.data_mem_cyc && ptop.data_mem_stb) begin
                data_transactions++;
                if (data_transactions < 20 || ptop.data_mem_addr == status_address)
                    $display("DATA %0d %b %08h %08h ACK %b", cycle,
                             ptop.data_mem_we, ptop.data_mem_addr,
                             ptop.data_mem_data_out, ptop.data_mem_ack);
            end
            if (ptop.u_Controller.finish_execution) begin
                if (ptop.u_Controller.Shared_Memory_Bank.Core_Shared_Memory.memory[status_address >> 2]
                    !== expected_status)
                    $fatal(1, "status readback mismatch at cycle %0d", cycle);
                $display("ACT_CONTROLLER_STATUS %08h CYCLE %0d",
                         ptop.u_Controller.Shared_Memory_Bank.Core_Shared_Memory.memory[status_address >> 2], cycle);
                $finish;
            end
        end
        $fatal(1, "ACT controller timeout at PC %08h, status %08h, end %08h, data count %0d",
               ptop.Processor.pc_if,
               ptop.u_Controller.Shared_Memory_Bank.Core_Shared_Memory.memory[status_address >> 2],
               ptop.u_Controller.end_position, data_transactions);
    end
endmodule
