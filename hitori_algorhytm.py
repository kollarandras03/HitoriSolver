from colorama import Fore, Back, Style # type: ignore
import time

# TODOS:
# fix the algorhytm that tries to solve the table when the deterministic approach fails
# finish the counter showing of how many tiles are remaining
# make it so that it is visible when a tile changes 
# make map generator
# make a more detailed validity checker


# CONSTANTS
WHITE  = "W"
GRAY   = "G"
BLACK  = "B"
RED    = "R"
NUMBER     = 0
COLOR      = 1
ACCESSABLE = 2
COL = "Column"
ROW = "Row"

#starting time
start = time.time()
t0 = time.process_time()

# TO BE IMPLEMENTED
# 5 x 
# 5 5  - a sarokban lévő fekete kell legyen

# 5
# 5 1  - a nem megegyező érték fehér kell legyen

# F x - a sarokban lévő fekete lehet
# F F

class CheckedException(Exception):
    pass
class OutIndexingException(Exception):
    pass

class Table:
    def __init__(self,file : str):
        self.__table = []
        with open(file, 'r') as f:
            for line in f:
                self.__table.append([int(word) for word in line.split()])
        self.__lengthx = len(self.__table)
        self.__lengthy = len(self.__table[0])
        for i in range(self.__lengthx):
            for j in range(self.__lengthy):
                self.__table[i][j] = [self.__table[i][j], GRAY, False]
    def GetField(self,x : int,y : int):
        if x < 0 or y < 0 or x >= self.__lengthx or y >= self.__lengthy:
            return None
        else:
            return self.__table[x][y]
    def SetAccess(self,x : int, y : int, isAccessable : bool) -> None:
        self.__table[x][y][ACCESSABLE] = isAccessable
    def SetColor(self,x : int,y : int,color) -> None:
        try:
            self.__table[x][y][COLOR] = color
        except:
            raise OutIndexingException()
    def GetLengthX(self) -> int:
        return self.__lengthx
    def GetLengthY(self) -> int:
        return self.__lengthy
    def NoIsolation(self) -> bool:
        for i in range(self.__lengthx):
            for j in range(self.__lengthy):
                if not self.GetField(i,j)[ACCESSABLE]:
                    return False
        return True

