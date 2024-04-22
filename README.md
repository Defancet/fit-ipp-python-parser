# Implementation documentation for the 1. task for IPP 2023/2024 <br> Name and surname: Maksim Kalutski <br> Login: xkalut00

The IPPcode24 Code Analyzer, implemented in Python 3.10, is designed as a filter script (`parse.py`) that reads
IPPcode24 source code from standard input, checks for lexical and syntactic correctness, and outputs an XML
representation of the program according to specification.

## Usage

The script is designed to be run from the command line, with the following usage:

```
python3 parse.py [--input FILE] [--help]
```

- `--input FILE` specifies the input file with IPPcode24 source code. If not specified, the script reads from standard
  input.
- `--help` displays the help message with usage information.

## Implementation Details

### Libraries and Tools

The script uses the following standard libraries:

- `argparse`: for command-line argument parsing.
- `sys`: for standard input/output and error handling.
- `re`: for regular expression-based lexical analysis.
- `xml.etree.ElementTree`: for generating XML output.

### Error Handling

Error codes are used to indicate specific types of failures, such as:

- `0`: Successful execution.
- `21`: Missing or incorrect header.
- `23`: Lexical or syntactic error in the source code.
- `99`: Internal error.

### Lexical and Syntactic Analysis

- Lexical analysis is conducted using regular expressions to identify valid identifiers, literals, and instruction
  formats.
- Syntactic analysis ensures each instruction complies with IPPcode24's format and operand type expectations.

### XML Generation

The script uses the `xml.etree.ElementTree` library to generate well-formed XML, ensuring correct nesting and attribute
assignment for instructions and their operands. The XML output is formatted for human readability.

### Edge Cases and Specific Solutions

- **Comments**: Ignores comments and empty lines in the input, ensuring they do not affect the analysis.
- **Case Sensitivity**: Distinguishes between case-sensitive and case-insensitive parts of the language, particularly
  instruction names and operand types.
- **Unknown Instructions**: Implements a default error mechanism for unrecognized instructions.
- **Special Characters in Strings**: Uses escape sequences for special characters in strings, ensuring accurate XML
  representation.
- **Type Checking**: Ensures correct operand types for each instruction, including variable names, literals, and labels.

## Conclusion

The `parse.py` script represents solution for analyzing and converting IPPcode24 into its XML representation. It
features command-line usage, regular expression-based lexical analysis, structured XML output, error handling, and type
checking. This script effectively validates IPPcode24 syntax and could be expanded for further tasks like integration
into an interpreter.