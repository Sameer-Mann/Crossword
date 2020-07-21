# Crossword

![](https://cs50.harvard.edu/ai/2020/projects/3/crossword/images/crossword.png)

# Background

![](https://cs50.harvard.edu/ai/2020/projects/3/crossword/images/structure.png)

How might you go about generating a crossword puzzle? Given the structure of a crossword puzzle (i.e., which squares of the grid are meant to be filled in with a letter), and a list of words to use, the problem becomes one of choosing which words should go in each vertical or horizontal sequence of squares. We can model this sort of problem as a constraint satisfaction problem. Each sequence of squares is one variable, for which we need to decide on its value (which word in the domain of possible words will fill in that sequence). Consider the following crossword puzzle structure.

# Crossword Structure

In this structure, we have four variables, representing the four words we need to fill into this crossword puzzle (each indicated by a number in the above image). Each variable is defined by four values: the row it begins on (its i value), the column it begins on (its j value), the direction of the word (either down or across), and the length of the word. Variable 1, for example, would be a variable represented by a row of 1 (assuming 0 indexed counting from the top), a column of 1 (also assuming 0 indexed counting from the left), a direction of across, and a length of 4.

As with many constraint satisfaction problems, these variables have both unary and binary constraints. The unary constraint on a variable is given by its length. For Variable 1, for instance, the value BYTE would satisfy the unary constraint, but the value BIT would not (it has the wrong number of letters). Any values that don’t satisfy a variable’s unary constraints can therefore be removed from the variable’s domain immediately.

The binary constraints on a variable are given by its overlap with neighboring variables. Variable 1 has a single neighbor: Variable 2. Variable 2 has two neighbors: Variable 1 and Variable 3. For each pair of neighboring variables, those variables share an overlap: a single square that is common to them both. We can represent that overlap as the character index in each variable’s word that must be the same character. For example, the overlap between Variable 1 and Variable 2 might be represented as the pair (1, 0), meaning that Variable 1’s character at index 1 necessarily must be the same as Variable 2’s character at index 0 (assuming 0-indexing, again). The overlap between Variable 2 and Variable 3 would therefore be represented as the pair (3, 1): character 3 of Variable 2’s value must be the same as character 1 of Variable 3’s value.

For this problem, we’ll add the additional constraint that all words must be different: the same word should not be repeated multiple times in the puzzle.

The challenge ahead, then, is write a program to find a satisfying assignment: a different word (from a given vocabulary list) for each variable such that all of the unary and binary constraints are met.

# Specification

Complete the implementation of enforce_node_consistency, revise, ac3, assignment_complete, consistent, order_domain_values, selected_unassigned_variable, and backtrack in generate.py so that your AI generates complete crossword puzzles if it is possible to do so.

1. The enforce_node_consistency function should update self.domains such that each variable is node consistent.

1. Recall that node consistency is achieved when, for every variable, each value in its domain is consistent with the variable’s unary constraints. In the case of a crossword puzzle, this means making sure that every value in a variable’s domain has the same number of letters as the variable’s length.
2. To remove a value x from the domain of a variable v, since self.domains is a dictionary mapping variables to sets of values, you can call self.domains[v].remove(x).
3. No return value is necessary for this function.

The revise function should make the variable x arc consistent with the variable y.

1. x and y will both be Variable objects representing variables in the puzzle.
2. Recall that x is arc consistent with y when every value in the domain of x has a possible value in the domain of y that does not cause a conflict. (A conflict in the context of the crossword puzzle is a square for which two variables disagree on what character value it should take on.)
3. To make x arc consistent with y, you’ll want to remove any value from the domain of x that does not have a corresponding possible value in the domain of y.
4. Recall that you can access self.crossword.overlaps to get the overlap, if any, between two variables.
5. The domain of y should be left unmodified.
6. The function should return True if a revision was made to the domain of x; it should return False if no revision was made.

The ac3 function should, using the AC3 algorithm, enforce arc consistency on the problem. Recall that arc consistency is achieved when all the values in each variable’s domain satisfy that variable’s binary constraints.

1. Recall that the AC3 algorithm maintains a queue of arcs to process. This function takes an optional argument called arcs, representing an initial list of arcs to process. If arcs is None, your function should start with an initial queue of all of the arcs in the problem. Otherwise, your algorithm should begin with an initial queue of only the arcs that are in the list arcs (where each arc is a tuple (x, y) of a variable x and a different variable y).
2. Recall that to implement AC3, you’ll revise each arc in the queue one at a time. Any time you make a change to a domain, though, you may need to add additional arcs to your queue to ensure that other arcs stay consistent.
3. You may find it helpful to call on the revise function in your implementation of ac3.
4. If, in the process of enforcing arc consistency, you remove all of the remaining values from a domain, return False (this means it’s impossible to solve the problem, since there are no more possible values for the variable). Otherwise, return True.
5. You do not need to worry about enforcing word uniqueness in this function (you’ll implement that check in the consistent function.)

The assignment_complete function should (as the name suggests) check to see if a given assignment is complete.

1. An assignment is a dictionary where the keys are Variable objects and the values are strings representing the words those variables will take on.
2. An assignment is complete if every crossword variable is assigned to a value (regardless of what that value is).
3. The function should return True if the assignment is complete and return False otherwise.

The consistent function should check to see if a given assignment is consistent.

1. An assignment is a dictionary where the keys are Variable objects and the values are strings representing the words those variables will take on. Note that the assignment may not be complete: not all variables will necessarily be present in the assignment.
2. An assignment is consistent if it satisfies all of the constraints of the problem: that is to say, all values are distinct, every value is the correct length, and there are no conflicts between neighboring variables.
3. The function should return True if the assignment is consistent and return False otherwise.

The order_domain_values function should return a list of all of the values in the domain of var, ordered according to the least-constraining values heuristic.

1. var will be a Variable object, representing a variable in the puzzle.
2. Recall that the least-constraining values heuristic is computed as the number of values ruled out for neighboring unassigned variables. That is to say, if assigning var to a particular value results in eliminating n possible choices for neighboring variables, you should order your results in ascending order of n.
3. Note that any variable present in assignment already has a value, and therefore shouldn’t be counted when computing the number of values ruled out for neighboring unassigned variables.

For domain values that eliminate the same number of possible choices for neighboring variables, any ordering is acceptable.

1. Recall that you can access self.crossword.overlaps to get the overlap, if any, between two variables.
2. It may be helpful to first implement this function by returning a list of values in any arbitrary order (which should still generate correct crossword puzzles). 3. Once your algorithm is working, you can then go back and ensure that the values are returned in the correct order.
4. You may find it helpful to sort a list according to a particular key: Python contains some helpful functions for achieving this.

The select_unassigned_variable function should return a single variable in the crossword puzzle that is not yet assigned by assignment, according to the minimum remaining value heuristic and then the degree heuristic.

1. An assignment is a dictionary where the keys are Variable objects and the values are strings representing the words those variables will take on. You may assume that the assignment will not be complete: not all variables will be present in the assignment.
2. Your function should return a Variable object. You should return the variable with the fewest number of remaining values in its domain. If there is a tie between variables, you should choose among whichever among those variables has the largest degree (has the most neighbors). If there is a tie in both cases, you may choose arbitrarily among tied variables.
3. It may be helpful to first implement this function by returning any arbitrary unassigned variable (which should still generate correct crossword puzzles). Once your algorithm is working, you can then go back and ensure that you are returning a variable according to the heuristics.

The backtrack function should accept a partial assignment assignment as input and, using backtracking search, return a complete satisfactory assignment of variables to values if it is possible to do so.
