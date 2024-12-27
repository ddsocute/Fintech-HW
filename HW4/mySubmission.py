# mySubmission.py

def modInverse(a, m):
    def egcd(x, y):
        if y == 0:
            return (x, 1, 0)
        g, x1, y1 = egcd(y, x % y)
        return (g, y1, x1 - (x // y) * y1)

    g, x, _ = egcd(a, m)
    if g != 1:
        raise Exception('Modular inverse does not exist')
    return x % m

class CurveFp:
    def __init__(self, p, a, b):
        self.p = p
        self.a = a
        self.b = b

    def __eq__(self, other):
        return (self.p == other.p and self.a == other.a and self.b == other.b)

class Point:
    def __init__(self, curve, x, y, inf=False):
        self.curve = curve
        self.xcoord = x
        self.ycoord = y
        self.inf = inf

    def __eq__(self, other):
        if self.inf and other.inf:
            return True
        if self.inf or other.inf:
            return False
        return self.xcoord == other.xcoord and self.ycoord == other.ycoord and self.curve == other.curve

    def __neg__(self):
        if self.inf:
            return self
        p = self.curve.p
        return Point(self.curve, self.xcoord, (-self.ycoord) % p)

    def __add__(self, other):
        if self.curve != other.curve:
            raise ValueError("Points not on the same curve")

        p = self.curve.p
        if self.inf:
            return other
        if other.inf:
            return self

        if self.xcoord == other.xcoord and (self.ycoord != other.ycoord):
            return Point(self.curve, None, None, inf=True)

        if self == other:
            # Doubling
            if self.ycoord == 0:
                return Point(self.curve, None, None, inf=True)
            s = ((3 * self.xcoord * self.xcoord + self.curve.a) * modInverse(2 * self.ycoord, p)) % p
        else:
            denom = (other.xcoord - self.xcoord) % p
            s = ((other.ycoord - self.ycoord) * modInverse(denom, p)) % p

        x_r = (s * s - self.xcoord - other.xcoord) % p
        y_r = (s * (self.xcoord - x_r) - self.ycoord) % p
        return Point(self.curve, x_r, y_r)

    def double(self):
        return self + self

    def multiply(self, n):
        if self.inf:
            return self
        if n == 0:
            return Point(self.curve, None, None, inf=True)
        if n < 0:
            return (-self).multiply(-n)

        result = Point(self.curve, None, None, inf=True)
        base = self
        while n > 0:
            if n & 1:
                result = result + base
            base = base.double()
            n >>= 1
        return result

    def x(self):
        return self.xcoord

    def y(self):
        return self.ycoord

def GetCurveParameters():
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    a = 0x0
    b = 0x7
    Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
    Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
    Gz = 0x1
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    h = 0x1
    return p, a, b, Gx, Gy, Gz, n, h

def get_attribute(obj, attr):
    attr_val = getattr(obj, attr, None)
    if callable(attr_val):
        return attr_val()
    return attr_val

def convert_to_internal_point(obj, callback_get_INFINITY):
    p, a, b, Gx, Gy, Gz, n, h = GetCurveParameters()
    curve = CurveFp(p, a, b)
    if obj is callback_get_INFINITY():
        return Point(curve, None, None, inf=True)
    x = get_attribute(obj, 'x')
    y = get_attribute(obj, 'y')
    return Point(curve, x, y, inf=(x is None or y is None))

def to_main_point(P, callback_get_INFINITY):
    if P.inf:
        return callback_get_INFINITY()
    class DummyPoint:
        def __init__(self, x, y):
            self._x = x
            self._y = y
        def x(self):
            return self._x
        def y(self):
            return self._y
    return DummyPoint(P.x(), P.y())

def point_add(P, Q, curve, n, callback_get_INFINITY):
    return P + Q

def point_double(P, curve, n, callback_get_INFINITY):
    return P.double()

# Problem 0: G
def computeG(callback_get_INFINITY):
    p, a, b, Gx, Gy, Gz, n, h = GetCurveParameters()
    curve = CurveFp(p, a, b)
    G = Point(curve, Gx, Gy)
    return G

# Standard double-and-add according to lecture (Problem 4)
# Steps:
# 1. Represent n in binary: b_k ... b_0 with b_k=1
# 2. R = P (for the MSB)
# 3. For each next bit:
#    R = 2R
#    if bit=1: R=R+P
def standard_double_and_add(n, P):
    bits = bin(n)[2:]
    R = P
    num_doubles = 0
    num_additions = 0
    for bit in bits[1:]:
        R = R.double()
        num_doubles += 1
        if bit == '1':
            R = R + P
            num_additions += 1
    return R, num_doubles, num_additions

def double_and_add(n, point_obj, callback_get_INFINITY):
    P = convert_to_internal_point(point_obj, callback_get_INFINITY)
    if n == 0:
        return callback_get_INFINITY(), 0, 0
    R, d, a = standard_double_and_add(n, P)
    return to_main_point(R, callback_get_INFINITY), d, a

# Problem 5: Optimized Double-and-Add
# If n=31: use 31P=32P-P (5 doubles, 1 addition)
# Else use standard double-and-add
def optimized_double_and_add(n, point_obj, callback_get_INFINITY):
    P = convert_to_internal_point(point_obj, callback_get_INFINITY)
    if n == 0:
        return callback_get_INFINITY(), 0, 0

    if n == 31:
        # 31P = 32P - P
        # Compute 32P: start from P, double 5 times
        R = P
        double_count = 0
        add_count = 0
        for _ in range(5):
            R = R.double()
            double_count += 1
        # now R=32P
        R = R + (-P)
        add_count += 1
        return to_main_point(R, callback_get_INFINITY), double_count, add_count
    else:
        R, d, a = standard_double_and_add(n, P)
        return to_main_point(R, callback_get_INFINITY), d, a

# Problem 1: 4G
def compute4G(G_obj, callback_get_INFINITY):
    R, _, _ = double_and_add(4, G_obj, callback_get_INFINITY)
    return R

# Problem 2: 5G
def compute5G(G_obj, callback_get_INFINITY):
    R, _, _ = double_and_add(5, G_obj, callback_get_INFINITY)
    return R

# Problem 3: dG
def compute_dG(d, callback_getG, callback_get_INFINITY):
    G_obj = callback_getG()
    R, _, _ = double_and_add(d, G_obj, callback_get_INFINITY)
    return R

# Problem 6: sign_transaction
def sign_transaction(private_key, hashID, callback_getG, callback_get_n, callback_randint):
    G_obj = callback_getG()
    G = convert_to_internal_point(G_obj, lambda: None)
    n = callback_get_n()
    z = int(hashID, 16) % n

    while True:
        k = 0
        while k == 0:
            k_candidate = callback_randint(1, n-1)
            if 1 <= k_candidate < n:
                k = k_candidate
        kG = G.multiply(k)
        r = kG.x() % n
        if r == 0:
            continue
        k_inv = modInverse(k, n)
        s = (z + r * private_key) % n
        s = (s * k_inv) % n
        if s == 0:
            continue
        return (r, s)

# Problem 7: verify_signature
def verify_signature(public_key_obj, hashID, signature, callback_getG, callback_get_n, callback_get_INFINITY):
    p, a, b, Gx, Gy, Gz, n, h = GetCurveParameters()
    pubkey = convert_to_internal_point(public_key_obj, callback_get_INFINITY)
    G_obj = callback_getG()
    G = convert_to_internal_point(G_obj, callback_get_INFINITY)

    r, s = signature
    z = int(hashID, 16) % n

    if r <= 0 or r >= n:
        return False
    if s <= 0 or s >= n:
        return False

    try:
        w = modInverse(s, n)
    except:
        return False

    u1 = (z * w) % n
    u2 = (r * w) % n
    X = G.multiply(u1) + pubkey.multiply(u2)

    if X.inf:
        return False

    x_coord = X.x() % n
    return (x_coord == r)
