from queue import LifoQueue
from functools import wraps


class DivByZero(Exception):
    """
    Error: Div by zero.
    """


class VMSegfault(Exception):
    """
    Error: exception thrown when an invalid memory address is requested.
    """


class VMStackFail(Exception):
    """
    Error: exception thrown when the stack content is not as expected.
    """


class InvalidInstruction(Exception):
    """
    Error: exception thrown when a instruction could not be decoded.
    """


def check_argument_length(n=1):
    """
    Decorator for the vm functions.
    It checks if there are enough items on the stack.
    If not a stackfail exception is raised.
    :param n: Number of arguments which needs to be on the stack.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(vm_state, arg):
            if vm_state.stack.qsize() < n:
                raise VMStackFail("[VM] Error: Not enough arguments.")
            return func(vm_state, arg)
        return wrapper
    return decorator


class VMState:
    """
    All vm execution state information is stored in here
    """

    def __init__(self):
        # Where in the program code are we?
        self.pc = 0

        # Stores which id is given the next instruction that is registered.
        self.next_op_id = 0

        # The main execution state stack.
        self.stack = LifoQueue()

        # Mapping of instruction name to operation id.
        self.instruction_ids = {}

        # Mapping of operation id to action.
        self.instruction_actions = {}

        # output string of the vm.
        self.vm_output = ""

        # Create the vm.
        self.create_vm()

    def create_vm(self):
        """
        Creates the vm with all available instructions registered.
        Instructions are registered with the register_function.
        """

        self.register_instruction("PRINT", self.vm_print)
        self.register_instruction("LOAD_CONST", self.vm_load_const)
        self.register_instruction("ADD", self.vm_add)
        self.register_instruction("EXIT", self.vm_exit)
        self.register_instruction("POP", self.vm_pop)
        self.register_instruction("DIV", self.vm_div)
        self.register_instruction("EQ", self.vm_eq)
        self.register_instruction("NEQ", self.vm_neq)
        self.register_instruction("DUP", self.vm_dup)
        self.register_instruction("JMP", self.vm_jmp)
        self.register_instruction("JMPZ", self.vm_jmpz)
        self.register_instruction("WRITE", self.vm_write)
        self.register_instruction("WRITE_CHAR", self.vm_write_char)

    def register_instruction(self, name, action):
        """
        Register a function to the vm.
        :param name: The function name. Acts as texual identifier.
        :param action: The function which should be executed.
        """

        self.instruction_ids[name] = self.next_op_id
        self.instruction_actions[self.next_op_id] = action
        self.next_op_id += 1

    def assemble(self, input_code):
        """
        Converts the given input string to executable code.
        The code itself is just a list of instructions.

        :param input_code: the program text which will be converted to executable instructions.
        :return: The instructions list. The list contains executable instructions.
        """

        code = []
        # Get each line. Filter empty lines.
        for line in filter(None, input_code.split("\n")):
            # words[0] -> op_name
            # words[1] -> argument
            words = line.split(" ")

            # Only one instruction and max one argument
            if len(words) >= 3:
                raise InvalidInstruction(f"Error: More than one instruction argument: {line}")

            if words[0] not in self.instruction_ids:
                raise InvalidInstruction(f"Unknown instruction: {words[0]}")

            # Parse the argument and save the instruction id and the argument for later execution.
            code.append((self.instruction_ids[words[0]], int(words[1]) if len(words) == 2 else None))

        return code

    def run(self, code):
        """
        Execute the given instructions.

        :param code: The instructions to execute.
        :return: A tuple containing the top element on the stack after the execution and the output string.
        """

        while True:
            if self.pc < 0 or self.pc >= len(code):
                raise VMSegfault("[VM] Error: invalid pc.")

            op_id, arg = code[self.pc]

            self.pc += 1
            status = self.instruction_actions[op_id](arg)

            if not status:
                break

        return self.stack.queue[-1], self.vm_output

    ##
    # VM Functions
    ##
    @check_argument_length()
    def vm_print(self, _):
        print(self.stack.queue[-1])
        return True

    def vm_load_const(self, arg):
        self.stack.put(arg)
        return True

    @check_argument_length(2)
    def vm_add(self, _):
        tos = self.stack.get()
        tos_1 = self.stack.get()

        self.stack.put(tos + tos_1)

        return True

    @check_argument_length()
    def vm_exit(self, _):
        return False

    @check_argument_length()
    def vm_pop(self, _):
        self.stack.get()
        return True

    @check_argument_length(2)
    def vm_div(self, _):
        tos = self.stack.get()
        tos_1 = self.stack.get()

        if tos == 0:
            raise DivByZero("[VM] Error: Divide by zero.")

        self.stack.put(tos_1 // tos)
        return True

    @check_argument_length(2)
    def vm_eq(self, _):
        self.stack.put(1 if self.stack.get() == self.stack.get() else 0)
        return True

    @check_argument_length(2)
    def vm_neq(self, _):
        self.stack.put(0 if self.stack.get() == self.stack.get() else 1)
        return True

    @check_argument_length()
    def vm_dup(self, _):
        self.stack.put(self.stack.queue[-1])
        return True

    def vm_jmp(self, arg):
        self.pc = arg
        return True

    @check_argument_length()
    def vm_jmpz(self, arg):
        if not self.stack.queue[-1]:
            self.stack.get()
            self.pc = arg
        return True

    @check_argument_length()
    def vm_write(self, _):
        self.vm_output = self.vm_output + str(self.stack.queue[-1])
        return True

    @check_argument_length()
    def vm_write_char(self, _):
        self.vm_output = self.vm_output + chr(self.stack.queue[-1])
        return True
