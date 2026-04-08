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
    NEWLINE = 8
    SPACE = 9
    INCREM=10
    DECREM=11
    SEMICOLON=12
    LBRACE=13
    RBRACE=14
    ASSIGN = 15
    EQ = 16
    LTHAN = 17
    GTHAN = 18
    KEYWORD=19
keywords = ["if","else","break","while","for","return","false","true","int","float",
            "char","string","bool","void"]
colors = {
    Symbol.KEYWORD: "#AF00DB",   # fiolet (czytelny, ale nie agresywny)
    Symbol.ID: "#001080",        # ciemny granat zamiast czerni
    Symbol.INT: "#098658",       # zielony

    # operatory – ciemnoszare zamiast czarnych
    Symbol.ADD: "#333333",
    Symbol.SUB: "#333333",
    Symbol.MUL: "#333333",
    Symbol.DIV: "#333333",
    Symbol.ASSIGN: "#333333",
    Symbol.EQ: "#333333",
    Symbol.LTHAN: "#333333",
    Symbol.GTHAN: "#333333",

    # inkrementacja – lekko wyróżniona
    Symbol.INCREM: "#333333",
    Symbol.DECREM: "#333333",

    # nawiasy – inny odcień, żeby łatwo śledzić strukturę
    Symbol.LPAR: "#795E26",      
    Symbol.RPAR: "#795E26",
    Symbol.LBRACE: "#B26700",
    Symbol.RBRACE: "#B26700",

    # separator – najlżejszy
    Symbol.SEMICOLON: "#999999",
}

class Token:
    code : Symbol
    def __init__(self, cd, val):
        self.code = cd
        self.value = val
    def __str__(self):
        if self.code in (Symbol.INT,Symbol.ID, Symbol.KEYWORD):
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
        if self.iterator >= len(self.text):
            return None
        
        current_character = self.text[self.iterator]
        
        match current_character:
            case "=":
                self.iterator += 1
                if self.text[self.iterator] == "=":
                    self.iterator += 1
                    return Token(Symbol.EQ, "==")
                return Token(Symbol.ASSIGN, "=")
            case "+":
                self.iterator += 1
                if self.text[self.iterator] == "=":
                    self.iterator += 1
                    return Token(Symbol.INCREM, "+=")
                return Token(Symbol.ADD, "+")
            case "-":
                self.iterator += 1
                if self.text[self.iterator] == "=":
                    self.iterator += 1
                    return Token(Symbol.DECREM, "-=")
                return Token(Symbol.SUB, "-")
            case "<":
                self.iterator += 1
                return Token(Symbol.LTHAN, "<")
            case ">":
                self.iterator += 1
                return Token(Symbol.GTHAN, ">")
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
            case "{":
                self.iterator += 1
                return Token(Symbol.LBRACE, "{")
            case "}":
                self.iterator += 1
                return Token(Symbol.RBRACE, "}")
            case ";":
                self.iterator += 1
                return Token(Symbol.SEMICOLON, ";")
            case " ":
                self.iterator += 1
                return Token(Symbol.SPACE, "&nbsp")
            case "\n":
                self.iterator += 1
                return Token(Symbol.NEWLINE, "\n<br>\n")

        if current_character.isdigit():
            start = self.iterator
            while self.iterator < len(self.text) and self.text[self.iterator].isdigit():
                self.iterator += 1
            value = self.text[start:self.iterator]
            return Token(Symbol.INT, value)
        
        if current_character.isalpha():
            start = self.iterator
            while self.iterator < len(self.text) and self.text[self.iterator].isalnum():
                self.iterator += 1
            value = self.text[start:self.iterator]
            if value in keywords:
                return Token(Symbol.KEYWORD,value)
            return Token(Symbol.ID, value)
        
        raise ValueError(f"Invalid character: '{current_character}' at position {self.iterator}")

def creating_html(tokens, filename):
    with open(filename,"w") as f:
        f.write("<html>\n<body>\n")
        for token in tokens:
            if token.code in colors.keys():
                f.write("<span style=\"color: " + colors[token.code] + "\">"+ token.value +"</span>")
            else:
                f.write(token.value)
        f.write("\n</body>\n</html>")



with open("main.c","r") as f:
    content = f.read()
    print(content)
    scanner = Scanner(content)
    tokens = scanner.scan()
    for token in tokens:
        print(token)
    creating_html(tokens, "test.html")
