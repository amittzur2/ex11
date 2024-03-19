"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    
    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters, 
    and comments, which are ignored. There are three possible comment formats: 
    /* comment until closing */ , /** API comment until closing */ , and 
    // comment until the line's end.

    - 'xxx': quotes are used for tokens that appear verbatim ('terminals').
    - xxx: regular typeface is used for names of language constructs 
           ('non-terminals').
    - (): parentheses are used for grouping of language constructs.
    - x | y: indicates that either x or y can appear.
    - x?: indicates that x appears 0 or 1 times.
    - x*: indicates that x appears 0 or more times.

    ## Lexical Elements

    The Jack language includes five types of terminal elements (tokens).

    - keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' | 
               'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' |
               'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' | 
               'while' | 'return'
    - symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    - integerConstant: A decimal number in the range 0-32767.
    - StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
    - identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.

    ## Program Structure

    A Jack program is a collection of classes, each appearing in a separate 
    file. A compilation unit is a single class. A class is a sequence of tokens 
    structured according to the following context free syntax:
    
    - class: 'class' className '{' classVarDec* subroutineDec* '}'
    - classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    - type: 'int' | 'char' | 'boolean' | className
    - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) 
    - subroutineName '(' parameterList ')' subroutineBody
    - parameterList: ((type varName) (',' type varName)*)?
    - subroutineBody: '{' varDec* statements '}'
    - varDec: 'var' type varName (',' varName)* ';'
    - className: identifier
    - subroutineName: identifier
    - varName: identifier

    ## Statements

    - statements: statement*
    - statement: letStatement | ifStatement | whileStatement | doStatement | 
                 returnStatement
    - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    - ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' 
                   statements '}')?
    - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    - doStatement: 'do' subroutineCall ';'
    - returnStatement: 'return' expression? ';'

    ## Expressions
    
    - expression: term (op term)*
    - term: integerConstant | stringConstant | keywordConstant | varName | 
            varName '['expression']' | subroutineCall | '(' expression ')' | 
            unaryOp term
    - subroutineCall: subroutineName '(' expressionList ')' | (className | 
                      varName) '.' subroutineName '(' expressionList ')'
    - expressionList: (expression (',' expression)* )?
    - op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    - unaryOp: '-' | '~' | '^' | '#'
    - keywordConstant: 'true' | 'false' | 'null' | 'this'
    
    Note that ^, # correspond to shiftleft and shiftright, respectively.
    """




   
    keywords = {'class', 'constructor', 'function', 'method', 'field',
                'static', 'var', 'int', 'char', 'boolean', 'void', 'true',
                'false', 'null', 'this', 'let', 'do', 'if', 'else',
                'while', 'return'}
    symbols = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-',
                '*', '/', '&', '|', '<', '>', '=', '~', '^', '#'}

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

                Args:
                    input_stream (typing.TextIO): input stream.
                """

        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        self.input_lines = input_stream.read()#read the input
        self.remove_comments()#remove comments - now the input lines are splited list, without comments
        self.token_list = []
        for inpt in self.input_lines:
            self.token_list.extend(self.tokinizer(inpt))

        self.current_token_index = -1
        self.tokens_amount = len(self.token_list)
        self.current_token = ""
        self.current_token_wraped = ""

    def tokinizer(self,input_lines):
        tokens = []
        current_token = ''
        in_string = False

        for char in input_lines:
            if char == '"':
                if not in_string:
                    in_string = True
                    current_token += char
                else:
                    current_token += char
                    tokens.append(current_token)
                    current_token = ''
                    in_string = False
            elif in_string:
                current_token += char
            elif char.isspace():
                if current_token:
                    tokens.append(current_token)
                    current_token = ''
            elif char in self.symbols:
                if current_token:
                    tokens.append(current_token)
                    current_token = ''
                tokens.append(char)
            else:
                current_token += char

        if current_token:
            tokens.append(current_token)

        return tokens

    def clean_whitespace(self,input_lines):
        cleaned_lines = []

        # Remove whitespace from each line
        for line in input_lines:
            cleaned_line = ''.join(line.split())  # Remove all whitespace characters
            if cleaned_line:  # If the line is not empty after removing whitespace, add to cleaned lines
                cleaned_lines.append(cleaned_line)

        return cleaned_lines


    def remove_comments(self) -> None:
        """Removes all comments from the input stream.
        """
        index = 0
        final_text = ""
        while index < len(self.input_lines):
            char = self.input_lines[index]
            if char == "\"":
                # we are in a string so jump to the end of the string
                end_string_index = self.input_lines.find("\"", index + 1)
                # add the string to the final text
                final_text += self.input_lines[index:end_string_index + 1]
                # jump to the end of the string
                index = end_string_index + 1
            elif char == "/":
                # if it's a block comment we need to jump to the end of the block comment
                if self.input_lines[index + 1] == "*":
                    end_comment_index = self.input_lines.find("*/", index + 1)
                    # jump to the end of the comment
                    index = end_comment_index + 2
                    final_text += " "
                # if it's a line comment we need to jump to the end of the line
                elif self.input_lines[index + 1] == "/":
                    end_line_index = self.input_lines.find("\n", index + 1)
                    # jump to the end of the line
                    index = end_line_index + 1
                    final_text += " "
                else:
                    final_text += char
                    index += 1
            else:
                final_text += char
                index += 1
        self.input_lines = final_text.splitlines()



    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        return (self.current_token_index+1)<self.tokens_amount

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        if self.has_more_tokens():
            self.current_token_index+=1
            self.current_token = self.token_list[self.current_token_index]
            current_token_type = self.token_type()

            if current_token_type == "KEYWORD":
                self.current_token_wraped = "<keyword> "+self.current_token+" </keyword>"
            elif current_token_type == "SYMBOL":
                 self.current_token_wraped = "<symbol> "+ self.fit_to_symbol_to_xml(self.current_token) + " </symbol>"
            elif current_token_type == "IDENTIFIER":
                 self.current_token_wraped = "<identifier> "+self.current_token+" </identifier>"
            elif current_token_type == "INT_CONST":
                 self.current_token_wraped = "<integerConstant> "+self.current_token+" </integerConstant>"
            elif current_token_type == "STRING_CONST":
                 self.current_token_wraped = "<stringConstant> "+self.string_val()+" </stringConstant>"



    def fit_to_symbol_to_xml(self,symbol):
        dict = {'<':'&lt;','>':'&gt;','&':'&amp;'}
        if symbol in dict:
            return dict[symbol]
        return symbol

    def remove_string_quotes(self,string):
        return string[1:-1]

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        print("current token:",self.current_token)
        print("")
        if self.current_token in self.keywords:
            return 'KEYWORD'
        elif self.current_token in self.symbols:
            return 'SYMBOL'
        elif self.current_token.isdigit() and 0 <= int(self.current_token) <= 32767:
            return 'INT_CONST'
        elif self.current_token.startswith('"') and self.current_token.endswith('"') and len(self.current_token) > 1:
            return 'STRING_CONST'
        elif not self.current_token[0].isdigit() and self.current_token.replace("_", "").isalnum():
            return 'IDENTIFIER'
        else:
            return ""

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        return self.current_token.capitalize()

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        return self.current_token

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.
        """
        return self.current_token

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        return int(self.current_token)

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
        """
        return self.current_token[1:-1]




