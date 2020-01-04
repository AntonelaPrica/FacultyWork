class Parser:
    def __init__(self, grammar, word):
        self.grammar = grammar
        self.alpha = word + '$'
        self.pif = self.readPIF("PIF.txt")
        self.st = self.readFile("ST.txt")
        self.codificationTable = self.readCodificationTable()

    def parseSequence(self):
        beta = self.grammar.S + '$'
        pi = ''
        accepted = True
        ok = True
        while ok:
            if beta[0] == 'e':
                value = self.grammar.TABLE[('$', self.alpha[0])]
            else:
                value = self.grammar.TABLE[(beta[0], self.alpha[0])]
            if len(value) == 2:
                value[0] = value[0].replace(' ', '')
                beta = beta[1:]
                if value[0] != 'e':
                    beta = str(value[0]) + beta
                pi += str(value[1])
                print(self.grammar.P[value[1]])
            else:
                if len(value) == 1:
                    if value[0] == "POP":
                        beta = beta[1:]
                        self.alpha = self.alpha[1:]
                    elif value[0] == "ACC":
                        ok = False
                        accepted = True
                    else:
                        ok = False
                        accepted = False
        return accepted

    def readCodificationTable(self):
        filepath = 'codificationTable.txt'
        codificationTable = {}
        with open(filepath) as file:
            line = file.readline()
            while line:
                line = line.strip().split(' ')
                codificationTable[line[1]] = line[0]
                line = file.readline()
        return codificationTable

    def readFile(self, filename):
        st = {}
        with open(filename) as file:
            line = file.readline()
            while line:
                line = line.strip().replace(' ', '').split("|")
                st[line[0]] = line[1]
                file.readline()
                line = file.readline()
        return st

    def readPIF(self, filename):
        pif = []
        with open(filename) as file:
            line = file.readline()
            while line:
                line = line.strip().replace(' ', '').split("|")
                pif.append(line)
                file.readline()
                line = file.readline()
        return pif

    def parseByPIF(self):
        word = []
        for code, posST in self.pif:
            if posST == "-1":
                word.append(self.codificationTable[code])
            else:
                word.append(self.st[posST])
        word.append('$')
        print(word)

        beta = []
        beta.append(self.grammar.S)
        beta.append('$')
        pi = ''
        accepted = True
        ok = True
        while ok:
            if beta[0] == 'e':
                value = self.grammar.TABLE[('$', word[0])]
            else:
                value = self.grammar.TABLE[(beta[0], word[0])]
            if len(value) == 2:
                value[0] = value[0].split(' ')
                beta = beta[1:]
                if value[0] != 'e':
                    beta[0:0] = value[0]
                pi += str(value[1])
                print(self.grammar.P[value[1]])
            else:
                if len(value) == 1:
                    if value[0] == "POP":
                        beta = beta[1:]
                        word = word[1:]
                    elif value[0] == "ACC":
                        ok = False
                        accepted = True
                    else:
                        ok = False
                        accepted = False
        return accepted


