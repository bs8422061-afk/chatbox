import json
from pathlib import Path

from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "curibot-secret-key-change-in-production"

BASE_DIR = Path(__file__).resolve().parent
USERS_FILE = BASE_DIR / "data" / "users.json"
DEFAULT_USERS = {
    "admin": "password123",
    "demo": "demo",
    "alice": "python4ever",
}


def load_users() -> dict:
    if USERS_FILE.exists():
        try:
            users = json.loads(USERS_FILE.read_text(encoding="utf-8"))
            if isinstance(users, dict):
                return {
                    str(identifier).strip().lower(): str(password)
                    for identifier, password in users.items()
                    if str(identifier).strip() and str(password)
                }
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            pass

    save_users(DEFAULT_USERS)
    return DEFAULT_USERS.copy()


def save_users(users: dict) -> None:
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    USERS_FILE.write_text(
        json.dumps(dict(sorted(users.items())), indent=2),
        encoding="utf-8",
    )


def normalize_identifier(value: str) -> str:
    return value.strip().lower()


USERS = load_users()

# ══════════════════════════════════════════════════════════════
#  KEYWORD ALIASES — maps alternative phrasings to canonical keys
# ══════════════════════════════════════════════════════════════
ALIASES = {
    # loops
    "loops":           "python loops",
    "looping":         "python loops",
    "for loop":        "python loops",
    "while loop":      "python loops",
    "iteration":       "python loops",
    "iterate":         "python loops",
    # functions
    "functions":       "python functions",
    "function":        "python functions",
    "def":             "python functions",
    "method":          "python functions",
    # classes
    "classes":         "python classes",
    "class":           "python classes",
    "object":          "python classes",
    "oop":             "python oop",
    # data types
    "data types":      "python data types",
    "types":           "python data types",
    "type":            "python data types",
    # variables
    "variables":       "python variables",
    "variable":        "python variables",
    # exceptions / errors
    "exceptions":      "python exceptions",
    "exception":       "python exceptions",
    "error handling":  "python exceptions",
    "try except":      "python exceptions",
    "try/except":      "python exceptions",
    # decorators
    "decorators":      "python decorators",
    "decorator":       "python decorators",
    # generators
    "generators":      "python generators",
    "generator":       "python generators",
    "yield":           "python generators",
    # async
    "async":           "python async",
    "await":           "python async",
    "asyncio":         "python async",
    "asynchronous":    "python async",
    # comprehensions
    "comprehension":   "python comprehension",
    "list comprehension": "python comprehension",
    # inheritance
    "inheritance":     "python inheritance",
    "inherit":         "python inheritance",
    # memory
    "memory":          "python memory management",
    "garbage":         "python memory management",
    "gc":              "python memory management",
    # testing
    "testing":         "python testing",
    "unittest":        "python testing",
    "pytest":          "python testing",
    # GIL
    "gil":             "python gil",
    "global interpreter lock": "python gil",
    # file handling
    "file":            "python file handling",
    "files":           "python file handling",
    "open":            "python file handling",
    "read file":       "python file handling",
    "write file":      "python file handling",
    # modules
    "modules":         "python modules",
    "module":          "python modules",
    "import":          "python modules",
    # lambda
    "lambda":          "python lambda",
    # string methods
    "strings":         "python string methods",
    "string":          "python string methods",
    "str methods":     "python string methods",
    # list methods
    "list":            "python list methods",
    "lists":           "python list methods",
    "list methods":    "python list methods",
    # dict methods
    "dict":            "python dict methods",
    "dictionary":      "python dict methods",
    "dictionaries":    "python dict methods",
    # set methods
    "set":             "python set methods",
    "sets":            "python set methods",
    # big o
    "big o":           "what is big o",
    "big-o":           "what is big o",
    "time complexity": "what is big o",
    "complexity":      "what is big o",
    # recursion
    "recursion":       "python recursion",
    "recursive":       "python recursion",
    # list vs tuple
    "list vs tuple":   "python list vs tuple",
    "tuple vs list":   "python list vs tuple",
    "tuples":          "python list vs tuple",
    "tuple":           "python list vs tuple",
    # scope
    "scope":           "python scope",
    "global":          "python scope",
    "local":           "python scope",
    "nonlocal":        "python scope",
    # slicing
    "slicing":         "python slicing",
    "slice":           "python slicing",
    "indexing":        "python slicing",
    # map filter reduce
    "map":             "python map filter reduce",
    "filter":          "python map filter reduce",
    "reduce":          "python map filter reduce",
    # args kwargs
    "args":            "python args kwargs",
    "kwargs":          "python args kwargs",
    "*args":           "python args kwargs",
    "**kwargs":        "python args kwargs",
    # format / f-strings
    "f-string":        "python f strings",
    "f string":        "python f strings",
    "format":          "python f strings",
    "fstring":         "python f strings",
    # pip / packages
    "pip":             "python pip",
    "packages":        "python pip",
    "install":         "python pip",
    "virtual env":     "python pip",
    "venv":            "python pip",
    # dataclass
    "dataclass":       "python dataclass",
    "dataclasses":     "python dataclass",
    # walrus operator
    "walrus":          "python walrus operator",
    ":=":              "python walrus operator",
    # type hints
    "type hints":      "python type hints",
    "type hint":       "python type hints",
    "annotations":     "python type hints",
}

