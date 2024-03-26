from typing import List
from crc._crc import Configuration, Calculator

# Basic implementation if crc32
def crc32(message:bytearray, poly:int):
    bitmask = 0xFFFFFFFF
    crc = 0

    for byte in message:
        for i in range(8):
            b = byte & (1<<7) != 0
            divide = True if (crc & (1<<31) != 0) else False
            crc = (crc << 1) | b
            if divide:
                crc ^= poly
            byte <<= 1
        crc &= bitmask
    return crc

# Better implementation of crc32, leading/trailing zeros
def crc32_improved(message:bytearray, poly:int, final_xor:int=0): pass
# Implementation of crc32 with look up table
def crc32_lut(): pass

if __name__ == "__main__":

    data= bytearray(b'I love pizza some much!')
    data_zeros = bytearray(data) + bytearray([0x0, 0x0, 0x0, 0x0])

    poly = 0x04C11DB7

    testCRC = Configuration(
        width=32,
        polynomial=poly,
        init_value=0x0,
        final_xor_value=0xFFFFFFFF,
        reverse_input=False,
        reverse_output=False,
    )


    # Expected
    expected = Calculator(testCRC).checksum(data)
    expected_crc = data + bytearray([(expected >> 24) & 0xFF,(expected >> 16) & 0xFF,(expected>> 8) & 0xFF,(expected) & 0xFF])
    expected_remainder = Calculator(testCRC).checksum(expected_crc)

    # Actual
    actual = crc32(data_zeros, poly)
    data_crc = data + bytearray([(actual >> 24) & 0xFF,(actual >> 16) & 0xFF,(actual >> 8) & 0xFF,(actual) & 0xFF])
    test_remainder = crc32(data_crc, poly)

    print("Actual Data       :",data)
    print("Data with zeros   :",data_zeros)
    # print("Data with crc32   :",data_crc)
    # print("Data with config  :",expected_crc)
    print("Expected          :",hex(expected))
    print("Expected Remainder:",hex(expected_remainder))

    print("Actual            :",hex(actual))
    print("Actual Remainder  :",hex(test_remainder))
