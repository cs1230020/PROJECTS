
int count := 0;
while(count < 5) {
   print_int(count);
 count := count + 1;
}
int n := 10;
int sum := 0;
int i := 1;
while(i <= n) {
    sum := sum + i;
    i := i + 1;
}
print("Sum is:");
print_int(sum);  // Should print 55
int num := 5;
int factorial := 1;
while(num > 0) {
    factorial := factorial * num;
    num := num - 1;
}
print("Factorial is:");
print_int(factorial);  // Should print 120
vector v := 5[1.0, 2.0, 3.0, 4.0, 5.0];
int index := 0;
float sum_vector := 0.0;
while(index < 5) {
    sum_vector := sum_vector + v[index];
    index := index + 1;
}
print("Vector sum is:");
print_float(sum_vector);

vector numbers := 6[3.0, 7.0, 2.0, 8.0, 1.0, 5.0];
int pos := 1;
float max := numbers[0];
while(pos < 6) {
    bool a := (numbers[pos]>max);
    if a then {
        max := numbers[pos];
    }
    pos := pos + 1;
}
print("Maximum is:");
print_float(max);

// Fibonacci sequence using while
vector fib := 10[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0];
fib[0] := 0.0;
fib[1] := 1.0;
int idx := 2;
while (idx<10) {
    
    int c:= idx - 1;
    print_int(c);
    idx:= idx +1;
}
print("Fibonacci sequence:");
print_vector(fib);

vector fib := 10[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0];
fib[0] := 0.0;
fib[1] := 1.0;
int idx := 2;
while(idx < 10) {
    int c:= idx - 1;
    int d:= idx - 2;
    float f := fib[c];
    float g:= fib[d];
    float q := f + g;
    fib[idx]:= q;
    idx := idx + 1;
}
print("Fibonacci sequence:");
print_vector(fib);