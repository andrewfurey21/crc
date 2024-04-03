from functools import lru_cache
def reverse(n:int):return int('{:032b}'.format(n)[::-1], 2)

# Basic implementation if crc32
def crc32(message:bytearray, poly:int):
    bitmask = 0xFFFFFFFF
    crc = 0

    for byte in message:
        for _ in range(8):
            b = byte & (1<<7) != 0
            divide = True if (crc & (1<<31) != 0) else False
            crc = (crc << 1) | b
            if divide:
                crc ^= poly
            byte <<= 1
    return crc & bitmask

# Better implementation of crc32, leading/trailing zeros
def crc32_improved(message:bytearray, poly:int, init:int=0, final_xor:int=0):
    """
    init crc (fixes problem with erroneous insertions/deletions of preprended zeros)
    finial_xor (fixes problem with erroneous insertions/deletions of appended zeros)
    crc = crc xor (G & (B ^ Cr)) (has the effect of shifting the message r times, where r is the size of the crc)
    """
    bitmask = 0xFFFFFFFF
    crc = init

    for byte in message:
        for _ in range(8):
            b = bitmask if byte & (1<<7) != 0 else 0
            divide = bitmask if (crc & (1<<31)) != 0 else 0
            crc = (crc << 1) ^ (poly & (b ^ divide))
            byte <<= 1
    return (crc ^ final_xor) & bitmask

@lru_cache
def create_lut(poly): return [crc32(bytearray([x, 0, 0, 0, 0]), poly) for x in range(256)]
# Implementation of crc32 with look up table
def crc32_lut(message:bytearray, poly:int):
    """
    Generates a crc with a look up table for improved speed
    """
    bitmask = 0xFFFFFFFF
    crc = 0

    lut = create_lut(poly)
    for m in message:
        index = (int(m) ^ (crc >> 24)) & 0xFF
        crc = lut[index] ^ (crc << 8)

    return crc & bitmask

if __name__ == "__main__":

    data= bytearray(b'I love pizza so much!')
    data_zeros = bytearray(data) + bytearray([0x0, 0x0, 0x0, 0x0])

    poly = 0x04C11DB7

    # Actual
    actual = crc32(data_zeros, poly)
    data_crc = data + bytearray([(actual >> 24) & 0xFF,(actual >> 16) & 0xFF,(actual >> 8) & 0xFF,(actual) & 0xFF])
    test_remainder = crc32(data_crc, poly)

    actual_better = crc32_improved(data, poly)
    data_crc = data + bytearray([(actual_better >> 24) & 0xFF,(actual_better >> 16) & 0xFF,(actual_better >> 8) & 0xFF,(actual_better) & 0xFF])
    better_remainder = crc32(data_crc, poly)

    actual_lut = crc32_lut(data, poly)
    data_crc = data + bytearray([(actual_lut >> 24) & 0xFF,(actual_lut >> 16) & 0xFF,(actual_lut >> 8) & 0xFF,(actual_lut) & 0xFF])
    lut_remainder = crc32(data_crc, poly)

    print("Actual Data           :",data)
    print("Data with zeros       :",data_zeros)

    print("CRC32 Basic           :",hex(actual))
    print("CRC32 Basic Remainder :",hex(test_remainder))

    print("CRC32 Better          :",hex(actual_better))
    print("CRC32 Better Remainder:",hex(better_remainder))

    print("CRC32 LUT             :",hex(actual_lut))
    print("CRC32 LUT Remainder   :",hex(lut_remainder))
