import sys

from crossword import *
from collections import deque

class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }
        self.removals={}

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack({x:None for x in self.domains})

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains:
            for value in list(self.domains[var]):
                if len(value)!=var.length:
                    self.domains[var].remove(value)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        overlap = self.crossword.overlaps.get((x,y),None)
        rmv={}
        if overlap==None:
            return False
        fl1=False
        for value in list(self.domains[x]):
            fl=True
            for v in list(self.domains[y]):
                if v[overlap[1]]==value[overlap[0]]:
                    fl=False
                    break
            if fl:
                fl1=True
                self.domains[x].remove(value)
        return fl1

    def ac3(self):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        q=deque()
        for x in self.domains:
            for y in self.crossword.neighbors(x):
                q.append((x,y))
        while q:
            x,y=q.popleft()
            if self.revise(x,y):
                if len(self.domains[x])==0:
                    return False
                for z in self.crossword.neighbors(x):
                    q.append((z,y))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for x in assignment:
            if assignment[x]==None:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # to discard case of any duplicate values
        if len(set(assignment.values()))<len(assignment):
            return False
        for var in assignment:
            for x in self.crossword.neighbors(var):
                o = self.crossword.overlaps.get((var,x),None)
                if o!=None and assignment[var][o[0]]!=assignment[x][o[1]]:
                    return False

        return True

    def f(self,d,s,var):
        ct=0
        for x in d:
            if s in self.domains[x]:
                ct+=1
        return ct

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        d=[]
        for x in self.crossword.neighbors(var):
            if assignment[x]==None:
                d.append(x)
        # sorting the domain of a variable of the basis of how many
        # of it's neighbour it affects
        return sorted(self.domains[var],key=lambda x:self.f(d,x,var))

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        a=[]
        for x in assignment:
            if assignment[x]==None:
                a.append(x)
        a.sort(key=lambda x:len(self.domains[x]))
        return a[0]

    def change(self,assignment,var):
        # make any necessary changes to neighbors of the var to reduce the no. of calls
        s=assignment[var]
        for x in self.crossword.neighbors(var):
            if assignment[x]==None:
                i,j = self.crossword.overlaps.get((var,x))
                for value in list(self.domains[x]):
                    if s[i]!=value[j]:
                        self.domains[x].remove(value)
                        if self.removals.get(x)==None:
                            self.removals[x]=set([value])
                        else:
                            self.removals[x].add(value)

    def reverse(self):
        # it effectively reverse(i.e puts values back into the domains) which were removed by the change function
        for x in list(self.removals.keys()):
            self.domains[x] |= self.removals[x]
            self.removals.pop(x)

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a 

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            if self.consistent(assignment):
                return dict(assignment)
            return None
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var,assignment):
            assignment[var]=value
            self.change(assignment,var)
            v=self.backtrack(assignment)
            if v!=None:
                return v
            self.reverse()
            assignment[var]=None
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
