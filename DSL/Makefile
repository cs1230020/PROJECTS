# Makefile
OCAMLC = ocamlc
OCAMLYACC = ocamlyacc
OCAMLLEX = ocamllex
# Add -w -8 to suppress partial match warnings
# Add -w -11 to suppress redundant match warnings
# Add -w -26 to suppress unused variable warnings
OCAMLFLAGS = -g -w -8-11-26

# The main executable name
MAIN = dsl_interpreter

# Source files in order of compilation
SOURCES = ast.ml \
         parser.mli \
         parser.ml \
         lexer.ml \
         type_checker.ml \
         interpreter.ml \
         main.ml

# Default target
all: $(MAIN)

# Generate lexer
lexer.ml: lexer.mll
	$(OCAMLLEX) $<

# Generate parser
parser.ml parser.mli: parser.mly
	$(OCAMLYACC) $<

# Compile the interpreter
$(MAIN): $(SOURCES)
	$(OCAMLC) $(OCAMLFLAGS) -o $(MAIN) $(SOURCES)

# Run all tests
.PHONY: test
test: $(MAIN)
	@echo "Running tests..."
	@for test in tests/*.dsl; do \
		echo "\nTesting $$test:"; \
		./$(MAIN) $$test || exit 1; \
	done
	@echo "\nAll tests passed!"

# Clean build files
.PHONY: clean
clean:
	rm -f $(MAIN)
	rm -f *.cm[iox]
	rm -f parser.ml parser.mli lexer.ml