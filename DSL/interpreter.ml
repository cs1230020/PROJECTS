(* interpreter.ml *)
open Ast
open Printf
exception Runtime_error of string
(* Values that can be computed by the interpreter *)
type value =
  | VInt of int
  | VFloat of float
  | VBool of bool
  | VString of string
  | VVector of value list
  | VMatrix of value list list
  | VVoid
let rec string_of_value = function
  | VInt i -> string_of_int i
  | VFloat f -> string_of_float f
  | VBool b -> string_of_bool b
  | VString s -> s
  | VVector vs -> 
      "[" ^ String.concat ", " (List.map string_of_value vs) ^ "]"
  | VMatrix vss ->
      let row_strings = List.map (fun row ->
        "[" ^ String.concat ", " (List.map string_of_value row) ^ "]"
      ) vss in
      "[\n  " ^ String.concat ",\n  " row_strings ^ "\n]"
  | VVoid -> "void"
let read_file_content filename =
  try
    let chan = open_in filename in
    let content = really_input_string chan (in_channel_length chan) in
    close_in chan;
    String.trim content
  with _ -> 
    raise (Runtime_error ("Could not read file: " ^ filename))

let rec float_of_value = function
  | VFloat f -> f
  | VInt i -> float_of_int i
  | VBool b -> float_of_int (if b then 1 else 0)  (* Convert boolean to 0.0 or 1.0 *)
  | VString s -> 
      (try float_of_string s
       with Failure _ -> 
         raise (Runtime_error ("Cannot convert string '" ^ s ^ "' to float")))
  | VVector v -> 
      (match v with
       | [x] -> float_of_value x  (* Single element vector to float *)
       | _ -> raise (Runtime_error "Cannot convert vector with multiple elements to float"))
  | VMatrix m ->
      (match m with
       | [[x]] -> float_of_value x  (* Single element matrix to float *)
       | [] -> raise (Runtime_error "Cannot convert empty matrix to float")
       | _ -> raise (Runtime_error "Cannot convert multi-element matrix to float"))
  | VVoid -> 
      raise (Runtime_error "Cannot convert void to float")

let expected_type = ref None
let parse_vector_input str =
  try
    (* Format: size[elem1,elem2,...] *)
    let size_start = 0 in
    let bracket_start = String.index str '[' in
    let bracket_end = String.rindex str ']' in
    
    (* Parse size *)
    let size = int_of_string (String.sub str size_start (bracket_start - size_start)) in
    
    (* Parse elements *)
    let elements_str = String.sub str (bracket_start + 1) (bracket_end - bracket_start - 1) in
    let element_strs = String.split_on_char ',' elements_str in
    
    (* Convert elements to values *)
    let elements = List.map (fun s -> 
      try VFloat (float_of_string (String.trim s))
      with _ -> raise (Runtime_error ("Invalid vector element: " ^ s))
    ) element_strs in
    
    (* Verify size matches *)
    if List.length elements <> size then
      raise (Runtime_error (Printf.sprintf "Vector size mismatch: declared %d but got %d elements" 
                          size (List.length elements)))
    else
      VVector elements
  with
  | Not_found -> raise (Runtime_error "Invalid vector format. Expected: size[elem1,elem2,...]")
  | Failure _ -> raise (Runtime_error "Invalid number format in vector")

