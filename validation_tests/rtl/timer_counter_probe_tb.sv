module timer_counter_probe_tb;
    logic clk = 0;
    logic rst_n = 0;
    logic upper_i = 0;
    wire [31:0] read_o;
    wire [63:0] long_read_o;
    logic [31:0] first_read, second_read;

    always #5 clk = ~clk;

    Timer dut (
        .clk(clk), .rst_n(rst_n), .upper_i(upper_i),
        .read_o(read_o), .long_read_o(long_read_o)
    );

    initial begin
        repeat (2) @(negedge clk);
        rst_n = 1;
        @(negedge clk);
        first_read = read_o;
        repeat (4) @(negedge clk);
        second_read = read_o;
        if (second_read - first_read != 4) $fatal(1, "timer did not advance by four cycles");
        upper_i = 1;
        #1;
        if (read_o != 0) $fatal(1, "upper timer word was not zero after reset");
        $display("TIMER_COUNTER_PROBE_PASS");
        $finish;
    end
endmodule
