
import argparse
import sys
import re
import xml.etree.ElementTree as ET
import xml.dom.minidom

instructions = {
    "move": ["v", "s"],
    "createframe": [],
    "pushframe": [],
    "popframe": [],
    "defvar": ["v"],
    "call": ["l"],
    "return": [],

    "pushs": ["s"],
    "pops": ["v"],

    "add": ["v", "s", "s"],
    "sub": ["v", "s", "s"],
    "mul": ["v", "s", "s"],
    "idiv": ["v", "s", "s"],
    "lt": ["v", "s", "s"],
    "gt": ["v", "s", "s"],
    "eq": ["v", "s", "s"],
    "and": ["v", "s", "s"],
    "or": ["v", "s", "s"],
    "not": ["v", "s"],
    "int2char": ["v", "s"],
    "stri2int": ["v", "s", "s"],

    "read": ["v", "t"],
    "write": ["s"],

    "concat": ["v", "s", "s"],
    "strlen": ["v", "s"],
    "getchar": ["v", "s", "s"],
    "setchar": ["v", "s", "s"],

    "type": ["v", "s"],

    "label": ["l"],
    "jump": ["l"],
    "jumpifeq": ["l", "s", "s"],
    "jumpifneq": ["l", "s", "s"],
    "exit": ["s"],

    "dprint": ["s"],
    "break": []
}


def is_header(line):
    return re.match(r"^\s*\.IPPcode24\s*$", line, re.IGNORECASE)


def is_var(var):
    if "@" not in var:
        return False
    frame, name = var.split("@", 1)
    if frame not in ["GF", "TF", "LF"]:
        return False
    return bool(re.match(r"^[a-zA-Z_\-$&%*!?][\w\-$&%*!?]*$", name))


def is_symb(symb):
    if "@" not in symb:
        return False
    type_, value = symb.split("@", 1)
    if not is_type(type_):
        return False
    if type_ == "nil":
        return value == "nil"
    if type_ == "int":
        return bool(re.match(r"^-?\d+$", value)) or \
               bool(re.match(r"^-?0x[0-9a-fA-F]+$", value)) or \
               bool(re.match(r"^-?0o[0-7]+$", value)) or \
               bool(re.match(r"^\+?\d+$", value))
    if type_ == "bool":
        return value in ["true", "false"]
    if type_ == "string":
        return bool(re.match(r"^([^\\\s]|(\\[0-9]{3}))*$", value))

    return False


def is_type(type_):
    return bool(re.match(r"^(int|bool|string|nil)$", type_))


def is_label(label):
    return bool(re.match(r"^[a-zA-Z_\-$&%*!?][\w\-$&%*!?]*$", label))


def validate_operand_type(expected_type, actual_type, operand):
    if expected_type == "v" and actual_type == "var":
        return True
    if expected_type == "s" and actual_type in ["var", "int", "bool", "string", "nil"]:
        return True
    if expected_type == "l" and actual_type == "label":
        return True
    if expected_type == "t" and actual_type == "type":
        return True
    return False


def determine_operand_type_and_value(operand, expected_type):
    if expected_type == "l":
        if is_label(operand):
            return "label", operand
        else:
            print("Error: Invalid label format.", file=sys.stderr)
            sys.exit(23)
    elif is_type(operand):
        return "type", operand
    elif is_var(operand):
        return "var", operand
    elif is_symb(operand):
        type_, value = operand.split("@", 1)
        return type_, value
    else:
        print(f"Error: Invalid label format '{operand}'.", file=sys.stderr)
        sys.exit(23)


def parse_instruction(instruction, order):
    words = instruction.split(maxsplit=1)
    if len(words) < 1:
        print("Error: Missing instruction.", file=sys.stderr)
        sys.exit(23)

    instruction_name = words[0].lower()
    operands_raw = words[1:] if len(words) > 1 else [""]

    if instruction_name not in instructions:
        print(f"Error: Unknown instruction '{instruction_name}'.", file=sys.stderr)
        sys.exit(23)

    operands_expected = instructions[instruction_name]
    operands = re.split(r'\s+', operands_raw[0].strip()) if operands_raw else []

    if not operands_raw or operands_raw[0] == '':
        operands = []

    if len(operands) != len(operands_expected):
        print(
            f"Error: Incorrect number of operands for instruction '{instruction_name}'. Expected {len(operands_expected)}, got {len(operands)}.",
            file=sys.stderr)
        sys.exit(23)

    instruction_element = ET.Element("instruction", order=str(order), opcode=instruction_name.upper())

    for i, operand in enumerate(operands):
        expected_type = operands_expected[i]
        actual_type, actual_value = determine_operand_type_and_value(operand, expected_type)

        if not validate_operand_type(expected_type, actual_type, operand):
            print(
                f"Error: Incorrect type of operand {i + 1} for instruction '{instruction_name}'. Expected {expected_type}, got {actual_type}.",
                file=sys.stderr)
            sys.exit(23)

        operand_element = ET.SubElement(instruction_element, f"arg{i + 1}", type=actual_type)
        operand_element.text = actual_value

    return instruction_element


def generate_xml_output(instructions_xml):
    root = ET.Element("program", language="IPPcode24")
    for instruction_xml in instructions_xml:
        root.append(instruction_xml)

    rough_string = ET.tostring(root, 'utf-8')
    reparsed = xml.dom.minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")

    print(pretty_xml)


def main():
    parser = argparse.ArgumentParser(description="IPPcode24 parser")
    parser.add_argument('--input', type=argparse.FileType('r'), default=sys.stdin,
                        help='Input file with IPPcode24 code. Reads from standard input if not specified.')
    args = parser.parse_args()

    header_found = False
    instructions_xml = []
    order = 0

    for line in args.input:
        line = line.strip()
        if line.startswith("#") or not line:
            continue

        if not header_found:
            if is_header(line.split("#")[0].strip()):
                header_found = True
                continue
            else:
                print("Error: Missing or incorrect header.", file=sys.stderr)
                sys.exit(21)

        line = line.split("#")[0].strip()
        if line:
            order += 1
            instruction_xml = parse_instruction(line, order)
            instructions_xml.append(instruction_xml)

    if not header_found:
        print("Error: Missing or incorrect header.", file=sys.stderr)
        sys.exit(21)
    generate_xml_output(instructions_xml)


if __name__ == "__main__":
    main()
