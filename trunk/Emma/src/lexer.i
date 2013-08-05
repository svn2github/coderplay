char *token_types[] = {
        "DSTAR",
        "LE",
        "EQ",
        "GE",
        "NE",
        "PRINT",
        "READ",
        "IF",
        "ELIF",
        "ELSE",
        "WHILE",
        "FOR",
        "CONTINUE",
        "BREAK",
        "DEF",
        "RETURN",
        "NUL",
        "CLASS",
        "AND",
        "OR",
        "XOR",
        "NOT",
        "IMPORT",
        "PACKAGE",
        "TRY",
        "RAISE",
        "CATCH",
        "FINALLY",
        "SELF",
        "INTEGER",
        "FLOAT",
        "STRING",
        "IDENT"
};

int match_keyword() {
    if (strcmp(lexeme, "print") == 0)
        return PRINT;
    else if (strcmp(lexeme, "read") == 0)
        return READ;
    else if (strcmp(lexeme, "if") == 0)
        return IF;
    else if (strcmp(lexeme, "elif") == 0)
        return ELIF;
    else if (strcmp(lexeme, "else") == 0)
        return ELSE;
    else if (strcmp(lexeme, "while") == 0)
        return WHILE;
    else if (strcmp(lexeme, "for") == 0)
        return FOR;
    else if (strcmp(lexeme, "continue") == 0)
        return CONTINUE;
    else if (strcmp(lexeme, "break") == 0)
        return BREAK;
    else if (strcmp(lexeme, "def") == 0)
        return DEF;
    else if (strcmp(lexeme, "return") == 0)
        return RETURN;
    else if (strcmp(lexeme, "null") == 0)
        return NUL;
    else if (strcmp(lexeme, "class") == 0)
        return CLASS;
    else if (strcmp(lexeme, "and") == 0)
        return AND;
    else if (strcmp(lexeme, "or") == 0)
        return OR;
    else if (strcmp(lexeme, "not") == 0)
        return NOT;
    else if (strcmp(lexeme, "import") == 0)
        return IMPORT;
    else if (strcmp(lexeme, "package") == 0)
        return PACKAGE;
    else if (strcmp(lexeme, "try") == 0)
        return TRY;
    else if (strcmp(lexeme, "raise") == 0)
        return RAISE;
    else if (strcmp(lexeme, "catch") == 0)
        return CATCH;
    else if (strcmp(lexeme, "finally") == 0)
        return FINALLY;
    else if (strcmp(lexeme, "self") == 0)
        return SELF;
    else
        return ENDMARK;
}
