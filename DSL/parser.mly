%{
open Ast
open Printf
%}

%token <int> INT
%token <float> FLOAT
%token <string> STRING IDENT
%token INPUT PRINT
%token IF THEN ELSE FOR WHILE
%token TRUE FALSE
%token BOOL_TYPE INT_TYPE FLOAT_TYPE STRING_TYPE VECTOR_TYPE MATRIX_TYPE
%token INPUT_VECTOR INPUT_MATRIX INPUT_INT INPUT_FLOAT
%token PRINT_VECTOR PRINT_MATRIX PRINT_INT PRINT_FLOAT
%token VECTOR_INT VECTOR_FLOAT MATRIX_INT MATRIX_FLOAT
%token <string> INPUT_FILE PRINT_FILE
%token NOT AND OR ABS
%token PLUS MINUS TIMES DIVIDE REM
%token EQ NEQ LT LTE GT GTE
%token ASSIGN
%token DOT_PROD ANGLE MAG DIM
%token VECTOR_ADD VECTOR_SCALAR_MULT
%token MATRIX_ADD MATRIX_MULT MATRIX_SCALAR_MULT
%token TRANSPOSE DET INVERSE
%token SEMICOLON COMMA
%token LPAREN RPAREN LBRACE RBRACE LBRACKET RBRACKET
%token <string> INVALID_ASSIGN
%token OUTPUT
%token EOF

/* Operator precedence and associativity */
%right ASSIGN
%left OR
%left AND
%right NOT
%left EQ NEQ
%left LT LTE GT GTE
%left PLUS MINUS VECTOR_ADD MATRIX_ADD
%left DOT_PROD ANGLE
%left TIMES DIVIDE REM VECTOR_SCALAR_MULT MATRIX_SCALAR_MULT
%left MATRIX_MULT
%right UMINUS
%right TRANSPOSE
%right DET MAG DIM ABS
%nonassoc IDENT LPAREN

%start program
%type <Ast.program> program

%%

program:
| stmt_list EOF { $1 }
| error {
    let pos = Parsing.symbol_start_pos () in
    raise (Failure ("Syntax error at line " ^
    string_of_int pos.pos_lnum ^
    ", character " ^
    string_of_int (pos.pos_cnum - pos.pos_bol + 1)))
}
;

stmt_list:
| stmt { [$1] }
| stmt stmt_list { $1 :: $2 }
;

stmt:
/* Control Structures */
| IF expr THEN LBRACE stmt_list RBRACE
    { If($2, Seq($5), None) }
| IF expr THEN LBRACE stmt_list RBRACE ELSE LBRACE stmt_list RBRACE
    { If($2, Seq($5), Some(Seq($9))) }
| WHILE expr LBRACE stmt_list RBRACE
    { While($2, Seq($4)) }
| FOR LPAREN IDENT ASSIGN expr SEMICOLON expr SEMICOLON IDENT ASSIGN expr RPAREN LBRACE stmt_list RBRACE
    { For($3, $5, $7, Assign($9, $11), Seq($14)) }

/* Declarations without initialization */
| IDENT LBRACKET expr RBRACKET ASSIGN expr SEMICOLON
    { VectorElementAssign($1, $3, $6) }

| IDENT LBRACKET expr RBRACKET LBRACKET expr RBRACKET ASSIGN expr SEMICOLON
    { MatrixElementAssign($1, $3, $6, $9) }
| INT_TYPE IDENT SEMICOLON 
    { Decl("int", $2, Int(0)) }
| FLOAT_TYPE IDENT SEMICOLON 
    { Decl("float", $2, Float(0.0)) }
| BOOL_TYPE IDENT ASSIGN INPUT_FILE SEMICOLON
    { Decl("bool", $2, InputFile($4)) }
  | INT_TYPE IDENT ASSIGN INPUT_FILE SEMICOLON
    { Decl("int", $2, InputFile($4)) }
  | FLOAT_TYPE IDENT ASSIGN INPUT_FILE SEMICOLON
    { Decl("float", $2, InputFile($4)) }
  | STRING_TYPE IDENT ASSIGN INPUT_FILE SEMICOLON
    { Decl("string", $2, InputFile($4)) }
  | VECTOR_TYPE IDENT ASSIGN INPUT_FILE SEMICOLON
    { Decl("vector", $2, InputFile($4)) }
  | MATRIX_TYPE IDENT ASSIGN INPUT_FILE SEMICOLON
    { Decl("matrix", $2, InputFile($4)) }
| BOOL_TYPE IDENT SEMICOLON 
    { Decl("bool", $2, Bool(false)) }
| STRING_TYPE IDENT SEMICOLON 
    { Decl("string", $2, String("")) }
