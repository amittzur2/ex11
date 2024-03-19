"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """

    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        self.d = dict()
        self.s = dict()
        self.count_static = 0
        self.count_field = 0
        self.count_arg = 0
        self.count_var = 0


    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's 
        symbol table).
        """
        self.s = dict()
        self.count_arg = 0
        self.count_var = 0

    def define(self, name: str, type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns 
        it a running index. "STATIC" and "FIELD" identifiers have a class scope, 
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """

        if kind == "STATIC":
            self.d[(name, type, kind)] = self.count_static
            self.count_static += 1
        elif kind == "FIELD":
            self.d[(name, type, kind)] = self.count_field
            self.count_field += 1
        elif kind == "ARG":
            self.s[(name, type, kind)] = self.count_arg
            self.count_arg += 1
        elif kind == "VAR":
            self.s[(name, type, kind)] = self.count_var
            self.count_var += 1
        else:
            print("Vardec " + name + ", " + type + ", " + kind + " is invalid!")

    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in 
            the current scope.
        """
        if kind == "STATIC":
            return self.count_static
        if kind == "FIELD":
            return self.count_field
        if kind == "ARG":
            return self.count_arg
        if kind == "VAR":
            return self.count_var
        return 0

    def kind_of(self, name: str) -> str:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        for tup in self.s.keys():
            if tup[0] == name:
                return tup[2]

        for tup in self.d.keys():
            if tup[0] == name:
                return tup[2]



        return None

    def type_of(self, name: str) -> str:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        for tup in self.s.keys():
            if tup[0] == name:
                return tup[1]

        for tup in self.d.keys():
            if tup[0] == name:
                return tup[1]



        return None

    def index_of(self, name: str) -> int:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        for tup in self.s.keys():
            if tup[0] == name:
                return self.s[tup]

        for tup in self.d.keys():
            if tup[0] == name:
                return self.d[tup]


        return None
