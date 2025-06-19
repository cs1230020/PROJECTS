(* ast.ml *)

(* Exception for type errors *)
exception TypeError of string

(* Types supported by the language *)
type typ =
  | BoolType
  | IntType
  | FloatType
  | StringType
  | VectorType of vector_info
  | MatrixType of matrix_info

and vector_info = {
  size: int;
  element_type: typ;
}

and matrix_info = {
  rows: int;
  cols: int;
  element_type: typ;
}

(* Binary operators *)
type binop =
  | Add | Sub | Mul | Div | Mod
  | And | Or
  | Eq | Neq | Lt | Le | Gt | Ge
  | DotProduct | Angle
  | VectorAdd | VectorScalarMult
  | MatrixAdd | MatrixMult | MatrixScalarMult

(* Unary operators *)
type unop =
  | Neg | Not | Abs
  | Transpose | Det | Mag | Dim
  | Inverse

(* Expressions and Statements defined mutually recursively *)
type expr =
  | Int of int
  | Float of float
  | Bool of bool
  | String of string
  | Var of string
  | BinOp of binop * expr * expr
  | UnOp of unop * expr
  | Vector of int * typ * expr list (* size, element type, elements *)
  | Matrix of int * int * typ * expr list list
  | VectorAccess of string * expr (* vector[index] *)
  | MatrixAccess of string * expr * expr
  | Input of string option  (* None for standard input, Some string for prompt *)
  | InputInt
  | InputFloat
  | InputVector
  | InputMatrix
  | InputFile of string
and stmt =
  
  | Decl of string * string * expr
  | VectorDecl of string * expr
  | MatrixDecl of string * expr
  | Assign of string * expr
  | If of expr * stmt * stmt option
  | While of expr * stmt
  | For of string * expr * expr * stmt * stmt
  | Seq of stmt list
  | Print of expr
  | PrintInt of expr
  | PrintFloat of expr
  | PrintVector of expr
  | PrintMatrix of expr
  | PrintFile of string * expr
  | Input of string option
  | InputInt
  | InputFloat
  | InputVector
  | InputMatrix
  | InputFile of string
  | VectorElementAssign of string * expr * expr 
  | MatrixElementAssign of string * expr * expr * expr

type program = stmt list