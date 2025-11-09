import itertools
import random
from itertools import permutations


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells
        

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:  
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:    
            self.cells.remove(cell)
        


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        
        self.moves_made.add(cell)                           ### Add to moves made
        self.mark_safe(cell)                                ### Mark cell as safe
        
        
        ### Add new sentence to knowledge base
        # Loop over all cells within one row and column
        
        surrounding = set()
        overlap = 0                                         ### count how many cells overlap with mines
        for i in range(cell[0]-1, cell[0]+2):
            for j in range(cell[1]-1, cell[1]+2):
                if (i, j) in self.mines:
                    overlap += 1
                if ((i, j) not in self.safes and
                    i >=0 and i < self.height and
                    j >=0 and j < self.width and
                    (i, j) not in self.mines):
                    surrounding.add((i, j))
        sentence = Sentence(surrounding, count-overlap)     ### to avoid overcounting
        self.knowledge.append(sentence)
        
        ### Infer which cells are safe or mines
        ### If one set of cells is a subset of another set, we can infer new knowledge
        ### While this is true, we want to check for mines mark them. Repeat for safes
        ### But now what if some of the remaining sets of cells are subsets of other sets in the knowledge base
        ### Repeat this loop until we cannot infer any new knowledge
        
        # Checks whether a set of a subset of another set
        def check_subsets():
            for p in permutations(self.knowledge, 2):
                new_count = 0
                if p[0].cells.issubset(p[1].cells):
                    difference = p[1].cells.difference(p[0].cells)
                    new_count = p[1].count - p[0].count
                    s = Sentence(difference, new_count)
                    if s not in self.knowledge:
                        self.knowledge.append(s)
                        global switch
                        switch = True
        
        # Infers which cells are mines in knowledge base
        def function_for_mines():
            inferred_mines = set()
            for s in self.knowledge:
                if s.known_mines() is not None:
                    for m in s.known_mines():
                        inferred_mines.add(m)
            if inferred_mines:
                for m in inferred_mines:
                    self.mark_mine(m)
                    
        # Inferes which cells are safes in knowledge base        
        def function_for_safes():
            inferred_safes = set()
            for s in self.knowledge:
                if s.known_safes() is not None:
                    for n in s.known_safes():
                        inferred_safes.add(n)
            if inferred_safes:
               for n in inferred_safes:
                   self.mark_safe(n)
        
        # Iterate through the three functions while new knowledge is still generated
        global switch
        switch = True
        while switch:
            switch = False
            check_subsets()
            function_for_mines()
            function_for_safes()
        
    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        safe_choices = []
        for i in range(self.height):
            for j in range(self.width):
                if ((i, j) in self.safes and (i, j) not in self.moves_made and (i, j) not in self.mines):
                    safe_choices.append((i,j))
        if len(safe_choices) > 0:
            print('Safe choices: ' + str(safe_choices))
            print('Mines: ' + str(self.mines))
            return random.choice(safe_choices)
        else:
            self.make_random_move()
            
    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        choices = []
        for i in range(self.height):
            for j in range(self.width):
                if((i, j) not in self.moves_made and (i, j) not in self.mines):
                    choices.append((i, j))
        if len(choices) > 0:
            return random.choice(choices)
        else:
            return None
        
        
        
