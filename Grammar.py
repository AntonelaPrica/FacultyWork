import copy


class Grammar:
    def __init__(self, N, E, P, S):
        self.N = N  # Non-terminals
        self.E = E  # Terminals
        self.P = P  # Productions
        self.S = S  # Starting point
        self.FIRST = dict()
        self.FOLLOW = dict()
        self.TABLE = dict()
        self.build_first()
        self.build_follow()
        self.build_table()

    @staticmethod
    def parse_line(line):
        # Only get what comes after the '='
        return line.strip().split(' ')[2:]

    @staticmethod
    def read_file(file_name):
        with open(file_name) as file:
            N = Grammar.parse_line(file.readline())
            E = Grammar.parse_line(file.readline())
            S = Grammar.parse_line(file.readline())[0]  # Only get the letter

            file.readline()  # P =

            # Parse all productions
            P = []
            for line in file:
                lhs, rhs = line.split('->')
                lhs = lhs.strip()
                rhs = [value.strip() for value in rhs.split('|')]

                for value in rhs:
                    P.append((lhs, value))

            return Grammar(N, E, P, S)

    def is_regular(self):
        """
        S -> aA | bB | X
        A -> aA | cB
        B -> c
        """

        # TODO read this once
        with open('grammar.txt') as file:
            N_unused = Grammar.parse_line(file.readline())
            E_unused = Grammar.parse_line(file.readline())
            S_unused = Grammar.parse_line(file.readline())[0]  # Only get the letter

            file.readline()  # P =

            # Parse all productions
            P = [line.strip() for line in file]

        starting_point_goes_into_epsilon = False
        starting_point_in_rhs = False

        for p in P:
            # Get rhs elements
            for element in p.replace(' ', '')[3:].split('|'):
                if len(element) > 2:
                    return False

                # First element has to be a terminal (or epsilon)
                if element[0] not in self.E and element[0] != 'E':
                    return False

                if element[0] == self.S:
                    starting_point_in_rhs = True

                if len(element) == 2:
                    if element[1] not in self.N:
                        return False

                    if element[1] == self.S:
                        starting_point_in_rhs = True

                # if the starting point goes in Epsilon (E), S cannot be in rhs
                if p[0] == self.S:
                    if element == 'E':
                        starting_point_goes_into_epsilon = True

        if starting_point_goes_into_epsilon and starting_point_in_rhs:
            return False

        return True

    @staticmethod
    def from_fa(fa):
        N = fa.Q
        E = fa.E
        S = fa.q0
        P = []

        # Starting point is final state in FA
        if fa.q0 in fa.F:
            P.append((fa.q0, 'E'))

        for transition in fa.S:
            lhs, state2 = transition
            state1, route = lhs
            print("state1: {} = route {} = state2 {}".format(state1, route, state2))
            P.append((state1, route + state2))

            if state2 in fa.F:
                P.append((state1, route))

        return Grammar(N, E, P, S)

    def get_first(self, element):
        # first(terminal) = terminal
        if element in self.E:
            return element
        elif element in self.N:
            if element in self.FIRST.keys():
                return self.FIRST[element]
            else:
                raise Exception("First for this element has not been computed yet")
        else:
            raise Exception("Unknown element passed into get_first()")

    def is_terminal(self, elem):
        """
        :param elem:
        :return: returns true if elem is a terminal, false otherwise
        """

        return elem in self.E

    def is_nonterminal(self, elem):
        """
        :param elem:
        :return: returns true if elem is a nonterminal, false otherwise
        """

        return elem in self.N

    def get_first_table(self):
        return self.FIRST

    def build_first(self):
        # initialization
        lastIteration = dict()
        for nonterminal in self.N:
            lastIteration[nonterminal] = []
            productions = [[lhs, rhd] for lhs, rhd in self.P if nonterminal == lhs and (rhd.strip().split(' ')[0] in self.E or rhd == "e")]
            # add first elem from productions with non-terminal on first position
            for [lhs, rhd] in productions:
                lastIteration[lhs].append(rhd.strip().split(' ')[0])

        ok = False
        while not ok:
            newIteration = copy.deepcopy(lastIteration)
            for nonterminal in self.N:
                # get all production for non-terminal A
                productions = [[lhs, rhd] for lhs, rhd in self.P if nonterminal == lhs]
                for [lhs, rhs] in productions:
                    # for each production of A construct set alfa
                    stop = False
                    alfa = []
                    if not stop:
                        if rhs == "e":
                            alfa.append(rhs)
                        else:
                            for x in rhs.split(' '):
                                if not stop:
                                    if x in self.E:
                                        alfa.append(x)
                                    elif x in self.N:
                                        if lastIteration[x] != []:
                                            alfa.append(lastIteration[x])
                                        else:
                                            # cannot be computed yet since we have an empty set
                                            stop = True
                                    else:
                                        raise Exception("Unknown element in the rhs")
                    if stop == False:
                        # if first element of alfa is a list
                        if isinstance(alfa[0], list):
                            for elem in alfa[0]:
                                if elem not in newIteration[nonterminal]:
                                    newIteration[nonterminal].append(elem)
                        else:
                            # if first element of alfa is only an element
                            if alfa[0] not in newIteration[nonterminal]:
                                newIteration[nonterminal].append(alfa[0])
            if newIteration == lastIteration:
                ok = True
            lastIteration = copy.deepcopy(newIteration)
        self.FIRST = lastIteration

    def build_follow(self):
        # initialize - first iteration
        lastIteration = dict()
        for nonterminal in self.N:
            lastIteration[nonterminal] = []
            if nonterminal == self.S:
                lastIteration[nonterminal].append("e")

        ok = False
        while not ok:
            newIteration = copy.deepcopy(lastIteration)
            for nonterminal in self.N:
                # get productions where A is in the right hand side
                productions = [[lhs, rhd] for lhs, rhd in self.P if nonterminal in rhd]
                for lhs, rhd in productions:
                    # beta is the sequence which follows the non-terminal A in the production
                    beta = rhd.split(nonterminal, 1)[1]
                    if beta != '':
                        beta = beta.strip().split(' ')[0]
                        res = self.get_first(beta)
                        # add all symbols != from epsilon(e)
                        if isinstance(res, list):
                            for e in res:
                                if e not in newIteration[nonterminal] and e != "e":
                                    newIteration[nonterminal].append(e)
                            # if in the FIRST(beta) we have epsilon then
                            # get all the symbols from the last iteration for the left hand side(B) of the product
                            if "e" in res:
                                for elem in lastIteration[lhs]:
                                    if elem not in newIteration[nonterminal]:
                                        newIteration[nonterminal].append(elem)
                        elif res != "e" and res not in newIteration[nonterminal]:
                            # beta is non-terminal
                            newIteration[nonterminal].append(res)
                    else:
                        # A is the last character in the production
                        # get all the symbols from the last iteration for the left hand side(B) of the product
                        for elem in lastIteration[lhs]:
                            if elem not in newIteration[nonterminal]:
                                newIteration[nonterminal].append(elem)
            # if the last 2 iterations are equal then the FOLLOW configuration will be the last one computed
            if newIteration == lastIteration:
                ok = True
            lastIteration = copy.deepcopy(newIteration)
        self.FOLLOW = lastIteration

    def build_table(self):
        rows = []
        columns = []
        for elem in self.N:
            rows.append(elem)
        for elem in self.E:
            rows.append(elem)
            columns.append(elem)
        rows.append("$")
        columns.append("$")
        for row in rows:
            for column in columns:
                if row == "$" and column == "$":
                    self.TABLE[(row, column)] = ["ACC"]
                elif row == column:
                    self.TABLE[(row, column)] = ["POP"]
                else:
                    self.TABLE[(row, column)] = ["ERR"]
        for i in range(0, len(self.P)):
            [lhs, rhs] = self.P[i]
            if rhs == 'e':
                symbols = self.FOLLOW[lhs]
                for symbol in symbols:
                    if symbol == "e":
                        self.TABLE[(lhs, "$")] = [rhs, i]
                    else:
                        self.TABLE[(lhs, symbol)] = [rhs, i]
            else:
                terminals = self.get_first(rhs.strip().split(' ')[0])
                if isinstance(terminals, list):
                    for terminal in terminals:
                        self.TABLE[(lhs, terminal)] = [rhs, i]
                    if 'e' in terminals:
                        symbols = self.FOLLOW[lhs]
                        for symbol in symbols:
                            self.TABLE[(lhs, symbol)] = [rhs, i]
                else:
                    if terminals != 'e':
                        self.TABLE[(lhs, terminals)] = [rhs, i]
                    else:
                        symbols = self.FOLLOW[lhs]
                        for symbol in symbols:
                            self.TABLE[(lhs, symbol)] = [rhs, i]

    def __str__(self):
        return "N = { " + ', '.join(self.N) + " }\n" \
                                              "E = { " + ', '.join(self.E) + " }\n" \
                                                                             "P = { " + str(self.P) + " }\n" \
                                                                                                      "S = { " + self.S + " }"