# ══════════════════════════════════════════════════════════════
#  Q&A DATABASE
# ══════════════════════════════════════════════════════════════
qaDatabase = {
    # ── Greetings ──────────────────────────────────────────────
    "hi":            "Hello there! 👋 I'm CuriBot.ai — your Python tutor. Ask me anything!",
    "hello":         "Hey! Great to see you! 🌟 I'm ready to help you learn Python.",
    "good morning":  "Good morning! ☀️ Ready to sharpen your coding skills today?",
    "good afternoon":"Good afternoon! 🌤️ Let's dive into some Python concepts!",
    "good evening":  "Good evening! 🌙 Perfect time for some coding practice!",
    "good night":    "Good night! 😴 Rest well — your brain consolidates learning during sleep!",
    "bye":           "Goodbye! 👋 Keep coding every day — consistency is key!",
    "see you":       "See you soon! 🚀 Keep building awesome things!",
    "thank you":     "You're very welcome! 😊 Happy to help. Keep asking questions!",
    "thanks":        "No problem at all! 👍 That's what I'm here for. Keep learning!",
    "who are you":   "I'm CuriBot.ai 🤖 — an AI-powered Python tutor built with Flask!",
    "what can you do": "I can answer your questions about Python — from basics to advanced topics like OOP, async, memory management, data structures, and more!",

    # ── Python Basics ──────────────────────────────────────────
    "what is python": (
        "Python is a high-level, interpreted, dynamically-typed programming language created by Guido van Rossum in 1991. "
        "It emphasises code readability with clean syntax using indentation instead of braces. "
        "Python supports multiple paradigms: procedural, object-oriented, and functional programming. "
        "It's widely used in web development (Flask, Django), data science (NumPy, Pandas), AI/ML (TensorFlow, PyTorch), automation, and scripting. 🐍"
    ),
    "python intro":    "Python is a beginner-friendly, high-level language known for its clean syntax. It's great for scripting, web apps, data science, and AI. Type 'what is python' for a full overview! 🐍",
    "python overview": "Python is one of the most popular programming languages in the world. It powers Instagram, YouTube, NASA tools, and countless AI applications. Ask me about specific topics to dive deeper!",
    "python basics":   "Python basics include: variables, data types, operators, conditionals (if/elif/else), loops (for/while), functions (def), and importing modules. What would you like to explore?",
    "python for beginners": (
        "Python is perfect for beginners! Here's why:\n"
        "• Clean, readable syntax — almost like pseudocode\n"
        "• No need to declare variable types\n"
        "• Huge community and tons of learning resources\n"
        "• Runs on Windows, Mac, and Linux\n"
        "• Interactive mode (REPL) lets you experiment instantly\n"
        "Start with: variables → data types → if/else → loops → functions → classes 🚀"
    ),
    "python data types": (
        "Python has rich built-in data types:\n"
        "• int — whole numbers: x = 42\n"
        "• float — decimals: pi = 3.14\n"
        "• str — text: name = 'Alice'\n"
        "• bool — True / False\n"
        "• list — ordered, mutable: [1, 2, 3]\n"
        "• tuple — ordered, immutable: (1, 2, 3)\n"
        "• set — unique, unordered: {1, 2, 3}\n"
        "• dict — key-value pairs: {'a': 1}\n"
        "• NoneType — represents absence: None\n"
        "• bytes / bytearray — binary data"
    ),
    "python variables": (
        "Python variables are dynamically typed — no need to declare types explicitly.\n"
        "x = 10          # int\n"
        "name = 'Alice'  # str\n"
        "pi = 3.14       # float\n"
        "active = True   # bool\n"
        "You can check the type with type(x). Python uses duck typing: if it behaves like a type, it is that type."
    ),
    "python variables vs constants": (
        "Python doesn't have built-in constants, but by convention, uppercase variable names indicate constants:\n"
        "PI = 3.14  # treated as a constant\n"
        "Variables can be reassigned:\n"
        "x = 10\n"
        "x = 20  # x now points to 20\n\n"
        "For true immutability, consider using a frozen dataclass or a class with @property."
    ),
    "python loops": (
        "Python has two main loop types:\n"
        "FOR LOOP — iterates over a sequence:\n"
        "  for i in range(5): print(i)  # prints 0-4\n"
        "  for item in ['a','b','c']: print(item)\n\n"
        "WHILE LOOP — runs while condition is true:\n"
        "  while x > 0: x -= 1\n\n"
        "Loop control:\n"
        "  break     — exit the loop entirely\n"
        "  continue  — skip to next iteration\n"
        "  else      — runs if loop completes without break\n\n"
        "Useful: enumerate() gives index + value, zip() pairs two iterables."
    ),
    "python for loop":   "A for loop iterates over any iterable (list, string, range, dict, etc.).\nExample:\n  for i in range(1, 6):\n      print(i)  # 1 2 3 4 5\n  for char in 'hello':\n      print(char)",
    "python while loop": "A while loop repeats as long as its condition is True.\nExample:\n  count = 0\n  while count < 5:\n      print(count)\n      count += 1\nAlways ensure the condition eventually becomes False to avoid infinite loops!",
    "python loop examples": (
        "Common Python loop patterns:\n"
        "# Reverse iteration\n"
        "for i in range(10, 0, -1): print(i)\n\n"
        "# Loop with index\n"
        "for idx, val in enumerate(['a','b','c']): print(idx, val)\n\n"
        "# Zip two lists\n"
        "for a, b in zip([1,2,3], ['x','y','z']): print(a, b)\n\n"
        "# List comprehension (compact loop)\n"
        "squares = [x**2 for x in range(10)]\n\n"
        "# While with break\n"
        "while True:\n    user = input('Type quit to exit: ')\n    if user == 'quit': break"
    ),
    "python recursion": (
        "Recursion is when a function calls itself.\n"
        "def factorial(n):\n"
        "    if n == 0: return 1   # base case\n"
        "    return n * factorial(n-1)\n\n"
        "print(factorial(5))  # 120\n\n"
        "Always define a BASE CASE to stop the recursion.\n"
        "Python's default recursion limit is 1000 (sys.setrecursionlimit() to change).\n"
        "For deep recursion, consider iterative solutions or memoization."
    ),
    "python functions": (
        "Functions in Python are defined with 'def'. They support default args, *args, **kwargs, and type hints.\n"
        "def greet(name: str, greeting: str = 'Hello') -> str:\n"
        "    return f'{greeting}, {name}!'\n\n"
        "*args captures extra positional arguments as a tuple.\n"
        "**kwargs captures extra keyword arguments as a dict.\n"
        "Functions are first-class objects — you can pass them as arguments or return them."
    ),
    "python args kwargs": (
        "*args and **kwargs let functions accept a variable number of arguments.\n"
        "def func(*args, **kwargs):\n"
        "    print(args)    # tuple of positional args\n"
        "    print(kwargs)  # dict of keyword args\n\n"
        "func(1, 2, 3, name='Alice', age=25)\n"
        "# args = (1, 2, 3)\n"
        "# kwargs = {'name': 'Alice', 'age': 25}\n\n"
        "Also useful for unpacking:\n"
        "  nums = [1, 2, 3]\n"
        "  print(*nums)           # prints: 1 2 3\n"
        "  d = {'a': 1, 'b': 2}\n"
        "  func(**d)              # same as func(a=1, b=2)"
    ),
    "python lambda": (
        "Lambda creates small anonymous functions in a single line.\n"
        "square = lambda x: x ** 2       # square(5) → 25\n"
        "add = lambda a, b: a + b        # add(3, 4) → 7\n"
        "Lambdas are commonly used with map(), filter(), and sorted():\n"
        "  sorted(names, key=lambda n: n.lower())\n"
        "  list(map(lambda x: x*2, [1,2,3]))  → [2,4,6]"
    ),
    "python classes": (
        "Classes in Python use the 'class' keyword. __init__ is the constructor.\n"
        "class Animal:\n"
        "    def __init__(self, name, sound):\n"
        "        self.name = name\n"
        "        self.sound = sound\n"
        "    def speak(self):\n"
        "        return f'{self.name} says {self.sound}!'\n\n"
        "dog = Animal('Rex', 'Woof')\n"
        "print(dog.speak())  # Rex says Woof!\n"
        "Python supports single and multiple inheritance, class methods, static methods, and properties."
    ),
    "python indentation": (
        "Python uses indentation (4 spaces) to define code blocks instead of braces.\n"
        "def greet(name):\n"
        "    if name:\n"
        "        print(f'Hello, {name}!')\n"
        "    else:\n"
        "        print('Hello, World!')\n\n"
        "Consistent indentation is crucial — mixing tabs and spaces causes IndentationError."
    ),
    "python inheritance": (
        "Inheritance allows a class to reuse code from a parent class.\n"
        "class Vehicle:\n"
        "    def __init__(self, brand): self.brand = brand\n"
        "    def drive(self): return 'Driving...'\n\n"
        "class Car(Vehicle):\n"
        "    def __init__(self, brand, doors):\n"
        "        super().__init__(brand)\n"
        "        self.doors = doors\n"
        "    def drive(self): return f'{self.brand} car driving!'\n\n"
        "Python supports multiple inheritance: class C(A, B). Use super() to call parent methods."
    ),
    "python exceptions": (
        "Python handles errors with try/except/else/finally blocks.\n"
        "try:\n"
        "    result = 10 / 0\n"
        "except ZeroDivisionError as e:\n"
        "    print(f'Error: {e}')\n"
        "except (TypeError, ValueError) as e:\n"
        "    print(f'Type/Value error: {e}')\n"
        "else:\n"
        "    print('No error occurred!')\n"
        "finally:\n"
        "    print('This always runs.')\n\n"
        "Raise your own: raise ValueError('Invalid input!')\n"
        "Custom exception: class MyError(Exception): pass"
    ),
    "python comprehension": (
        "Comprehensions provide a concise way to create collections.\n"
        "LIST:  [x**2 for x in range(10) if x % 2 == 0]  → [0,4,16,36,64]\n"
        "DICT:  {k: v for k, v in pairs if v > 0}\n"
        "SET:   {x.lower() for x in words}\n"
        "GEN:   (x**2 for x in range(100))  # lazy, memory-efficient\n\n"
        "Nested: [cell for row in matrix for cell in row]  # flatten 2D list"
    ),
    "python decorators": (
        "Decorators are functions that wrap other functions to add behaviour.\n"
        "def timer(func):\n"
        "    import time\n"
        "    def wrapper(*args, **kwargs):\n"
        "        start = time.time()\n"
        "        result = func(*args, **kwargs)\n"
        "        print(f'Took {time.time()-start:.4f}s')\n"
        "        return result\n"
        "    return wrapper\n\n"
        "@timer\n"
        "def slow_function(): time.sleep(1)\n\n"
        "Built-in decorators: @staticmethod, @classmethod, @property, @functools.wraps"
    ),
    "python async": (
        "Python async/await enables non-blocking concurrent code using asyncio.\n"
        "import asyncio\n\n"
        "async def fetch_data(url):\n"
        "    await asyncio.sleep(1)  # simulate I/O\n"
        "    return f'Data from {url}'\n\n"
        "async def main():\n"
        "    results = await asyncio.gather(\n"
        "        fetch_data('url1'), fetch_data('url2')\n"
        "    )\n"
        "    print(results)\n\n"
        "asyncio.run(main())\n"
        "Async is ideal for I/O-bound tasks: web requests, file ops, database queries."
    ),
    "python generators": (
        "Generators produce values lazily using 'yield' — great for large data streams.\n"
        "def fibonacci():\n"
        "    a, b = 0, 1\n"
        "    while True:\n"
        "        yield a\n"
        "        a, b = b, a + b\n\n"
        "fib = fibonacci()\n"
        "print([next(fib) for _ in range(8)])  # [0,1,1,2,3,5,8,13]\n\n"
        "Generators save memory vs lists. Use send() to pass values in, throw() to inject exceptions."
    ),
    "python list methods": (
        "Essential Python list methods:\n"
        "• append(x)    — add x to end\n"
        "• extend([x])  — add multiple items\n"
        "• insert(i, x) — insert at index i\n"
        "• remove(x)    — remove first occurrence\n"
        "• pop(i)       — remove & return item at i\n"
        "• sort()       — sort in-place (key=, reverse=)\n"
        "• sorted(lst)  — return new sorted list\n"
        "• reverse()    — reverse in-place\n"
        "• index(x)     — find position of x\n"
        "• count(x)     — count occurrences\n"
        "• copy()       — shallow copy\n"
        "• clear()      — empty the list"
    ),
    "python dict methods": (
        "Essential Python dict methods:\n"
        "• d.get(key, default) — safe access, no KeyError\n"
        "• d.keys()            — view of all keys\n"
        "• d.values()          — view of all values\n"
        "• d.items()           — view of (key, value) pairs\n"
        "• d.update({...})     — merge another dict\n"
        "• d.pop(key)          — remove and return value\n"
        "• d.setdefault(k, v)  — set if key missing\n"
        "• d.copy()            — shallow copy\n"
        "• dict.fromkeys(keys) — create dict from list\n"
        "Use ** unpacking to merge: {**d1, **d2}"
    ),
    "python string methods": (
        "Essential Python string methods:\n"
        "• .upper() / .lower() / .title() / .swapcase()\n"
        "• .strip() / .lstrip() / .rstrip() — remove whitespace\n"
        "• .split(sep) — split into list\n"
        "• .join(lst)  — join list into string\n"
        "• .replace(old, new)\n"
        "• .find(sub) / .index(sub) — search\n"
        "• .startswith(s) / .endswith(s)\n"
        "• .format(**kwargs) or f-strings: f'Hi {name}'\n"
        "• .encode() / .decode()\n"
        "• .isdigit() / .isalpha() / .isalnum()"
    ),
    "python set methods": (
        "Essential Python set methods:\n"
        "• s.add(x)                 — add element\n"
        "• s.remove(x)              — remove (KeyError if missing)\n"
        "• s.discard(x)             — remove (no error if missing)\n"
        "• s.pop()                  — remove and return arbitrary element\n"
        "• s.clear()                — empty the set\n"
        "Set operations:\n"
        "• s.union(t)               — all unique elements\n"
        "• s.intersection(t)        — common elements\n"
        "• s.difference(t)          — in s but not t\n"
        "• s.symmetric_difference(t)— in either but not both\n"
        "Sets are unordered and cannot contain duplicates."
    ),
    "python list vs tuple": (
        "LISTS vs TUPLES:\n"
        "• Lists are mutable (can change); tuples are immutable (cannot).\n"
        "• Lists use more memory; tuples are more efficient.\n"
        "• Lists: append, remove, sort — tuples: fewer methods.\n"
        "• Use tuples for fixed data (coordinates, RGB), lists for dynamic collections.\n"
        "• Tuples can be dict keys; lists cannot.\n"
        "• Tuples are slightly faster to create and iterate."
    ),
    "python file handling": (
        "Python file I/O using the built-in open() function:\n"
        "# Read entire file\n"
        "with open('data.txt', 'r') as f:\n"
        "    content = f.read()\n\n"
        "# Read line by line\n"
        "with open('data.txt') as f:\n"
        "    for line in f:\n"
        "        print(line.strip())\n\n"
        "# Write to file\n"
        "with open('out.txt', 'w') as f:\n"
        "    f.write('Hello, World!')\n\n"
        "Modes: 'r' read, 'w' write, 'a' append, 'b' binary, 'r+' read+write.\n"
        "Always use 'with' to ensure the file is properly closed."
    ),
    "python modules": (
        "A module is any .py file. Python has thousands of built-in and third-party modules.\n"
        "import math                    # import whole module\n"
        "from os import path, getcwd    # import specific items\n"
        "import numpy as np             # import with alias\n\n"
        "Popular standard library modules:\n"
        "• os, sys — OS interactions\n"
        "• re — regular expressions\n"
        "• json — JSON parsing\n"
        "• datetime — dates and times\n"
        "• collections — deque, Counter, defaultdict\n"
        "• itertools — advanced iteration\n"
        "• pathlib — modern file paths\n"
        "• logging — application logging"
    ),
    "python oop": (
        "Python's OOP has four pillars:\n"
        "1. ENCAPSULATION: Hide internal state with _ (protected) or __ (private) prefixes.\n"
        "2. INHERITANCE: class Child(Parent) — reuse and extend parent code.\n"
        "3. POLYMORPHISM: Override methods in subclasses for different behaviour.\n"
        "4. ABSTRACTION: Use ABC + @abstractmethod to define interfaces.\n\n"
        "Additional: @property for getters/setters, @classmethod, @staticmethod, dunder methods (__str__, __repr__, __eq__, etc.)"
    ),
    "python memory management": (
        "Python manages memory automatically using:\n"
        "1. REFERENCE COUNTING: Every object tracks how many variables reference it.\n"
        "   When count hits 0, memory is freed immediately.\n"
        "2. CYCLIC GARBAGE COLLECTOR: Detects and cleans up circular references.\n\n"
        "Tips:\n"
        "• Use generators instead of large lists\n"
        "• del variable to remove references\n"
        "• Use __slots__ to reduce memory per object\n"
        "• Use gc module to control garbage collection\n"
        "• sys.getsizeof(obj) to check object size"
    ),
    "python testing": (
        "Python testing frameworks:\n"
        "UNITTEST (built-in):\n"
        "  import unittest\n"
        "  class TestMath(unittest.TestCase):\n"
        "      def test_add(self): self.assertEqual(add(1,2), 3)\n"
        "  unittest.main()\n\n"
        "PYTEST (popular, simpler):\n"
        "  def test_add(): assert add(1, 2) == 3\n"
        "  Run: pytest test_file.py -v\n\n"
        "• Use fixtures for setup/teardown\n"
        "• Mock external calls with unittest.mock\n"
        "• Measure coverage with pytest-cov"
    ),
    "python gil": (
        "The GIL (Global Interpreter Lock) is a mutex in CPython that allows only one thread "
        "to execute Python bytecode at a time, even on multi-core CPUs.\n\n"
        "IMPACT: Limits true parallelism for CPU-bound threads.\n"
        "WORKAROUNDS:\n"
        "• multiprocessing — separate processes, each with its own GIL\n"
        "• concurrent.futures.ProcessPoolExecutor\n"
        "• C extensions (NumPy releases GIL for heavy operations)\n"
        "• PyPy or Jython (alternative implementations)\n"
        "• Python 3.13+ introduces per-interpreter GIL (experimental)"
    ),

    # ── NEW: Scope ─────────────────────────────────────────────
    "python scope": (
        "Python uses LEGB scope rules:\n"
        "L — Local: variables inside the current function\n"
        "E — Enclosing: variables in enclosing functions (closures)\n"
        "G — Global: module-level variables\n"
        "B — Built-in: Python's built-in names (len, print, etc.)\n\n"
        "x = 'global'\n"
        "def outer():\n"
        "    x = 'enclosing'\n"
        "    def inner():\n"
        "        x = 'local'\n"
        "        print(x)  # 'local'\n"
        "    inner()\n"
        "    print(x)      # 'enclosing'\n\n"
        "Use 'global x' to modify a global var inside a function.\n"
        "Use 'nonlocal x' to modify an enclosing var inside a nested function."
    ),

    # ── NEW: Slicing ───────────────────────────────────────────
    "python slicing": (
        "Python slicing extracts parts of sequences using [start:stop:step].\n"
        "lst = [0, 1, 2, 3, 4, 5]\n"
        "lst[1:4]    → [1, 2, 3]   (index 1 to 3)\n"
        "lst[:3]     → [0, 1, 2]   (start to 2)\n"
        "lst[3:]     → [3, 4, 5]   (3 to end)\n"
        "lst[::2]    → [0, 2, 4]   (every 2nd)\n"
        "lst[::-1]   → [5, 4, 3, 2, 1, 0]  (reversed)\n\n"
        "Works on strings too:\n"
        "'hello'[1:4]  → 'ell'\n"
        "'hello'[::-1] → 'olleh'"
    ),

    # ── NEW: Map / Filter / Reduce ─────────────────────────────
    "python map filter reduce": (
        "Python's functional programming built-ins:\n\n"
        "MAP — apply a function to every item:\n"
        "  list(map(lambda x: x**2, [1,2,3,4]))  → [1,4,9,16]\n\n"
        "FILTER — keep items that pass a condition:\n"
        "  list(filter(lambda x: x%2==0, range(10)))  → [0,2,4,6,8]\n\n"
        "REDUCE — accumulate a result (from functools):\n"
        "  from functools import reduce\n"
        "  reduce(lambda a,b: a+b, [1,2,3,4,5])  → 15\n\n"
        "Modern Pythonic alternative: use list comprehensions or generator expressions instead."
    ),

    # ── NEW: F-strings ─────────────────────────────────────────
    "python f strings": (
        "F-strings (formatted string literals) are the fastest and most readable way to embed expressions in strings.\n"
        "name = 'Alice'\n"
        "age  = 30\n"
        "print(f'Hello, {name}! You are {age} years old.')\n\n"
        "Expressions inside {}:\n"
        "  f'{2 + 2}'           → '4'\n"
        "  f'{name.upper()}'    → 'ALICE'\n"
        "  f'{3.14159:.2f}'     → '3.14'   (format spec)\n"
        "  f'{1000000:,}'       → '1,000,000'\n"
        "  f'{True!r}'          → 'True'\n\n"
        "Python 3.12+: f-strings can contain nested f-strings and more complex expressions."
    ),

    # ── MORE: Core Python Topics ───────────────────────────────
    "python syntax": (
        "Python syntax is designed to be readable and minimal. Blocks use indentation instead of braces, and statements often end at the newline.\n"
        "Example:\n"
        "if x > 0:\n"
        "    print('positive')\n\n"
        "Keep indentation consistent, usually 4 spaces."
    ),
    "python operators": (
        "Python operators include arithmetic (+, -, *, /, //, %, **), comparison (==, !=, <, >, <=, >=), logical (and, or, not), and assignment (=, +=, -=).\n"
        "Use // for integer division and ** for powers."
    ),
    "python conditions": (
        "Conditional statements use if, elif, and else.\n"
        "Example:\n"
        "if score >= 90:\n"
        "    grade = 'A'\n"
        "elif score >= 80:\n"
        "    grade = 'B'\n"
        "else:\n"
        "    grade = 'C'"
    ),
    "python strings": (
        "Strings are immutable text values in Python. You can use single quotes, double quotes, or triple quotes for multiline text.\n"
        "Common methods include .lower(), .upper(), .strip(), .replace(), .split(), and .join()."
    ),
    "python numbers": (
        "Python numbers include int, float, and complex.\n"
        "Examples:\n"
        "x = 10\n"
        "y = 3.14\n"
        "z = 2 + 4j\n\n"
        "Use int for whole numbers and float for decimals."
    ),
    "python booleans": (
        "Booleans represent truth values: True and False.\n"
        "They are often used in conditions, comparisons, and logical expressions."
    ),
    "python lists": (
        "Lists are ordered, mutable collections.\n"
        "Example: nums = [1, 2, 3]\n"
        "Use append(), insert(), pop(), remove(), sort(), and reverse() to manage list data."
    ),
    "python tuples": (
        "Tuples are ordered, immutable collections.\n"
        "Example: point = (10, 20)\n"
        "Use tuples when the data should not change."
    ),
    "python dictionaries": (
        "Dictionaries store key-value pairs and are very fast for lookups.\n"
        "Example: user = {'name': 'Alice', 'age': 20}\n"
        "Access values with user['name'] or user.get('name')."
    ),
    "python sets": (
        "Sets are unordered collections of unique values.\n"
        "They are useful for removing duplicates and checking membership quickly."
    ),
    "python functions advanced": (
        "Functions can use default arguments, keyword-only arguments, *args, **kwargs, and return multiple values as tuples.\n"
        "They are first-class objects, so you can pass them around like variables."
    ),
    "python modules import": (
        "Use import to load modules.\n"
        "Examples:\n"
        "import math\n"
        "from datetime import datetime\n"
        "import os as operating_system\n\n"
        "A module is usually just a .py file."
    ),
    "python packages": (
        "A package is a collection of Python modules.\n"
        "Third-party packages are installed with pip, for example: pip install requests."
    ),
    "python virtual environment": (
        "Virtual environments isolate project dependencies.\n"
        "Create one with: python -m venv venv\n"
        "Activate it before installing packages so your project stays isolated."
    ),
    "python file": (
        "Use open() with a context manager for file handling.\n"
        "Example:\n"
        "with open('data.txt', 'r') as f:\n"
        "    content = f.read()\n\n"
        "Always close files by using with."
    ),
    "python json": (
        "The json module converts between Python objects and JSON text.\n"
        "Use json.dumps() to convert Python to JSON and json.loads() to convert JSON to Python."
    ),
    "python regex": (
        "Regular expressions are handled by the re module.\n"
        "Common functions include re.search(), re.match(), re.findall(), and re.sub()."
    ),
    "python datetime": (
        "The datetime module handles dates and times.\n"
        "Use datetime.now() for the current time and timedelta for time arithmetic."
    ),
    "python logging": (
        "The logging module is better than print() for real applications.\n"
        "It supports log levels like debug, info, warning, error, and critical."
    ),
    "python testing advanced": (
        "Testing helps you verify that code works as expected.\n"
        "Popular tools include unittest, pytest, and unittest.mock for mocking dependencies."
    ),
    "python decorators advanced": (
        "Decorators wrap a function to add behavior without changing its code.\n"
        "They are often used for logging, timing, authorization, and caching."
    ),
    "python generators advanced": (
        "Generators use yield to produce values lazily.\n"
        "They are memory efficient and useful for large datasets or infinite sequences."
    ),
    "python threading": (
        "Threading is useful for I/O-bound tasks, but CPython has the GIL, so CPU-bound threads do not run Python bytecode in true parallel."
    ),
    "python multiprocessing": (
        "Multiprocessing uses separate processes instead of threads, so it can run CPU-bound work in parallel."
    ),
    "python async await": (
        "async and await are used for asynchronous programming.\n"
        "They are useful for I/O-bound work like web requests, databases, and sockets."
    ),
    "python comprehension advanced": (
        "Comprehensions create lists, sets, and dictionaries in a compact way.\n"
        "They are often shorter and clearer than building collections with loops."
    ),
    "python type hints advanced": (
        "Type hints improve readability and help tools like pyright and mypy catch bugs earlier.\n"
        "They do not change runtime behavior."
    ),
    "python dataclasses advanced": (
        "Dataclasses are a clean way to build classes that mainly store data.\n"
        "They can auto-generate __init__, __repr__, and __eq__."
    ),
    "python oop advanced": (
        "OOP in Python includes encapsulation, inheritance, polymorphism, and abstraction.\n"
        "Use classes when you want to group data and behavior together."
    ),
    "python error handling": (
        "Use try, except, else, and finally to handle errors gracefully.\n"
        "You can also raise your own exceptions when input is invalid."
    ),
    "python recursion advanced": (
        "Recursion is a function calling itself.\n"
        "Always use a base case or the function can recurse forever."
    ),
    "python scope advanced": (
        "Python uses LEGB scope rules: Local, Enclosing, Global, Built-in.\n"
        "Use global and nonlocal carefully when you need to rebind outer variables."
    ),
    "python slicing advanced": (
        "Slicing works with sequences like lists, strings, and tuples.\n"
        "The pattern is [start:stop:step]."
    ),
    "python lambda advanced": (
        "Lambda creates small anonymous functions.\n"
        "Use it when you need a short function for map(), filter(), sorted(), or similar helpers."
    ),
    "python big o": (
        "Big O describes how runtime or memory grows as input grows.\n"
        "Common examples are O(1), O(log n), O(n), O(n log n), and O(n^2)."
    ),
    "python interview questions": (
        "Common interview topics include data types, loops, functions, OOP, error handling, generators, decorators, async, and list/dict/set operations."
    ),
    "python builtins": (
        "Python built-in functions include print(), len(), type(), range(), sum(), min(), max(), sorted(), enumerate(), zip(), map(), filter(), any(), all(), and input().\n"
        "They are available without importing anything."
    ),
    "python iterator": (
        "An iterator is an object that returns items one at a time with next().\n"
        "Iterables like lists, strings, and ranges can be turned into iterators with iter()."
    ),
    "python iterables": (
        "An iterable is any object you can loop over with for.\n"
        "Examples include list, tuple, string, dict, set, range, and file objects."
    ),
    "python context manager": (
        "A context manager is used with the with statement to manage resources safely.\n"
        "It is commonly used for files, locks, and database connections."
    ),
    "python with statement": (
        "The with statement automatically handles setup and cleanup.\n"
        "Example:\n"
        "with open('data.txt') as f:\n"
        "    text = f.read()"
    ),
    "python classes methods": (
        "Python classes can define instance methods, class methods, and static methods.\n"
        "Instance methods use self, class methods use cls, and static methods do not access instance state directly."
    ),
    "python object": (
        "In Python, everything is an object: numbers, strings, functions, classes, and even modules.\n"
        "Objects have identity, type, and value."
    ),
    "python exception handling": (
        "Use try and except to catch errors, else for success-only code, and finally for cleanup.\n"
        "You can raise custom exceptions when you need to signal invalid input or unexpected state."
    ),
    "python inheritance advanced": (
        "Inheritance lets one class reuse and extend another.\n"
        "Use super() to call parent methods and avoid duplicating code."
    ),
    "python polymorphism": (
        "Polymorphism means different objects can respond to the same method name in different ways.\n"
        "For example, different classes can implement the same speak() method."
    ),
    "python encapsulation": (
        "Encapsulation means keeping data and the methods that work on it together inside a class.\n"
        "By convention, _name is protected and __name is name-mangled private state."
    ),
    "python abstraction": (
        "Abstraction hides implementation details and exposes only the important behavior.\n"
        "In Python, abstract base classes can be created with the abc module."
    ),
    "python abc": (
        "The abc module provides abstract base classes.\n"
        "Use @abstractmethod when you want subclasses to implement specific methods."
    ),
    "python property": (
        "@property lets you turn a method into a readable attribute.\n"
        "It is useful for computed values and controlled access to internal data."
    ),
    "python classmethod": (
        "@classmethod defines a method that receives the class as the first argument, usually named cls.\n"
        "It is often used for alternate constructors."
    ),
    "python staticmethod": (
        "@staticmethod defines a method that belongs to a class namespace but does not need self or cls.\n"
        "It is useful for utility logic related to the class."
    ),
    "python dunder methods": (
        "Dunder methods are special methods like __init__, __str__, __repr__, __len__, and __eq__.\n"
        "They let your objects integrate with Python syntax and built-ins."
    ),
    "python magic methods": (
        "Magic methods are the same as dunder methods.\n"
        "They customize how objects behave with operators, printing, comparisons, and iteration."
    ),
    "python list comprehension": (
        "List comprehensions create lists in one line.\n"
        "Example: squares = [x*x for x in range(10) if x % 2 == 0]"
    ),
    "python dict comprehension": (
        "Dict comprehensions create dictionaries in a compact form.\n"
        "Example: squares = {x: x*x for x in range(5)}"
    ),
    "python set comprehension": (
        "Set comprehensions create unique-value sets in one line.\n"
        "Example: letters = {ch.lower() for ch in 'Python'}"
    ),
    "python generator expression": (
        "A generator expression creates values lazily and uses less memory than a list comprehension.\n"
        "Example: total = sum(x*x for x in range(100))"
    ),
    "python unpacking": (
        "Unpacking assigns items from a sequence or mapping into variables.\n"
        "Examples:\n"
        "a, b = (1, 2)\n"
        "first, *rest = [1, 2, 3, 4]\n"
        "func(**{'name': 'Alice'})"
    ),
    "python args": (
        "*args collects extra positional arguments into a tuple.\n"
        "It is useful when a function should accept a variable number of positional values."
    ),
    "python kwargs": (
        "**kwargs collects extra keyword arguments into a dictionary.\n"
        "It is useful when a function should accept flexible named parameters."
    ),
    "python recursion depth": (
        "Python has a recursion limit to prevent infinite recursion from crashing the interpreter.\n"
        "You can inspect it or change it with sys.getrecursionlimit() and sys.setrecursionlimit()."
    ),
    "python garbage collection": (
        "Garbage collection frees memory that is no longer used.\n"
        "CPython uses reference counting and a cyclic garbage collector."
    ),
    "python memory management advanced": (
        "Python memory management is automatic, but you can help by avoiding huge temporary objects and using generators for large data."
    ),
    "python os": (
        "The os module helps you interact with the operating system.\n"
        "It can read environment variables, list directories, and work with paths and files."
    ),
    "python pathlib": (
        "pathlib provides an object-oriented way to work with file paths.\n"
        "It is often cleaner than building paths with strings."
    ),
    "python sys": (
        "The sys module gives access to Python runtime details like argv, path, stdin, stdout, and recursion limit."
    ),
    "python math": (
        "The math module provides mathematical functions such as sqrt(), ceil(), floor(), sin(), cos(), and pi."
    ),
    "python statistics": (
        "The statistics module provides mean, median, mode, variance, and standard deviation helpers."
    ),
    "python collections": (
        "The collections module includes Counter, deque, defaultdict, namedtuple, and OrderedDict."
    ),
    "python itertools": (
        "The itertools module provides fast iterator building blocks like product, permutations, combinations, chain, and cycle."
    ),
    "python functools": (
        "The functools module provides tools like lru_cache, reduce, partial, and wraps."
    ),
    "python caching": (
        "Caching stores the result of expensive work so it can be reused later.\n"
        "In Python, functools.lru_cache is a common caching tool for functions."
    ),
    "python serialization": (
        "Serialization means converting data into a storable or transferable format.\n"
        "JSON is common, and pickle can serialize many Python objects."
    ),
    "python pickle": (
        "pickle serializes Python objects into bytes and restores them later.\n"
        "Use it carefully with untrusted data because it can execute code during loading."
    ),
    "python copying": (
        "Shallow copy duplicates the outer container, while deep copy recursively duplicates nested objects.\n"
        "The copy module provides copy() and deepcopy()."
    ),
    "python shallow copy": (
        "A shallow copy makes a new container, but nested objects are still shared."
    ),
    "python deep copy": (
        "A deep copy creates a fully independent copy, including nested objects."
    ),
    "python errors": (
        "Common Python errors include SyntaxError, NameError, TypeError, ValueError, IndexError, KeyError, and ImportError.\n"
        "Reading the traceback helps you find the line and cause of the issue."
    ),
    "python debug": (
        "Debugging in Python often uses print(), logging, pdb, or your IDE debugger.\n"
        "Start from the traceback and narrow down the failing line."
    ),
    "python pip install": (
        "Use pip install package_name to add third-party libraries to your environment.\n"
        "Example: pip install requests"
    ),
    "python requirements": (
        "requirements.txt lists the packages a project needs.\n"
        "Use pip freeze > requirements.txt to generate it and pip install -r requirements.txt to install from it."
    ),
    "python virtualenv": (
        "Virtualenv or venv creates isolated Python environments so one project does not break another."
    ),
    "python framework": (
        "Popular Python web frameworks include Flask and Django.\n"
        "Flask is lightweight and flexible, while Django is full-featured and opinionated."
    ),
    "python flask": (
        "Flask is a lightweight web framework for building Python web apps and APIs.\n"
        "It is good for small to medium projects and learning web development."
    ),
    "python django": (
        "Django is a high-level Python web framework with built-in admin, ORM, auth, and routing.\n"
        "It is great for larger, structured applications."
    ),
    "python api": (
        "An API is a way for programs to communicate.\n"
        "In Python, APIs are often built with Flask, FastAPI, or Django REST Framework."
    ),
    "python json api": (
        "JSON APIs send and receive data as JSON, which is easy to read and widely used for web apps."
    ),
    "python testing pytest": (
        "pytest is a popular testing framework that uses simple assert statements and strong plugin support."
    ),
    "python unittest": (
        "unittest is Python's built-in testing framework with TestCase classes and assertion helpers."
    ),
    "python mock": (
        "Mocking replaces real dependencies during tests so you can test one unit of code in isolation.\n"
        "The unittest.mock module is commonly used for this."
    ),
    "python cli": (
        "A CLI is a command-line interface.\n"
        "Python CLI tools are often built with argparse, click, or typer."
    ),
    "python argparse": (
        "argparse helps you build command-line arguments and options for Python scripts."
    ),
    "python sql": (
        "Python can work with SQL databases using modules and libraries like sqlite3, psycopg2, and SQLAlchemy."
    ),
    "python sqlite": (
        "sqlite3 is the built-in module for using SQLite databases in Python."
    ),
    "python orm": (
        "An ORM maps database tables to Python objects.\n"
        "SQLAlchemy and Django ORM are widely used examples."
    ),
    "python serialization json": (
        "JSON is one of the most common serialization formats in Python because it is human readable and easy to exchange with other systems."
    ),
    "python performance": (
        "Python performance improves when you choose the right data structures, avoid unnecessary loops, use built-ins, and profile before optimizing."
    ),
    "python profiling": (
        "Profiling helps find slow parts of your program.\n"
        "Common tools include cProfile and timeit."
    ),
    "python timeit": (
        "timeit measures small bits of Python code so you can compare performance accurately."
    ),
    "python multithreading": (
        "Multithreading is good for I/O-bound work, but CPython's GIL limits true parallel execution of Python bytecode."
    ),
    "python multiprocessing advanced": (
        "Multiprocessing uses separate processes and can speed up CPU-heavy tasks, but processes cost more memory than threads."
    ),
    "python data science": (
        "Python is widely used in data science with libraries like NumPy, Pandas, Matplotlib, Seaborn, and SciPy."
    ),
    "python numpy": (
        "NumPy is the core library for fast numerical computing in Python, especially for arrays and vectorized math."
    ),
    "python pandas": (
        "Pandas is a data analysis library for tables, time series, filtering, grouping, and cleaning data."
    ),
    "python matplotlib": (
        "Matplotlib is a plotting library for making charts and visualizations in Python."
    ),
    "python seaborn": (
        "Seaborn builds on Matplotlib and makes statistical visualizations easier and nicer-looking."
    ),
    "python machine learning": (
        "Python is popular for machine learning with libraries like scikit-learn, TensorFlow, and PyTorch."
    ),
    "python ai": (
        "Python is one of the main languages used in AI because of its simple syntax and powerful ecosystem."
    ),
    "python web development": (
        "Python web development is commonly done with Flask, Django, FastAPI, and related tools."
    ),
    "python automation": (
        "Python is excellent for automation: file cleanup, data processing, web scraping, testing, and repetitive tasks."
    ),
    "python scripting": (
        "Python scripting means writing small programs to automate tasks or glue other tools together."
    ),
    "python interview": (
        "Python interview questions often focus on data structures, OOP, generators, decorators, error handling, and how Python handles memory and references."
    ),
    "python advanced topics": (
        "Advanced Python topics include decorators, generators, context managers, descriptors, metaclasses, async, multiprocessing, and profiling."
    ),
    "python everything": (
        "I can help with Python basics, data types, functions, classes, OOP, files, modules, packages, exceptions, decorators, generators, async, threading, multiprocessing, testing, web development, data science, and many other Python topics."
    ),

    # ── NEW: pip / virtual environments ───────────────────────
    "python pip": (
        "pip is Python's package installer. Use it to install third-party libraries.\n\n"
        "# Install a package\n"
        "pip install requests\n\n"
        "# Install specific version\n"
        "pip install flask==3.0.0\n\n"
        "# List installed packages\n"
        "pip list\n\n"
        "# Save dependencies\n"
        "pip freeze > requirements.txt\n\n"
        "# Install from requirements file\n"
        "pip install -r requirements.txt\n\n"
        "VIRTUAL ENVIRONMENTS — isolate project dependencies:\n"
        "  python -m venv venv          # create\n"
        "  source venv/bin/activate     # activate (Linux/Mac)\n"
        "  venv\\Scripts\\activate       # activate (Windows)\n"
        "  deactivate                   # deactivate"
    ),

    # ── NEW: Dataclasses ───────────────────────────────────────
    "python dataclass": (
        "Dataclasses (Python 3.7+) auto-generate __init__, __repr__, and __eq__.\n"
        "from dataclasses import dataclass, field\n\n"
        "@dataclass\n"
        "class Point:\n"
        "    x: float\n"
        "    y: float\n"
        "    label: str = 'origin'\n\n"
        "p = Point(1.0, 2.5)\n"
        "print(p)  # Point(x=1.0, y=2.5, label='origin')\n\n"
        "Use @dataclass(frozen=True) for immutable instances.\n"
        "Use field(default_factory=list) for mutable defaults.\n"
        "Cleaner than regular classes for data-only objects!"
    ),

    # ── NEW: Walrus operator ───────────────────────────────────
    "python walrus operator": (
        "The walrus operator (:=), introduced in Python 3.8, assigns a variable as part of an expression.\n\n"
        "# Without walrus:\n"
        "data = fetch_data()\n"
        "if data:\n"
        "    process(data)\n\n"
        "# With walrus:\n"
        "if data := fetch_data():\n"
        "    process(data)\n\n"
        "Useful in while loops:\n"
        "  while chunk := file.read(1024):\n"
        "      process(chunk)\n\n"
        "And in comprehensions:\n"
        "  [y := f(x), y**2, y**3]"
    ),

    # ── NEW: Type hints ────────────────────────────────────────
    "python type hints": (
        "Type hints (PEP 484, Python 3.5+) make code more readable and enable static analysis.\n"
        "from typing import List, Dict, Optional, Tuple, Union\n\n"
        "def greet(name: str) -> str:\n"
        "    return f'Hello, {name}'\n\n"
        "def process(items: List[int]) -> Dict[str, int]:\n"
        "    return {'sum': sum(items)}\n\n"
        "Optional[str] = Union[str, None]  # may be None\n\n"
        "Python 3.10+ simplified syntax:\n"
        "  def foo(x: int | str) -> list[int]: ...\n\n"
        "Use mypy or pyright for static type checking. Type hints are NOT enforced at runtime!"
    ),

    # ── NEW: Big O Notation ────────────────────────────────────
    "what is big o": (
        "Big O Notation describes the time or space complexity of an algorithm as input grows.\n\n"
        "Common complexities (fastest → slowest):\n"
        "• O(1)      — Constant: dict lookup, list index\n"
        "• O(log n)  — Logarithmic: binary search\n"
        "• O(n)      — Linear: simple loop, list search\n"
        "• O(n log n)— Linearithmic: merge sort, timsort\n"
        "• O(n²)     — Quadratic: nested loops, bubble sort\n"
        "• O(2ⁿ)     — Exponential: recursive Fibonacci (naive)\n"
        "• O(n!)     — Factorial: brute-force permutations\n\n"
        "Python list operations:\n"
        "• append/pop (end): O(1)\n"
        "• insert/remove (middle): O(n)\n"
        "• 'in' operator on list: O(n) — use set for O(1)"
    ),

    "default": "I'm not sure about that. Try asking about Python topics like loops, functions, classes, decorators, or type hints! 🐍"
}


