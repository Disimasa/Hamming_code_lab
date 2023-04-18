import math
import random


class HammingCode:
    def __init__(self, word_length, base):
        self.word_length = word_length
        self.control_bits = self.get_control_bits()
        self.base = base
        self.errors_inserted = 0
        self.errored_words = 0
        self.correct_words = 0
        self.errors_fixed = 0

    def get_control_bits(self):
        control_bits = []
        current_bit = 1
        while current_bit <= self.word_length:
            control_bits.append(current_bit)
            current_bit *= 2
        return control_bits

    def encode(self, text: str) -> str:
        bin_str = ''.join([self.get_bin(symbol) for symbol in text])
        # print(f'Бинарный код текста - {bin_str}')
        res_str = ''
        for chunk_start in range(0, math.ceil(len(bin_str) / self.word_length)):
            res_str += self.encode_chunk(bin_str[chunk_start * self.word_length:(chunk_start + 1) * self.word_length])
        return res_str

    def encode_chunk(self, chunk: str) -> str:
        chunk_list = list(chunk)
        for control_bit in self.control_bits:
            if control_bit < len(chunk):
                chunk_list.insert(control_bit - 1, 0)

        control_bits_dict = self.get_control_bits_stat(chunk_list)
        for control_bit in self.control_bits:
            if control_bit < len(chunk):
                chunk_list[control_bit - 1] = str(control_bits_dict[control_bit] % 2)

        return ''.join(chunk_list)

    @staticmethod
    def get_power_expansions(number: int) -> list:
        return [1 << idx for idx, bit in enumerate(bin(number)[:1:-1]) if bit == "1"]

    def decode(self, bin_text, fix_error=False):
        self.errors_inserted = 0
        self.errored_words = 0
        self.correct_words = 0
        self.errors_fixed = 0
        chunk_length = len(self.control_bits) + self.word_length
        decoded_bin = ''
        for chunk_start in range(math.ceil(len(bin_text) / chunk_length)):
            decoded_bin += self.decode_chunk(bin_text[chunk_start * chunk_length:(chunk_start + 1) * chunk_length],
                                             fix_error)
        # print(f'Раскодированный бинарный код текста - {decoded_bin}')

        res_text = ''
        for char_start in range(math.ceil(len(decoded_bin) / self.base)):
            res_text += chr(int(decoded_bin[char_start * self.base:(char_start + 1) * self.base], 2))

        return res_text

    def decode_chunk(self, chunk: str, fix_error=False) -> str:
        chunk_list = list(chunk)
        if fix_error:
            control_bits_dict = self.get_control_bits_stat(chunk_list)
            errored_control_bits = []
            for control_bit in self.control_bits:
                if control_bit < len(chunk_list):
                    if chunk_list[control_bit - 1] != str(control_bits_dict[control_bit] % 2):
                        errored_control_bits.append(control_bit)
            if errored_control_bits:
                error_ind = sum(errored_control_bits) - 1
                if chunk_list[error_ind] == '1':
                    chunk_list[error_ind] = '0'
                else:
                    chunk_list[error_ind] = '1'
                self.errors_fixed += 1
                self.errored_words += 1
            else:
                self.correct_words += 1

        for control_bit in reversed(self.control_bits):
            if control_bit < len(chunk):
                del chunk_list[control_bit - 1]

        return ''.join(chunk_list)

    def get_control_bits_stat(self, chunk: list) -> dict:
        control_bits_dict = {}
        for control_bit in self.control_bits:
            control_bits_dict[control_bit] = 0

        for bit_ind, bit in enumerate(chunk):
            if bit_ind + 1 not in self.control_bits:
                power_expansions = self.get_power_expansions(bit_ind + 1)
                for power in power_expansions:
                    control_bits_dict[power] += int(bit)

        return control_bits_dict

    def get_bin(self, symbol: str) -> str:
        return f'{{0:0{self.base}b}}'.format(ord(symbol))

    def add_error(self, bin_text: str) -> str:
        chunk_length = len(self.control_bits) + self.word_length

        errored_text = ''
        for chunk_start in range(math.ceil(len(bin_text) / chunk_length)):
            chunk = list(bin_text[chunk_start * chunk_length:(chunk_start + 1) * chunk_length])
            if random.randint(0, 2) == 1:
                self.errors_inserted += 1
                error_ind = random.randint(0, len(chunk) - 1)
                if chunk[error_ind] == '1':
                    chunk[error_ind] = '0'
                else:
                    chunk[error_ind] = '1'
            errored_text += ''.join(chunk)

        return errored_text


def get_crc16(x):
    a = 0xFFFF
    b = 0xA001
    for byte in x:
        a ^= ord(byte)
        for i in range(8):
            last = a % 2
            a >>= 1
            if last == 1:
                a ^= b
    s = hex(a).upper()
    return s


file = open('text.txt', 'r', encoding='utf-8')
text = ''.join(file.readlines())
print(f'Контрольная сумма - {get_crc16(text)}')

hamming = HammingCode(word_length=71, base=16)  # Передаем длину слова без учета контрольных битов (78 - 7 = 71)
encoded_text = hamming.encode(text)
errored_text = hamming.add_error(encoded_text)

print(f'Раскодированный текст с ошибками- {hamming.decode(errored_text, fix_error=False)}')
print(f'Раскодированный текст с исправленными ошибками- {hamming.decode(errored_text, fix_error=True)}')
print(f'Неверно доставленных слов - {hamming.errored_words}')
print(f'Правильно доставленных слов - {hamming.correct_words}')
print(f'Исправлено ошибок - {hamming.errors_fixed}')