let parse_matrix_input str =
  try
    (* Format: rows,cols[[elem1,elem2],[elem3,elem4]] *)
    let comma_pos = String.index str ',' in
    let first_bracket = String.index str '[' in
    
    (* Parse dimensions *)
    let rows = int_of_string (String.sub str 0 comma_pos) in
    let cols = int_of_string (String.sub str (comma_pos + 1) (first_bracket - comma_pos - 1)) in
    
    (* Extract the content between the outer brackets *)
    let content = String.sub str (first_bracket + 1) 
                   (String.length str - first_bracket - 2) in
    
    (* Split into rows (by ],[) *)
    let row_strs = String.split_on_char ']' content in
    let row_strs = List.filter (fun s -> String.length s > 0) 
                    (List.map (fun s -> String.trim (String.trim s)) row_strs) in
    
    (* Process each row *)
    let matrix = List.map (fun row_str ->
      (* Remove the leading [ if present *)
      let row_str = if String.contains row_str '[' then
                      String.sub row_str 
                        (String.index row_str '[' + 1)
                        (String.length row_str - String.index row_str '[' - 1)
                    else row_str in
      (* Split into elements *)
      let elements = String.split_on_char ',' row_str in
      List.map (fun elem ->
        let elem = String.trim elem in
        try 
          (* Try parsing as float first *)
          VFloat (float_of_string elem)
        with _ -> 
          raise (Runtime_error ("Invalid matrix element: " ^ elem))
      ) elements
    ) row_strs in
    
    (* Verify dimensions *)
    if List.length matrix <> rows then
      raise (Runtime_error (Printf.sprintf "Matrix row count mismatch: declared %d but got %d rows" 
                          rows (List.length matrix)))
    else if List.exists (fun row -> List.length row <> cols) matrix then
      raise (Runtime_error (Printf.sprintf "Matrix column count mismatch: all rows must have %d columns" cols))
    else
      VMatrix matrix
  with
  | Not_found -> raise (Runtime_error "Invalid matrix format. Expected: rows,cols[[elem1,elem2],[elem3,elem4]]")
  | Failure _ -> raise (Runtime_error "Invalid number format in matrix")
  
let convert_input_string type_name input_str =
  try
    match type_name with
    | "int" -> 
        VInt (int_of_string input_str)
    | "float" -> 
        VFloat (float_of_string input_str)
    | "bool" ->
        let lower_input = String.lowercase_ascii input_str in
        if lower_input = "true" then VBool true
        else if lower_input = "false" then VBool false
        else raise (Runtime_error "Invalid boolean input (use 'true' or 'false')")
    | "string" -> 
        VString input_str
    | "vector" ->
        parse_vector_input input_str
    | "matrix" ->
        parse_matrix_input input_str
    | _ -> 
        raise (Runtime_error ("Unsupported type for input conversion: " ^ type_name))
  with
  | Runtime_error msg -> raise (Runtime_error msg)
  | _ -> raise (Runtime_error ("Invalid input format for type " ^ type_name))
let safe_float_of_value v msg =
  try float_of_value v
  with Runtime_error e -> raise (Runtime_error (msg ^ ": " ^ e))

(* Helper function for numeric operations *)
let numeric_to_float = function
  | VInt i -> float_of_int i
  | VFloat f -> f
  | v -> raise (Runtime_error ("Expected numeric value, got " ^ string_of_value v))
let convert_element_to_float elem =
  match elem with
  | VInt i -> float_of_int i
  | VFloat f -> f
  | _ -> raise (Runtime_error ("Cannot convert " ^ string_of_value elem ^ " to float"))

(* Helper function for safe numeric conversion *)
let safe_numeric_conversion v =
  match v with
  | VInt _ | VFloat _ -> float_of_value v
  | _ -> raise (Runtime_error ("Expected numeric value, got " ^ string_of_value v))

(* Helper function for matrix element conversion *)
let convert_matrix_element_to_float elem =
  try float_of_value elem
  with Runtime_error msg ->
    raise (Runtime_error ("Invalid matrix element: " ^ msg))

(* Add these at the top of the file *)
let read_vector_input () =
  try
    let input_str = read_line() in
    match parse_vector_input input_str with
    | VVector elements -> elements  (* Return just the list of elements *)
    | _ -> raise (Runtime_error "Invalid vector input")
  with
  | Failure _ -> raise (Runtime_error "Invalid vector input")
  | End_of_file -> raise (Runtime_error "Unexpected end of input")


let read_matrix_input () =
  try
    let input_str = read_line() in
    match parse_matrix_input input_str with
    | VMatrix elements -> elements  (* Return just the list of lists of elements *)
    | _ -> raise (Runtime_error "Invalid matrix input")
  with
  | Failure _ -> raise (Runtime_error "Invalid input for matrix")
  | End_of_file -> raise (Runtime_error "Unexpected end of input")
let matrix_inverse matrix =
  match matrix with
  | VMatrix m ->
      if List.length m <> List.length (List.hd m) then
        raise (Runtime_error "Matrix inverse requires square matrix")
      else
        let n = List.length m in
        
        (* Convert all elements to float for consistent calculation *)
        let float_matrix = List.map (fun row ->
          List.map (fun elem ->
            match elem with
            | VInt i -> VFloat (float_of_int i)
            | VFloat f -> VFloat f
            | _ -> raise (Runtime_error "Matrix elements must be numeric")
          ) row
        ) m in
        
        (* Calculate determinant *)
        let rec det matrix =
          match matrix with
          | [[VFloat f]] -> f
          | [[VFloat a; VFloat b]; [VFloat c; VFloat d]] -> 
              a *. d -. b *. c
          | _ ->
              let n = List.length matrix in
              let first_row = List.hd matrix in
              let rest = List.tl matrix in
              List.fold_left (fun acc j ->
                let sub = List.map (fun row ->
                  List.filteri (fun i _ -> i <> j) row
                ) rest in
                let sign = if j mod 2 = 0 then 1.0 else -1.0 in
                match List.nth first_row j with
                | VFloat x -> acc +. sign *. x *. (det sub)
                | _ -> raise (Runtime_error "Invalid matrix element in determinant")
              ) 0.0 (List.init n (fun x -> x))
        in
        
        let det_val = det float_matrix in
        if det_val = 0.0 then
          raise (Runtime_error "Matrix is not invertible (determinant is zero)")
        else
          (* Calculate cofactor matrix *)
          let cofactor_matrix = List.mapi (fun i row ->
            List.mapi (fun j _ ->
              (* Create submatrix by removing row i and column j *)
              let sub = List.filteri (fun k _ -> k <> i) float_matrix |>
                        List.map (fun row -> List.filteri (fun k _ -> k <> j) row) in
              let sign = if (i + j) mod 2 = 0 then 1.0 else -1.0 in
              VFloat (sign *. (det sub))
            ) row
          ) float_matrix in
          
          (* Transpose cofactor matrix - inline implementation *)
          let rows = List.length cofactor_matrix in
          let cols = List.length (List.hd cofactor_matrix) in
          let transposed = Array.make_matrix cols rows (List.hd (List.hd cofactor_matrix)) in
          List.iteri (fun i row ->
            List.iteri (fun j elem ->
              transposed.(j).(i) <- elem
            ) row
          ) cofactor_matrix;
          let adjugate = List.map Array.to_list (Array.to_list transposed) in
          
          (* Multiply by 1/det *)
          VMatrix (List.map (fun row ->
            List.map (fun elem ->
              match elem with
              | VFloat f -> VFloat (f /. det_val)
              | _ -> raise (Runtime_error "Invalid matrix element")
            ) row
          ) adjugate)
  | _ -> raise (Runtime_error "Cannot compute inverse of non-matrix value")
(* Environment to store variable values *)
module Env = Map.Make(String)
type environment = value Env.t

(* Convert values to strings for printing *)


(* Helper functions for matrix operations *)
let matrix_transpose matrix =
  match matrix with
  | VMatrix m ->
      if m = [] then VMatrix []
      else
        let rows = List.length m in
        let cols = List.length (List.hd m) in
        let transposed = Array.make_matrix cols rows (List.hd (List.hd m)) in
        List.iteri (fun i row ->
          List.iteri (fun j elem ->
            transposed.(j).(i) <- elem
          ) row
        ) m;
        VMatrix (List.map Array.to_list (Array.to_list transposed))
  | _ -> raise (Runtime_error "Cannot transpose non-matrix value")

let matrix_determinant matrix =
  let rec det m =
    match m with
    | [[x]] -> x
    | _ ->
        let n = List.length m in
        let first_row = List.hd m in
        let rest = List.tl m in
        List.fold_left (fun acc j ->
          let sub = List.map (fun row ->
            List.filteri (fun i _ -> i <> j) row
          ) rest in
          match List.nth first_row j with
          | VFloat x -> VFloat (x *. (float_of_value (det sub)))
          | _ -> raise (Runtime_error "Non-float in determinant calculation")
        ) (VFloat 0.0) (List.init n (fun x -> x))
  in
  match matrix with
  | VMatrix m ->
      if List.length m <> List.length (List.hd m) then
        raise (Runtime_error "Determinant requires square matrix")
      else
        det m
  | _ -> raise (Runtime_error "Cannot compute determinant of non-matrix value")

let rec eval_unop op v =
  match op with
  | Neg -> 
      (match v with
       | VInt i -> VInt (-i)
       | VFloat f -> VFloat (-.f)
       | _ -> raise (Runtime_error "Negation requires numeric type"))

  | Not ->
      (match v with
       | VBool b -> VBool (not b)
       | _ -> raise (Runtime_error "Logical NOT requires boolean type"))

  | Abs ->
      (match v with
       | VInt i -> VInt (abs i)
       | VFloat f -> VFloat (abs_float f)
       | _ -> raise (Runtime_error "Absolute value requires numeric type"))

  | Transpose ->
      (match v with
       | VMatrix m -> 
          if m = [] then VMatrix []
          else
            let rows = List.length m in
            let cols = List.length (List.hd m) in
            let transposed = Array.make_matrix cols rows (List.hd (List.hd m)) in
            List.iteri (fun i row ->
              List.iteri (fun j elem ->
                transposed.(j).(i) <- elem
              ) row
            ) m;
            VMatrix (List.map Array.to_list (Array.to_list transposed))
       | _ -> raise (Runtime_error "Transpose operation requires matrix type"))

  | Det ->
    (match v with
     | VMatrix m ->
         if List.length m <> List.length (List.hd m) then
           raise (Runtime_error "Determinant requires square matrix")
         else
           let rec det_helper matrix =
             match matrix with
             | [[x]] -> 
                 (match x with
                  | VFloat f -> VFloat f
                  | VInt i -> VFloat (float_of_int i)
                  | _ -> raise (Runtime_error "Matrix elements must be numeric"))
             | [[a; b]; [c; d]] ->  (* Special case for 2x2 matrix *)
                 let get_num v = match v with
                   | VFloat f -> f
                   | VInt i -> float_of_int i
                   | _ -> raise (Runtime_error "Matrix elements must be numeric")
                 in
                 let det_2x2 = (get_num a) *. (get_num d) -. (get_num b) *. (get_num c) in
                 VFloat det_2x2
             | _ ->
                 let n = List.length matrix in
                 let first_row = List.hd matrix in
                 let rest = List.tl matrix in
                 List.fold_left (fun acc j ->
                   let sub = List.map (fun row ->
                     List.filteri (fun i _ -> i <> j) row
                   ) rest in
                   let sign = if j mod 2 = 0 then 1.0 else -1.0 in  (* Add alternating sign *)
                   match List.nth first_row j, acc with
                   | VFloat x, VFloat acc_val -> 
                       let sub_det = det_helper sub in
                       (match sub_det with
                        | VFloat d -> VFloat (acc_val +. sign *. x *. d)
                        | _ -> raise (Runtime_error "Invalid determinant calculation"))
                   | VInt x, VFloat acc_val ->
                       let sub_det = det_helper sub in
                       (match sub_det with
                        | VFloat d -> VFloat (acc_val +. sign *. (float_of_int x) *. d)
                        | _ -> raise (Runtime_error "Invalid determinant calculation"))
                   | _ -> raise (Runtime_error "Matrix elements must be numeric")
                 ) (VFloat 0.0) (List.init n (fun x -> x))
           in
           det_helper m
     | _ -> raise (Runtime_error "Determinant operation requires matrix type"))
  
  | Mag ->
      (match v with
       | VVector vec ->
           let squared_sum = List.fold_left (fun acc elem ->
             match acc, elem with
             | VFloat acc', VFloat x -> VFloat (acc' +. (x *. x))
             | VFloat acc', VInt x -> 
                 let fx = float_of_int x in
                 VFloat (acc' +. (fx *. fx))
             | VInt acc', VFloat x -> 
                 let facc = float_of_int acc' in
                 VFloat (facc +. (x *. x))
             | VInt acc', VInt x -> 
                 let facc = float_of_int acc' in
                 let fx = float_of_int x in
                 VFloat (facc +. (fx *. fx))
             | _ -> raise (Runtime_error "Invalid vector element type in magnitude calculation")
           ) (VFloat 0.0) vec in
           match squared_sum with
           | VFloat sum -> VFloat (sqrt sum)
           | _ -> raise (Runtime_error "Invalid magnitude calculation")
       | _ -> raise (Runtime_error "Magnitude operation requires vector type"))

  

  | Dim ->
      (match v with
       | VVector vec -> 
           VInt (List.length vec)
       | VMatrix m -> 
        match m with
        | [] -> VVector []
        | row::_ -> 
            let rows = List.length m in
            let cols = List.length row in
            VVector [VInt rows; VInt cols]
       | _ -> raise (Runtime_error "Dimension operation requires vector or matrix type"))
    | Inverse ->
    match v with
    | VMatrix _ -> matrix_inverse v
    | _ -> raise (Runtime_error "Inverse operation requires matrix type")
(* Main evaluation functions *)

and eval_expr env = function
  | Int i -> VInt i
  | Float f -> VFloat f
  | Bool b -> VBool b
  | String s -> VString s
  | Var x -> 
      (try Env.find x env
       with Not_found -> 
         raise (Runtime_error ("Undefined variable: " ^ x)))
  
  | Vector(size, _, elements) ->
      let evaluated_elements = 
        List.map (eval_expr env) elements in
      VVector evaluated_elements

   | Matrix(rows, cols, _, elements) ->
      let evaluated_elements = 
        List.map (List.map (eval_expr env)) elements in
      (* Verify all elements are numeric (int or float) *)
      List.iter (fun row ->
        List.iter (fun elem ->
          match elem with
          | VInt _ | VFloat _ -> ()
          | _ -> raise (Runtime_error "Matrix elements must be numeric (int or float)")
        ) row
      ) evaluated_elements;
      VMatrix evaluated_elements

  | BinOp(op, e1, e2) ->
      let v1 = eval_expr env e1 in
      let v2 = eval_expr env e2 in
      eval_binop op v1 v2

  | UnOp(op, e) ->
      let v = eval_expr env e in
      eval_unop op v

  | VectorAccess(var, index) ->
      let vector = eval_expr env (Var var) in
      let idx = eval_expr env index in
      (match vector, idx with
       | VVector vs, VInt i ->
           if i < 0 || i >= List.length vs then
             raise (Runtime_error "Vector index out of bounds")
           else
             List.nth vs i
       | _ -> raise (Runtime_error "Invalid vector access"))

  | MatrixAccess(var, row, col) ->
      let matrix = eval_expr env (Var var) in
      let r = eval_expr env row in
      let c = eval_expr env col in
      (match matrix, r, c with
       | VMatrix ms, VInt i, VInt j ->
           if i < 0 || i >= List.length ms then
             raise (Runtime_error "Matrix row index out of bounds")
           else
             let row = List.nth ms i in
             if j < 0 || j >= List.length row then
               raise (Runtime_error "Matrix column index out of bounds")
             else
               List.nth row j
       | _ -> raise (Runtime_error "Invalid matrix access"))

  | Input(prompt) ->
    (match prompt with
     | Some msg -> 
         Printf.printf "%s" msg;
         flush stdout
     | None -> ());
    (match !expected_type with
     | Some "vector" -> VVector (read_vector_input ())
     | Some "matrix" -> VMatrix (read_matrix_input ())
     | Some type_name ->
         let input_str = read_line() in
         convert_input_string type_name input_str
     | None -> 
         VString (read_line()))  (* Default to string if no type context *)
  | InputFile filename ->
    try
        let content = read_file_content filename in
        let trimmed_content = String.trim content in
        match !expected_type with
        | Some "bool" ->
            let lower_content = String.lowercase_ascii trimmed_content in
            if lower_content = "true" then VBool true
            else if lower_content = "false" then VBool false
            else raise (Runtime_error ("Invalid boolean in file '" ^ filename ^ "': use 'true' or 'false'"))
        | Some "int" ->
            (try VInt (int_of_string trimmed_content)
             with Failure _ -> 
                raise (Runtime_error ("Invalid integer in file '" ^ filename ^ "': " ^ trimmed_content)))
        | Some "float" ->
            (try VFloat (float_of_string trimmed_content)
             with Failure _ -> 
                raise (Runtime_error ("Invalid float in file '" ^ filename ^ "': " ^ trimmed_content)))
        | Some "string" ->
            VString content  (* Don't trim strings to preserve formatting *)
        | Some "vector" ->
            (try parse_vector_input trimmed_content
             with Runtime_error msg -> 
                raise (Runtime_error ("Invalid vector in file '" ^ filename ^ "': " ^ msg)))
        | Some "matrix" ->
            (try parse_matrix_input trimmed_content
             with Runtime_error msg -> 
                raise (Runtime_error ("Invalid matrix in file '" ^ filename ^ "': " ^ msg)))
        | Some t ->
            raise (Runtime_error ("Unsupported type for file input: " ^ t))
        | None ->
            VString content  (* Default to string if no type specified *)
    with
    | Sys_error _ -> 
        raise (Runtime_error ("Could not read file: " ^ filename))
    | Runtime_error msg -> 
        raise (Runtime_error msg)
    | Failure msg -> 
        raise (Runtime_error ("Error reading file '" ^ filename ^ "': " ^ msg))
and eval_binop op v1 v2 =
  match op, v1, v2 with
  (* Arithmetic operations for integers *)
  | Add, VInt i1, VInt i2 -> VInt (i1 + i2)
  | Sub, VInt i1, VInt i2 -> VInt (i1 - i2)
  | Mul, VInt i1, VInt i2 -> VInt (i1 * i2)
  | Div, VInt i1, VInt i2 -> 
      if i2 = 0 then raise (Runtime_error "Division by zero")
      else VInt (i1 / i2)
  | Mod, VInt i1, VInt i2 ->
      if i2 = 0 then raise (Runtime_error "Modulo by zero")
      else VInt (i1 mod i2)

  (* Arithmetic operations for floats *)
  | Add, VFloat f1, VFloat f2 -> VFloat (f1 +. f2)
  | Sub, VFloat f1, VFloat f2 -> VFloat (f1 -. f2)
  | Mul, VFloat f1, VFloat f2 -> VFloat (f1 *. f2)
  | Div, VFloat f1, VFloat f2 ->
      if f2 = 0.0 then raise (Runtime_error "Division by zero")
      else VFloat (f1 /. f2)

  (* Type promotion: int to float *)
  | Add, VInt i1, VFloat f2 -> VFloat ((float_of_int i1) +. f2)
  | Add, VFloat f1, VInt i2 -> VFloat (f1 +. (float_of_int i2))
  | Sub, VInt i1, VFloat f2 -> VFloat ((float_of_int i1) -. f2)
  | Sub, VFloat f1, VInt i2 -> VFloat (f1 -. (float_of_int i2))
  | Mul, VInt i1, VFloat f2 -> VFloat ((float_of_int i1) *. f2)
  | Mul, VFloat f1, VInt i2 -> VFloat (f1 *. (float_of_int i2))
  | Div, VInt i1, VFloat f2 ->
      if f2 = 0.0 then raise (Runtime_error "Division by zero")
      else VFloat ((float_of_int i1) /. f2)
  | Div, VFloat f1, VInt i2 ->
      if i2 = 0 then raise (Runtime_error "Division by zero")
      else VFloat (f1 /. (float_of_int i2))

  (* Boolean operations *)
  | And, VBool b1, VBool b2 -> VBool (b1 && b2)
  | Or, VBool b1, VBool b2 -> VBool (b1 || b2)

  (* Comparison operations for integers *)
  | Eq, VInt i1, VInt i2 -> VBool (i1 = i2)
  | Neq, VInt i1, VInt i2 -> VBool (i1 <> i2)
  | Lt, VInt i1, VInt i2 -> VBool (i1 < i2)
  | Le, VInt i1, VInt i2 -> VBool (i1 <= i2)
  | Gt, VInt i1, VInt i2 -> VBool (i1 > i2)
  | Ge, VInt i1, VInt i2 -> VBool (i1 >= i2)

  (* Comparison operations for floats *)
  | Eq, VFloat f1, VFloat f2 -> VBool (f1 = f2)
  | Neq, VFloat f1, VFloat f2 -> VBool (f1 <> f2)
  | Lt, VFloat f1, VFloat f2 -> VBool (f1 < f2)
  | Le, VFloat f1, VFloat f2 -> VBool (f1 <= f2)
  | Gt, VFloat f1, VFloat f2 -> VBool (f1 > f2)
  | Ge, VFloat f1, VFloat f2 -> VBool (f1 >= f2)
  (* Add to eval_binop *)
  (* String comparisons *)
  | Eq, VString s1, VString s2 -> VBool (s1 = s2)
  | Neq, VString s1, VString s2 -> VBool (s1 <> s2)
  | Lt, VString s1, VString s2 -> VBool (s1 < s2)
  | Le, VString s1, VString s2 -> VBool (s1 <= s2)
  | Gt, VString s1, VString s2 -> VBool (s1 > s2)
  | Ge, VString s1, VString s2 -> VBool (s1 >= s2)
  | Eq, VInt i1, VFloat f2 -> VBool (float_of_int i1 = f2)
  | Eq, VFloat f1, VInt i2 -> VBool (f1 = float_of_int i2)
  | Neq, VInt i1, VFloat f2 -> VBool (float_of_int i1 <> f2)
  | Neq, VFloat f1, VInt i2 -> VBool (f1 <> float_of_int i2)
    (* Mixed numeric comparisons *)
  | Eq, VInt i1, VFloat f2 -> VBool (float_of_int i1 = f2)
  | Eq, VFloat f1, VInt i2 -> VBool (f1 = float_of_int i2)
  | Neq, VInt i1, VFloat f2 -> VBool (float_of_int i1 <> f2)
  | Neq, VFloat f1, VInt i2 -> VBool (f1 <> float_of_int i2)
  (* Add similar cases for Lt, Le, Gt, Ge *)

  (* Vector operations *)
  | VectorAdd, VVector v1, VVector v2 ->
      if List.length v1 <> List.length v2 then
        raise (Runtime_error "Vector addition requires vectors of same size")
      else
        VVector (List.map2 (fun x y -> 
          match x, y with
          | VFloat f1, VFloat f2 -> VFloat (f1 +. f2)
          | VInt i1, VInt i2 -> VInt (i1 + i2)
          | VFloat f1, VInt i2 -> VFloat (f1 +. float_of_int i2)
          | VInt i1, VFloat f2 -> VFloat (float_of_int i1 +. f2)
          | _ -> raise (Runtime_error "Invalid vector element types")
        ) v1 v2)

  | VectorScalarMult, VVector v, VFloat f ->
      VVector (List.map (fun x ->
        match x with
        | VFloat f1 -> VFloat (f1 *. f)
        | VInt i -> VFloat (float_of_int i *. f)
        | _ -> raise (Runtime_error "Invalid vector element type")
      ) v)
  | VectorScalarMult, VFloat f, VVector v ->
      VVector (List.map (fun x ->
        match x with
        | VFloat f1 -> VFloat (f *. f1)
        | VInt i -> VFloat (f *. float_of_int i)
        | _ -> raise (Runtime_error "Invalid vector element type")
      ) v)

  | DotProduct, VVector v1, VVector v2 ->
      if List.length v1 <> List.length v2 then
        raise (Runtime_error "Dot product requires vectors of same size")
      else
        let products = List.map2 (fun x y ->
          match x, y with
          | VFloat f1, VFloat f2 -> f1 *. f2
          | VInt i1, VInt i2 -> float_of_int (i1 * i2)
          | VFloat f1, VInt i2 -> f1 *. float_of_int i2
          | VInt i1, VFloat f2 -> float_of_int i1 *. f2
          | _ -> raise (Runtime_error "Invalid vector element types")
        ) v1 v2 in
        VFloat (List.fold_left (+.) 0.0 products)

  | Angle, VVector v1, VVector v2 ->
    if List.length v1 <> List.length v2 then
      raise (Runtime_error "Vectors must be same size for angle calculation");
    let dot = eval_binop DotProduct (VVector v1) (VVector v2) in
    let mag1 = eval_unop Mag (VVector v1) in
    let mag2 = eval_unop Mag (VVector v2) in
    (match dot, mag1, mag2 with
     | VFloat d, VFloat m1, VFloat m2 ->
         if m1 = 0.0 || m2 = 0.0 then
           raise (Runtime_error "Cannot compute angle with zero vector")
         else
           VFloat (acos (d /. (m1 *. m2)))
     | _ -> raise (Runtime_error "Invalid vector operation"))
  (* Matrix operations *)
  | MatrixAdd, VMatrix m1, VMatrix m2 ->
      if List.length m1 <> List.length m2 then
        raise (Runtime_error "Matrix addition requires matrices of same dimensions")
      else if List.length m1 = 0 then
        VMatrix []
      else if List.length (List.hd m1) <> List.length (List.hd m2) then
        raise (Runtime_error "Matrix addition requires matrices of same dimensions")
      else
        VMatrix (List.map2 (fun row1 row2 ->
          List.map2 (fun x y ->
            match x, y with
            | VFloat f1, VFloat f2 -> VFloat (f1 +. f2)
            | VInt i1, VInt i2 -> VInt (i1 + i2)
            | VFloat f1, VInt i2 -> VFloat (f1 +. float_of_int i2)
            | VInt i1, VFloat f2 -> VFloat (float_of_int i1 +. f2)
            | _ -> raise (Runtime_error "Invalid matrix element types")
          ) row1 row2
        ) m1 m2)

  | MatrixMult, VMatrix m1, VMatrix m2 ->
      if List.length m1 = 0 || List.length m2 = 0 then
        VMatrix []
      else if List.length (List.hd m1) <> List.length m2 then
        raise (Runtime_error "Invalid matrix multiplication dimensions")
      else
        let cols2 = List.length (List.hd m2) in
        let m2_trans = match matrix_transpose (VMatrix m2) with
          | VMatrix mt -> mt
          | _ -> raise (Runtime_error "Matrix transpose failed") in
        VMatrix (List.map (fun row1 ->
          List.map (fun col2 ->
            match eval_binop DotProduct (VVector row1) (VVector col2) with
            | VFloat f -> VFloat f
            | _ -> raise (Runtime_error "Invalid matrix multiplication")
          ) m2_trans
        ) m1)

  | MatrixScalarMult, VMatrix m, VFloat f ->
      VMatrix (List.map (fun row ->
        List.map (fun x ->
          match x with
          | VFloat f1 -> VFloat (f1 *. f)
          | VInt i -> VFloat (float_of_int i *. f)
          | _ -> raise (Runtime_error "Invalid matrix element type")
        ) row
      ) m)
  | MatrixScalarMult, VFloat f, VMatrix m ->
      VMatrix (List.map (fun row ->
        List.map (fun x ->
          match x with
          | VFloat f1 -> VFloat (f *. f1)
          | VInt i -> VFloat (f *. float_of_int i)
          | _ -> raise (Runtime_error "Invalid matrix element type")
        ) row
      ) m)

  (* Error cases *)
  | _ -> raise (Runtime_error "Invalid binary operation")

let read_file_content filename =
  try
    let chan = open_in filename in
    let content = really_input_string chan (in_channel_length chan) in
    close_in chan;
    content
  with 
  | Sys_error msg -> raise (Runtime_error ("File error: " ^ msg))
  | End_of_file -> raise (Runtime_error ("Unexpected end of file: " ^ filename))
let parse_file_content content type_name =
  try
    match type_name with
    | "bool" ->
        let lower_content = String.lowercase_ascii content in
        if lower_content = "true" then VBool true
        else if lower_content = "false" then VBool false
        else raise (Runtime_error "Invalid boolean in file (use 'true' or 'false')")
    | "int" -> 
        VInt (int_of_string content)
    | "float" -> 
        VFloat (float_of_string content)
    | "string" -> 
        VString content
    | "vector" ->
        parse_vector_input content
    | "matrix" ->
        parse_matrix_input content
    | _ -> 
        raise (Runtime_error ("Unsupported type for file input: " ^ type_name))
  with
  | Runtime_error msg -> raise (Runtime_error msg)
  | Failure _ -> raise (Runtime_error ("Invalid format in file for type " ^ type_name))

let rec eval_stmt env = function
  | Seq stmts ->
      List.fold_left eval_stmt env stmts

  | Decl(type_name, var, expr) ->
    expected_type := Some type_name;
    let value = eval_expr env expr in
    expected_type := None;
    Env.add var value env

  | Assign(var, expr) ->
    let var_type = 
      match Env.find var env with
      | VInt _ -> Some "int"
      | VFloat _ -> Some "float"
      | VBool _ -> Some "bool"
      | VString _ -> Some "string"
      | VVector _ -> Some "vector"
      | VMatrix _ -> Some "matrix"
      | _ -> None
    in
    expected_type := var_type;
    let value = eval_expr env expr in
    expected_type := None;
    Env.add var value env

  | If(cond, then_stmt, else_stmt_opt) ->
      (match eval_expr env cond with
       | VBool true -> eval_stmt env then_stmt
       | VBool false ->
           (match else_stmt_opt with
            | Some stmt -> eval_stmt env stmt
            | None -> env)
       | _ -> raise (Runtime_error "Non-boolean condition in if statement"))

  | While(cond, body) ->
      let rec loop env =
        match eval_expr env cond with
        | VBool true ->
            let new_env = eval_stmt env body in
            loop new_env
        | VBool false -> env
        | _ -> raise (Runtime_error "Non-boolean condition in while loop")
      in loop env

  | For(var, init, cond, incr, body) ->
    let env' = eval_stmt env (Decl("int", var, init)) in
    let rec loop env =
      match eval_expr env cond with
      | VBool true ->
          let env_after_body = eval_stmt env body in
          let env_after_incr = eval_stmt env_after_body incr in  (* Fixed: using env_after_body instead of env_after_incr *)
          loop env_after_incr
      | VBool false -> env
      | _ -> raise (Runtime_error "Non-boolean condition in for loop")
    in loop env'

  | Print expr ->
      let value = eval_expr env expr in
      let () = printf "%s\n" (string_of_value value) in
      env

  | PrintInt expr ->
      let value = eval_expr env expr in
      (match value with
       | VInt i -> 
           let () = printf "%d\n" i in
           env
       | _ -> raise (Runtime_error "Expected integer for print_int"))

  | PrintFloat expr ->
      let value = eval_expr env expr in
      (match value with
       | VFloat f -> 
           let () = printf "%f\n" f in
           env
       | _ -> raise (Runtime_error "Expected float for print_float"))

  | PrintVector expr ->
      let value = eval_expr env expr in
      (match value with
       | VVector v -> 
           let () = printf "%s\n" (string_of_value (VVector v)) in
           env
       | _ -> raise (Runtime_error "Expected vector for print_vector"))

  | PrintMatrix expr ->
      let value = eval_expr env expr in
      (match value with
       | VMatrix m -> 
           let () = printf "%s\n" (string_of_value (VMatrix m)) in
           env
       | _ -> raise (Runtime_error "Expected matrix for print_matrix"))

  | Input _ | InputInt | InputFloat | InputVector | InputMatrix ->
      env  (* These are handled in eval_expr *)

  | InputFile filename ->
      let content = read_file_content filename in
      (match !expected_type with
       | Some type_name -> 
           let value = parse_file_content content type_name in
           Env.add "_file_content" value env
       | None -> 
           (* Default to string if no type is specified *)
           Env.add "_file_content" (VString content) env)
  | PrintFile(filename, expr) ->
      let value = eval_expr env expr in
      let content = string_of_value value in
      (try
        let chan = open_out filename in
        try
          output_string chan content;
          close_out chan;
          env
        with e ->
          close_out chan;
          raise (Runtime_error ("Error writing to file: " ^ Printexc.to_string e))
      with _ -> 
        raise (Runtime_error ("Could not open file for writing: " ^ filename)))

  | VectorDecl(var, expr) ->
    expected_type := Some "vector";  (* Set the expected type to vector *)
    let value = eval_expr env expr in
    expected_type := None;
    (match value with
     | VVector _ -> Env.add var value env
     | VString s -> 
         (* Try to parse the string as a vector *)
         let vector_value = parse_vector_input s in
         Env.add var vector_value env
     | _ -> raise (Runtime_error "Expected vector value in vector declaration"))
  | MatrixDecl(var, expr) ->
    expected_type := Some "matrix";  (* Set the expected type to matrix *)
    let value = eval_expr env expr in
    expected_type := None;
    (match value with
     | VMatrix _ -> Env.add var value env
     | VString s -> 
         (* Try to parse the string as a matrix *)
         let matrix_value = parse_matrix_input s in
         Env.add var matrix_value env
     | _ -> raise (Runtime_error "Expected matrix value in matrix declaration"))
  | VectorElementAssign(var, index_expr, value_expr) ->
      let vector = 
        try Env.find var env
        with Not_found -> raise (Runtime_error ("Undefined vector: " ^ var))
      in
      let index = eval_expr env index_expr in
      let new_value = eval_expr env value_expr in
      (match vector, index with
       | VVector elements, VInt i ->
           if i < 0 || i >= List.length elements then
             raise (Runtime_error "Vector index out of bounds")
           else
             let new_elements = 
               List.mapi (fun j x -> if j = i then new_value else x) elements
             in
             Env.add var (VVector new_elements) env
       | _ -> raise (Runtime_error "Invalid vector element assignment"))
  | MatrixElementAssign(var, row_expr, col_expr, value_expr) ->
      let matrix = 
        try Env.find var env
        with Not_found -> raise (Runtime_error ("Undefined matrix: " ^ var))
      in
      let row = eval_expr env row_expr in
      let col = eval_expr env col_expr in
      let new_value = eval_expr env value_expr in
      (match matrix, row, col with
       | VMatrix elements, VInt i, VInt j ->
           if i < 0 || i >= List.length elements then
             raise (Runtime_error "Matrix row index out of bounds")
           else if j < 0 || j >= List.length (List.nth elements i) then
             raise (Runtime_error "Matrix column index out of bounds")
           else
             let new_elements = 
               List.mapi (fun r row ->
                 if r = i then
                   List.mapi (fun c x -> if c = j then new_value else x) row
                 else row
               ) elements
             in
             Env.add var (VMatrix new_elements) env
       | _ -> raise (Runtime_error "Invalid matrix element assignment"))

(* In interpreter.ml *)
let interpret (program : Ast.stmt list) =
  let env = Env.empty in
  try
    let final_env = List.fold_left eval_stmt env program in
    printf "Program executed successfully\n";
    final_env
  with
  | Runtime_error msg ->
      printf "Runtime error: %s\n" msg;
      exit 1
  | Division_by_zero ->
      printf "Runtime error: Division by zero\n";
      exit 1
  | _ ->
      printf "Unknown runtime error\n";
      exit 1