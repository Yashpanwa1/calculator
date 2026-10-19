import tkinter as tk
import ast
import operator

# Windows-style dark calculator
BG = "#202020"
DISPLAY_BG = "#202020"
BTN = "#323232"
BTN_HOVER = "#414141"
OP_BTN = "#323232"
EQUAL_BTN = "#4CC2FF"
TEXT = "#FFFFFF"
MUTED = "#AAAAAA"

root = tk.Tk()
root.title("Calculator")
root.geometry("340x520")
root.resizable(False, False)
root.configure(bg=BG)

expression = ""
just_calculated = False

display = tk.StringVar(value="0")
history = tk.StringVar(value="")

history_label = tk.Label(
    root, textvariable=history, bg=DISPLAY_BG,
    fg=MUTED, anchor="e", font=("Segoe UI", 11)
)
history_label.pack(fill="x", padx=18, pady=(20, 0))

screen = tk.Label(
    root, textvariable=display, bg=DISPLAY_BG,
    fg=TEXT, anchor="e", font=("Segoe UI", 34),
    height=2
)
screen.pack(fill="x", padx=18)

# Safely evaluate only arithmetic expressions
OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
    ast.Mod: operator.mod,
}

def safe_eval(node):
    if isinstance(node, ast.Expression):
        return safe_eval(node.body)
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        a = safe_eval(node.left)
        b = safe_eval(node.right)
        if isinstance(node.op, ast.Div) and b == 0:
            raise ZeroDivisionError
        return OPS[type(node.op)](a, b)
    if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
        return OPS[type(node.op)](safe_eval(node.operand))
    raise ValueError("Invalid expression")

def format_number(value):
    if isinstance(value, float):
        if not value == value or abs(value) == float("inf"):
            return "Error"
        return f"{value:.10g}"
    return str(value)

def update():
    display.set(expression if expression else "0")

def press(key):
    global expression, just_calculated

    if key == "C":
        expression = ""
        history.set("")
        just_calculated = False

    elif key == "CE":
        expression = ""
        just_calculated = False

    elif key == "⌫":
        expression = expression[:-1]
        just_calculated = False

    elif key == "=":
        if not expression:
            return
        try:
            result = safe_eval(ast.parse(expression, mode="eval"))
            history.set(expression + " =")
            expression = format_number(result)
            just_calculated = True
        except ZeroDivisionError:
            expression = ""
            display.set("Cannot divide by zero")
            history.set("")
            just_calculated = False
            return
        except (ValueError, SyntaxError, OverflowError):
            expression = ""
            display.set("Error")
            history.set("")
            just_calculated = False
            return

    elif key == "%":
        try:
            result = safe_eval(ast.parse(expression, mode="eval"))
            expression = format_number(result / 100)
        except (ValueError, SyntaxError, ZeroDivisionError):
            return
        just_calculated = False

    elif key == "±":
        if expression:
            try:
                expression = format_number(
                    -safe_eval(ast.parse(expression, mode="eval"))
                )
            except (ValueError, SyntaxError, ZeroDivisionError):
                return
        just_calculated = False

    else:
        if just_calculated:
            if key in "+-*/":
                pass
            else:
                expression = ""
                history.set("")
        just_calculated = False

        if key == ".":
            # Avoid multiple decimal points in the current number
            current = expression.replace("+", " ").replace("-", " ")
            current = current.replace("*", " ").replace("/", " ")
            if "." in current.split()[-1] if current.split() else False:
                return
            if not expression or expression[-1] in "+-*/":
                expression += "0"
        expression += key

    update()

# Button layout
buttons = [
    ["%", "CE", "C", "⌫"],
    ["1/x", "x²", "√x", "÷"],
    ["7", "8", "9", "×"],
    ["4", "5", "6", "−"],
    ["1", "2", "3", "+"],
    ["±", "0", ".", "="],
]

def click(key):
    if key == "÷":
        press("/")
    elif key == "×":
        press("*")
    elif key == "−":
        press("-")
    elif key == "1/x":
        try:
            value = safe_eval(ast.parse(expression, mode="eval"))
            if value == 0:
                raise ZeroDivisionError
            history.set(f"1/({expression}) =")
            press("C")
            press(str(1 / value))
        except (ValueError, SyntaxError, ZeroDivisionError):
            display.set("Cannot divide by zero")
    elif key == "x²":
        try:
            value = safe_eval(ast.parse(expression, mode="eval"))
            history.set(f"sqr({expression}) =")
            expression_result = format_number(value * value)
            global_expression(expression_result)
        except (ValueError, SyntaxError):
            pass
    elif key == "√x":
        import math
        try:
            value = safe_eval(ast.parse(expression, mode="eval"))
            if value < 0:
                raise ValueError
            history.set(f"√({expression}) =")
            global_expression(format_number(math.sqrt(value)))
        except (ValueError, SyntaxError):
            display.set("Invalid input")
    else:
        press(key)

def global_expression(value):
    global expression, just_calculated
    expression = value
    just_calculated = True
    update()

# Keyboard support
def keyboard(event):
    key = event.keysym
    char = event.char
    if char in "0123456789.+-*/":
        press(char)
    elif key in ("Return", "KP_Enter"):
        press("=")
    elif key == "BackSpace":
        press("⌫")
    elif key == "Escape":
        press("C")
    elif char == "%":
        press("%")

# Build buttons
grid = tk.Frame(root, bg=BG)
grid.pack(fill="both", expand=True, padx=8, pady=8)

for r, row in enumerate(buttons):
    grid.rowconfigure(r, weight=1)
    for c, key in enumerate(row):
        grid.columnconfigure(c, weight=1)

        color = EQUAL_BTN if key == "=" else BTN
        fg = "#000000" if key == "=" else TEXT

        btn = tk.Button(
            grid, text=key,
            font=("Segoe UI", 15),
            bg=color, fg=fg,
            activebackground=BTN_HOVER,
            activeforeground=TEXT,
            relief="flat", bd=0,
            cursor="hand2",
            command=lambda k=key: click(k)
        )
        btn.grid(
            row=r, column=c,
            sticky="nsew", padx=3, pady=3
        )

        if key != "=":
            btn.bind(
                "<Enter>",
                lambda e, b=btn: b.configure(bg=BTN_HOVER)
            )
            btn.bind(
                "<Leave>",
                lambda e, b=btn: b.configure(bg=BTN)
            )

root.bind("<Key>", keyboard)
root.mainloop()
