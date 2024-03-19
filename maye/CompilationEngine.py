"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """


        self.is_void = False
        self.vm = VMWriter(output_stream)
        self.tokenizer = input_stream
        self.num_tabs = 0
        self.num_label_while = 0
        self.num_label_if = 0
        self.symbol_table = SymbolTable()
        self.class_name = ""
        self.function_name = ""
        self.sub_type = ""

        self.op_map = {
            "+": "ADD", "-": "SUB", "-": "NEG", "=": "EQ", "&gt;": "GT", "&lt;": "LT",
            "&amp;": "AND", "|": "OR", "~": "NOT", "^": "SHIFTLEFT", "#": "SHIFTRIGHT"
        }

        self.kind_map = {
            "VAR": "local", "STATIC": "static", "FIELD": "this", "ARG": "argument"
        }

    def process(self, s):
        token = ""
        ident = ""

        if self.tokenizer.token_type() == "KEYWORD":
            ident = "keyword"
            token = self.tokenizer.keyword().lower()
        if self.tokenizer.token_type() == "SYMBOL":
            ident = "symbol"
            token = self.tokenizer.symbol()
        if self.tokenizer.token_type() == "IDENTIFIER":
            ident = "identifier"
            token = self.tokenizer.identifier()
        if self.tokenizer.token_type() == "STRING_CONST":
            ident = "stringConstant"
            token = self.tokenizer.string_val()
        if self.tokenizer.token_type() == "INT_CONST":
            ident = "integerConstant"
            token = self.tokenizer.int_val()

        if token not in s:
            print("syntax error in token " + token + " of type " + self.tokenizer.token_type()
                  + " which was supposed to be in" + str(s)
                  + " in line number " + str(self.tokenizer.num_line) + ":\n" + self.tokenizer.line)

        #else:
        #    self.o.write("  "*self.num_tabs + "<" + ident + "> " + token + " </" + ident + ">\n")

        self.tokenizer.advance()

        return token


    def compile_class(self) -> None:
        self.symbol_table = SymbolTable()

        #self.o.write("  "*self.num_tabs + "<class>\n")
        self.num_tabs += 1

        self.process(["class"])
        self.class_name = self.process([self.tokenizer.identifier()])
        self.process(["{"])

        while self.tokenizer.token_type() == "KEYWORD" and \
                (self.tokenizer.keyword() == "FIELD" or self.tokenizer.keyword() == "STATIC"):
            self.compile_class_var_dec()

        while self.tokenizer.token_type() == "KEYWORD" and \
            (self.tokenizer.keyword() == "CONSTRUCTOR" or self.tokenizer.keyword() == "FUNCTION" \
             or self.tokenizer.keyword() == "METHOD"):
            self.compile_subroutine()

        self.process(["}"])

        self.num_tabs -= 1
        #self.o.write("  "*self.num_tabs + "</class>\n")

        #print(str(self.symbol_table.d))




    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        #self.o.write("  " * self.num_tabs + "<classVarDec>\n")
        self.num_tabs += 1

        kind = self.process(["static", "field"]).upper()
        type = self.process(["int", "char", "boolean", self.tokenizer.identifier()])
        name = self.process([self.tokenizer.identifier()])
        self.symbol_table.define(name, type, kind)

        while self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ",":
            self.process([","])
            name = self.process([self.tokenizer.identifier()])
            self.symbol_table.define(name, type, kind)

        self.process([";"])



        self.num_tabs -= 1
        #self.o.write("  " * self.num_tabs + "</classVarDec>\n")

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        self.symbol_table.start_subroutine()

        #self.o.write("  " * self.num_tabs + "<subroutineDec>\n")
        self.num_tabs += 1
        self.num_label_while = 0
        self.num_label_if = 0

        self.sub_type = self.process(["constructor", "function", "method"])
        if self.sub_type == "method":
            self.symbol_table.define("this", self.class_name, "ARG")


        self.is_void = (self.process(["void", "int", "char", "boolean", self.tokenizer.identifier()]) == "void")

        function_name = self.process([self.tokenizer.identifier()])
        self.process(["("])
        self.compile_parameter_list()
        self.process([")"])


        self.compile_subroutine_body(function_name)

        self.num_tabs -= 1
        #self.o.write("  " * self.num_tabs + "</subroutineDec>\n")

        #print(str(self.symbol_table.s))


    def compile_subroutine_body(self, function_name) -> None:
        #self.o.write("  " * self.num_tabs + "<subroutineBody>\n")
        self.num_tabs += 1


        self.process(["{"])
        while self.tokenizer.token_type() == "KEYWORD" and self.tokenizer.keyword() == "VAR":
            self.compile_var_dec()

        self.vm.write_function(self.class_name + "." + function_name, self.symbol_table.var_count("VAR"))

        if self.sub_type == "method":
            self.vm.write_push("argument", 0)
            self.vm.write_pop("pointer", 0)

        if self.sub_type == "constructor":
            self.vm.write_push("constant", self.symbol_table.var_count("FIELD"))
            self.vm.write_call("Memory.alloc", 1)
            self.vm.write_pop("pointer", 0)

        self.compile_statements()

        self.process(["}"])

        self.num_tabs -= 1
        #self.o.write("  " * self.num_tabs + "</subroutineBody>\n")

    def compile_parameter_list(self) -> int:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        parameterList
        """
        #self.o.write("  " * self.num_tabs + "<parameterList>\n")
        self.num_tabs += 1
        num_args = 0

        if (self.tokenizer.token_type() == "KEYWORD" and self.tokenizer.keyword() in ["INT", "CHAR", "BOOLEAN"]) or \
                self.tokenizer.token_type() == "IDENTIFIER":
            type = self.process(["int", "char", "boolean", self.tokenizer.identifier()])
            name = self.process([self.tokenizer.identifier()])
            self.symbol_table.define(name, type, "ARG")
            num_args += 1

            while self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ",":
                self.process([","])
                type = self.process(["int", "char", "boolean", self.tokenizer.identifier()])
                name = self.process([self.tokenizer.identifier()])
                self.symbol_table.define(name, type, "ARG")
                num_args += 1

        self.num_tabs -= 1
        #self.o.write("  " * self.num_tabs + "</parameterList>\n")

        return num_args

    def compile_var_dec(self) -> None:
        #self.o.write("  " * self.num_tabs + "<varDec>\n")
        self.num_tabs += 1

        self.process(["var"])
        type = self.process(["int", "char", "boolean", self.tokenizer.identifier()])
        name = self.process([self.tokenizer.identifier()])
        self.symbol_table.define(name, type, "VAR")

        while self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ",":
            self.process([","])
            name = self.process([self.tokenizer.identifier()])
            self.symbol_table.define(name, type, "VAR")

        self.process([";"])

        self.num_tabs -= 1
        #self.o.write("  " * self.num_tabs + "</varDec>\n")



    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        #self.o.write("  " * self.num_tabs + "<statements>\n")
        self.num_tabs += 1

        while self.tokenizer.token_type() == "KEYWORD" and \
                self.tokenizer.keyword() in ["LET", "IF", "WHILE", "DO", "RETURN"]:
            if self.tokenizer.keyword() == "LET":
                self.compile_let()
            elif self.tokenizer.keyword() == "IF":
                self.compile_if()
            elif self.tokenizer.keyword() == "WHILE":
                self.compile_while()
            elif self.tokenizer.keyword() == "DO":
                self.compile_do()
            elif self.tokenizer.keyword() == "RETURN":
                self.compile_return()

        self.num_tabs -= 1
        #self.o.write("  " * self.num_tabs + "</statements>\n")

    def compile_do(self) -> None:
        """Compiles a do statement."""
        #---------------------------------------------------- ADD NEW IMPLEMENTATIONS TO EXPRESSION LIST AS WELL------------
        #self.o.write("  " * self.num_tabs + "<doStatement>\n")
        self.num_tabs += 1
        num_args = 0
        var_cond = True

        self.process(["do"])
        function_name = self.process([self.tokenizer.identifier()])
        var_name = function_name

        if self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ".":
            self.process(["."])
            if self.symbol_table.type_of(var_name) is not None:
                function_name = self.symbol_table.type_of(var_name) + "." + self.process([self.tokenizer.identifier()])
            else:
                var_cond = False
                function_name = var_name + "." + self.process([self.tokenizer.identifier()])
        else:
            function_name = self.class_name + "." + var_name


        if self.symbol_table.type_of(var_name) is None:
            #AMMEND LATER, HOW DO YOU KNOW IF YOU SHOULD PUSH THE POINTER????
            if function_name[:function_name.index(".")] == self.class_name and var_cond:
                num_args += 1
                self.vm.write_push("pointer", 0)
        elif self.symbol_table.kind_of(var_name) in self.kind_map.keys():
            self.vm.write_push(self.kind_map[self.symbol_table.kind_of(var_name)], self.symbol_table.index_of(var_name))
            num_args += 1


        self.process(["("])
        num_args += self.compile_expression_list()
        self.process([")"])



        self.process([";"])

        self.vm.write_call(function_name, num_args)
        self.vm.write_pop("temp", 0)

        self.num_tabs -= 1
        #self.o.write("  " * self.num_tabs + "</doStatement>\n")


    def compile_let(self) -> None:
        """Compiles a let statement."""
        #self.o.write("  " * self.num_tabs + "<letStatement>\n")
        self.num_tabs += 1
        is_arr = False

        self.process(["let"])
        name = self.process([self.tokenizer.identifier()])
        if self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == "[":
            is_arr = True
            self.process(["["])
            self.compile_expression()
            self.process(["]"])
            self.vm.write_push(self.kind_map[self.symbol_table.kind_of(name)], self.symbol_table.index_of(name))
            self.vm.write_arithmetic("ADD")
        self.process(["="])
        self.compile_expression()
        self.process([";"])

        if is_arr:
            self.vm.write_pop("temp", 0)
            self.vm.write_pop("pointer", 1)
            self.vm.write_push("temp", 0)
            self.vm.write_pop("that", 0)
        else:
            self.vm.write_pop(self.kind_map[self.symbol_table.kind_of(name)], self.symbol_table.index_of(name))

        self.num_tabs -= 1
        #self.o.write("  " * self.num_tabs + "</letStatement>\n")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        #self.o.write("  " * self.num_tabs + "<whileStatement>\n")
        self.num_tabs += 1
        num_label_while = self.num_label_while
        self.num_label_while += 1

        self.vm.write_label("WHILE_EXP" + str(num_label_while))

        self.process(["while"])
        self.process(["("])
        self.compile_expression()
        self.process([")"])

        self.vm.write_arithmetic("NOT")
        self.vm.write_if("WHILE_END" + str(num_label_while))

        self.process(["{"])
        self.compile_statements()
        self.process(["}"])

        self.vm.write_goto("WHILE_EXP" + str(num_label_while))
        self.vm.write_label("WHILE_END" + str(num_label_while))


        self.num_tabs -= 1
        #self.o.write("  " * self.num_tabs + "</whileStatement>\n")

    def compile_return(self) -> None:
        """Compiles a return statement."""
        #self.o.write("  " * self.num_tabs + "<returnStatement>\n")
        self.num_tabs += 1

        self.process(["return"])
        if self.tokenizer.token_type() != "SYMBOL" or self.tokenizer.symbol() != ";":
            self.compile_expression()
        self.process([";"])

        if self.is_void:
            self.vm.write_push("constant", 0)

        self.vm.write_return()

        self.num_tabs -= 1
        #self.o.write("  " * self.num_tabs + "</returnStatement>\n")

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        #self.o.write("  " * self.num_tabs + "<ifStatement>\n")
        self.num_tabs += 1
        num_label_if = self.num_label_if
        self.num_label_if += 1

        self.process(["if"])
        self.process(["("])
        self.compile_expression()
        self.process([")"])

        self.vm.write_if("IF_TRUE" + str(num_label_if))
        self.vm.write_goto("IF_FALSE" + str(num_label_if))
        self.vm.write_label("IF_TRUE" + str(num_label_if))

        self.process(["{"])
        self.compile_statements()
        self.process(["}"])

        if self.tokenizer.token_type() == "KEYWORD" and self.tokenizer.keyword() == "ELSE":
            self.vm.write_goto("IF_END" + str(num_label_if))
            self.vm.write_label("IF_FALSE" + str(num_label_if))
            self.process(["else"])
            self.process(["{"])
            self.compile_statements()
            self.process(["}"])
            self.vm.write_label("IF_END" + str(num_label_if))
        else:
            self.vm.write_label("IF_FALSE" + str(num_label_if))


        self.num_tabs -= 1
        #self.o.write("  " * self.num_tabs + "</ifStatement>\n")

    def compile_expression(self) -> None:
        """Compiles an expression. """
        #self.o.write("  " * self.num_tabs + "<expression>\n")
        self.num_tabs += 1

        self.compile_term()
        while self.tokenizer.token_type() == "SYMBOL"  \
                and self.tokenizer.symbol() in ["+", "-", "*", "/", "&amp;", "|", "&lt;", "&gt;", "="]:
            og_op = self.process(["+", "-", "*", "/", "&amp;", "|", "&lt;", "&gt;", "="])
            self.compile_term()
            if og_op not in ["*", "/", "-"]:
                self.vm.write_arithmetic(self.op_map[og_op])
            elif og_op == "-":
                self.vm.write_arithmetic("SUB")
            elif og_op == "*":
                self.vm.write_call("Math.multiply", 2)
            else:
                self.vm.write_call("Math.divide", 2)

        self.num_tabs -= 1
        #self.o.write("  " * self.num_tabs + "</expression>\n")

    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        #self.o.write("  " * self.num_tabs + "<term>\n")
        self.num_tabs += 1

        if self.tokenizer.token_type() == "INT_CONST":
            int_const = int(self.process([self.tokenizer.int_val()]))
            self.vm.write_push("constant", int_const)
        elif self.tokenizer.token_type() == "STRING_CONST":
            string_const = self.process([self.tokenizer.string_val()])
            self.vm.write_push("constant", len(string_const))
            self.vm.write_call("String.new", 1)
            for ch in string_const:
                self.vm.write_push("constant", ord(ch))
                self.vm.write_call("String.appendChar", 2)
        elif self.tokenizer.token_type() == "KEYWORD" \
                and self.tokenizer.keyword() in ["TRUE", "FALSE", "NULL", "THIS"]:
            const = self.process(["true", "false", "null", "this"])
            if const in ["false", "null"]:
                self.vm.write_push("constant", 0)
            elif const == "true":
                self.vm.write_push("constant", 0)
                self.vm.write_arithmetic("NOT")
            else:
                self.vm.write_push("pointer", 0)
        elif self.tokenizer.token_type() == "IDENTIFIER":
            name = self.process([self.tokenizer.identifier()])
            if self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == "[":
                self.process(["["])
                self.compile_expression()
                self.process(["]"])
                self.vm.write_push(self.kind_map[self.symbol_table.kind_of(name)], self.symbol_table.index_of(name))
                self.vm.write_arithmetic("ADD")
                self.vm.write_pop("pointer", 1)
                self.vm.write_push("that", 0)
            elif self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() in [".", "("]:

                var_cond = True
                num_args = 0
                if self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ".":
                    self.process(["."])
                    if self.symbol_table.type_of(name) is not None:
                        function_name = self.symbol_table.type_of(name) + "." + self.process(
                            [self.tokenizer.identifier()])
                    else:
                        var_cond = False
                        function_name = name + "." + self.process([self.tokenizer.identifier()])
                else:
                    function_name = self.class_name + "." + name

                if self.symbol_table.type_of(name) is None:
                    if function_name[:function_name.index(".")] == self.class_name and var_cond:
                        num_args += 1
                        self.vm.write_push("pointer", 0)
                elif self.symbol_table.kind_of(name) in self.kind_map.keys():
                    self.vm.write_push(self.kind_map[self.symbol_table.kind_of(name)],
                                       self.symbol_table.index_of(name))
                    num_args += 1

                self.process(["("])
                num_args += self.compile_expression_list()
                self.process([")"])

                self.vm.write_call(function_name, num_args)

            else:
                self.vm.write_push(self.kind_map[self.symbol_table.kind_of(name)], self.symbol_table.index_of(name))
        elif self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.keyword() in ["-", "~"]:
            op = self.op_map[self.process(["-", "~", "^", "#"])]
            self.compile_term()
            self.vm.write_arithmetic(op)
        else:
            self.process(["("])
            self.compile_expression()
            self.process([")"])


        self.num_tabs -= 1
        #self.o.write("  " * self.num_tabs + "</term>\n")

    def compile_expression_list(self) -> int:
        #self.o.write("  " * self.num_tabs + "<expressionList>\n")
        self.num_tabs += 1
        num_args = 0


        """Compiles a (possibly empty) comma-separated list of expressions. expressionList"""
        if self.tokenizer.token_type() != "SYMBOL" or self.tokenizer.symbol() != ")":
            self.compile_expression()
            num_args += 1

            while self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ",":
                self.process([","])
                self.compile_expression()
                num_args += 1

        self.num_tabs -= 1
        #self.o.write("  " * self.num_tabs + "</expressionList>\n")

        return num_args

