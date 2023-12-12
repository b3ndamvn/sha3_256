import binascii
import re


class Sponge:
    def __init__(self, divided_pad_message: list):
        self.divided_pad_message = divided_pad_message
        self.b_length = 1600
        self.s = '0' * self.b_length
        self.p_array = [message.ljust(self.b_length, '0') for message in self.divided_pad_message]
        self.test = ''

    def determine_a(self, s) -> list:
        a = [[[[] for _ in range(64)] for _ in range(5)] for _ in range(5)]
        for y in range(5):
            for x in range(5):
                for z in range(64):
                    a[x][y][z] = s[64 * (5 * y + x) + z]
        print(f'determine_a result is {a}')
        return a

    def determine_s(self, a) -> str:
        s = ''
        for y in range(5):
            for x in range(5):
                for z in range(64):
                    s += str(a[x][y][z])
        print(f'determine_s result is {s}')
        return s

    def start_absorb(self):
        for i, p in enumerate(self.p_array):
            result = format(int(p, base=2) ^ int(self.s[:1088], base=2), 'b')
            a = self.determine_a(result)
            rnd_result = self.rnd(a, i)
            self.s = self.determine_s(rnd_result)
        print(f'start_absorb result is {self.s}')
        return self.s

    def rnd(self, a, i):
        new_a = a.copy()
        for _ in range(24):
            new_a = self.iota_function(self.xi_function(self.pi_function(self.theta_function(new_a))), i)
        print(f'rnd result is {new_a}')
        return new_a

    def theta_function(self, a: list) -> list:
        c = [[[] for _ in range(64)] for _ in range(5)]
        for x in range(5):
            for z in range(64):
                c[x][z] = int(a[x][0][z]) ^ int(a[x][1][z]) ^ int(a[x][2][z]) ^ int(a[x][3][z]) ^ int(a[x][4][z])
        d = [[[] for _ in range(64)] for _ in range(5)]
        for x in range(5):
            for z in range(64):
                d[x][z] = int(c[(x - 1) % 5][z]) ^ int(c[(x + 1) % 5][(z - 1) % 64])
        new_a = [[[[] for _ in range(64)] for _ in range(5)] for _ in range(5)]
        for x in range(5):
            for y in range(5):
                for z in range(64):
                    new_a[x][y][z] = int(a[x][y][z]) ^ d[x][z]
        print(f'theta-function result is {new_a}')
        return new_a

    def ro_function(self, a: list) -> list:
        new_a = [[[[] for _ in range(64)] for _ in range(5)] for _ in range(5)]
        for z in range(64):
            new_a[0][0][z] = a[0][0][z]
        x, y = 1, 0
        for t in range(24):
            for z in range(64):
                new_a[x][y][z] = a[x][y][(z - (t + 1) * (t + 2) / 2) % 64]
                x, y = y, (2 * x + 3 * y) % 5
        print(f'ro_function result is {new_a}')
        return new_a

    def pi_function(self, a: list) -> list:
        new_a = [[[[] for _ in range(64)] for _ in range(5)] for _ in range(5)]
        for x in range(5):
            for y in range(5):
                for z in range(64):
                    new_a[x][y][z] = a[(x + 3 * y) % 5][x][z]
        print(f'pi_function result is {new_a}')
        return new_a

    def xi_function(self, a: list) -> list:
        new_a = [[[[] for _ in range(64)] for _ in range(5)] for _ in range(5)]
        for x in range(5):
            for y in range(5):
                for z in range(64):
                    new_a[x][y][z] = int(a[x][y][z]) ^ ((int(a[(x + 1) % 5][y][z]) ^ 1) * int(a[(x + 2) % 5][y][z]))
        print(f'xi_function result is {new_a}')
        return new_a

    def rc_algorithm(self, t: int) -> int:
        if not t % 255:
            return 1
        r = list('10000000')
        for i in range(1, t % 255):
            r.insert(0, '0')
            r[-1] = int(r[-1]) ^ int(r[0])
            r[-5] = int(r[-5]) ^ int(r[0])
            r[-6] = int(r[-6]) ^ int(r[0])
            r[-7] = int(r[-7]) ^ int(r[0])
            r = r[:8]
        print(f'rc_algorithm result is {int(r[-1])}')
        return int(r[-1])

    def iota_function(self, a: list, i: int) -> list:
        new_a = a.copy()
        rc = list('0' * 64)
        for j in range(6):
            rc[2 ** j - 1] = self.rc_algorithm(j + 7 * i)
        for z in range(64):
            new_a[0][0][z] = int(new_a[0][0][z]) ^ int(rc[z])
        print(f'iota_function result is {new_a}')
        return new_a

    def start_squeezing(self):
        self.test = self.s
        z = self.test
        i = 0
        while len(z) < 256:
            a = self.determine_a(self.test)
            rnd_result = self.rnd(a, i)
            self.test = self.determine_s(rnd_result)
            z += self.test
            i += 1
        print(f'start_squeezing result is {z[-256:]}')
        return z[-256:]


class SHA3:
    def __init__(self, message):
        self.message = message
        self.RATE = 1088
        self.ROUNDS = 24
        self.binary_message = self.convert_to_binary()
        self.padded_message = self.pad_message()
        self.divided_pad_message = self.divide_into_blocks()

    def convert_to_binary(self):
        byte_message = bytearray(self.message, 'utf-8')
        result = []
        for byte in byte_message:
            binary = format(byte, 'b')
            result.append(binary)
        print(f'convert_to_binary result is {"".join(result)}')
        return ''.join(result)

    def pad_message(self):
        extension_bits_value = len(self.message) % self.RATE
        if extension_bits_value:
            padded_message = self.binary_message + '1'
            padded_message = padded_message.ljust(self.RATE-1, '0') + '1'
            return padded_message
        print(f'pad_message result is {self.binary_message}')
        return self.binary_message

    def divide_into_blocks(self):
        test = re.findall('\d' * self.RATE, self.padded_message)
        print(f'divide_into_blocks result is {test}')
        return re.findall('\d' * self.RATE, self.padded_message)

    def encrypt_message(self):
        sp = Sponge(self.divided_pad_message)
        z = sp.start_absorb()
        q = sp.start_squeezing()
        return q


if __name__ == '__main__':
    sha3 = SHA3('qwe')
    # print(len(str(hex(int(sha3.encrypt_message(), 2)))[2:]))
    print(str(hex(int(sha3.encrypt_message(), 2)))[2:])

