
matrix A := 3,3[[4.0,1.0,1.0],[2.0,5.0,2.0],[1.0,2.0,4.0]];
vector b := 3[8.0,3.0,11.0];
print_matrix(A);
print_vector(b);

// Convert vector b to a matrix (last column of augmented matrix)
matrix B := 3,1[[8.0],[3.0],[11.0]];

// Create augmented matrix [A|b]
matrix aug := 3,4[[4.0,1.0,1.0,8.0],[2.0,5.0,2.0,3.0],[1.0,2.0,4.0,11.0]];
print_matrix(aug);



vector dims := dim(aug);  // This will return [rows, cols]
int n := dims[0];        // number of rows
int m := dims[1];        // number of columns (including b)
int b := n - 1;

// Forward elimination
int i := 0;
while (i < b) {
    // Find maximum pivot in this column
    int max_row := i;
    float current_pivot := aug[i][i];
    float max_val := abs(current_pivot);
    int k := i + 1;
    while(k < n) {
        float temp_val := aug[k][i];
        float abs_val := abs(temp_val);

        if abs_val > max_val  then {
            
            max_val := abs_val;
            max_row := k;
        }
        k := k + 1;
    }

    // Swap rows if better pivot found
    if max_row != i then {
        int col := i;
        while(col < m) {
            float temp := aug[i][col];
            float swap_val := aug[max_row][col];
            aug[i][col] := swap_val;
            aug[max_row][col] := temp;
            col := col + 1;
        }
    }
    
    float pivot := aug[i][i];
    float pivot_abs := abs(pivot);
    float epsilon := 0.000001;

    if pivot_abs < epsilon then {
        print("No unique solution exists");
    } else {
        int j := i + 1;
        while(j < n) {
            float numerator := aug[j][i];
            float factor := numerator / pivot;
            
            int k := i;
            while(k < m) {
                float current := aug[j][k];
                float multiply := aug[i][k];
                float product := factor * multiply;
                float difference := current - product;
                aug[j][k] := difference;
                k := k + 1;
            }
            j := j + 1;
        }
    }
    i := i + 1;
}

print_matrix(aug);

// Check if system is solvable
int last_row := n - 1;
int last_col := n - 1;
float last_pivot := aug[last_row][last_col];
float last_pivot_abs := abs(last_pivot);
float small := 0.000001;

if last_pivot_abs < small then {
    print("System has no unique solution");
} else {
    // Back substitution
    vector x := 3[0.0, 0.0, 0.0];
    i := n - 1;
    while(i >= 0) {
        float sum := 0.0;
        int j := i + 1;
        while(j < n) {
            float coef := aug[i][j];
            float val := x[j];
            float product := coef * val;
            sum := sum + product;
            j := j + 1;
        }
        
        int last := m - 1;
        float rhs := aug[i][last];
        float diff := rhs - sum;
        float diag := aug[i][i];
        float diag_abs := abs(diag);
        
        if diag_abs < small then {
            print("Division by zero in back substitution");
        } else {
            float quotient := diff / diag;
            x[i] := quotient;
        }
        i := i - 1;
    }

    print("Solution:");
    print_vector(x);
}