| VECTOR_TYPE IDENT SEMICOLON
    { VectorDecl($2, Vector(0, IntType, [])) }
| MATRIX_TYPE IDENT SEMICOLON
    { MatrixDecl($2, Matrix(0, 0, IntType, [[]])) }

/* Declarations with initialization */
| INT_TYPE IDENT ASSIGN expr SEMICOLON 
    { Decl("int", $2, $4) }
| FLOAT_TYPE IDENT ASSIGN expr SEMICOLON 
    { Decl("float", $2, $4) }
| BOOL_TYPE IDENT ASSIGN expr SEMICOLON 
    { Decl("bool", $2, $4) }
| BOOL_TYPE IDENT ASSIGN INPUT LPAREN RPAREN SEMICOLON 
    { Decl("bool", $2, Input(None)) }
| BOOL_TYPE IDENT ASSIGN INPUT LPAREN STRING RPAREN SEMICOLON 
    { Decl("bool", $2, Input(Some($6))) }
| VECTOR_TYPE IDENT ASSIGN INPUT LPAREN RPAREN SEMICOLON
    { VectorDecl($2, Input(None)) }
| VECTOR_TYPE IDENT ASSIGN INPUT LPAREN STRING RPAREN SEMICOLON
    { VectorDecl($2, Input(Some($6))) }

/* Matrix input declaration */
| MATRIX_TYPE IDENT ASSIGN INPUT LPAREN RPAREN SEMICOLON
    { MatrixDecl($2, Input(None)) }
| MATRIX_TYPE IDENT ASSIGN INPUT LPAREN STRING RPAREN SEMICOLON
    { MatrixDecl($2, Input(Some($6))) }
| STRING_TYPE IDENT ASSIGN expr SEMICOLON 
    { Decl("string", $2, $4) }
| INT_TYPE IDENT ASSIGN INPUT LPAREN RPAREN SEMICOLON 
    { Decl("int", $2, Input(None)) }
| INT_TYPE IDENT ASSIGN INPUT LPAREN STRING RPAREN SEMICOLON 
    { Decl("int", $2, Input(Some($6))) }
| FLOAT_TYPE IDENT ASSIGN INPUT LPAREN RPAREN SEMICOLON 
    { Decl("float", $2, Input(None)) }
| FLOAT_TYPE IDENT ASSIGN INPUT LPAREN STRING RPAREN SEMICOLON 
    { Decl("float", $2, Input(Some($6))) }
| STRING_TYPE IDENT ASSIGN INPUT LPAREN RPAREN SEMICOLON 
    { Decl("string", $2, Input(None)) }
| STRING_TYPE IDENT ASSIGN INPUT LPAREN STRING RPAREN SEMICOLON 
    { Decl("string", $2, Input(Some($6))) }


/* Vector Declarations */
| VECTOR_TYPE IDENT ASSIGN INT LBRACKET expr_list RBRACKET SEMICOLON
    { 
      let size = $4 in
      let elements = $6 in
      let element_type = match List.hd elements with
        | Int _ -> IntType
        | Float _ -> FloatType
        | _ -> raise (Failure "Vector elements must be numeric (int or float)")
      in
      if List.length elements <> size then
        raise (Failure (sprintf "Vector size mismatch: expected %d elements, got %d" 
                       size (List.length elements)));
      List.iter (fun e -> match (e, element_type) with
        | (Int _, IntType) | (Float _, FloatType) -> ()
        | _ -> raise (Failure "Vector elements must be of consistent type")
      ) elements;
      VectorDecl($2, Vector(size, element_type, elements))
    }
| VECTOR_TYPE IDENT ASSIGN expr SEMICOLON
    { VectorDecl($2, $4) }

/* Matrix Declarations */
| MATRIX_TYPE IDENT ASSIGN INT COMMA INT LBRACKET matrix_list RBRACKET SEMICOLON
    {
      let rows = $4 in
      let cols = $6 in
      let elements = $8 in
      let element_type = match List.hd (List.hd elements) with
        | Int _ -> IntType
        | Float _ -> FloatType
        | _ -> raise (Failure "Matrix elements must be numeric (int or float)")
      in
      if List.length elements <> rows then
        raise (Failure (sprintf "Matrix row count mismatch: expected %d rows, got %d" 
                       rows (List.length elements)));
      List.iter (fun row ->
        if List.length row <> cols then
          raise (Failure (sprintf "Matrix column count mismatch: expected %d columns" cols));
        List.iter (fun e -> match (e, element_type) with
          | (Int _, IntType) | (Float _, FloatType) -> ()
          | _ -> raise (Failure "Matrix elements must be of consistent type")
        ) row
      ) elements;
      MatrixDecl($2, Matrix(rows, cols, element_type, elements))
    }
| MATRIX_TYPE IDENT ASSIGN expr SEMICOLON
    { MatrixDecl($2, $4) }