# ══════════════════════════════════════════════════════════════
#  RESPONSE LOGIC — alias-aware keyword matching
# ══════════════════════════════════════════════════════════════
def get_response(user_input: str) -> str:
    text = user_input.lower().strip()

    # 1. Direct key match
    for key in qaDatabase:
        if key in text:
            return qaDatabase[key]

    # 2. Alias match → resolve to canonical key, then look up
    for alias, canonical in ALIASES.items():
        if alias in text:
            if canonical in qaDatabase:
                return qaDatabase[canonical]

    return qaDatabase["default"]


# ══════════════════════════════════════════════════════════════
#  ROUTES
# ══════════════════════════════════════════════════════════════
@app.route("/")
def home():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if session.get("logged_in"):
            return redirect(url_for("home"))
        return render_template("login.html")

    # POST — JSON from fetch()
    data = request.get_json(silent=True) or {}
    username = normalize_identifier(data.get("username", ""))
    password = data.get("password", "").strip()

    if USERS.get(username) == password:
        session["logged_in"] = True
        session["username"]  = username
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Invalid username or password."})


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "GET":
        if session.get("logged_in"):
            return redirect(url_for("home"))
        return render_template(
            "forgot_password.html",
            username=request.args.get("username", ""),
        )

    data = request.get_json(silent=True) or request.form
    identifier = normalize_identifier(
        data.get("identifier") or data.get("username") or data.get("email") or ""
    )
    new_password = (data.get("new_password") or data.get("password") or "").strip()
    repeat_password = (data.get("repeat_password") or data.get("confirm_password") or "").strip()

    if not identifier:
        return jsonify({"success": False, "message": "Please enter your username or email."}), 400
    if not new_password:
        return jsonify({"success": False, "message": "Please enter a new password."}), 400
    if new_password != repeat_password:
        return jsonify({"success": False, "message": "Passwords do not match."}), 400
    if identifier not in USERS:
        return jsonify({"success": False, "message": "No account found for that username or email."}), 404

    USERS[identifier] = new_password
    save_users(USERS)
    session.clear()

    if request.is_json:
        return jsonify({"success": True, "message": "Password changed successfully."})
    return redirect(url_for("login", reset="1"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        if session.get("logged_in"):
            return redirect(url_for("home"))
        return render_template("signup.html", provider=request.args.get("provider", ""))

    data = request.get_json(silent=True) or request.form
    identifier = normalize_identifier(
        data.get("identifier") or data.get("username") or data.get("email") or ""
    )
    password = data.get("password", "").strip()

    if not identifier:
        return jsonify({"success": False, "message": "Please enter a username or email."}), 400
    if not password:
        return jsonify({"success": False, "message": "Please enter a password."}), 400
    if identifier in USERS:
        return jsonify({"success": False, "message": "That account already exists."}), 409

    USERS[identifier] = password
    save_users(USERS)

    if request.is_json:
        return jsonify({"success": True, "message": "Account created successfully."})
    return redirect(url_for("login", created="1"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/ask", methods=["POST"])
def ask():
    if not session.get("logged_in"):
        return jsonify({"response": "Please log in first."}), 401
    user_input = request.json.get("message", "")
    response   = get_response(user_input)
    return jsonify({"response": response})


# OAuth stubs — wire up with Flask-Dance or Authlib in production
@app.route("/auth/<provider>")
def oauth(provider):
    return redirect(url_for("signup", provider=provider))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)