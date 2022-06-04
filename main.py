#!/usr/bin/env python3
from VMState import vm


program = ("LOAD_CONST 432\n"
           "LOAD_CONST 905\n"
           "ADD\n"
           "PRINT\n"
           "LOAD_CONST 65\n"
           "WRITE_CHAR\n"
           "EXIT\n")

program2 = ("LOAD_CONST 100\n"
            "LOAD_CONST 0\n"
            "DIV\n"
            "EXIT")


def test_vm(program_str):
    print("Initializing vm...")
    vm_state = vm.VMState()

    try:
        code = vm_state.assemble(program_str)
        top, output = vm_state.run(code)
        print(f"Top: {top}, output: {output}")

    # Catch error and do something useful. I mean not like below xD
    except vm.VMStackFail as e:
        print(e)
    except vm.VMSegfault as e:
        print(f"{e}\nTried to access invalid memory at pc = {vm_state.pc}")
    except vm.DivByZero as e:
        print(e)


if __name__ == '__main__':
    test_vm(program)
