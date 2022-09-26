#!/usr/bin/env python3

from ctypes import c_ulong


b_word = 32
b_byte = 8
word = 4 
def shift_right(bits):
    return 1 << bits

def digit(a, b):
    return a >> ((b_word - ((b + 1)*b_byte)) & (shift_right(b_bytes) - 1))


# Lookup table (Dictionary) for each Roman symbol to Integer
Roman = {
    "I": 1,
    "V": 5,
    "X": 10,
    "L": 50,
    "C": 100,
    "D": 500,
    "M": 1000,
}

def toBin(n, bits=b_word) :
    res = []  
    i = shift_right(bits - 1)
    
    # Set a safety boundry for limiting what is correctly displaying
    if n > 2**bits - 1:
        raise OverflowError(f"Max value of arg {n} exceedes sizeof {bits} bits as max int {2**bits}")
        
    while(i > 0):
        if((n & i) != 0):
            res.append("1")
        else:
            res.append("0")
            
        i = i // 2

    return ''.join(res)

def convertToInt(roman_number):
    res = 0
    l = len(roman_number)
    i = 0
    while i < l:
        # Getting value from table
        r1 = Roman[roman_number[i]]
        # Look ahead to check next
        if i < l:
            r2 = Roman[roman_number[i + 1]]
            # If next symbol->value is equal to or greater than
            # the current then add to current else subtract
            # and skip the next symbol.
            if r1 >= r2:
                res = res + r1
                # Move index to next symbol
                i = i + 1
            else:
                res = res + r2 - r1
                # Skip the next symbol
                i = i + 2
        else:
            res = res + r1
            i = i + 1
    return res

if __name__ == "__main__":
    num = "MCMIV"
    res = convertToInt(num)
    print(f'Integer form is: {res}')
    print(f'Binary form is: {toBin(res, 16)}')
    print(f'Binary form is: {toBin(res, 8)}')
