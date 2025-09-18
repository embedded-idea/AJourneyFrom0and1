import os
import re
dirname = os.path.dirname(__file__)
inputfile = os.path.join(dirname,'program.asm')
outputfile = os.path.join(dirname,'program.bin')

annotation = re.compile(r"(.*?);.*")

codes = []

OP2 = {
    'ADD': 0x80,
    'SHL': 0x90,
    'SHR': 0xA0,
    'NOT': 0xB0,
    'AND': 0xC0,
    'OR': 0xD0,
    'XOR': 0xE0,
    'CMP': 0xF0,
    'LOAD':0x00,
    'STORE':0x10,
    'DATA':0x20,
    'IN':0x70,
    'OUT':0x78,
}
OP1 = {
    'JMPR': 0x30,
    'JMP': 0x40,
    'JC': 0x58,
    'JA': 0x54,
    'JE': 0x52,
    'JZ': 0x51,
    'JCA': 0x5C,
    'JCE': 0x5A,
    'JCZ': 0x59,
    'JAE': 0x56,
    'JAZ': 0x55,
    'JEZ': 0x53,
    'JCAE': 0x5E,
    'JCAZ': 0x5D,
    'JCEZ': 0x5B,
    'JAEZ': 0x57,
    'JCAEZ': 0x5F,
}

OP0 = {
    'CLEAR': 0x60
}

OP2SET = set(OP2.values())
OP1SET = set(OP1.values())
OP0SET = set(OP0.values())

REGISTERS = {
    "R0": 0,
    "R1": 1,
    "R2": 2,
    "R3": 3,
}

class Code(object):

    def __init__(self, number, source):
        self.numer = number
        self.source = source.upper()
        self.op = None
        self.dst = None
        self.src = None
        self.prepare_source()

    def get_op(self):
        if self.op in OP2:
            return OP2[self.op]
        if self.op in OP1:
            return OP1[self.op]
        if self.op in OP0:
            return OP0[self.op]
        raise SyntaxError(self)
    
    def get_am(self, addr):
        if not addr:
            return 0, 0
        if addr in REGISTERS:
            return REGISTERS[addr]
        if re.match(r'^[0-9]+$', addr):
            return int(addr)
        if re.match(r'^0X[0-9A-F]+$', addr):
            return int(addr, 16)
        raise SyntaxError(self)
    
    def prepare_source(self):
        tup = self.source.split(',')
        if len(tup) > 2:
            raise SyntaxError(self)
        if len(tup) == 2:
            self.src = tup[1].strip()
        tup = re.split(r" +", tup[0])
        if len(tup) > 2:
            raise SyntaxError(self)
        if len(tup) == 2:
            self.dst = tup[1].strip()
        self.op = tup[0].strip()

    def compile_code(self):
        op = self.get_op()
        if op == 0x70:#IN DATA,R0
            if self.dst == 'DATA':
                src = self.get_am(self.src)
                ir = op | src
            elif self.dst == 'ADDR':
                src = self.get_am(self.src)
                ir = op |1<<2| src
            return [ir,0,False]
        elif op == 0x78:
            if self.dst == 'DATA':
                src = self.get_am(self.src)
                ir = op | src
            elif self.dst == 'ADDR':
                src = self.get_am(self.src)
                ir = op |1<<2| src
            return [ir,0,False]
        else:
            dst = self.get_am(self.dst)
            src = self.get_am(self.src)
        immedate = False
        if op in OP2SET:
            ir = op | src<<2 | dst
            if op == 0x20:#DATA
                ir = op | dst
                immedate = True
                return [ir,src,immedate]
        elif op in OP1SET:
            ir = op | dst
            if op == 0x40 or op == 0x60 or op == 0x58 or op == 0x54 or op == 0x52 \
                or op == 0x51 or op == 0x5C or op == 0x5A or op == 0x59 \
                or op == 0x56 or op == 0x55 or op == 0x53 or op == 0x5E \
                or op == 0x5D or op == 0x5B or op == 0x57 or op == 0x5F:
                ir = op
                immedate = True
                return [ir,dst,immedate]
        else:
            ir = op

        return [ir,dst,immedate]

    def __repr__(self):
        return f'[{self.numer}] - {self.source}'

class SyntaxError(Exception):

    def __init__(self, code: Code, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code = code

def compile_program():
    with open(inputfile,encoding='utf8') as file:
        lines = file.readlines()
    for index, line in enumerate(lines):
        source = line.strip();
        if ';' in source:
            match = annotation.match(source)
            source = match.group(1)
        if not source:
            continue
        code = Code(index+1,source)
        codes.append(code)
        print(code)
    with open(outputfile, 'wb') as file:
        for code in codes:
            values = code.compile_code()
            if values[2] == True:
                result = values[0].to_bytes(1, byteorder='little')
                file.write(result)
                result = values[1].to_bytes(1, byteorder='little')
                file.write(result)
            else:
                result = values[0].to_bytes(1, byteorder='little')
                file.write(result)

def main():
    try:
        compile_program()
    except SyntaxError as e:
        print(f"SyntaxError at {e.code}")
    print('compiling completed')

if __name__ == '__main__':
    main()
