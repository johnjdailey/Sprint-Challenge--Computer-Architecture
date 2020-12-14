#cpu.py



"""CPU functionality."""

import sys


# Operators in machine code

HLT = 0b00000001 # Halt 
LDI = 0b10000010 # Load Immediate
PRN = 0b01000111 # Print
MUL = 0b10100010 # Multiply
PUSH = 0b01000101 # Push in stack
POP = 0b01000110 # Pop in stack
CALL = 0b01010000 # Calls a subroutine (function)
RET = 0b00010001 # Return from subroutine

# Sprint Challenge

CMP = 0b10100111 # Compare the values in two registers
JMP = 0b01010100 # Jump to the address stored in the given register
JEQ = 0b01010101 # If `equal` flag is set (true), jump to the address stored in the given register
JNE = 0b01010110 # If `E` flag is clear (false, 0), jump to the address stored in the given register.

SP = 7 # Stack Pointer


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # Create 256 bytes of RAM

        self.ram = [0] * 256

        # Create 8 reg

        self.registers = [0] * 8
        self.registers[7] = 0xF4

        # Set the program counter to 0

        self.pc = 0
        self.halted = False

        # Flags register to hold the current flags status

        self.FL = 0b00000000

    def load(self, filename):
        """Load a program into memory."""

        address = 0

#        # For now, we've just hardcoded a program:
#
#        program = [
#            # From print8.ls8
#            0b10000010, # LDI R0,8
#            0b00000000,
#            0b00001000,
#            0b01000111, # PRN R0
#            0b00000000,
#            0b00000001, # HLT
#        ]
#
#        for instruction in program:
#            self.ram[address] = instruction
#            address += 1

        # Loading a program from a file

        # Open the file

        with open(filename) as my_file:

            # Go through each line to parse and get the instruction
            
            for line in my_file:

                # Try and get the instruction/operand in the line
                
                comment_split = line.split("#")
                maybe_binary_number = comment_split[0]
                try:
                    x = int(maybe_binary_number, 2)
                    self.ram_write(x, address)
                    address += 1
                except:
                    continue

#        try:
#            with open(filename) as my_file:
#                for line in my_file:
#                    comment_split = line.split("#")
#                    maybe_binary_number = comment_split[0]
#        
#                    try:
#                        x = int(maybe_binary_number, 2)
#                        print("{:08b}: {:d}".format(x, x))
#                    except:
#                        print(f"failed to cast {maybe_binary_number} to an int")
#                        continue
#
#        except FileNotFoundError:
#            print("file not found...")


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        #if op == "ADD":
        #    self.reg[reg_a] += self.reg[reg_b]

        if op == MUL:
            self.registers[reg_a] *= self.registers[reg_b]
            self.pc += 3

       # Sprint Challenge

        elif op == CMP:
            if self.registers[reg_a] < self.registers[reg_b]:
                self.FL = 0b00000100
            if self.registers[reg_a] > self.registers[reg_b]:
                self.FL = 0b00000010
            if self.registers[reg_a] == self.registers[reg_b]:
                self.FL = 0b00000001

        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def ram_read(self, address):
        """
        Reads the value at the designated address of RAM
        """
        return self.ram[address]

    def ram_write(self, value, address):
        """
        Writes a value to RAM at the designated address
        """
        self.ram[address] = value

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        while not self.halted:
            instruction_to_execute = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            self.execute_instruction(instruction_to_execute, operand_a, operand_b)

    def execute_instruction(self, instruction, operand_a, operand_b):
        if instruction == HLT:
            self.halted = True

            # Increment pointer counter to the next instruction
            
            self.pc += 1

        elif instruction == PRN:
            print(self.registers[operand_a])

            # Increment pointer counter to the next instruction

            self.pc += 2

        elif instruction == LDI:
            self.registers[operand_a] = operand_b

            # Increment pointer counter to the next instruction

            self.pc += 3

        # MUL should be in the alu

        elif instruction == MUL:
            self.alu(instruction, operand_a, operand_b)
            #self.registers[operand_a] *= self.registers[operand_b]
            #self.pc += 3

        elif instruction == PUSH:
            
            # Decrement the stack pointer
            
            self.registers[SP] -= 1

            # Store the operand in the stack

            self.ram_write(self.registers[operand_a], self.registers[SP])

            # Increment pointer counter to the next instruction

            self.pc += 2

        elif instruction == POP:

            # Pops the value from the top of the stack and stores it in the given register

            # Read the value from the top of the stack

            self.registers[operand_a] = self.ram_read(self.registers[SP])

            # Increment the stack pointer

            self.registers[SP] += 1

            # Increment pointer counter to the next instruction
            
            self.pc += 2

        elif instruction == CALL:

            # Push address of next instruction to stack
    
            self.registers[SP] -= 1
            self.ram_write(self.pc+2, self.registers[SP])

            # Jump to the address at the given register

            self.pc = self.registers[operand_a]
       
        elif instruction == RET:

            self.pc = self.ram_read(self.registers[SP])
            self.registers[SP] += 1

        # Sprint Challenge

        # Compare the values in two registers

        elif instruction == CMP:
            self.alu(instruction, operand_a, operand_b)
            self.pc += 3

        # Jump to the address stored in the given register

        elif instruction == JMP:

            # Get the address from the register

            register_number = self.ram_read(self.pc + 1)

            # Set pc to the address

            self.pc = self.registers[register_number]
 
        # If `equal` flag is set (true), jump to the address stored in the given register

        elif instruction == JEQ:

            if self.FL == 0b00000001:
                register_number = self.ram_read(self.pc +1)
                self.pc = self.registers[register_number]
            else:
                self.pc += 2

        # If `E` flag is clear (false, 0), jump to the address stored in the given register.

        elif instruction == JNE:
            if self.FL != 0b00000001:
                register_number = self.ram_read(self.pc +1)
                self.pc = self.registers[register_number]
            else:
                self.pc += 2
                
        else:
            print("idk what to do.")
            pass
