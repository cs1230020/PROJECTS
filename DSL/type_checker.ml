open Ast
open Printf

(* Exception for type errors *)
exception TypeError of string
let expected_type = ref None
(* Symbol Table Module *)
module SymbolTable = struct
  let table = Hashtbl.create 100
  
  let add name typ = Hashtbl.replace table name typ
  let find name = Hashtbl.find_opt table name
  let clear () = Hashtbl.clear table
end

let rec string_of_type = function
  | BoolType -> "bool"
  | IntType -> "int"
  | FloatType -> "float"
  | StringType -> "string"
  | VectorType info -> 
      sprintf "vector<%s>[%d]" 
        (string_of_type info.element_type) 
        info.size
  | MatrixType info -> 
      sprintf "matrix<%s>[%d,%d]" 
        (string_of_type info.element_type) 
        info.rows 
        info.cols

(* Debug function to print environment *)
let print_env () =
  Printf.printf "Environment:\n";
  Hashtbl.iter (fun name typ ->
    Printf.printf "  %s: %s\n" name (string_of_type typ)
  ) SymbolTable.table

let rec type_check_expr (e : expr) : typ =
  match e with
  | Int _ -> IntType
  | Float _ -> FloatType
  | Bool _ -> BoolType
  | String _ -> StringType
  | Var x ->
      (match SymbolTable.find x with
       | Some t -> t
       | None -> raise (TypeError ("Undefined variable " ^ x)))
  | Input _ -> StringType
  | InputInt -> IntType
  | InputFloat -> FloatType
  | InputVector -> 
      VectorType { size = 0; element_type = FloatType }
  | InputMatrix -> 
      MatrixType { rows = 0; cols = 0; element_type = FloatType }
  | InputFile _ ->  (* Add this case *)
      (match !expected_type with
       | Some "bool" -> BoolType
       | Some "int" -> IntType
       | Some "float" -> FloatType
       | Some "string" -> StringType
       | Some "vector" -> VectorType { size = 0; element_type = FloatType }
       | Some "matrix" -> MatrixType { rows = 0; cols = 0; element_type = FloatType }
       | Some t -> raise (TypeError ("Unsupported type for file input: " ^ t))
       | None -> StringType)

  | Vector(size, t, elements) ->
      if List.length elements <> size then
        raise (TypeError (sprintf 
          "Vector size mismatch: expected %d elements, got %d" 
          size (List.length elements)));
      check_vector_declaration size t elements

  | Matrix(rows, cols, t, elements) ->
      if List.length elements <> rows then
        raise (TypeError (sprintf 
          "Matrix row count mismatch: expected %d rows, got %d" 
          rows (List.length elements)));
      List.iter (fun row ->
        if List.length row <> cols then
          raise (TypeError (sprintf 
            "Matrix column count mismatch: expected %d columns" cols))
      ) elements;
      check_matrix_declaration rows cols t elements

  | UnOp(op, e1) ->
      let t1 = type_check_expr e1 in
      (match op with
      | Neg ->
          (match t1 with
          | IntType | FloatType -> t1
          | _ -> raise (TypeError "Negation requires numeric type"))
      | Not ->
          if t1 = BoolType then BoolType
          else raise (TypeError "Not requires boolean")
      | Abs ->
          if t1 = IntType || t1 = FloatType then t1
          else raise (TypeError "Abs requires numeric type")
      | Transpose ->
          (match t1 with
          | MatrixType info -> 
              MatrixType { info with rows = info.cols; cols = info.rows }
          | _ -> raise (TypeError "Transpose requires matrix"))
      | Inverse ->
    (match t1 with
    | MatrixType info when info.rows = info.cols -> 
        MatrixType info  (* Inverse has same dimensions as original *)
    | MatrixType _ -> 
        raise (TypeError "Matrix inverse requires square matrix")
    | _ -> raise (TypeError "Inverse operation requires matrix"))
      | Det ->
        (match t1 with
        | MatrixType info when info.rows = info.cols -> 
            FloatType
        | MatrixType _ -> 
            raise (TypeError "Determinant requires square matrix")
        | _ -> raise (TypeError "Determinant operation requires matrix"))
      | Mag ->
          (match t1 with
          | VectorType _ -> FloatType
          | _ -> raise (TypeError "Magnitude requires vector"))
      | Dim ->
          (match t1 with
          | VectorType _ -> IntType
          | MatrixType info -> 
        VectorType { 
          size = 2; 
          element_type = IntType 
        } 
          | _ -> raise (TypeError "Dimension requires vector or matrix")))

  | BinOp(op, e1, e2) ->
      let t1 = type_check_expr e1 in
      let t2 = type_check_expr e2 in
      (match op with
      | Add | Sub | Mul | Div | Mod ->
    (match t1, t2 with
    | IntType, IntType -> IntType
    | FloatType, FloatType -> FloatType
    | IntType, FloatType | FloatType, IntType -> FloatType  (* Added this line for type promotion *)
    | _ -> raise (TypeError "Type mismatch in arithmetic operation"))
      | And | Or ->
          if t1 = BoolType && t2 = BoolType then BoolType
          else raise (TypeError "Boolean operation requires boolean operands")
      | Eq | Neq | Lt | Le | Gt | Ge ->
          (match t1, t2 with
          | IntType, IntType | FloatType, FloatType -> BoolType
          | _ -> raise (TypeError "Type mismatch in comparison"))
      | DotProduct ->
    (match t1, t2 with
    | VectorType v1, VectorType v2 when v1.size = v2.size ->
        if v1.element_type = v2.element_type then
            v1.element_type  (* Returns same type as vector elements *)
        else
            raise (TypeError "Vector element types must match for dot product")
    | _, _ -> raise (TypeError "Dot product requires vectors of same size"))
      | Angle ->
    (match t1, t2 with
    | VectorType v1, VectorType v2 ->
        if v1.size <> v2.size then
          raise (TypeError (sprintf 
            "Angle operation requires vectors of same size: %d != %d" 
            v1.size v2.size));
        (* Both vectors should contain numeric elements *)
        if (v1.element_type <> IntType && v1.element_type <> FloatType) ||
           (v2.element_type <> IntType && v2.element_type <> FloatType) then
          raise (TypeError "Vector elements must be numeric for angle calculation");
        FloatType  (* Angle is always returned as float (radians) *)
    | _, _ -> raise (TypeError "Angle operation requires two vectors"))
      | VectorAdd ->
          (match t1, t2 with
          | VectorType v1, VectorType v2 ->
              if v1.size <> v2.size then
                raise (TypeError (sprintf 
                  "Vector size mismatch in addition: %d != %d" 
                  v1.size v2.size));
              if v1.element_type <> v2.element_type then
                raise (TypeError "Vector element types must match for addition");
              VectorType v1
          | _, _ -> raise (TypeError "Vector addition requires two vectors"))
      | VectorScalarMult ->
    (match t1, t2 with
    | VectorType v, IntType | IntType, VectorType v ->
        VectorType v
    | VectorType v, FloatType | FloatType, VectorType v ->
        VectorType { v with element_type = FloatType }  (* Promotes int vector to float when multiplied by float *)
    | _, _ -> raise (TypeError "Vector scalar multiplication type mismatch"))
      | MatrixAdd ->
          (match t1, t2 with
          | MatrixType m1, MatrixType m2 
            when m1.rows = m2.rows && m1.cols = m2.cols 
            && m1.element_type = m2.element_type ->
              MatrixType m1
          | _, _ -> raise (TypeError "Matrix addition requires matrices of same dimensions and type"))
      | MatrixMult ->
          (match t1, t2 with
          | MatrixType m1, MatrixType m2 when m1.cols = m2.rows ->
              MatrixType {
                rows = m1.rows;
                cols = m2.cols;
                element_type = m1.element_type
              }
          | _, _ -> raise (TypeError "Invalid matrix multiplication dimensions"))
      
      | MatrixScalarMult ->
    (match t1, t2 with
    | MatrixType m1, IntType | IntType, MatrixType m1 ->
        MatrixType m1
    | MatrixType m1, FloatType | FloatType, MatrixType m1 ->
        MatrixType { m1 with element_type = FloatType }  (* Promotes int matrix to float when multiplied by float *)
    | _, _ -> raise (TypeError "Matrix scalar multiplication type mismatch")))

  | VectorAccess(var, index) ->
      (match SymbolTable.find var with
       | Some (VectorType info) ->
           let index_type = type_check_expr index in
           (match index_type, index with
           | IntType, Int i ->
               if i < 0 || i >= info.size then
                 raise (TypeError (sprintf 
                   "Vector index out of bounds: index %d, vector size %d" 
                   i info.size))
               else
                 info.element_type
           | IntType, _ -> info.element_type
           | _, _ -> raise (TypeError "Vector index must be an integer"))
       | _ -> raise (TypeError (var ^ " is not a vector")))

  | MatrixAccess(var, row, col) ->
      (match SymbolTable.find var with
       | Some (MatrixType info) ->
           let row_type = type_check_expr row in
           let col_type = type_check_expr col in
           (match (row_type, col_type, row, col) with
           | (IntType, IntType, Int r, Int c) ->
               if r < 0 || r >= info.rows then
                 raise (TypeError (sprintf 
                   "Matrix row index out of bounds: index %d, matrix rows %d" 
                   r info.rows))
               else if c < 0 || c >= info.cols then
                 raise (TypeError (sprintf 
                   "Matrix column index out of bounds: index %d, matrix columns %d" 
                   c info.cols))
               else
                 info.element_type
           | (IntType, IntType, _, _) -> info.element_type
           | _, _, _, _ -> raise (TypeError "Matrix indices must be integers"))
       | _ -> raise (TypeError (var ^ " is not a matrix")))

