
import sys
import re
import yaml


class CheriInterpreter:
    def __init__(self):
        self.variables = {}

    def tokenize(self, code):
        """Break code into tokens"""
        code = re.sub(r'#.*', '', code)

        tokens = []
        i = 0
        while i < len(code):
            # Skip whitespace
            if code[i].isspace():
                i += 1
                continue

            # Numbers
            if code[i].isdigit():
                j = i
                while j < len(code) and (code[j].isdigit() or code[j] == '.'):
                    j += 1
                tokens.append(("NUMBER", code[i:j]))
                i = j
                continue

            if code[i] == '"':
                j = i + 1
                while j < len(code) and code[j] != '"':
                    j += 1
                if j < len(code):  # Make sure we found the closing quote
                    tokens.append(("STRING", code[i + 1:j]))
                    i = j + 1
                else:
                    raise SyntaxError("Unterminated string")
                continue

            if code[i].isalpha() or code[i] == '_':
                j = i
                while j < len(code) and (code[j].isalnum() or code[j] == '_'):
                    j += 1
                word = code[i:j]
                if word == "var":
                    tokens.append(("VAR", word))
                elif word == "print":
                    tokens.append(("PRINT", word))
                elif word == "if":
                    tokens.append(("IF", word))
                elif word == "else":
                    tokens.append(("ELSE", word))
                elif word == "for":
                    tokens.append(("FOR", word))
                elif word == "while":
                    tokens.append(("WHILE", word))
                else:
                    tokens.append(("IDENTIFIER", word))
                i = j
                continue

            if code[i:i + 2] in ["==", "!=", "<=", ">="]:
                tokens.append(("OPERATOR", code[i:i + 2]))
                i += 2
                continue

            if code[i] in "+-*/=<>(){}[]":
                tokens.append(("OPERATOR", code[i]))
                i += 1
                continue

            if code[i] == "+":
                tokens.append(("OPERATOR", "+"))
                i += 1
                continue

            if code[i] == ";":
                tokens.append(("SEMICOLON", ";"))
                i += 1
                continue

            raise SyntaxError(f"Unrecognized character: {code[i]}")

        return tokens

    def parse_and_execute(self, tokens):
        i = 0
        while i < len(tokens):
            token_type, token_value = tokens[i]
            if token_type == "VAR":
                i += 1
                if i < len(tokens) and tokens[i][0] == "IDENTIFIER":
                    var_name = tokens[i][1]
                    i += 1
                    if i < len(tokens) and tokens[i][0] == "OPERATOR" and tokens[i][1] == "=":
                        i += 1
                        value, i = self.parse_expression(tokens, i)
                        self.variables[var_name] = value
                    else:
                        raise SyntaxError("Expected '=' after variable name")
                else:
                    raise SyntaxError("Expected identifier after 'var'")

            elif token_type == "PRINT":
                i += 1
                value, i = self.parse_expression(tokens, i)
                print(value)

            else:
                i += 1

    def parse_expression(self, tokens, i):
        if i >= len(tokens):
            raise SyntaxError("Unexpected end of input")

        token_type, token_value = tokens[i]

        if token_type == "NUMBER":
            try:
                return float(token_value), i + 1
            except ValueError:
                raise SyntaxError(f"Invalid number: {token_value}")

        elif token_type == "STRING":
            return token_value, i + 1

        elif token_type == "IDENTIFIER":
            if token_value in self.variables:
                return self.variables[token_value], i + 1
            else:
                raise NameError(f"Variable '{token_value}' not defined")

        elif token_type == "OPERATOR" and token_value == "(":
            left_value, i = self.parse_expression(tokens, i + 1)

            if i < len(tokens) and tokens[i][0] == "OPERATOR" and tokens[i][1] in "+-*/":
                op = tokens[i][1]
                i += 1
                right_value, i = self.parse_expression(tokens, i)

                if op == "+":
                    result = left_value + right_value
                elif op == "-":
                    result = left_value - right_value
                elif op == "*":
                    result = left_value * right_value
                elif op == "/":
                    if right_value == 0:
                        raise ZeroDivisionError("Division by zero")
                    result = left_value / right_value

                if i < len(tokens) and tokens[i][0] == "OPERATOR" and tokens[i][1] == ")":
                    return result, i + 1
                else:
                    raise SyntaxError("Expected closing parenthesis")
            else:
                if i < len(tokens) and tokens[i][0] == "OPERATOR" and tokens[i][1] == ")":
                    return left_value, i + 1
                else:
                    raise SyntaxError("Expected operator or closing parenthesis")

        elif token_type == "STRING":
            value = token_value
            i += 1
            while i < len(tokens) and tokens[i][0] == "OPERATOR" and tokens[i][1] == "+":
                i += 1
                right_value, i = self.parse_expression(tokens, i)
                value += str(right_value)
            return value, i

        else:
            raise SyntaxError(f"Unexpected token: {token_type}, {token_value}")

    def run_file(self, filename):
        try:
            with open(filename, 'r') as f:
                code = f.read()
            tokens = self.tokenize(code)
            self.parse_and_execute(tokens)
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False


def main():
    if len(sys.argv) != 2:
        print("Usage: python cheri_interpreter.py <filename>")
        return

    interpreter = CheriInterpreter()
    interpreter.run_file(sys.argv[1])


if __name__ == "__main__":
    main()

