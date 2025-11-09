import sys

from crossword import *

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
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
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
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        
        for var in self.crossword.variables:
            for word in self.domains[var].copy():
                if var.length != len(word):
                    self.domains[var].remove(word)
        

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        
        revised = False
        
        if self.crossword.overlaps[x, y] is not None:
            i = self.crossword.overlaps[x, y][0]
            j = self.crossword.overlaps[x, y][1]
            for word_x in self.domains[x].copy():
                
                # Assume no suitable word_y exists
                flag = False
                for word_y in self.domains[y]:
                    if word_x[i] == word_y[j]:
                        flag = True
                        # Exit inner loop if a suitable word_y is found
                        break
                
                if flag == False:
                    self.domains[x].remove(word_x)
                    revised = True
                    
        return revised
    

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        
        queue = []
        for v1 in self.crossword.variables:
            for v2 in self.crossword.neighbors(v1):
                queue.append((v1, v2))
        
        while len(queue) != 0:
            sample = queue.pop(0)
            if self.revise(sample[0], sample[1]) == True:
                if len(self.domains[sample[0]]) == 0:
                    return False
                else:
                    for v3 in self.crossword.neighbors(v1):
                        if v3 != sample[1]:
                            queue.append((v3, v1))
        return True
    
    
    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        
        for var in self.crossword.variables:
            if var not in assignment:
                return False
            
        return True
    
    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        consistent = True
        
        for var in assignment:
            # Check unary constraints
            if len(assignment[var]) != var.length:
                consistent = False
                
            # Check binary constraints
            
            for neighbor in self.crossword.neighbors(var):
                #if neighbor not yet in assigment, all is fine
                if neighbor not in assignment:
                    consistent = True
                else:
                    i = self.crossword.overlaps[var, neighbor][0]
                    j = self.crossword.overlaps[var, neighbor][1]
                    if assignment[var][i] != assignment[neighbor][j]:
                        consistent = False
                    
        return consistent

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        
        # Initialize a dictionary of form Word: Number of eliminated words
        my_dict = {}
        
        # Get list of unassigned neighbors of var
        list_neighbors = []
        for neighbor in self.crossword.neighbors(var):
            if neighbor not in assignment:
                list_neighbors.append(neighbor)
        
        # Loop over each word in the domain of var
        for word in self.domains[var]:
            
            # Initialize number of mismatches for each word
            count = 0
            
            # Loop over all unassigned neighbors of var
            for neighbor in list_neighbors:
                
                # Find overlaps if any exist
                if self.crossword.overlaps[var, neighbor] is not None:
                    (i, j) = self.crossword.overlaps[var, neighbor]
                
                # Loop over each candidate word in the neighbor's domain
                # and count the number of mismatches
                for candidate in self.domains[neighbor]:
                    if word[(i,j)[0]] != candidate[(i,j)[1]]:
                        count += 1
            
            my_dict[word] = count
        
        # Sort dictionary by value
        sorted_dict = dict(sorted(my_dict.items(), key = lambda x: x[1]))
        
        # Return list of sorted keys
        return list(sorted_dict.keys())


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        
        # Call methods to get suscriptable objects
        domains = self.domains
        neighbors = self.crossword.neighbors
        
        # Create a new dictionary {var: [number of possible values, degree]}
        new_dict = {}
        for var in domains.keys():
            num_val = len(domains[var])
            num_neighbors = len(neighbors(var))
            new_dict[var] = [num_val, num_neighbors]
        
        # Sort this dictionary by the sum of the values
        ranked_dict = dict(sorted(new_dict.items(), key = lambda x: x[1][0] + x[1][1]))
        
        # Choose the first variable that's not part of assignment
        for var in ranked_dict:
            if var not in assignment:
                return var
        
        # If no variable is found return None
        return None
    
        
    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        
        if self.assignment_complete(assignment):
            return assignment
        else:
            var = self.select_unassigned_variable(assignment)
            for value in self.order_domain_values(var, assignment):
                assignment.update({var: value})
                if self.consistent(assignment):
                    result = self.backtrack(assignment)
                    if result != False:
                        return result
                else:
                    del assignment[var]
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
