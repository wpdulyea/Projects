import pytest
import socket
from conftest import convert


# res = convertToInt(num)
# print(f'Integer form is: {res}')
# print(f'Binary form is: {toBin(res, 16)}')
# print(f'Binary form is: {toBin(res, 8)}')


class TestRomanNumerals:
    small_num = "IV"
    big_num = "MCMIV"
    invalid_char = "FF"
    invalid_seq = "XXXVVVI"

    def test_small_number(self):
        res = convert.convertToInt(self.small_num)
        assert 4 == res

    def test_big_number(self):
        res = convert.convertToInt(self.big_num)
        assert 1904 == res

    def test_invalid_sequence(self):
        pass

    def test_invalid_characters(self):
        pass


class TestBinary:
    def test_8bit(self):
        bits = 8
        msb = 2**(bits-1)
        m_lsb = msb + 1
        res = convert.toBin(1, bits)
        assert "00000001" == res
        res = convert.toBin(msb, bits)
        assert "10000000" == res
        res = convert.toBin(m_lsb, bits)
        assert "10000001" == res

    def test_16bit(self):
        bits = 16
        msb = 2**(bits-1)
        m_lsb = msb + 1
        res = convert.toBin(1, bits)
        assert "0000000000000001" == res
        res = convert.toBin(msb, bits)
        assert "1000000000000000" == res
        res = convert.toBin(m_lsb, bits)
        assert "1000000000000001" == res 

    def test_32bit(self):
        bits = 32
        msb = 2**(bits-1)
        m_lsb = msb + 1
        res = convert.toBin(1, bits)
        assert "00000000000000000000000000000001" == res
        res = convert.toBin(msb, bits)
        assert "10000000000000000000000000000000" == res
        res = convert.toBin(m_lsb, bits)
        assert "10000000000000000000000000000001" == res

    def test_64bit(self):
        pass

    def test_raise_overflow_Exception(self):
        bits = 8
        msb = 2**(bits-1)
        m_lsb = msb + 1
        with pytest.raises(OverflowError):
            res = convert.toBin(2**bits, bits)

    def test_set_all_bits(self):
        bits = 8
        msb = 2**(bits-1)
        m_lsb = msb + 1
        res = convert.toBin(2**bits - 1, bits)
        assert "11111111" == res

    def test_0(self):
        bits = 8
        msb = 2**(bits-1)
        m_lsb = msb + 1
        res = convert.toBin(0, bits)
        assert "00000000" == res

    def test_invalid_characters(self):
        pass
