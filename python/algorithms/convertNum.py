#!/usr/bin/env python3

from ctypes import c_ulong

b_word = 32
b_byte = 8
word = 4


def shift_right(bits):
    return 1 << bits


def mask(a, b):
    return a >> ((b_word - ((b + 1) * b_byte)) & (shift_right(b_bytes) - 1))


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


def toBinStr(n, bits=b_word):
    """
    Convert n to binary string representation of bits length
    :param int n: unsigned integer value to represent
    :param int bits: number of bits to represent
    :return: string represention of n of length bits
    :raises OverflowError: if n would exceed bits in size
    :raises TypeError: if n is not an integer
    :raises ValueError: if n is a negative value
    """
    # Do some basic checks on params.
    if not isinstance(n, int):
        raise TypeError(f":param n={n}: needs to be an integer value")
    if 0 > n:
        raise ValueError(f"param n={n}: needs to be a positive value")
    # Set a safety boundry for limiting what is correctly displaying
    if n > 2 ** bits - 1:
        raise OverflowError(
            f"Max value of arg {n} exceedes sizeof {bits} bits as max int {2**bits}"
        )
    # ToDo:: Need to impose some limits on param bits to ensure we represent reasonable bounderies such as:
    # size of word or byte on a particular plaform. It be arbitrary since this is only for display but
    # may still need to be some multiple of 2. e.g. if bits // 2 is not 0 then raise exception.
    res = []
    i = shift_right(bits - 1)

    while i > 0:
        if (n & i) != 0:
            res.append("1")
        else:
            res.append("0")

        i = i // 2

    return "".join(res)


def romanToInt(roman_number):
    """
    C style implentation of converting Roman numeral string to its
    integer representation.
    :param roman_number: Any string of Roman numbers
    :return int: integer value equivelent
    :raises TypeError: if roman_number is not a string
    :raises ValueError: if string contains non-roman numerical characters
    :raises Exception: of Roman number appears 3 or more consequative times
    """
    res = 0
    l = len(roman_number)
    i = 0
    c_count = 0

    while i < l:
        # Getting value from table
        try:
            r1 = Roman[roman_number[i]]
        except KeyError:
            raise KeyError(
            f"{roman_number[i]} is not a valid roman number: Valid characters {Roman.keys()}"
        )

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
            if r1 == r2:
                c_count += 1
            else:
                c_count = 1
        else:
            res = res + r1
            i = i + 1
        if c_count >= 3:
            raise Exception(
                f"Illegal occurance of {roman_numeral[i]} in {roman_number} Error"
            )
    return res


if __name__ == "__main__":
    num = "MCMIV"
    res = romanToInt(num)
    print(f"Integer form is: {res}")
    print(f"Binary form is: {toBinStr(res, 16)}")
    print(f"Binary form is: {toBinStr(res, 8)}")
