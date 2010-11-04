module tb_prime_detector;

reg [3:0] I;
wire [0:0] O;

initial begin
    $from_myhdl(
        I
    );
    $to_myhdl(
        O
    );
end

prime_detector dut(
    I,
    O
);

endmodule
