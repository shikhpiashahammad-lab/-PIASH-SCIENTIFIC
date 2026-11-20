import ast
import math
from functools import partial

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup

Window.clearcolor = (0.035, 0.045, 0.065, 1)

class SafeCalculator:
    def __init__(self):
        self.degrees = True
        self.inverse = False
        self.history = []

    def calculate(self, expression):
        expression = expression.replace("×", "*").replace("÷", "/").replace("^", "**")
        expression = expression.replace("π", "pi").replace("√", "sqrt")
        tree = ast.parse(expression, mode="eval")
        value = self._eval(tree.body)
        if isinstance(value, complex):
            raise ValueError("Complex results are not supported")
        return value

    def _eval(self, node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.Num):
            return node.n
        if isinstance(node, ast.BinOp):
            a, b = self._eval(node.left), self._eval(node.right)
            ops = {ast.Add: lambda: a+b, ast.Sub: lambda: a-b,
                   ast.Mult: lambda: a*b, ast.Div: lambda: a/b,
                   ast.Pow: lambda: a**b, ast.Mod: lambda: a%b}
            for kind, fn in ops.items():
                if isinstance(node.op, kind):
                    return fn()
            raise ValueError("Unsupported operator")
        if isinstance(node, ast.UnaryOp):
            v = self._eval(node.operand)
            if isinstance(node.op, ast.UAdd): return v
            if isinstance(node.op, ast.USub): return -v
            raise ValueError("Unsupported sign")
        if isinstance(node, ast.Name):
            names = {"pi": math.pi, "e": math.e}
            if node.id in names: return names[node.id]
            raise ValueError("Unknown value")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            name = node.func.id
            args = [self._eval(x) for x in node.args]
            angle = math.radians(args[0]) if self.degrees and args else (args[0] if args else 0)
            funcs = {
                "sin": lambda: math.sin(angle), "cos": lambda: math.cos(angle),
                "tan": lambda: math.tan(angle), "asin": lambda: math.degrees(math.asin(args[0])) if self.degrees else math.asin(args[0]),
                "acos": lambda: math.degrees(math.acos(args[0])) if self.degrees else math.acos(args[0]),
                "atan": lambda: math.degrees(math.atan(args[0])) if self.degrees else math.atan(args[0]),
                "sqrt": lambda: math.sqrt(args[0]), "log": lambda: math.log10(args[0]),
                "ln": lambda: math.log(args[0]), "abs": lambda: abs(args[0]),
                "factorial": lambda: math.factorial(int(args[0])),
                "exp": lambda: math.exp(args[0])
            }
            if name not in funcs: raise ValueError("Function not allowed")
            return funcs[name]()
        raise ValueError("Invalid expression")


class CalculatorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.calc = SafeCalculator()
        self.mode = "BASIC"
        self.inverse = False
        self.root_box = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(9))
        self.add_widget(self.root_box)

        header = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        header.add_widget(Label(text="[b]PIASH[/b] [color=55C7FF]SCIENTIFIC[/color]",
                                markup=True, font_size="20sp", halign="left"))
        self.mode_btn = Button(text="DEG", size_hint_x=None, width=dp(68),
                               background_normal="", background_color=(0.12,0.19,0.28,1))
        self.mode_btn.bind(on_release=self.toggle_angle)
        header.add_widget(self.mode_btn)
        self.root_box.add_widget(header)

        self.display = TextInput(text="", hint_text="0", multiline=False,
                                 readonly=False, font_size="30sp", size_hint_y=None,
                                 height=dp(88), halign="right", padding=[dp(12),dp(22)],
                                 background_color=(0.075,0.095,0.13,1),
                                 foreground_color=(0.95,0.97,1,1), cursor_color=(0.3,0.8,1,1))
        self.root_box.add_widget(self.display)

        tabs = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        for name in ("BASIC", "SCIENTIFIC"):
            b = Button(text=name, background_normal="", background_color=(0.12,0.34,0.48,1))
            b.bind(on_release=partial(self.set_mode, name))
            tabs.add_widget(b)
        self.root_box.add_widget(tabs)

        self.keys = BoxLayout(orientation="vertical", spacing=dp(7))
        self.root_box.add_widget(self.keys)
        self.render_keys()

        bottom = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        for label, fn in (("HIST", self.show_history), ("INV", self.toggle_inverse), ("⌫", self.backspace), ("AC", self.clear)):
            b = Button(text=label, background_normal="", background_color=(0.17,0.2,0.27,1))
            b.bind(on_release=lambda _b, f=fn: f())
            bottom.add_widget(b)
        self.root_box.add_widget(bottom)

    def toggle_angle(self, *_):
        self.calc.degrees = not self.calc.degrees
        self.mode_btn.text = "DEG" if self.calc.degrees else "RAD"

    def set_mode(self, mode, *_):
        self.mode = mode
        self.render_keys()

    def toggle_inverse(self):
        self.inverse = not self.inverse
        self.render_keys()

    def render_keys(self):
        self.keys.clear_widgets()
        if self.mode == "BASIC":
            rows = [["7","8","9","÷"],["4","5","6","×"],["1","2","3","−"],["0",".","(",")"],["π","^","+","="]]
        else:
            rows = [["sin(","cos(","tan(","sqrt("],
                    ["asin(","acos(","atan(","log("],
                    ["ln(","exp(","abs(","factorial("],
                    ["7","8","9","÷"],["4","5","6","×"],
                    ["1","2","3","−"],["0",".","π","+"],["^","(",")","="]]
            if self.inverse:
                rows[0] = ["asin(","acos(","atan(","sqrt("]
                rows[1] = ["sin(","cos(","tan(","log("]
        for row in rows:
            line = BoxLayout(spacing=dp(7))
            for key in row:
                color = (0.13,0.2,0.29,1)
                if key == "=": color = (0.02,0.48,0.72,1)
                elif key in ("÷","×","−","+","^"): color = (0.16,0.29,0.39,1)
                b = Button(text=key, font_size="18sp", background_normal="", background_color=color)
                b.bind(on_release=partial(self.press, key))
                line.add_widget(b)
            self.keys.add_widget(line)

    def press(self, key, *_):
        if key == "=":
            self.solve()
        elif key == "−":
            self.display.text += "-"
        elif key == "×":
            self.display.text += "*"
        elif key == "÷":
            self.display.text += "/"
        else:
            self.display.text += key

    def solve(self):
        try:
            original = self.display.text
            result = self.calc.calculate(original)
            shown = str(round(result, 10)) if isinstance(result, float) else str(result)
            self.calc.history.append(original + " = " + shown)
            self.display.text = shown
        except Exception:
            self.display.text = "Error"

    def clear(self, *_):
        self.display.text = ""

    def backspace(self, *_):
        self.display.text = self.display.text[:-1]

    def show_history(self, *_):
        content = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))
        history = "\n".join(self.calc.history[-12:]) or "No calculations yet"
        content.add_widget(Label(text=history))
        close = Button(text="CLOSE", size_hint_y=None, height=dp(42))
        popup = Popup(title="Calculation History", content=content, size_hint=(0.9,0.6))
        close.bind(on_release=popup.dismiss)
        content.add_widget(close)
        popup.open()


class PiashScientificApp(App):
    def build(self):
        self.title = "PIASH SCIENTIFIC"
        manager = ScreenManager()
        manager.add_widget(CalculatorScreen(name="calculator"))
        return manager

if __name__ == "__main__":
    PiashScientificApp().run()
