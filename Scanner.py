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

class Scanner:
    def __init__(self, text):
        self.tokens = list()
        self.text : str = text.strip()
        self.iterator = 0
        self.current_token: str = ""

    def scan(self):
        while len(self.text) > self.iterator:
            self.tokens.append(self.get_next_token())
            self.iterator += 1
        return self.tokens


    def get_next_token(self) -> Token:
        current_character = self.text[self.iterator]
        while current_character in " \n":
            self.iterator+=1
            current_character = self.text[self.iterator]
        match current_character:
            case "+":
                return Token(Symbol.ADD,"+")
            case "-":
                return Token(Symbol.SUB,"-")
            case "*":
                return Token(Symbol.MUL,"*")
            case "/":
                return Token(Symbol.DIV,"/")
            case "(":
                return Token(Symbol.LPAR,"(")
            case ")":
                return Token(Symbol.RPAR,")")
        if current_character.isdigit():
            self.current_token = "" + current_character
            self.iterator +=1
            while len(self.text) > self.iterator:
                current_character = self.text[self.iterator]
                if current_character.isdigit():
                    self.current_token += current_character
                    self.iterator += 1
                else:
                    break
            self.iterator -= 1
            return Token(Symbol.INT, int(self.current_token))
        if current_character.isalpha():
            self.current_token = "" + current_character
            self.iterator +=1
            while len(self.text) > self.iterator:
                current_character = self.text[self.iterator]
                if current_character.isalnum():
                    self.current_token += current_character
                    self.iterator += 1
                else:
                    break
            self.iterator -= 1
            return Token(Symbol.ID, self.current_token)
            

class Token:
    code : Symbol
    def __init__(self, cd, val):
        self.code = cd
        self.value = val
        

skaner = Scanner("2+3*(76+8/3)+ 3*(9-3) ")
tokeny = skaner.scan()
for t in tokeny:
    print(t.code, " ", t.value)