and check_vector_declaration size element_type elements =
  List.iter (fun e ->
    let et = type_check_expr e in
    match et with
    | IntType when element_type = IntType -> ()
    | FloatType when element_type = FloatType -> ()
    | _ -> raise (TypeError "Vector element type mismatch")
  ) elements;
  VectorType { size = size; element_type = element_type }

and check_matrix_declaration rows cols element_type elements =
  List.iter (fun row ->
    List.iter (fun e ->
      let et = type_check_expr e in
      match et with
      | IntType when element_type = IntType -> ()
      | FloatType when element_type = FloatType -> ()
      | IntType when element_type = FloatType -> ()  (* Allow int in float matrix *)
      | _ -> raise (TypeError "Matrix element type mismatch")
    ) row
  ) elements;
  MatrixType { rows = rows; cols = cols; element_type = element_type }
let rec type_check_stmt (s : stmt) : unit =
  try
    match s with
    | Decl(t, x, e) ->
        let et = type_check_expr e in
        let expected = match t with
          | "bool" -> 
              (match e with
               | Input _ | InputFile _ -> BoolType
               | _ -> BoolType)
          | "int" -> 
              (match e with
               | Input _ | InputInt | InputFile _ -> IntType
               | _ -> IntType)
          | "float" -> 
              (match e with
               | Input _ | InputFloat | InputFile _ -> FloatType
               | _ -> FloatType)
          | "string" -> 
              (match e with
               | Input _ | InputFile _ -> StringType
               | _ -> StringType)
          | "vector" ->
              (match e with
               | InputVector | InputFile _ -> 
                   VectorType { size = 0; element_type = FloatType }
               | _ -> et)
          | "matrix" ->
              (match e with
               | InputMatrix | InputFile _ -> 
                   MatrixType { rows = 0; cols = 0; element_type = FloatType }
               | _ -> et)
          | _ -> raise (TypeError ("Unknown type " ^ t))
        in
        if et = expected || 
           (match e with 
            | Input _ | InputFile _ -> true 
            | InputInt when t = "int" -> true
            | InputFloat when t = "float" -> true
            | InputVector when t = "vector" -> true
            | InputMatrix when t = "matrix" -> true
            | _ -> false) 
        then
          SymbolTable.add x expected
        else 
          raise (TypeError "Declaration type mismatch")

    | VectorDecl(x, e) ->
        (match e with
        | InputVector -> 
            SymbolTable.add x (VectorType { size = 0; element_type = FloatType })
        | Input _ ->
            SymbolTable.add x (VectorType { size = 0; element_type = FloatType })
        | _ ->
            let et = type_check_expr e in
            match et with
            | VectorType info -> SymbolTable.add x (VectorType info)
            | _ -> raise (TypeError "Expected vector type in vector declaration"))

    | MatrixDecl(x, e) ->
        (match e with
        | InputMatrix -> 
            SymbolTable.add x (MatrixType { rows = 0; cols = 0; element_type = FloatType })
        | Input _ ->
            SymbolTable.add x (MatrixType { rows = 0; cols = 0; element_type = FloatType })
        | _ ->
            let et = type_check_expr e in
            match et with
            | MatrixType info -> SymbolTable.add x (MatrixType info)
            | _ -> raise (TypeError "Expected matrix type in matrix declaration"))

    | Assign(x, e) ->
        let expr_type = type_check_expr e in
        (match SymbolTable.find x with
         | Some var_type ->
             (match e with
              | Input _ | InputInt | InputFloat | InputVector | InputMatrix ->
                  (match (var_type, e) with
                   | (IntType, (InputInt | Input _)) -> ()
                   | (FloatType, (InputFloat | Input _)) -> ()
                   | (StringType, Input _) -> ()
                   | (VectorType _, InputVector) -> ()
                   | (MatrixType _, InputMatrix) -> ()
                   | _ -> raise (TypeError "Input type mismatch"))
              | _ ->
                  if var_type = expr_type then ()
                  else raise (TypeError "Assignment type mismatch"))
         | None ->
             raise (TypeError ("Variable '" ^ x ^ "' must be declared before use")))

    | If(e, s1, s2opt) ->
        let cond_type = type_check_expr e in
        if cond_type <> BoolType then
          raise (TypeError "If condition must be boolean");
        type_check_stmt s1;
        (match s2opt with
         | Some s2 -> type_check_stmt s2
         | None -> ())

    | While(e, s) ->
        let cond_type = type_check_expr e in
        if cond_type <> BoolType then
          raise (TypeError "While condition must be boolean");
        type_check_stmt s

    | For(var, init, cond, incr, body) ->
        type_check_stmt (Decl("int", var, init));
        let cond_type = type_check_expr cond in
        if cond_type <> BoolType then
          raise (TypeError "For loop condition must be boolean");
        type_check_stmt incr;
        type_check_stmt body

    | Seq stmts ->
        List.iter type_check_stmt stmts
    
    | Print e | PrintInt e | PrintFloat e | PrintVector e | PrintMatrix e ->
        ignore (type_check_expr e)

    | PrintFile(_, e) ->
        ignore (type_check_expr e)

       | Input _ | InputInt | InputFloat | InputVector | InputMatrix | InputFile _ ->
        ()
    | VectorElementAssign(var, index, value) ->
        (match SymbolTable.find var with
         | Some (VectorType info) ->
             let index_type = type_check_expr index in
             let value_type = type_check_expr value in
             if index_type <> IntType then
               raise (TypeError "Vector index must be an integer");
             (match value_type with
              | IntType | FloatType -> ()  (* Allow both int and float assignments *)
              | _ -> raise (TypeError "Vector element must be numeric"))
         | _ -> raise (TypeError (var ^ " is not a vector")))
      | MatrixElementAssign(var, row_expr, col_expr, value) ->
        (match SymbolTable.find var with
         | Some (MatrixType info) ->
             let row_type = type_check_expr row_expr in
             let col_type = type_check_expr col_expr in
             let value_type = type_check_expr value in
             
             (* Check indices are integers *)
             if row_type <> IntType || col_type <> IntType then
               raise (TypeError "Matrix indices must be integers");
             
             (* Check value type *)
             (match value_type with
              | IntType | FloatType -> ()  (* Allow both int and float assignments *)
              | _ -> raise (TypeError "Matrix element must be numeric"));
             
             (* Check bounds if indices are constants *)
             (match (row_expr, col_expr) with
              | (Int r, Int c) ->
                  if r < 0 || r >= info.rows then
                    raise (TypeError "Matrix row index out of bounds");
                  if c < 0 || c >= info.cols then
                    raise (TypeError "Matrix column index out of bounds")
              | _ -> ())
         | _ -> raise (TypeError (var ^ " is not a matrix")))

  with TypeError msg ->
    raise (TypeError msg)

let type_check (program : program) : unit =
  try
    SymbolTable.clear ();
    List.iter type_check_stmt program;
    (* Return unit if successful *)
    ()
  with TypeError msg ->
    raise (TypeError msg)