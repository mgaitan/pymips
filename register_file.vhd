-- File: register_file.vhd
-- Generated by MyHDL 0.6
-- Date: Wed Nov  3 21:49:50 2010

library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;
use std.textio.all;

use work.pck_myhdl_06.all;

entity register_file is
    port (
        read_reg1: in unsigned(4 downto 0);
        read_reg2: in unsigned(4 downto 0);
        write_reg: in unsigned(4 downto 0);
        data_in: in signed (31 downto 0);
        write_control: in unsigned(0 downto 0);
        out_data1: out signed (31 downto 0);
        out_data2: out signed (31 downto 0)
    );
end entity register_file;

architecture MyHDL of register_file is

type t_array_mem is array(0 to 32-1) of signed (31 downto 0);
signal mem: t_array_mem;

begin


REGISTER_FILE_WRITE: process (write_control, data_in, write_reg) is
begin
    if to_boolean(write_control) then
        mem(to_integer(write_reg)) <= data_in;
    end if;
end process REGISTER_FILE_WRITE;

REGISTER_FILE_READ: process (mem(0), mem(1), mem(2), mem(3), mem(4), mem(5), mem(6), mem(7), mem(8), mem(9), mem(10), mem(11), mem(12), mem(13), mem(14), mem(15), mem(16), mem(17), mem(18), mem(19), mem(20), mem(21), mem(22), mem(23), mem(24), mem(25), mem(26), mem(27), mem(28), mem(29), mem(30), mem(31), read_reg1, write_control, read_reg2) is
begin
    if (not to_boolean(write_control)) then
        out_data1 <= mem(to_integer(read_reg1));
        out_data2 <= mem(to_integer(read_reg2));
    end if;
end process REGISTER_FILE_READ;

end architecture MyHDL;
