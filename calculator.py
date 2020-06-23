import re

class KeyWord:
    def __init__(self, name, regex):
        self.name = name
        self.regex = regex

class Token:
    def __init__(self, t, value, start, end):
        self.type = t
        self.value = value
        self.start = start
        self.end = end

class Lexer:
    """
    Lexer used to getting tokesn
    """
    def __init__(self):
        self.text = ""
        self.keyWords = []
        self.delimiters = ["+", "-", "/", "*", "%", "(", ")", "^", "\n", " "]
        self.ignore = [" "]
        self.newTokens = []
        self.setTokens()

    #Define our keywords
    def setTokens(self):
        self.keyWords.append(KeyWord("NUMBER", re.compile(r"([0-9]*\.[0-9]+)|([0-9]+\.[0-9]*)|([0-9])")))
        self.keyWords.append(KeyWord("PLUS", re.compile(r"\+")))
        self.keyWords.append(KeyWord("MINUS", re.compile("-")))
        self.keyWords.append(KeyWord("TIMES", re.compile(r"\*")))
        self.keyWords.append(KeyWord("DIVIDE", re.compile(r"\/")))
        self.keyWords.append(KeyWord("MODULO", re.compile("%")))
        self.keyWords.append(KeyWord("INDEX", re.compile(r"\^")))
        self.keyWords.append(KeyWord("OPENBRACKET", re.compile(r"\(")))
        self.keyWords.append(KeyWord("CLOSEBRACKET", re.compile(r"\)")))

    def setText(self, text):
        self.text = text.strip() + "\n"

    def getTokens(self):
        self.newTokens = []
        word = ""

        #Loop through input
        for i in range(0, len(self.text)):

            #Check for ignore characters
            ignoreFound = False
            if self.text[i] in self.ignore:
                ignoreFound = True

            tokenFound = False
            #Look for a delimiter
            for d in self.delimiters:
                if tokenFound:
                    break
                #If a delimiter is found
                if self.text[i] == d:
                    #Look for keyword
                    for t in self.keyWords:
                        match = t.regex.match(word)
                        if match:
                            self.newTokens.append(Token(t.name, word, (i - len(word)), i))
                            word = ""
                            tokenFound = True
                            break
                    #Check if delimiter has a token
                    if not ignoreFound:
                        for t in self.keyWords:
                            match = t.regex.match(d)
                            if match:
                                self.newTokens.append(Token(t.name, d, i, i))
                                tokenFound = True
                                break
            if not tokenFound and not ignoreFound:
                word += self.text[i]

        self.newTokens.append(Token("EOF", "", i, i))        
        return self.newTokens

class ParseError:
    def __init__(self, error, token):
        self.error = error
        self.token = token

class Parser:
    """
    Recursive decent parser
    Grammer used:    
    Expression: = Term {("+" | "-") Term}
    Term: = Factor {("*" | "/" | "%") Factor}
    Factor: = [-] RealNumber | [-] "(" Expression ")"
    RealNumber: = Digit{Digit} | [Digit] "." {Digit}
    """
    
    def __init__(self):
        self.tokens = []
        self.currentToken = None
        self.index = 0
        self.errors = []
    
    #Set tokens
    def setTokens(self, tokens):
        self.tokens = tokens
        self.index = 0
        self.errors = []
        self.currentToken = self.tokens[self.index]
    
    #Consume a token
    def eat(self):
        if self.index+1 < len(self.tokens):
            self.index += 1
            self.currentToken = self.tokens[self.index]

    #Look at next token
    def lookAhead(self):
        if self.index +1 < len(self.tokens):
            return self.tokens[self.index+1]
        return self.tokens[self.index]

    #Get tokens type
    def getTokenType(self):
        return self.currentToken.type
    
    #Get a tokens value
    def getTokenValue(self):
        return self.currentToken.value

    def getErrors(self):
        return self.errors

    #Parse tokens
    def parse(self):
        result = self.term()
        #Calculate plus and minus expressions
        while self.getTokenType() == "PLUS" or self.getTokenType() == "MINUS":
            operator = self.getTokenType()
            self.eat()
            secondNumber = self.term()
            if operator == "PLUS":
                result += secondNumber
            elif operator == "MINUS":
                result -= secondNumber
        return result

    #calaculate times and divide expressions
    def term(self):
        firstNumber = self.factor()

        while self.getTokenType() == "TIMES" or self.getTokenType() == "DIVIDE" or self.getTokenType() == "MODULO" or self.getTokenType() == "INDEX":
            operator = self.getTokenType()
            self.eat()
            secondNumber = self.factor()
            if operator == "INDEX":
                firstNumber = firstNumber ** secondNumber
            elif operator == "TIMES":
                firstNumber *= secondNumber
            elif operator == "DIVIDE":
                if secondNumber == 0:
                    self.errors.append(ParseError("Cannot divide by 0", self.currentToken))
                else:
                    firstNumber /= secondNumber
            elif operator == "MODULO":
                firstNumber %= secondNumber
        
        return firstNumber

    #Get number or expression in brackets
    def factor(self):

        #Check if number should be minus
        isMinus = False
        if self.getTokenType() == "MINUS" and self.lookAhead().type == "NUMBER":
            self.eat()
            isMinus = True

        if self.getTokenType() == "NUMBER":
            number = float(self.getTokenValue())
            if isMinus:
                number *= -1
            self.eat()
            return number
        
        elif self.getTokenType() == "OPENBRACKET":
            self.eat()
            value = self.parse()
            if isMinus:
                value *= -1
            if self.getTokenType() == "CLOSEBRACKET":
                self.eat()
                return value
        else:
            self.errors.append(ParseError("Expected number or (", self.currentToken))
            self.eat()
            return 0

def main():
    lexer = Lexer()
    parser = Parser()
    while True:
        i = input("Input: ")
        lexer.setText(i)
        parser.setTokens(lexer.getTokens())
        value = parser.parse()
        errors = parser.getErrors()
        print(f"Answer: {value} ")
        for e in errors:
            print(e.error)
             
if __name__ == "__main__":
    main()

