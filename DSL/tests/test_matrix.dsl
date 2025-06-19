// Matrix Declaration and Basic Operations
matrix A := 2,2[[1.0,2.0],[3.0,4.0]];
print("Matrix A:");
print_matrix(A);

matrix B := 2,2[[5.0,6.0],[7.0,8.0]];
print("Matrix B:");
print_matrix(B);

// Matrix Addition
matrix C := A +m B;
print("A + B =");
print_matrix(C);

// Matrix Scalar Multiplication
float scalar := 2.0;
matrix D := A *m scalar;
print("2 * A =");
print_matrix(D);

// Matrix Multiplication
matrix E := A **m B;
print("A * B =");
print_matrix(E);

// Matrix Transpose
matrix F := transpose(A);
print("Transpose of A:");
print_matrix(F);


// Matrix Dimensions
vector dims := dim(A);
print("Dimensions of A:");
print_vector(dims);

// Matrix Element Access
float element := A[0][0];
print("A[0][0] =");
print_float(element);

// 3x3 Matrix Operations
matrix M1 := 3,3[[1.0,2.0,3.0],[4.0,5.0,6.0],[7.0,8.0,9.0]];
print("3x3 Matrix M1:");
print_matrix(M1);

matrix M2 := 3,3[[9.0,8.0,7.0],[6.0,5.0,4.0],[3.0,2.0,1.0]];
print("3x3 Matrix M2:");
print_matrix(M2);

// 3x3 Addition
matrix M3 := M1 +m M2;
print("M1 + M2 =");
print_matrix(M3);

// 3x3 Multiplication
matrix M4 := M1 **m M2;
print("M1 * M2 =");
print_matrix(M4);

// Determinant of 2x2 matrix
matrix det_test := 2,2[[4.0,-2.0],[-1.0,3.0]];
print("Matrix for determinant:");
print_matrix(det_test);
float det_val := det(det_test);
print("Determinant =");
print_float(det_val);

// Determinant of 3x3 matrix
matrix det_test3 := 3,3[[1.0,2.0,3.0],[0.0,1.0,4.0],[5.0,6.0,0.0]];
print("3x3 Matrix for determinant:");
print_matrix(det_test3);
float det_val3 := det(det_test3);
print("Determinant =");
print_float(det_val3);

// Matrix inverse (2x2)
matrix inv_test := 2,2[[4.0,7.0],[2.0,6.0]];
print("Matrix for inverse:");
print_matrix(inv_test);
matrix inverse := inv(inv_test);
print("Inverse =");
print_matrix(inverse);

// Verify inverse multiplication
matrix identity := inv_test **m inverse;
print("Original * Inverse (should be identity):");
print_matrix(identity);

// Matrix-Vector multiplication
matrix M := 2,2[[1.0,2.0],[3.0,4.0]];
vector v := 2[1.0,2.0];
print("Matrix M:");
print_matrix(M);
print("Vector v:");
print_vector(v);

// Special matrices
// Identity matrix
matrix I := 3,3[[1.0,0.0,0.0],[0.0,1.0,0.0],[0.0,0.0,1.0]];
print("3x3 Identity matrix:");
print_matrix(I);

// Upper triangular matrix
matrix U := 3,3[[1.0,2.0,3.0],[0.0,4.0,5.0],[0.0,0.0,6.0]];
print("Upper triangular matrix:");
print_matrix(U);

// Lower triangular matrix
matrix L := 3,3[[1.0,0.0,0.0],[2.0,3.0,0.0],[4.0,5.0,6.0]];
print("Lower triangular matrix:");
print_matrix(L);

// Diagonal matrix
matrix D := 3,3[[2.0,0.0,0.0],[0.0,3.0,0.0],[0.0,0.0,4.0]];
print("Diagonal matrix:");
print_matrix(D);

// Matrix operations with different sizes
matrix rect1 := 2,3[[1.0,2.0,3.0],[4.0,5.0,6.0]];
matrix rect2 := 3,2[[1.0,2.0],[3.0,4.0],[5.0,6.0]];
print("Rectangular matrix 1:");
print_matrix(rect1);
print("Rectangular matrix 2:");
print_matrix(rect2);

// Multiplication of rectangular matrices
matrix rect_mult := rect1 **m rect2;
print("rect1 * rect2 (2x3 * 3x2 = 2x2):");
print_matrix(rect_mult);

// Transpose of rectangular matrix
matrix rect_trans := transpose(rect1);
print("Transpose of rect1:");
print_matrix(rect_trans);

// Matrix with integer elements
matrix int_matrix := 2,2[[1.0,2.0],[3.0,4.0]];
print("Matrix with integer elements:");
print_matrix(int_matrix);

// Matrix with mixed integer and float elements
matrix mixed_matrix := 2,2[[1.0,2.5],[3.7,4.0]];
print("Matrix with mixed elements:");
print_matrix(mixed_matrix);