`timescale 1ns/1ps

module act4_cv32e40s_serial_tb;
    logic clk = 0;
    always #5 clk = ~clk;
    logic rst_n = 0, rx = 1;
    wire tx, miso, intr;
    logic [31:0] status_address, expected_status;
    logic [31:0] host_words [0:131071];
    logic [31:0] segment_ranges [0:127];
    integer segment_count;
    byte reply [0:7];
    processorci_top ptop (
        .sys_clk(clk), .rst_n(rst_n), .rx(rx), .tx(tx),
        .sck(1'b0), .cs(1'b1), .mosi(1'b0), .miso(miso),
        .rw(1'b0), .intr(intr)
    );

    task automatic send_byte(input byte value);
        @(negedge clk); rx = 0;
        repeat (11) @(negedge clk);
        for (int bit_index = 0; bit_index < 8; bit_index++) begin
            rx = value[bit_index];
            repeat (11) @(negedge clk);
        end
        rx = 1;
        repeat (12) @(negedge clk);
    endtask

    task automatic send_command(input byte opcode, input logic [23:0] immediate);
        logic [31:0] command_word;
        command_word = {immediate, opcode};
        for (int byte_index = 3; byte_index >= 0; byte_index--)
            send_byte(command_word[8*byte_index +: 8]);
    endtask

    task automatic receive_byte(output byte value);
        @(negedge tx);
        repeat (16) @(negedge clk);
        for (int bit_index = 0; bit_index < 8; bit_index++) begin
            value[bit_index] = tx;
            repeat (11) @(negedge clk);
        end
        if (tx !== 1'b1) $fatal(1, "serial stop bit missing");
    endtask

    task automatic send_word(input logic [31:0] value);
        for (int byte_index = 3; byte_index >= 0; byte_index--)
            send_byte(value[8*byte_index +: 8]);
    endtask

    task automatic receive_word(output logic [31:0] value);
        byte fragment;
        value = 0;
        for (int byte_index = 0; byte_index < 4; byte_index++) begin
            receive_byte(fragment);
            value = {value[23:0], fragment};
        end
    endtask

    initial begin
        logic [31:0] readback;
        logic [31:0] diagnostic_count;
        if (!$value$plusargs("status=%h", status_address) ||
            !$value$plusargs("expected=%h", expected_status))
            $fatal(1, "status and expected plusargs are required");
        repeat (10) @(negedge clk);
        rst_n = 1;
        repeat (10) @(negedge clk);
        if ($test$plusargs("serial_load")) begin
            if (!$value$plusargs("segment_count=%d", segment_count) || segment_count > 64)
                $fatal(1, "valid segment count required");
            $readmemh("host_image.hex", host_words);
            $readmemh("ranges.hex", segment_ranges);
            for (int segment = 0; segment < segment_count; segment++) begin
                send_command(8'h55, segment_ranges[2*segment] >> 8);
                send_command(8'h6c, segment_ranges[2*segment][7:0]);
                send_command(8'h65, segment_ranges[2*segment+1]);
                for (int word_index = 0; word_index < segment_ranges[2*segment+1]; word_index++)
                    send_word(host_words[(segment_ranges[2*segment] >> 2) + word_index]);
                repeat (30) @(negedge clk);
            end
        end
        send_command(8'h55, status_address >> 8); // accumulator upper address
        send_command(8'h6c, status_address[7:0]);
        send_command(8'h65, 24'd1); // write one diagnostic status word
        send_word(32'hfeedbeef);
        repeat (30) @(negedge clk);
        send_command(8'h4c, status_address[25:2]);
        receive_word(readback);
        if (readback !== 32'hfeedbeef) $fatal(1, "serial write/readback failed: %08h", readback);
        send_command(8'h65, 24'd1); // clear tohost before ACT execution
        send_word(32'b0);
        repeat (30) @(negedge clk);
        send_command(8'h4c, status_address[25:2]);
        receive_word(readback);
        if (readback !== 0) $fatal(1, "serial status clear failed: %08h", readback);
        send_command(8'h54, $test$plusargs("expect_timeout") ? 24'd20000 : 24'd100000);
        repeat (30) @(negedge clk);
        send_command(8'h44, $test$plusargs("expect_timeout") ?
                     (status_address + 32'h40) >> 2 : status_address[25:2]);
        repeat (30) @(negedge clk);
        send_command(8'h75, 24'd0); // execute until status write
        for (int i = 0; i < 8; i++) receive_byte(reply[i]);
        if ({reply[0],reply[1],reply[2],reply[3]} !== 32'h6c75636b)
            $fatal(1, "bad completion marker %h %h %h %h", reply[0],reply[1],reply[2],reply[3]);
        if ($test$plusargs("expect_timeout")) begin
            if (reply[7][0]) $fatal(1, "controller missed requested timeout");
        end else if (!reply[7][0]) $fatal(1, "controller reported timeout");
        if (ptop.u_Controller.Shared_Memory_Bank.Core_Shared_Memory.memory[status_address >> 2]
            !== expected_status)
            $fatal(1, "status memory mismatch");
        send_command(8'h4c, status_address[25:2]);
        receive_word(readback);
        if (readback !== expected_status)
            $fatal(1, "ACT serial status readback mismatch: %08h", readback);
        send_command(8'h4c, 24'h7f000 >> 2);
        receive_word(readback);
        if (expected_status == 3 && readback == 0)
            $fatal(1, "ACT failure produced no serial-readable diagnostics");
        diagnostic_count = readback;
        if (expected_status == 3) begin
            $display("ACT_SERIAL_DIAGNOSTICS_BEGIN");
            for (int offset = 0; offset < diagnostic_count && offset < 1024; offset += 4) begin
                send_command(8'h4c, (24'h7f100 + offset) >> 2);
                receive_word(readback);
                for (int lane = 0; lane < 4 && offset + lane < diagnostic_count; lane++)
                    $write("%c", readback[8*lane +: 8]);
            end
            $display("\nACT_SERIAL_DIAGNOSTICS_END");
        end
        if ($test$plusargs("expect_timeout"))
            $display("ACT_SERIAL_TIMEOUT %08h DIAGNOSTIC_BYTES %0d", expected_status, diagnostic_count);
        else
            $display("ACT_SERIAL_STATUS %08h DIAGNOSTIC_BYTES %0d", expected_status, diagnostic_count);
        $finish;
    end

    initial begin
        repeat (40000000) @(posedge clk);
        $fatal(1, "serial ACT run timed out at PC %08h, interpreter state %0d",
               ptop.Processor.pc_if, ptop.u_Controller.Interpreter.state);
    end
endmodule
