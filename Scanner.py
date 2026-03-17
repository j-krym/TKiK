from enum import Enum





class Symbol(Enum):
    ID = 0
    INT = 1
    LPAR = 2
    RPAR = 3
    ADD = 4
    SUB =5
    MUL = 6
    DIV = 7


class Token:
    code : Symbol
    def __init__(self, cd, val):
        self.code = cd
        self.value = val
    def __str__(self):
        if self.code in (Symbol.INT,Symbol.ID):
            return self.code.__str__() + " " + str(self.value)
        return self.code.__str__()
    
class Scanner:
    def __init__(self, text):
        self.tokens = list()
        self.text : str = text.strip()
        self.iterator = 0
        self.current_token: str = ""

    def scan(self):
        self.tokens = []
        while True:
            token = self.get_next_token()
            if token is None:
                break
            self.tokens.append(token)
        return self.tokens

    def get_next_token(self) -> Token:
        while self.iterator < len(self.text) and self.text[self.iterator] in " \n":
            self.iterator += 1
        
        if self.iterator >= len(self.text):
            return None
        
        current_character = self.text[self.iterator]
        
        match current_character:
            case "+":
                self.iterator += 1
                return Token(Symbol.ADD, "+")
            case "-":
                self.iterator += 1
                return Token(Symbol.SUB, "-")
            case "*":
                self.iterator += 1
                return Token(Symbol.MUL, "*")
            case "/":
                self.iterator += 1
                return Token(Symbol.DIV, "/")
            case "(":
                self.iterator += 1
                return Token(Symbol.LPAR, "(")
            case ")":
                self.iterator += 1
                return Token(Symbol.RPAR, ")")
        
        if current_character.isdigit():
            start = self.iterator
            while self.iterator < len(self.text) and self.text[self.iterator].isdigit():
                self.iterator += 1
            value = int(self.text[start:self.iterator])
            return Token(Symbol.INT, value)
        
        if current_character.isalpha():
            start = self.iterator
            while self.iterator < len(self.text) and self.text[self.iterator].isalnum():
                self.iterator += 1
            value = self.text[start:self.iterator]
            return Token(Symbol.ID, value)
        
        raise ValueError(f"Invalid character: '{current_character}' at position {self.iterator}")
            

skaner = Scanner("2+3*(76+8/3)+ 3*(9-3) alfa ")
tokeny = skaner.scan()
for t in tokeny:
    print(t)
