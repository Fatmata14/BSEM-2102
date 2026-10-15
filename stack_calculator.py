

import sys
from pathlib import Path

# --------------------------------------------------------------------------
# 1. Stack class
# --------------------------------------------------------------------------
class Stack:
    """A simple LIFO stack backed by a Python list."""

    def __init__(self):
        self._items = []

    def push(self, item):
        """Add an item to the top of the stack."""
        self._items.append(item)

    def pop(self):
        """Remove and return the top item. Raises if the stack is empty."""
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self):
        """Return the top item without removing it."""
        if self.is_empty():
            raise IndexError("peek from empty stack")
        return self._items[-1]

    def is_empty(self):
        return len(self._items) == 0

    def size(self):
        return len(self._items)


# --------------------------------------------------------------------------
# 2. Expression parsing and evaluation
# --------------------------------------------------------------------------
BINARY_OPS = {"+", "-", "*", "/"}
UNARY_MINUS = "u-"                       # internal symbol for negation
PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2, UNARY_MINUS: 3}


def tokenize(expression):
    """Split an expression string into numbers, operators and parentheses.

    A '-' is treated as unary (negation) when it appears at the start of the
    expression, after '(' or after another operator.
    """
    tokens = []
    i, n = 0, len(expression)
    while i < n:
        ch = expression[i]
        if ch.isspace():
            i += 1
        elif ch.isdigit() or ch == ".":
            j = i
            while j < n and (expression[j].isdigit() or expression[j] == "."):
                j += 1
            text = expression[i:j]
            if text.count(".") > 1 or text == ".":
                raise ValueError(f"invalid number '{text}'")
            tokens.append(float(text) if "." in text else int(text))
            i = j
        elif ch in BINARY_OPS:
            previous = tokens[-1] if tokens else None
            is_unary = (
                ch == "-"
                and (previous is None or previous == "(" or previous in PRECEDENCE)
            )
            tokens.append(UNARY_MINUS if is_unary else ch)
            i += 1
        elif ch in "()":
            tokens.append(ch)
            i += 1
        else:
            raise ValueError(f"invalid character '{ch}'")
    return tokens


def apply_operator(op, values):
    """Pop the operand(s) for `op` from the value stack and push the result."""
    if op == UNARY_MINUS:
        values.push(-values.pop())
        return
    if values.size() < 2:
        raise ValueError("malformed expression")
    right = values.pop()
    left = values.pop()
    if op == "+":
        values.push(left + right)
    elif op == "-":
        values.push(left - right)
    elif op == "*":
        values.push(left * right)
    elif op == "/":
        if right == 0:
            raise ZeroDivisionError("division by zero")
        values.push(left / right)


def evaluate_expression(expression):
    """Evaluate an infix expression using an operand stack and operator stack.

    Handles + - * /, parentheses, precedence, left-associativity and unary minus.
    """
    values = Stack()      # operands
    operators = Stack()   # operators and '('

    for token in tokenize(expression):
        if isinstance(token, (int, float)):
            values.push(token)
        elif token == "(":
            operators.push(token)
        elif token == ")":
            while not operators.is_empty() and operators.peek() != "(":
                apply_operator(operators.pop(), values)
            if operators.is_empty():
                raise ValueError("mismatched parentheses")
            operators.pop()                       # discard '('
        else:                                      # an operator
            while (
                not operators.is_empty()
                and operators.peek() != "("
                and token != UNARY_MINUS           # unary ops are right-assoc.
                and PRECEDENCE[operators.peek()] >= PRECEDENCE[token]
            ):
                apply_operator(operators.pop(), values)
            operators.push(token)

    while not operators.is_empty():
        op = operators.pop()
        if op == "(":
            raise ValueError("mismatched parentheses")
        apply_operator(op, values)

    if values.size() != 1:
        raise ValueError("malformed expression")
    return values.pop()


def format_result(value):
    """Show whole numbers without a decimal point (e.g. 17.0 -> 17)."""
    value = round(value, 10)
    if value == int(value):
        return str(int(value))
    return str(value)


# --------------------------------------------------------------------------
# 3 & 4. File processing
# --------------------------------------------------------------------------
def is_separator(line):
    """A separator line contains only dashes (e.g. -----)."""
    stripped = line.strip()
    return len(stripped) > 0 and set(stripped) == {"-"} and len(stripped) >= 3


def process_file(input_path, output_path):
    """Read expressions, evaluate them and write results in the same layout."""
    results = []
    with open(input_path, "r", encoding="utf-8") as infile:
        for raw in infile:
            line = raw.rstrip("\n")
            if is_separator(line) or line.strip() == "":
                results.append(line)               # keep separators / blanks
                continue
            try:
                results.append(format_result(evaluate_expression(line)))
            except (ValueError, ZeroDivisionError, IndexError) as err:
                results.append(f"Error: {err}")

    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.write("\n".join(results) + "\n")
    return results


def main():
    script_dir = Path(__file__).resolve().parent
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    else:
        input_path = script_dir / "input.txt"

    if len(sys.argv) > 2:
        output_path = sys.argv[2]
    else:
        output_path = script_dir / "output.txt"

    try:
        process_file(str(input_path), str(output_path))
    except FileNotFoundError:
        print(f"Error: could not find '{input_path}'.")
        sys.exit(1)
    print(f"Done. Results written to '{output_path}'.")


if __name__ == "__main__":
    main()
