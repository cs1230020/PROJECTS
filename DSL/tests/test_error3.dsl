// Invalid matrix operations
matrix m1 := 2,2[[1.0,2.0],[3.0,4.0]];
matrix m2 := 3,3[[1.0,2.0,3.0],[4.0,5.0,6.0],[7.0,8.0,9.0]];
// matrix m3 := m1 +m m2;  // Different size matrices
 matrix m4 := m1 **m m2; // Invalid multiplication dimensions
