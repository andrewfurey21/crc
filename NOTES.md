# Notes on CRC

## What is CRC?

CRC stands for cyclic redundancy check. It is a small number (or checksum) that you add to the end of your message, that helps the receiver identify if there are any errors in the message it received (which is why it's redundant.)

## How to Calculate CRC

You calculate a CRC by using GF(2) polynomials. There are loads of explanations online about this, and because I'm not an expert in algebraic field theory I'm not going to cover all the reasons why we use it. There are a bunch of reasons why we use it, it gives the checksum a lot of strength when checking for burst errors and if we were building this in hardware, it would be very straightforward, just a few xor gates. I'm not going to prove why, that is an exercise left to the viewer I suppose. 

Here is a quick example of subtraction/addition and then division.

We calculate the CRC by using a generator. The equation is simply Mx^r + C mod G = 0, where M is the message, C is our check sum and G is our generator polynomial. We are trying to find the remainder of M / G. We append this remainder to our message. The receiver can then recalculate the remainder and check with the given checksum. Alternatively, because it's much simpler in a hardware implementation, you can check if the entire message, checksum included has a remainder of 0 when divided by the generator.

## Implement Naive version

```python
# Basic implementation if crc32
def crc32(message:bytearray, poly:int):
    bitmask = 0xFFFFFFFF
    crc = 0

    for byte in message:
        for _ in range(8):
            b = byte & (1<<7) != 0
            divide = bitmask if (crc & (1<<31) != 0) else 0
            crc = (crc << 1) | b
            crc ^= (poly & divide)
            byte <<= 1
    return crc & bitmask
```

## Improved Version

There are a few things we can do to improve this. First of all, we should worry about inserted or deleted zeroes at the beginning of the message. A number is still divisible by another number if we add a bunch of zeros the the most significant part of it, but if we add more zeros to a message, that will change the meaning of the message.

```python
zero = bytearray(1)
data = zero + bytearray(b'This is a string')
```

The remainder is identical, but we have a different message. How do we fix this? It turns out its very simple. We append a bunch of nonzero bits to the message. These bits don't get sent over the network or whereever, it's just part of our crc function. This is the init param.

Another problem is if the message we send over ends in a zero, and extra zeros get appended or deleted. If you multiply a number X by Y, where Y is divisible by Z, then X times Y is still divisble by Z. A simple fix to it is adding a number to it, generally all 1's (remember addtion is just xor). This is the final_xor param that we'll add to our function.

```python
data= bytearray(b'I love pizza!')
data_zeros = bytearray(data) + bytearray([0x0, 0x0, 0x0, 0x0])
actual = crc32(data_zeros, poly)
data_crc = data + bytearray([(actual >> 24) & 0xFF,(actual >> 16) & 0xFF,(actual >> 8) & 0xFF,(actual) & 0xFF]) + zero
test_remainder = crc32(data_crc, poly)
```

There is also one small thing we can do. It's kind of annoying having to add in all the extra zeros at the end here. And if were writing this as a hardware description, it would also be kind of a pain. There's a small proof that will make our lives easier, that I will explain because it took a bit of searching and time when I was trying to understand it.

Proof.

```python
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
```

## Look Up table

A really easy and quick optimization is to use a look up table. It turns out that when you divide one number by another, the remainder will never change. So we can calculate crcs nbits at a time. For what we're doing, we'll just use bytes but you could do this over 32bits or bigger even.

We'll create a list of crcs using our crc32 improved function, for all the numbers between 0 and 256. SO all the way up to 255.

```python
def create_lut(poly): return [crc32_improved(bytearray([x]), poly) for x in range(256)]
```

We create a look up table using this function, and then loop over every byte. We calculate the index of the look up table by xoring the byte with the msbyte of the crc. We then shift the crc by a byte and xor it with our crc.

```python
def crc32_lut(message:bytearray, poly:int):
    """
    Generates a crc with a look up table for improved speed
    """
    bitmask = 0xFFFFFFFF
    crc = 0

    lut = create_lut(poly)
    for m in message:
        index = (int(m) ^ (crc >> 24)) & 0xFF
        crc = (crc << 8) ^ lut[index]

    return crc & bitmask
```