| VECTOR_TYPE IDENT ASSIGN INPUT_VECTOR LPAREN RPAREN SEMICOLON
    { VectorDecl($2, InputVector) }
| MATRIX_TYPE IDENT ASSIGN INPUT_MATRIX LPAREN RPAREN SEMICOLON
    { MatrixDecl($2, InputMatrix) }
    

/* Simple Assignment */
| IDENT ASSIGN expr SEMICOLON 
    { Assign($1, $3) }

/* Input/Output Operations */
| PRINT LPAREN expr RPAREN SEMICOLON { Print($3) }
| PRINT_INT LPAREN expr RPAREN SEMICOLON { PrintInt($3) }
| PRINT_FLOAT LPAREN expr RPAREN SEMICOLON { PrintFloat($3) }
| PRINT_VECTOR LPAREN expr RPAREN SEMICOLON { PrintVector($3) }
| PRINT_MATRIX LPAREN expr RPAREN SEMICOLON { PrintMatrix($3) }
| PRINT_FILE LPAREN expr RPAREN SEMICOLON { PrintFile($1, $3) }
| INPUT LPAREN STRING RPAREN SEMICOLON { Input(Some($3)) }
| INPUT LPAREN RPAREN SEMICOLON { Input(None) }
| INPUT_INT LPAREN RPAREN SEMICOLON { InputInt }
| INPUT_FLOAT LPAREN RPAREN SEMICOLON { InputFloat }
| INPUT_VECTOR LPAREN RPAREN SEMICOLON { InputVector }
| INPUT_MATRIX LPAREN RPAREN SEMICOLON { InputMatrix }
| INPUT_FILE LPAREN RPAREN SEMICOLON { InputFile($1) }

/* Block */
| LBRACE stmt_list RBRACE { Seq($2) }
;

expr:
/* Constants and Variables */
| INT { Int($1) }
| FLOAT { Float($1) }
| STRING { String($1) }
| TRUE { Bool(true) }
| FALSE { Bool(false) }
| IDENT { Var($1) }
| LPAREN expr RPAREN { $2 }

/* Unary Operations */
| MINUS expr %prec UMINUS { UnOp(Neg, $2) }
| NOT expr { UnOp(Not, $2) }
| ABS expr { UnOp(Abs, $2) }
| TRANSPOSE expr { UnOp(Transpose, $2) }
| DET expr { UnOp(Det, $2) }
| MAG expr { UnOp(Mag, $2) }
| DIM expr { UnOp(Dim, $2) }
| INVERSE expr { UnOp(Inverse, $2) }

/* Binary Operations */
| expr PLUS expr { BinOp(Add, $1, $3) }
| expr MINUS expr { BinOp(Sub, $1, $3) }
| expr TIMES expr { BinOp(Mul, $1, $3) }
| expr DIVIDE expr { BinOp(Div, $1, $3) }
| expr REM expr { BinOp(Mod, $1, $3) }
| expr AND expr { BinOp(And, $1, $3) }
| expr OR expr { BinOp(Or, $1, $3) }
| expr EQ expr { BinOp(Eq, $1, $3) }
| expr NEQ expr { BinOp(Neq, $1, $3) }
| expr LT expr { BinOp(Lt, $1, $3) }
| expr LTE expr { BinOp(Le, $1, $3) }
| expr GT expr { BinOp(Gt, $1, $3) }
| expr GTE expr { BinOp(Ge, $1, $3) }


/* Vector and Matrix Operations */
| expr DOT_PROD expr { BinOp(DotProduct, $1, $3) }
| ANGLE LPAREN expr COMMA expr RPAREN { BinOp(Angle, $3, $5) }
| expr VECTOR_ADD expr { BinOp(VectorAdd, $1, $3) }
| expr VECTOR_SCALAR_MULT expr { BinOp(VectorScalarMult, $1, $3) }
| expr MATRIX_ADD expr { BinOp(MatrixAdd, $1, $3) }
| expr MATRIX_MULT expr { BinOp(MatrixMult, $1, $3) }
| expr MATRIX_SCALAR_MULT expr { BinOp(MatrixScalarMult, $1, $3) }

/* Vector and Matrix Access */
| IDENT LBRACKET expr RBRACKET
    { VectorAccess($1, $3) }
| IDENT LBRACKET expr RBRACKET LBRACKET expr RBRACKET
    { MatrixAccess($1, $3, $6) }
;

/* List Constructions */
expr_list:
| expr { [$1] }
| expr COMMA expr_list { $1 :: $3 }
;

matrix_list:
| LBRACKET expr_list RBRACKET { [$2] }
| LBRACKET expr_list RBRACKET COMMA matrix_list { $2 :: $5 }
;