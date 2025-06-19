(* main.ml *)
open Printf
open Lexing
open Parser
open Type_checker
open Interpreter

(* Function to read an entire file into a string *)
let read_file filename =
  let chan = open_in filename in
  let content = really_input_string chan (in_channel_length chan) in
  close_in chan;
  content

(* Function to initialize lexing buffer with position tracking *)
let init_lexbuf filename content =
  let lexbuf = Lexing.from_string content in
  let pos = lexbuf.Lexing.lex_curr_p in
  lexbuf.Lexing.lex_curr_p <- { pos with
    Lexing.pos_fname = filename;
    Lexing.pos_lnum = 1;
  };
  lexbuf

(* Function to parse and handle syntax errors *)
let parse_with_error lexbuf =
  try
    Parser.program Lexer.token lexbuf
  with
  | Parsing.Parse_error -> 
      let pos = lexbuf.Lexing.lex_curr_p in
      printf "Syntax error at line %d position %d\n" 
        pos.Lexing.pos_lnum
        (pos.Lexing.pos_cnum - pos.Lexing.pos_bol + 1);
      exit 1
  | Failure msg ->
      printf "Lexer error: %s\n" msg;
      exit 1

(* Main function *)
let () =
  if Array.length Sys.argv <> 2 then begin
    printf "Usage: %s <filename.dsl>\n" Sys.argv.(0);
    exit 1
  end;

  let filename = Sys.argv.(1) in
  try
    (* Read the input file *)
    let input = read_file filename in

    (* Create lexing buffer *)
    let lexbuf = init_lexbuf filename input in

    (* Parse the input *)
    let ast = parse_with_error lexbuf in

    (* Type check the AST *)
    (try
      Type_checker.type_check ast;
      printf "Type checking successful!\n"
    with
    | Type_checker.TypeError msg ->
        printf "Type error: %s\n" msg;
        exit 1);

    (* Interpret the AST *)
    ignore (Interpreter.interpret ast)

  with
  | Sys_error msg ->
      printf "System error: %s\n" msg;
      exit 1