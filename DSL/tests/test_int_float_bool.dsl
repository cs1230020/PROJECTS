// Integer declarations and operations
int a := 5;
int b := 3;
print("Integers a and b:");
print_int(a);
print_int(b);

// Basic integer arithmetic
int sum := a + b;
print("a + b =");
print_int(sum);

int diff := a - b;
print("a - b =");
print_int(diff);

int prod := a * b;
print("a * b =");
print_int(prod);

int quot := a / b;
print("a / b =");
print_int(quot);

int rem := a % b;
print("a % b =");
print_int(rem);

// Float declarations and operations
float x := 5.5;
float y := 2.5;
print("Floats x and y:");
print_float(x);
print_float(y);

// Basic float arithmetic
float fsum := x + y;
print("x + y =");
print_float(fsum);

float fdiff := x - y;
print("x - y =");
print_float(fdiff);

float fprod := x * y;
print("x * y =");
print_float(fprod);

float fdiv := x / y;
print("x / y =");
print_float(fdiv);

// Mixed integer and float operations
float mixed1 := x + a;
print("float + int:");
print_float(mixed1);

float mixed2 := b * x;
print("int * float:");
print_float(mixed2);

// Comparisons with integers
bool int_eq := a == b;
print("a == b:");
print(int_eq);

bool int_neq := a != b;
print("a != b:");
print(int_neq);

bool int_lt := a < b;
print("a < b:");
print(int_lt);

bool int_gt := a > b;
print("a > b:");
print(int_gt);

bool int_le := a <= b;
print("a <= b:");
print(int_le);

bool int_ge := a >= b;
print("a >= b:");
print(int_ge);

// Comparisons with floats
bool float_eq := x == y;
print("x == y:");
print(float_eq);

bool float_neq := x != y;
print("x != y:");
print(float_neq);

bool float_lt := x < y;
print("x < y:");
print(float_lt);

bool float_gt := x > y;
print("x > y:");
print(float_gt);

bool float_le := x <= y;
print("x <= y:");
print(float_le);

bool float_ge := x >= y;
print("x >= y:");
print(float_ge);

bool a := true;
bool b := !a;
print(a);
print(b);





