"""
This module consists of two parts: one written in the Maxima Computer 
Algebra System language <http://maxima.sourceforge.net/>, and the other a Python
script to read in and translate the results obtained from Maxima to Python.

In the Maxima script, the standardized gamma and lambda coefficients are 
first defined in terms of the unstandardized parameters.
These parameters *might*, but need not be, free parameters of the 
model for a given MTMM analysis.

The analytical derivatives of the standardized coefficients are then taken 
for each parameter. This yields a (number of parameters) x (number coefficients)
size matrix of analytical expressions in terms of the parameters.

This matrix is read in by the Python script and used by the ``parse_lisrel``
module to calculate the variance-covariance matrix of the standardized 
coefficients. 

See also the ``get_var_standardized`` function in ``parse_lisrel``.
"""
#!/usr/bin/python

import os, re, sys

from param_dicts_9x6 import paramdict, scoefdict


def pythonize_maxima(maxpath='derivmatrix.txt'):
    """Read in Maxima file which contains the analytic expressions for the first
       derivatives of the standardized estimates w.r.t. the parameters and convert it 
       into a Python expression that can be evaluated.
       Returns string that will evaluate to a list of strings to be evaluated.
       """
    der_file = open(maxpath, 'rb')

    linesep = re.compile(r'-9[\n\r]', re.MULTILINE)
    commasep = re.compile(r'([^,\[\]]+)([,\]])', re.MULTILINE)
    number = re.compile(r'(?<![a-z0-9])([0-9]+)', re.MULTILINE)
    powerop = re.compile(r'\^', re.MULTILINE)
    index = re.compile(r'([a-z]{2})([0-9]{1,2})([0-9]{1,2})', re.MULTILINE)

    der_str = der_file.read()
    der_str = linesep.sub(r'], \n[', der_str) # recognize rows
    der_str = commasep.sub(r"r'\1'\2", der_str) # make list of strings to be evaluated
    der_str = number.sub(r'\1.0', der_str) # make numbers floats
    der_str = powerop.sub(r'**', der_str)  # maxima uses ^ while python uses ** for powers
    der_str = index.sub(r'\1[\2-1,\3-1]', der_str)  # indexing from ga11 to ga[0,0]
    der_str = '[' + der_str[2:-2] + ']' # enclose in list constructor, remove beg & end
    der_str = der_str.replace('\n', ' ') # remove newlines
    der_str = der_str.replace('],', '],\n') # newlines between list elts
    der_str = der_str.replace('\',', '\',\n') # newlines between list elts

    return der_str

def get_derivs(maxpath='derivmatrix.txt'):
    """Use pythonize_maxima() to obtain a list of lists of strings to be evaluated.
       Returns a list 'derivs'.

       Each list in derivs refers to the first derivatives wrt to one free parameter.
       (the order is in paramdict)

       Each string in each of these lists refers to one standardized coefficient.
       (the order is in scoefdict and also in the handy-to-read scoefs.names file
       which can be read by R scan() )
     
       The string can be evaluated in an environment where the relevant matrices are
       present as NumPy.matrices or arrays. Also 'from math import sqrt' is needed."""
    derivs = eval(pythonize_maxima(maxpath))

    return derivs



