import unittest
import random

from myhdl import Signal, intbv, Simulation, delay

from pymips.alu import ALU

class TestALU(unittest.TestCase):

    def setUp(self):
        self.control_i = Signal(intbv(0)[4:])
        self.op1_i = Signal(intbv(0)[32:])
        self.op2_i = Signal(intbv(0)[32:])
        self.out_i = Signal(intbv(0,  min=-(2**31), max=2**31-1))
        self.zero_i = Signal(bool(False))

        self.alu_i = ALU(self.control_i, self.op1_i, self.op2_i, self.out_i, self.zero_i)

        #control_func = (('0000', 'AND'), ('0001', 'OR'),  ('0010', 'add'), ('0110', 'substract'), ('0111', 'set on <'), ('1100', 'NOR') )

    def testBench_add(self):

        def stimulus():

            a, b = self.op1_i.next, self.op2_i.next = [Signal(intbv(random.randint(0, 255))[32:]) for i in range(2)]

            self.control_i.next = intbv('0010')[4:] #add function
            expected = a + b
            yield delay(1)

            self.assertEqual(int(self.out_i), expected)

        sim = Simulation(self.alu_i, stimulus())
        sim.run()


def main():
    unittest.main()

if __name__ == '__main__':
    main()
