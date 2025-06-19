(* lexer.mll *)
{
open Parser  (* Use parser's token definitions *)
open Printf

(* Helper function for debugging/printing tokens *)
let string_of_token = function
  | INT i -> sprintf "INT(%d)" i
  | FLOAT f -> sprintf "FLOAT(%f)" f
  | STRING s -> sprintf "STRING(%s)" s
  | IDENT s -> sprintf "IDENT(%s)" s
  | INVALID_ASSIGN s -> sprintf "INVALID_ASSIGN(%s)" s
  | INPUT -> "INPUT"
  | PRINT -> "PRINT"
  | IF -> "IF"
  | THEN -> "THEN"
  | ELSE -> "ELSE"
  | FOR -> "FOR"
  | WHILE -> "WHILE"
  | TRUE -> "TRUE"
  | FALSE -> "FALSE"
  | BOOL_TYPE -> "BOOL_TYPE"
  | INT_TYPE -> "INT_TYPE"
  | FLOAT_TYPE -> "FLOAT_TYPE"
  | STRING_TYPE -> "STRING_TYPE"
  | VECTOR_TYPE -> "VECTOR_TYPE"
  | MATRIX_TYPE -> "MATRIX_TYPE"
  | INPUT_VECTOR -> "INPUT_VECTOR"
  | INPUT_MATRIX -> "INPUT_MATRIX"
  | INPUT_INT -> "INPUT_INT"
  | INPUT_FLOAT -> "INPUT_FLOAT"
  | PRINT_VECTOR -> "PRINT_VECTOR"
  | PRINT_MATRIX -> "PRINT_MATRIX"
  | PRINT_INT -> "PRINT_INT"
  | PRINT_FLOAT -> "PRINT_FLOAT"
  | VECTOR_INT -> "VECTOR_INT"
  | VECTOR_FLOAT -> "VECTOR_FLOAT"
  | MATRIX_INT -> "MATRIX_INT"
  | MATRIX_FLOAT -> "MATRIX_FLOAT"
  | INPUT_FILE s -> sprintf "INPUT_FILE(%s)" s
  | PRINT_FILE s -> sprintf "PRINT_FILE(%s)" s
  | NOT -> "NOT"
  | AND -> "AND"
  | OR -> "OR"
  | ABS -> "ABS"
  | PLUS -> "PLUS"
  | MINUS -> "MINUS"
  | TIMES -> "TIMES"
  | DIVIDE -> "DIVIDE"
  | REM -> "REM"
  | EQ -> "EQ"
  | NEQ -> "NEQ"
  | LT -> "LT"
  | LTE -> "LTE"
  | GT -> "GT"
  | GTE -> "GTE"
  | ASSIGN -> "ASSIGN"
  | DOT_PROD -> "DOT_PROD"
  | ANGLE -> "ANGLE"
  | MAG -> "MAG"
  | DIM -> "DIM"
  | VECTOR_ADD -> "VECTOR_ADD"
  | VECTOR_SCALAR_MULT -> "VECTOR_SCALAR_MULT"
  | MATRIX_ADD -> "MATRIX_ADD"
  | MATRIX_MULT -> "MATRIX_MULT"
  | MATRIX_SCALAR_MULT -> "MATRIX_SCALAR_MULT"
  | TRANSPOSE -> "TRANSPOSE"
  | DET -> "DET"
  | INVERSE -> "INVERSE"
  | SEMICOLON -> "SEMICOLON"
  | COMMA -> "COMMA"
  | LPAREN -> "LPAREN"
  | RPAREN -> "RPAREN"
  | LBRACE -> "LBRACE"
  | RBRACE -> "RBRACE"
  | LBRACKET -> "LBRACKET"
  | RBRACKET -> "RBRACKET"
  | OUTPUT -> "OUTPUT"
  | EOF -> "EOF"
}

let digit = ['0'-'9']
let integer = digit+
let float = digit+ '.' digit* ('e' ['+' '-']? digit+)?
let letter = ['a'-'z' 'A'-'Z']
let identifier = letter (letter | digit | '_' | ''')*
let invalid_identifier = digit+ (letter | digit | '_' | ''')+
let invalid_assign_target = digit+ | invalid_identifier
let whitespace = [' ' '\t' '\r' '\n']
let string = '"' [^ '"']* '"'
let single_quoted = ''' [^ ''']* ''' 
let keywords = "True" | "False" | "Input" | "Print" | "if" | "then" | "else" 
            | "for" | "while" | "bool" | "int" | "float" | "vector" | "matrix" | "string"

let digit = ['0'-'9']
let integer = digit+
let float = digit+ '.' digit* ('e' ['+' '-']? digit+)?
let letter = ['a'-'z' 'A'-'Z']
let identifier = letter (letter | digit | '_' | ''')*
let invalid_identifier = digit+ (letter | digit | '_' | ''')+
let invalid_assign_target = digit+ | invalid_identifier
let whitespace = [' ' '\t' '\r' '\n']
let string_literal = '"' [^'"']* '"'
let single_quoted = ''' [^''']* '''

rule token = parse
| whitespace { token lexbuf }
| "//" [^ '\n']* { token lexbuf }
| "/*" { comment lexbuf }

(* Constants - Numbers and Strings *)
| '-'? integer as i { INT(int_of_string i) }  (* Allow optional minus sign *)
| '-'? float as f { FLOAT(float_of_string f) }  
| string_literal as s { 
    let len = String.length s in
    STRING(String.sub s 1 (len - 2))  (* Remove quotes *)
}

(* Types *)
| "bool" { BOOL_TYPE }
| "int" { INT_TYPE }
| "float" { FLOAT_TYPE }
| "string" { STRING_TYPE }
| "vector" { VECTOR_TYPE }
| "matrix" { MATRIX_TYPE }

(* Print Commands *)
| "print" { PRINT }
| "print_int" { PRINT_INT }
| "print_float" { PRINT_FLOAT }
| "print_vector" { PRINT_VECTOR }
| "print_matrix" { PRINT_MATRIX }

(* Input Commands *)
| "input" { INPUT }
| "input_int" { INPUT_INT }
| "input_float" { INPUT_FLOAT }
| "input_vector" { INPUT_VECTOR }
| "input_matrix" { INPUT_MATRIX }

(* Vector and Matrix Operations *)
| "dot" { DOT_PROD }
| "angle" { ANGLE }
| "mag" { MAG }
| "dim" { DIM }
| "transpose" { TRANSPOSE }
| "det" { DET }
| "inv" { INVERSE }
| "+v" { VECTOR_ADD }
| "*v" { VECTOR_SCALAR_MULT }
| "+m" { MATRIX_ADD }
| "**m" { MATRIX_MULT }
| "*m" { MATRIX_SCALAR_MULT }
| "abs" { ABS }

(* Boolean Operations *)
| "true" { TRUE }
| "false" { FALSE }
| "!" { NOT }
| "&&" { AND }
| "||" { OR }

(* Control Flow *)
| "if" { IF }
| "then" { THEN }
| "else" { ELSE }
| "for" { FOR }
| "while" { WHILE }

(* Operators *)
| ":=" { ASSIGN }
| "+" { PLUS }
| "-" { MINUS }
| "*" { TIMES }
| "/" { DIVIDE }
| "%" { REM }
| "==" { EQ }
| "!=" { NEQ }
| "<=" { LTE }
| "<" { LT }
| ">=" { GTE }
| ">" { GT }

(* Delimiters *)
| "(" { LPAREN }
| ")" { RPAREN }
| "{" { LBRACE }
| "}" { RBRACE }
| "[" { LBRACKET }
| "]" { RBRACKET }
| ";" { SEMICOLON }
| "," { COMMA }

(* Identifiers *)
| identifier as id { IDENT(id) }
| invalid_identifier as id  
    { 
        printf "Lexical error: Invalid identifier '%s'. Identifiers cannot start with numbers\n" id;
        exit 1 
    }

(* Error handling for invalid assignments *)
| (digit+ as num) ":="  
    { 
        printf "Lexical error: Invalid assignment target '%s'. Variables cannot start with numbers\n" num;
        exit 1 
    }
| (invalid_identifier as id) ":="
    {
        printf "Lexical error: Invalid assignment target '%s'. Variables cannot start with numbers\n" id;
        exit 1
    }

(* File operations *)
| "input_file" whitespace* '"' ([^'"']* as fname) '"' { 
    let processed_fname = String.trim fname in
    INPUT_FILE processed_fname 
}
| "print_file" whitespace* '"' ([^'"']* as fname) '"' { PRINT_FILE fname }

| eof { EOF }
| _ as c { 
    printf "Lexical error: Unexpected character '%c'\n" c;
    exit 1 
}

and comment = parse
| "*/" { token lexbuf }
| "\n" { Lexing.new_line lexbuf; comment lexbuf }
| _ { comment lexbuf }
| eof {
    printf "Error: Unterminated comment\n";
    exit 1
}

{
let rec print_tokens lexbuf =
  let tok = token lexbuf in
  match tok with
  | EOF -> 
      print_endline "EOF"
  | _ -> 
      print_endline (string_of_token tok);
      print_tokens lexbuf

let () =
  let in_chan =
    if Array.length Sys.argv > 1 then
      open_in Sys.argv.(1)
    else
      stdin
  in
  let lexbuf = Lexing.from_channel in_chan in
  print_tokens lexbuf
}