class Model:
    # Constructor
    def __init__(self,table : Table):
        self.table : Table = table
        self.lengthx : int = table.GetLengthX()
        self.lengthy : int = table.GetLengthY()
        self.errors = []
        self.cache = []
        self.changed : bool = True
        self.remaining = self.lengthx * self.lengthy
        self.changedVals = []
        self.findingTail = False
    # String Representation
    def __repr__(self):
        representation = ""
        for i in range(self.lengthx):
            representation += Back.LIGHTWHITE_EX
            for j in range(self.lengthy):
                if self.GetField(i,j)[NUMBER] < 10:
                    num = " " + f"{self.GetField(i,j)[NUMBER]}"
                else:
                    num = f"{self.GetField(i,j)[NUMBER]}"

                #if [i,j] in self.changedVals: 
                #    representation += Back.LIGHTYELLOW_EX

                if self.GetField(i,j)[COLOR] == WHITE:
                    representation += Fore.LIGHTGREEN_EX + num + " "
                if self.GetField(i,j)[COLOR] == GRAY:
                    representation += f"\x1b[38;2;255;255;255;{0.5 * 255}m{Fore.LIGHTBLACK_EX}{num} \x1b[0m"
                if self.GetField(i,j)[COLOR] == BLACK:
                    representation += Fore.RED + num + " "
                if self.GetField(i,j)[COLOR] == RED:
                    representation += Fore.BLUE + num + " "
                representation += Back.LIGHTWHITE_EX
                
            representation += Style.RESET_ALL + "\n"
            #representation += f"Remaining tiles: {self.remaining}\n"
        if self.changed:
            self.changed = False
            self.changedVals = []
            return representation
        else:
            return "Table did not change"
    # Return field if exists, otherwise returns None
    def GetField(self, x,y):
        if x < 0 or y < 0 or x >= self.lengthx or y >= self.lengthy:
            self.errors.append(f"Index was out of bounds in function call:GetField({x},{y})")
            raise OutIndexingException()
        else:
            return self.table.GetField(x,y)
        
    # If index exists and field was white, sets color and returns true, otherwise returns false
    def SetColor(self,i,j,color):
        if i < 0 or j < 0:
            self.errors.append(f"Negative index in function: SetColor({i},{j},{color})")
            return False
        if i >= self.lengthx or j >= self.lengthy:
            self.errors.append(f"Index too large in function: SetColor({i},{j},{color})")
            return False
        if self.GetField(i,j)[COLOR] != GRAY:
            self.errors.append(f"Cannot color a non-gray element in function: SetColor({i},{j},{color})")
            return False
        self.table.SetColor(i,j,color)
        self.changed = True
        self.remaining -= 1
        if self.remaining == 0:
            print("\n\nBoard is finished:")
            print(self)
        self.changedVals.append([i,j])
        if color == BLACK:
            self.OnColoredBlack(i,j)
            return True
        if color == WHITE:
            self.OnColoredWhite(i,j)
            return True
        
    # Runs the methods to try and solve the table
    def Solve(self):
        self.MapF(self.OneSpaceBetween) # UNIQUE
        print(self)
        self.MapF(self.TwoInRows) # UNIQUE
        print(self)
        self.MapF(self.TwoInCols) # UNIQUE
        print(self)
        self.DoubleTwoColumns() # UNIQUE
        print(self)
        self.DoubleTwoRows() # UNIQUE
        print(self)
        self.MapF(self.WhiteSingleton) # REP
        print(self)
        self.MapF(self.PaintTailsBlack) # REP
        print(self)
        #self.MapF(self.MarkThenFlood)
        #print(self)
    
    # needs fixing
    def MarkThenFlood(self, x, y):
        if self.GetField(x,y)[COLOR] != GRAY:
            return
        tmp = []
        tiles = self.remaining
        self.remaining = -1
        for i in range(self.lengthx):
            tmp.append([])
            for j in range(self.lengthy):
                tmp[i].append(self.GetField(i,j)[COLOR])
        self.SetColor(x,y,BLACK)
        self.Solve()
        isolated = self.NoIsolation()         
        for i in range(self.lengthx):
            for j in range(self.lengthy):
                self.SetColor(i,j,GRAY)
                self.SetColor(i,j,tmp[i][j])
                self.changedVals = []
        self.remaining = tiles
        if isolated:
            self.SetColor(x,y,WHITE)


    # If this is gray and whiteNeighbours + 1 == neighbours, then it can be black 
    def PaintTailsBlack(self, x, y):
        if self.GetField(x,y)[COLOR] != GRAY:
            return
        coords = [(x+1,y+1),
                  (x+1,y  ),
                  (x+1,y-1),
                  (x  ,y-1),
                  (x  ,y+1),
                  (x-1,y  ),
                  (x-1,y+1),
                  (x-1,y-1)
                  ]

        tiles = []
        for c in coords:
            try:
                tiles.append(self.GetField(c[0],c[1]))
            except OutIndexingException:
                pass
        cleaned = list(filter((lambda x: x != None), tiles))
        neighbours = len(cleaned)
        whiteCount = len(list(filter((lambda x: x[COLOR] == WHITE),cleaned)))
        if whiteCount + 1 == neighbours and whiteCount == 7 or whiteCount == neighbours:
            self.SetColor(x,y,BLACK)

    # This should be called to any black's neighbour, prevents enclosing of white
    def PreventObstruction(self, x , y):
        coords = [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]
        tiles = []
        for c in coords:
            try:
                tiles.append(self.GetField(c[0],c[1]))
            except OutIndexingException:
                pass
        cleaned = list(filter((lambda x: x != None), tiles))
        neighbours = len(cleaned)
        blackCount = len(list(filter((lambda x: x[COLOR] == BLACK),cleaned)))

        if blackCount + 1 == neighbours:
            self.SetColor(x+1,y,WHITE)
            self.SetColor(x-1,y,WHITE)
            self.SetColor(x,y+1,WHITE)
            self.SetColor(x,y-1,WHITE)

    # This should be called when a Field gets colored to white
    def OnColoredWhite(self, x, y):
        self.BlackSingleton(x,y)

    # This should be called when a Field gets colored to black
    def OnColoredBlack(self, x, y):
        # Checks if it reduced the occurence of a num to 1 in that row or column
        num = self.GetField(x,y,)[NUMBER]
        for i in range(self.lengthx):
            if self.GetField(i,y,)[NUMBER] == num and self.GetField(i,y,)[COLOR] != BLACK and i != x:
                self.WhiteSingleton(i,y)
        for j in range(self.lengthy):
            if self.GetField(x,j,)[NUMBER] == num and self.GetField(x,j,)[COLOR] != BLACK and j != y:
                self.WhiteSingleton(x,j)
        
        self.PreventObstruction(x-1,y)
        self.PreventObstruction(x+1,y)
        self.PreventObstruction(x,y-1)
        self.PreventObstruction(x,y+1)

        # Set surrounding colors white 
        self.SetColor(x-1,y,WHITE)
        self.SetColor(x+1,y,WHITE)
        self.SetColor(x,y-1,WHITE)
        self.SetColor(x,y+1,WHITE)  

    # Returns true if the board is valid, returns false otherwise
    def ValidityCheck(self):
        return self.NoIsolation()
    # Maps a function through every element of table, logs exceptions
    def MapF(self, func):
        for i in range(self.lengthx):
            for j in range(self.lengthy):
                    try:
                        func(i,j)
                    except CheckedException:
                        pass
                    
    # If two of the same number appers in a row, every other num in row should be black
    def TwoInRows(self,i,j):
        try:
            if self.GetField(i,j)[NUMBER] == self.GetField(i,j+1)[NUMBER]:
                num = self.GetField(i,j)[NUMBER]
                self.cache.append([num,i,j,ROW])
                for y in range(self.lengthy):
                    if num == self.GetField(i,y)[NUMBER] and y != j and y != j+1:
                        self.SetColor(i,y,BLACK)
        except OutIndexingException:
            raise CheckedException()
        
    # If two of the same number appers in a column, every other num in column should be black
    def TwoInCols(self, i, j):
        try:
            if self.GetField(i,j)[NUMBER] == self.GetField(i+1,j)[NUMBER]:
                num = self.GetField(i,j)[NUMBER]
                self.cache.append([num, i, j, COL])
                for x in range(self.lengthx):
                    if num == self.GetField(x,j)[NUMBER] and x != i and x != i+1:
                        self.SetColor(x,j,BLACK)
        except OutIndexingException:
            raise CheckedException()
        
    # If two of the same number is separated by exactly one tile, that tile should be white
    def OneSpaceBetween(self, i, j):
        try:
            if self.GetField(i,j)[NUMBER] == self.GetField(i,j+2)[NUMBER]:
                self.SetColor(i,j+1,WHITE)
            if self.GetField(i,j)[NUMBER] == self.GetField(i+2,j)[NUMBER]:
                self.SetColor(i+1,j,WHITE)
        except OutIndexingException:
            raise CheckedException()
        
    # Runs from the top left, checks the whole board for inaccesable areas
    def NoIsolation(self):
        # Set every tiles accessability to false
        for i in range(self.lengthx): 
            for j in range(self.lengthy):
                self.table.SetAccess(i,j,False)
        
        # If tile is black, it is accessable, if white or gray, then also call this on the neighbours
        def CheckNeighbours(i,j):
            if i < 0 or j < 0 or i >= self.lengthx or j >= self.lengthy:
                return
            if self.GetField(i,j)[COLOR] == BLACK:
                self.table.SetAccess(i,j,True)
            elif self.GetField(i,j)[COLOR] == WHITE or self.GetField(i,j)[COLOR] == GRAY:
                self.table.SetAccess(i,j,True)
                try:
                    if not self.GetField(i-1,j)[ACCESSABLE]:
                        CheckNeighbours(i-1,j)
                except OutIndexingException:
                    pass
                try:
                    if not self.GetField(i+1,j)[ACCESSABLE]:
                        CheckNeighbours(i+1,j)
                except OutIndexingException:
                    pass
                try:
                    if not self.GetField(i,j-1)[ACCESSABLE]:
                        CheckNeighbours(i,j-1)
                except OutIndexingException:
                    pass
                try:
                    if not self.GetField(i,j+1)[ACCESSABLE]:
                        CheckNeighbours(i,j+1)
                except OutIndexingException:
                    pass
            else: # Red or invalid color was given
                pass 
        
        # Starting from a non-black field 
        if self.table.GetField(0,0)[COLOR] != BLACK:
            self.table.SetAccess(0,0,True)
            CheckNeighbours(0,0)
        elif self.table.GetField(0,1)[COLOR] != BLACK:
            self.table.SetAccess(0,1,True)
            CheckNeighbours(0,1)
        else:
            raise Exception("Found two black tiles next to each other in isolation check!")
        return self.table.NoIsolation()
    
    def DoubleTwoRows(self):
        elements = list(filter(lambda x : x[3] == ROW , self.cache))
        for e1 in elements:
            for e2 in elements:
                if e1 == e2:
                    continue # paint black [x,j] [x, j+1]
                if e1[0] == e2[0] and e1[1] != e2[1] and e1[2] == e2[2]:
                    j = e1[2]
                    num = e1[0]
                    for x in range(self.lengthx): # paint black [i,y] [i+1, y] 
                        if self.GetField(x,j)[NUMBER] != num or self.GetField(x,j+1)[NUMBER] != num:
                            if self.GetField(x,j)[NUMBER] == num: 
                                self.SetColor(x,j, BLACK)
                            if self.GetField(x, j+1)[NUMBER] == num:
                                self.SetColor(x,j+1, BLACK)
    
    def DoubleTwoColumns(self):
        elements = list(filter(lambda x : x[3] == COL , self.cache))
        for e1 in elements:
            for e2 in elements:
                if e1 == e2:
                    continue
                if e1[0] == e2[0] and e1[1] == e2[1] and e1[2] != e2[2]:
                    i = e1[1]
                    num = e1[0]
                    for y in range(self.lengthy): # paint black [i,y] [i+1, y] 
                        if self.GetField(i,y)[NUMBER] != num or self.GetField(i+1,y)[NUMBER] != num:
                            if self.GetField(i,y)[NUMBER] == num: 
                                self.SetColor(i,y, BLACK)
                            if self.GetField(i+1, y)[NUMBER] == num:
                                self.SetColor(i+1,y, BLACK)
                     
    # Sets the field to white, if it is the only non-black number in that row and column
    def WhiteSingleton(self,i,j):
        num = self.GetField(i,j)[NUMBER]
        flag = True
        for x in range(self.lengthx):
            if self.GetField(x,j,)[NUMBER] == num and self.GetField(x,j,)[COLOR] != BLACK and i != x:
                flag = False
        for y in range(self.lengthy):
            if self.GetField(i,y,)[NUMBER] == num and self.GetField(i,y,)[COLOR] != BLACK and j != y:
                flag = False
        if flag:
            self.SetColor(i,j,WHITE)
    
    def BlackSingleton(self,i,j):
        num = self.GetField(i,j)[NUMBER]
        for x in range(self.lengthx):
            if self.GetField(x,j,)[NUMBER] == num and self.GetField(x,j,)[COLOR] != BLACK and i != x:
                self.SetColor(x,j,BLACK)
        for y in range(self.lengthy):
            if self.GetField(i,y,)[NUMBER] == num and self.GetField(i,y,)[COLOR] != BLACK and j != y:
                self.SetColor(i,y,BLACK)

table = Table(input("Input path of file:"))
model = Model(table)
model.Solve()
print(model)
end = time.time()

# total time taken
print("Succesfully exited in: ", end-start)
print("Time elapsed: ", time.process_time() - t0)



