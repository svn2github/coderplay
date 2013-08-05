#include "allobject.h"
#include "Emma.h"
#include "lexer.h"
#include "lexer.i"


char *lexeme;
long ival;
double fval;

void
lexer_init() {
    if (source.line == NULL) { // only if no input string is set
        source.line = (char *) malloc (BUFSIZ * sizeof(char));
        source.line[0] = '\0'; // initiate as blank line
    }
    lexeme = (char *) malloc (BUFSIZ * sizeof(char));
}


void lexer_free() {
    free(source.line);
    free(lexeme);
}

static void
source_balance() {
    if (source.peek == '{') {
        source.nulcb++;
    }
    else if (source.peek == '}') {
        source.nulcb--;
        if (source.nulcb < 0) {
            log_error(SYNTAX_ERROR, "redundant right curly bracket");
        }
    }
}

static int
process_exponential(int length) {
    int expval = 0, sign = 1;
    if (source.peek == '-' || source.peek =='+') {
        if (source.peek == '-')
            sign = -1;
        lexeme[length++] = source.peek;
        nextc();
    }
    while (isdigit(source.peek)) {
        lexeme[length++] = source.peek;
        expval = 10*expval + (source.peek - '0');
        nextc();
    }
    lexeme[length] = '\0';
    return expval*sign;
}

static int
process_fraction(int intpart, int length) {

    EmObject *ob;
    double d;
    int expval;

    // if a fraction part is found
    if (isdigit(source.peek)) {
        fval = intpart;
        d = 10.0;
        // loop for the float digit
        while (isdigit(source.peek)) {
            lexeme[length++] = source.peek;
            fval += (source.peek - '0')/d;
            d *= 10.0;
            nextc();
        }
        // check for scientific notation
        if (source.peek != 'e' && source.peek != 'E') {
            lexeme[length] = '\0';
        } else {
            lexeme[length++] = source.peek;
            nextc();
            expval = process_exponential(length);
            fval = fval * pow(10, expval);
        }
    } else if (source.peek == 'e' || source.peek == 'E') {
        lexeme[length++] = source.peek;
        nextc();
        expval = process_exponential(length);
        fval = intpart * pow(10, expval);
    } else {
        lexeme[length] = '\0';
        fval = intpart;
    }
    if ((ob = hashobject_lookup_by_string(constTable, lexeme)) == NULL) {
        ob = newfloatobject(fval);
        constTable = hashobject_insert_by_string(constTable, lexeme, ob);
    }
    DECREF(ob);
    return FLOAT;
}

/*
 * The reading is performed here. There we should really deal with the
 * prompt output (e.g. PS1, PS2) here. Thus the parser should not care
 * about any I/O. It simply asks for token and build syntax tree.
 */

int
get_token() {

    int tag;
    int length;
    char quote;
    EmObject *ob;

    while (1) {
        // ignore whites and CR for Linux
        while (source.peek == ' ' || source.peek == '\t' || source.peek == CHAR_CR)
            nextc();

        if (source.peek == '#')
            while (source.peek != CHAR_LF)
                nextc();

        if (source.peek == CHAR_LF) {
            source.peek = ' ';
            return CHAR_LF;
        }

        // following line is to accommodate Linux end-of-line sequence
        if (source.peek == CHAR_CR && source.lastPeek == CHAR_LF) {
            source.peek = ' ';
            continue;
        }

        // Only comments and EOL are allowed after line continuation
        // symbol. So if the code reaches here with continuation mode
        // on, it is an error.
        if (source.isContinue) {
            log_error(SYNTAX_ERROR,
                    "illegal tokens after line continuation symbol");
        }

        if (source.peek == ENDMARK)
            return ENDMARK; // end of INPUT

        if (source.peek == '>') {
            if (matchc('='))
                return GE;
            else
                return '>';
        }
        else if (source.peek == '=') {
            if (matchc('='))
                return EQ;
            else
                return '=';
        }
        else if (source.peek == '<') {
            if (matchc('='))
                return LE;
            else
                return '<';
        }
        else if (source.peek == '*') {
            if (matchc('*'))
                return DSTAR;
            else
                return '*';
        }

        // Numbers
        length = 0;
        if (isdigit(source.peek)) {
            ival = 0;
            while (isdigit(source.peek)) {
                lexeme[length++] = source.peek;
                ival = 10*ival + (source.peek - '0');
                nextc();
            }

            // make sure it is an integer
            if (source.peek != '.' && source.peek != 'e' && source.peek != 'E') {
                lexeme[length] = '\0';
                if ((ob = hashobject_lookup_by_string(constTable, lexeme)) == NULL) {
                    ob = newintobject(ival);
                    constTable = hashobject_insert_by_string(constTable, lexeme,
                            ob);
                }
                DECREF(ob);
                return INTEGER;
            } else { // we have a float
                if (source.peek == '.') {
                    lexeme[length++] = source.peek;
                    nextc();
                }
                return process_fraction(ival, length);
            }
        }

        length = 0;
        // float number starts with a dot, i.e. no integer part
        if (source.peek == '.') {
            lexeme[length++] = source.peek;
            nextc();
            if (isdigit(source.peek)) {
                return process_fraction(0, length);
            } else {
                return '.';
            }
        }

        // Strings
        // TODO Interpret escape sequence
        length = 0;
        if (source.peek == '"' || source.peek == '\'') {
            lexeme[length++] = quote = source.peek;
            do {
                nextc();
                lexeme[length++] = source.peek;
            } while (!(source.peek == quote && source.lastPeek != '\\'));
            lexeme[length] = '\0';
            if ((ob = hashobject_lookup_by_string(constTable, lexeme)) == NULL) {
                lexeme[length - 1] = '\0'; // -1 to erase ending quote
                ob = newstringobject(lexeme + 1); // +1 to skip leading quote
                // Now add the quote to use as key
                lexeme[length - 1] = quote;
                lexeme[length] = '\0';
                constTable = hashobject_insert_by_string(constTable, lexeme,
                        ob);
            }
            DECREF(ob);

            nextc(); // read pass the ending quote
            return STRING;
        }

        length = 0;
        // Identifiers
        if (isalpha(source.peek) || source.peek == '_') {
            while (isalnum(source.peek) || source.peek == '_') {
                lexeme[length++] = source.peek;
                nextc();
            }
            lexeme[length] = '\0';
            tag = match_keyword();
            if (tag) // keywords
                return tag;
            else // identifier
                return IDENT;
        }

        // Any single character token
        tag = source.peek;

        // Check source bracket balance
        source_balance();

        // Important, source.peek is set to blank so next call can proceed.
        source.peek = ' ';


        // line continuation
        if (tag == '\\') {
            source.isContinue = 1;
            continue;
        }

        return tag;
    }
}



