A MIPS processor implemented with Python
========================================

What it is
-----------

PyMIPS is a formal implementation of a MIPS_ pipelined processor.

In particular, it's a 5 stages DLX_ processor, as described in the book
*Computer Organization and Design* by John Hennessy and David Patterson
[PatHen05]_

It's was not tested in hardware, but its (VHDL) description was tested and simulated
succesfully and should be ready to try in a FPGA_


How it is implemented
---------------------

To describe hardware formally, a HDL_ computer language is necessary.
Popular HDL languages are VHDL_ and Verilog but I need
(because I have no time nor stomach to that kind of
evilness) and want to use Python.

So, MyHDL_ was my option.

How to try it
-------------

PyMIPS isn't a traditional *for-end-user* software. Instead, you could
think about it as MIPS procesor simulator: a program to run your (trivial)
programs.

Install
++++++++

PyMIPS requires only MyHDL_ to run. To install you could use pip::

 $ git clone https://github.com/nqnwebs/pymips.git
 $ cd pymips
 $ pip install -r requirements.txt

(As usual, I recommend to to this in a virtualenv)

Run
+++

The main module is ``dlx.py``. PyMIPS execute a simple RISC bytecode (HEX data).
By default it runs ``programs/simple.txt``::

  $ python pymips/dlx.py

No compiler is given, but you could check the default program to write your own
and run as argument::

  $ python pymips/dlx.py your_program.txt

Documentation
-------------

There is a report (in spanish) which was the academic document of this project
You can `download from here <https://github.com/downloads/nqnwebs/pymips/informe.pdf>`_ (pdf - 0.6mb)


Feedback
--------

Would you like to continue this project? May be try it in real hardware ?
Or add a GUI and use as user-friendly simulator ?

So, I would like to read from you. Please write me
to gaitan(at)gmail.com


How this project was born
--------------------------

From http://article.gmane.org/gmane.comp.python.myhdl/1536/ :

    Hi everybody.

    this is the situation: I'm a student  with one subject left (and the final
    project, which it's almost cooked [1]_ )  to get a dregree in Computer Engineering
    [2]_ at Córdoba, Argentina. This subject is computer architecture.

    To pass and be happy I must implement a DLX/MIPS pipelined processor. I would like to get my degree someday in the rest of 2010.
    I forget what I ever knew about VHDL and I never knew Verilog. but I enjoy very much programming python.

    My gantt diagram says that I have a month to do this.  Do you think MyHDL it's my workhorse ?

    seriously, I'll be bothering here for a while. be patience. and thanks in advance.

    BTW, any open source MIPS-like project in MyHDL over there?






.. _MIPS: http://en.wikipedia.org/wiki/MIPS_architecture
.. _HDL : http://en.wikipedia.org/wiki/Hardware_description_language
.. _VHDL: http://en.wikipedia.org/wiki/VHDL
.. _DLX: http://en.wikipedia.org/wiki/DLX
.. _FPGA: http://en.wikipedia.org/wiki/FPGA
.. _MyHDL: http://myhdl.org

.. [1] http://code.google.com/p/gpec2010/
.. [2] http://computacion.efn.uncor.edu/  (probably a 404, the net and electric lines at the university sucks)

.. [PatHen05] : *Computer Organization and Design, 3th
                                        edition*, David Patterson and John
                                        Hennessy, Morgan Kaufmman Publishers,
                                        CA, 2005
