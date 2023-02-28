from audioop import add

# A Arithmetic add 0001
# B Arithmetic addi 1101
# C Arithmetic sub 1011
# D Arithmetic subi 0101
# E Logic and 1010
# F Logic andi 0110
# G Logic or 0111
# H Logic ori 1111
# I Logic sll 1001
# J Logic srl 0000
# K Logic nor 0100
# L Memory lw 0010
# M Memory sw 0011
# N Control beq 1100
# O Control bneq 1110
# P Control j 1000
# JALMKDFGPIECNBOH


mapped_registers = {
    "$zero": "0000",
    "$t0": "0111",
    "$t1": "0001",
    "$t2": "0010",
    "$t3": "0011",
    "$t4": "0100"
}

# opcodes for the instructions
instruction_type = {
    "sll": ("S", "1001"),
    "lw": ("I", "0010"),
    "andi": ("I", "0110"),
    "subi": ("I", "0101"),
    "addi": ("I", "1101"),
    "and": ("R", "1010"),
    "add": ("R", "0001"),
    "ori": ("I", "1111"),
    "sw": ("I", "0011"),
    "j": ("J", "1000"),
    "beq": ("I", "1100"),
    "or": ("R", "0111"),
    "bneq": ("I", "1110"),
    "nor": ("R", "0100"),
    "sub": ("R", "1011"),
    "srl": ("S", "0000"),
}

labels = dict()


def convertToHex(*argv):
    result = ''
    for arg in argv:
        result += hex(int(arg, 2))[2:]
    return result


def load_store_handle(inst_sep) -> str:
    instruction_name, r2 = inst_sep[0].split(' ')
    instruction_name = instruction_name.strip()

    opcode = instruction_type.get(instruction_name)[1]
    r2 = mapped_registers.get(r2.strip())
    r1 = inst_sep[1].strip()
    start = r1.find('(')
    end = r1.find(')')
    shmt = int(r1[:start])
    shmt = bin(shmt)[2:].zfill(4)
    r1 = mapped_registers.get(r1[start + 1:end])
    return convertToHex(opcode, r1, r2, shmt)


def RSI_control(inst_sep, format, i) -> str:
    instruction_name, r1 = inst_sep[0].split(' ')
    instruction_name = instruction_name.strip()
    if instruction_name == 'lw' or instruction_name == 'sw':
        return load_store_handle(inst_sep)

    # findn and get the opcode from the dictionary
    opcode = instruction_type.get(instruction_name)[1]
    r1 = mapped_registers.get(r1.strip())
    r2 = mapped_registers.get(inst_sep[1].strip())
    # assign the remaining to r3
    r3 = inst_sep[2].strip()

    # like add $t1,$t2,$t3
    # in this case the last register(r3) is our src reg2
    # 1st reg(r1) is dest reg
    if format == 'R':
        r3 = mapped_registers.get(r3)
        return convertToHex(opcode, r2, r3, r1)

    if instruction_name == 'beq' or instruction_name == 'bneq':
        jmp_to = labels.get(r3)
        if i < jmp_to:
            r3 = jmp_to - i - 1
        else:
            r3 = i - jmp_to + 1
            r3 = (1 << 4) - r3  # twos complement
    r3 = int(r3)
    r3 = ((1 << 4) + r3) if r3 < 0 else r3
    r3 = bin(r3)[2:].zfill(4)

    return convertToHex(opcode, r2, r1, r3)


# applicable for only J format's instructions
# i denotes the line number
def J_control(inst_sep, i) -> str:
    instruction_name, jmpaddr = inst_sep[0].split(' ')[:2]
    instruction_name = instruction_name.strip()
    jmpaddr = labels.get(jmpaddr.strip())

    opcode = instruction_type.get(instruction_name)[1]
    # jmpaddr = bin(jumpaddr)[2:].zfill(8)
    # fill the last 4 bits to 0
    return convertToHex(opcode) + hex(jmpaddr)[2:].zfill(2) + '0'


def generateCode(inst: str, i=-1) -> str:
    commaSeperatedParts = inst.split(',')
    instruction_name = commaSeperatedParts[0].split(' ')[0].strip()
    if instruction_name not in instruction_type:
        print('Invalid instruction found!!!!!!!!: ' + instruction_name)
        exit(1)

        # if valid instruction,get the format and corressponding opcode from the dictionary
    format, opcode = instruction_type.get(instruction_name)
    if format == 'R' or format == 'I' or format == 'S':
        return RSI_control(commaSeperatedParts, format, i)
    else:
        return J_control(commaSeperatedParts, i)


try:
    asm_input = open('in.asm', 'r')
except:
    print('\033[91m' + "inst.asm file not found" + '\033[0m')
    exit(1)

fout = open('out.hex', 'w')
ftemp = open('temp.hex', 'w')
code_lines = asm_input.readlines()

# find labels an push them in dictionary
for i, line in enumerate(code_lines):
    if line == "":
        continue
    line = line.strip()
    colon = line.find(':')
    # if gets colon,extracts the label name and put it in the dictonary
    if colon != -1:
        labels[line[:colon]] = i
# strip comments
for i, line in enumerate(code_lines):
    comment = line.find(';')
    if comment != -1:
        line = line[:comment].strip()

    # just for checking purpose
    print(line, end='' if line.endswith('\n') else '\n')

    # check if any labels
    colon_start = line.find(':')
    if colon_start != -1:
        line = line[colon_start + 1:].strip()  # strip label

    if line == "":  # if no instruction after label, then exit
        hexCode = '0000'
    else:  # else convert instruction of each line  to hexCode
        hexCode = generateCode(line, i)

    print("Machine code: " + hexCode, end='\n\n')
    ftemp.write("0x" + hexCode + ",")
    fout.write(hexCode + '\n')
fout.close()
ftemp.close()
asm_input.close()
