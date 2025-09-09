class X:
    def __init__(self):
        pass

    def __repr__(self):
        return "X"

    def evaluate(self, x_value):
        # Return an Int carrying the provided x_value
        return Int(x_value)

    def simplify(self):
        # X cannot be simplified further
        return self


class Int:
    def __init__(self, i):
        self.i = i

    def __repr__(self):
        return str(self.i)

    def evaluate(self, x_value):
        # Constants evaluate to themselves
        return Int(self.i)

    def simplify(self):
        # Constants are already simple
        return self


class Add:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def __repr__(self):
        return repr(self.p1) + " + " + repr(self.p2)

    def evaluate(self, x_value):
        v1 = self.p1.evaluate(x_value).i
        v2 = self.p2.evaluate(x_value).i
        return Int(v1 + v2)

    def simplify(self):
        a = self.p1.simplify()
        b = self.p2.simplify()
        # 0 + X -> X, X + 0 -> X
        if isinstance(a, Int) and a.i == 0:
            return b
        if isinstance(b, Int) and b.i == 0:
            return a
        # 3 + 5 -> 8
        if isinstance(a, Int) and isinstance(b, Int):
            return Int(a.i + b.i)
        return Add(a, b)


class Mul:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def __repr__(self):
        if isinstance(self.p1, Add):
            if isinstance(self.p2, Add):
                return "( " + repr(self.p1) + " ) * ( " + repr(self.p2) + " )"
            return "( " + repr(self.p1) + " ) * " + repr(self.p2)
        if isinstance(self.p2, Add):
            return repr(self.p1) + " * ( " + repr(self.p2) + " )"
        return repr(self.p1) + " * " + repr(self.p2)

    def evaluate(self, x_value):
        v1 = self.p1.evaluate(x_value).i
        v2 = self.p2.evaluate(x_value).i
        return Int(v1 * v2)

    def simplify(self):
        a = self.p1.simplify()
        b = self.p2.simplify()
        # X * 0 -> 0, 0 * X -> 0
        if (isinstance(a, Int) and a.i == 0) or (isinstance(b, Int) and b.i == 0):
            return Int(0)
        # X * 1 -> X, 1 * X -> X
        if isinstance(a, Int) and a.i == 1:
            return b
        if isinstance(b, Int) and b.i == 1:
            return a
        # 3 * 5 -> 15
        if isinstance(a, Int) and isinstance(b, Int):
            return Int(a.i * b.i)
        return Mul(a, b)


class Sub:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def __repr__(self):
        # Parenthesize additive operands to preserve order
        left = f"( {self.p1!r} )" if isinstance(self.p1, (Add, Sub)) else repr(self.p1)
        right = f"( {self.p2!r} )" if isinstance(self.p2, (Add, Sub)) else repr(self.p2)
        return f"{left} - {right}"

    def evaluate(self, x_value):
        v1 = self.p1.evaluate(x_value).i
        v2 = self.p2.evaluate(x_value).i
        return Int(v1 - v2)

    def simplify(self):
        a = self.p1.simplify()
        b = self.p2.simplify()
        # X - 0 -> X
        if isinstance(b, Int) and b.i == 0:
            return a
        # 5 - 3 -> 2
        if isinstance(a, Int) and isinstance(b, Int):
            return Int(a.i - b.i)
        return Sub(a, b)


class Div:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def __repr__(self):
        # Parenthesize additive operands to preserve precedence
        left_needs_paren = isinstance(self.p1, (Add, Sub))
        right_needs_paren = isinstance(self.p2, (Add, Sub))
        left = f"( {self.p1!r} )" if left_needs_paren else repr(self.p1)
        right = f"( {self.p2!r} )" if right_needs_paren else repr(self.p2)
        return f"{left} / {right}"

    def evaluate(self, x_value):
        v1 = self.p1.evaluate(x_value).i
        v2 = self.p2.evaluate(x_value).i
        if v2 == 0:
            raise ZeroDivisionError("Division by zero during evaluation")
        return Int(v1 // v2)  # integer division

    def simplify(self):
        a = self.p1.simplify()
        b = self.p2.simplify()
        # 0 / X -> 0 (if X != 0 not checked here; stays algebraic)
        if isinstance(a, Int) and a.i == 0 and not (isinstance(b, Int) and b.i == 0):
            return Int(0)
        # X / 1 -> X
        if isinstance(b, Int) and b.i == 1:
            return a
        # 6 / 2 -> 3 (integer division)
        if isinstance(a, Int) and isinstance(b, Int):
            if b.i == 0:
                # keep as Div to avoid raising during simplification
                return Div(a, b)
            return Int(a.i // b.i)
        return Div(a, b)


# Original polynomial example
poly = Add(Add(Int(4), Int(3)), Add(X(), Mul(Int(1), Add(Mul(X(), X()), Int(1)))))
print("Original polynomial:", poly)

# Test new Sub and Div classes
print("\n--- Testing Sub and Div classes ---")
try:
    sub_poly = Sub(Int(10), Int(3))
    print("Subtraction:", sub_poly)
except Exception as e:
    print("❌ Subtraction test failed -", e)

try:
    div_poly = Div(Int(15), Int(3))
    print("Division:", div_poly)
except Exception as e:
    print("❌ Division test failed -", e)

# Test evaluation
print("\n--- Testing evaluation ---")
try:
    simple_poly = Add(Sub(Mul(Int(2), X()), Int(1)), Div(Int(6), Int(2)))
    print("Test polynomial:", simple_poly)
    result = simple_poly.evaluate(4)
    print(f"Evaluation for X=4: {result}")
except Exception as e:
    print("❌ Evaluation test failed -", e)

try:
    original_result = poly.evaluate(2)
    print(f"Original polynomial evaluation for X=2: {original_result}")
except Exception as e:
    print("❌ Original polynomial evaluation failed -", e)

# Option to run comprehensive tests
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("\n" + "=" * 60)
        print("Running comprehensive test suite...")
        print("=" * 60)
        from test_polynomial import run_all_tests

        run_all_tests()
    else:
        print("\n💡 To run comprehensive tests, use: python polynomial.py --test")
        print("💡 Or run directly: python test_polynomial.py")
