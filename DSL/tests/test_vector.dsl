// test_vector.dsl

// Vector Declaration and Basic Operations
vector v1 := 4[1.0, 2.0, 3.0, 4.0];
print("Vector v1:");
print_vector(v1);

vector v2 := 4[5.0, 6.0, 7.0, 8.0];
print("Vector v2:");
print_vector(v2);
// Vector Addition
vector v3 := v1 +v v2;
print("v1 + v2 =");
print_vector(v3);

// Vector Scalar Multiplication
float scalar := 2.0;
vector v4 := v1 *v scalar;
print("2 * v1 =");
print_vector(v4);

vector v5 := scalar *v v1;
print("v1 * 2 =");
print_vector(v5);

// Vector Dot Product
float dot_result := v1 dot v2;
print("v1 . v2 =");
print_float(dot_result);

// Vector Magnitude
float mag1 := mag(v1);
print("Magnitude of v1:");
print_float(mag1);

// Vector Dimension
int dim1 := dim(v1);
print("Dimension of v1:");
print_int(dim1);

// Vector Element Access
float elem := v1[2];
print("v1[2] =");
print_float(elem);

// Vector with different sizes
vector v6 := 3[1.0, 2.0, 3.0];
vector v7 := 3[4.0, 5.0, 6.0];
print("3D vectors:");
print_vector(v6);
print_vector(v7);

// Angle between vectors
float angle_result := angle(v6, v7);
print("Angle between v6 and v7 (in radians):");
print_float(angle_result);

// Vector with integer elements (should be converted to float)
vector v8 := 3[1.0, 2.0, 3.0];
print("Vector with integer elements:");
print_vector(v8);

// Zero vector
vector zero_vec := 3[0.0, 0.0, 0.0];
print("Zero vector:");
print_vector(zero_vec);

// Unit vectors
vector unit_x := 3[1.0, 0.0, 0.0];
vector unit_y := 3[0.0, 1.0, 0.0];
vector unit_z := 3[0.0, 0.0, 1.0];
print("Unit vectors:");
print_vector(unit_x);
print_vector(unit_y);
print_vector(unit_z);

// Dot products with unit vectors (should give components)
float x_comp := unit_x dot v6;
float y_comp := unit_y dot v6;
float z_comp := unit_z dot v6;
print("Components of v6:");
print_float(x_comp);
print_float(y_comp);
print_float(z_comp);

// Vector operations with mixed types
vector v9 := 4[1.0, 2.5, 3.0, 4.5];
print("Vector with mixed elements:");
print_vector(v9);

// Multiple operations
vector v10 := (v1 +v v2) *v 0.5;
print("Average of v1 and v2:");
print_vector(v10);

// Perpendicular vectors
vector v11 := 2[1.0, 0.0];
vector v12 := 2[0.0, 1.0];
float perp_angle := angle(v11, v12);
print("Angle between perpendicular vectors (should be π/2):");
print_float(perp_angle);

// Parallel vectors
vector v13 := 2[1.0, 1.0];
vector v14 := 2[2.0, 2.0];
float para_angle := angle(v13, v14);
print("Angle between parallel vectors (should be 0):");
print_float(para_angle);

// Vector element modification
vector v15 := 3[1.0, 2.0, 3.0];
print("Original vector:");
print_vector(v15);
v15[1] := 5.0;
print("After modifying second element:");
print_vector(v15);

// Magnitude of different vectors
vector v16 := 2[3.0, 4.0];
float mag16 := mag(v16);
print("Magnitude of [3,4] (should be 5):");
print_float(mag16);

// Normalized vector (unit vector)
float mag_v13 := mag(v13);
vector v13_norm := v13 *v (1.0 / mag_v13);
print("Normalized vector (should have magnitude 1):");
print_vector(v13_norm);
float mag_norm := mag(v13_norm);
print("Magnitude of normalized vector (should be 1):");
print_float(mag_norm);

// Vector subtraction using addition and scalar multiplication
vector v17 := v1 +v (v2 *v -1.0);
print("v1 - v2 =");
print_vector(v17);

// Dot product properties
float dot1 := v1 dot v1;
float mag_squared := mag(v1) * mag(v1);
print("v1 · v1 =");
print_float(dot1);
print("||v1||^2 =");
print_float(mag_squared);

// Testing orthogonality
vector v18 := 2[1.0, 1.0];
vector v19 := 2[1.0, -1.0];
float orth_dot := v18 dot v19;
print("Dot product of orthogonal vectors (should be 0):");
print_float(orth_dot);