========================================================================
Diseño y codificación de un procesador MIPS/DLX con pipeline de 5 etapas
========================================================================

:Autor: Martín Gaitán <gaitan@gmail.com>
:Docente: Adriana Damiani
:Fecha: Noviembre de 2010

:Asignatura: Arquitectura de computadoras, FCEFyN, UNC


.. header::

   .. oddeven::

      .. class:: headertable

      +---+---------------------+----------------+
      |   |.. class:: centered  |.. class:: right|
      |   |                     |                |
      |   | ###Section###       |     ###Page### |
      +---+---------------------+----------------+

      .. class:: headertable

      +---------------+---------------------+---+
      |               |.. class:: centered  |   |
      |               |                     |   |
      |     ###Page###|    ###Section###    |   |
      +---------------+---------------------+---+


.. contents::

.. section-numbering::


Introducción
============

En este trabajo se desarrolla y simula un procesador DLX utilizando el 
lenguaje de programación Python_ mediante el uso del paquete MyHDL_. 




Sobre el lenguaje
=================

Python es un lenguaje de programación de alto nivel cuya filosofía hace hincapié 
en una sintaxis muy limpia y legible.

Se trata de un lenguaje de programación multiparadigma ya que soporta 
orientación a objetos, programación imperativa y funcional. Es un lenguaje interpretado, 
usa tipado dinámico, es fuertemente tipado y es multiplataforma.

MyHDL es un paquete (un conjunto de módulos y funciones Python) que permite utilizar 
la potencia de alto nivel de Python en reemplazo de un lenguaje de descripción de hardware 
tradicional. Más aun, con algunas restricciones menores, el código Python-MyHDL 
es convertible a VHDL o Verilog automáticamente. 

También es posible generar un archivo de descripción de forma de onda de las 
señales (archivos * .vcd *) implicadas en un determinado diseño. 

En el sitio web de MyHDL_ se detallan muchas ventajas de su uso. [1]_

Entre ellas se destacan: 

 * Facilidad de uso: Python es mucho más fácil de aprender que VHDL o Verilog
 * Uso de técnicas modernas de desarrollo de software aplicadas al diseño de hardware:
   por ejemplo, pruebas unitarias, y la metodológia asociada *“test-driven development”*
 * Unificar diseño algoritmico y descripción de hardware
 * Centralizar el desarrollo cuando hay que codificar lo mismo en VHDL y Verilog
 * y mucho más... 


.. [1] http://www.myhdl.org/doku.php/why


.. _Python: http://python.org
.. _MyHDL: http://myhdl.org


Marco Teórico
=============


Segmentación
------------

El interior del procesador DLX está segmentado en cinco etapas de pipeline y 
en cada una de ellas se realizarán las operaciones de las tareas en el ciclo 
normal de una instrucción, es decir, búsqueda de la instrucción 
(identificado con el bloque IF), decodificación de la instrucción 
(identificado con el bloque ID), ejecución de la operación 
(identificado con el bloque EX), acceso a memoria 
(identificado con el bloque MEM) y almacenamiento del resultado de la 
operación (identificado con el bloque WB). 

 .. image:: img/segmentation.png
    :align: center
    :width: 80 %

La ejecución de las instrucciones se superponen en el tiempo de la siguiente 
manera:

 .. image:: img/overlapping.png
    :width: 80 %
    :align: center

Etapas y Latchs
---------------

Los *latchs* se encargan de retener y estabilizar los datos entre las etapas.
manteniendo la integridad de las señales y permitiendo así altas 
velocidades de procesamiento. 
Son los componentes que permiten la paralelización de la etapas.  



Datapath
========


 .. image:: img/datapath.png
    :width: 100 %


