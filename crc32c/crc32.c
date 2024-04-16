#include "string.h"
#include "stdlib.h"
#include "stdio.h"

#include <immintrin.h>

#define ONES 0xFFFFFFFF

int crc32(char* message, int len, int poly, int init, int final_xor) {
    int crc = init;

    for (int i = 0; i < len; i++) {
        char byte = message[i];
        for (int j = 0; j < 8; j++) {
            int divide = crc & (1<<31);
            int b = (byte & (1<<7)) > 0;
            byte <<= 1;
            crc = (crc << 1) | b;
            if (divide) crc ^= poly;
        }
    }

    return crc ^ final_xor;
}

int crc32_better(char* message, int len, int poly, int init, int final_xor) {
    int crc = init;
    for (int i = 0; i < len; i++) {
        char byte = message[i];
        for (int j = 0; j < 8; j++) {
            int divide = (crc & (1<<31) ) == 0 ? 0 : ONES;
            int b = (byte & (1 << 7)) == 0 ? 0 : ONES;
            byte <<= 1;
            crc = (crc << 1) ^ (poly & (b ^ divide));
        }
    }
    return crc ^ final_xor;
}

int* crc32_look_up_table(int poly) {
    int* table = malloc(sizeof(int) * 256);
    for (int i = 0; i < 256; i++) {
        char message = (char)i;
        int crc = crc32_better(&message, 1, poly, 0, 0);
        table[i] = crc;
    }
    return table;
}

int crc32_use_lut(int* table, char* message, int len) {
    int crc = 0;

    for (int i = 0; i < len; i++) {
        unsigned char index = message[i] ^ (crc >> 24);
        crc = (crc << 8) ^ table[index];
    }

    return crc;
}

int crc32_vector(char* message, int len, int init, int final_xor) {
    int crc = init;

    for (int i = 0; i < len; i++) {
        unsigned char byte = message[i];
        crc = _mm_crc32_u8(crc, byte);
    }

    return crc ^ final_xor;
}

int main(void) {
    char* message = "I love pizza!";
    int message_len = strlen(message);

    int poly = 0x04C11DB7;

    int* lut = crc32_look_up_table(poly);
    int crc_using_lut = crc32_use_lut(lut, message, message_len);

    int crc_vec = crc32_vector(message, message_len, 0, 0);

    printf("Message: %s\n", message);
    printf("CRC: 0x%x\n", crc_using_lut);
    printf("CRC Vec: 0x%x\n", crc_vec);
}
