UK Modulus Checking
===================

Python implementation of the VocaLink UK Bank Account Modulus Checking logic as of the VocaLink 3.10 spec.

Installation
------------

    pip install ukmodulus


Usage
-----

    from ukmodulus import validate_number
    validate_number('089999', '66374958')

Limitations
-----------

Doesn't currently deal with account numbers which are not 8 digits long. (i.e. doesn't implement the exceptions listed in 4.2 of the VocaLink spec).
