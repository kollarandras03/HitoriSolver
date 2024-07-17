from colorama import Fore, Back, Style # type: ignore
import sys
from typing import List, Optional, Union, Tuple, MutableMapping
from enum import Enum
from copy import deepcopy

class Color(Enum):
    WHITE = 1
    GRAY = 2
    BLACK = 3
    def __str__(self) -> str:
        return self.name

class Tile:
    def __init__(self,value: int, color: Color) -> None:
        self.__value: int = value
        self.__color: Color = color
        self.__accessable: bool = True
    def GetValue(self) -> int:
        return self.__value
    def GetColor(self) -> Color:
        return self.__color
    def IsAccessable(self) -> int:
        return self.__accessable
    def SetColor(self, color: Color):
        self.__color = color
    def SetAccessability(self, accessable: bool):
        self.__accessable = accessable
    def __str__(self):
        return f"(v:{self.__value},c:{self.__color},a:{self.__accessable})"
    def __repr__(self):
        return f"(v:{self.__value},c:{self.__color},a:{self.__accessable})"



class Table:
    def __init__(self, file: str):
        self.__table: List[List[Tile]] = []
        tempTable = []
        try:
            with open(file, 'r') as f:
                for line in f:
                    tempTable.append([int(word) for word in line.split()])
                    self.__table.append([])
            self.__lengthx = len(tempTable)
            self.__lengthy = len(tempTable[0])
            for i in range(self.__lengthx):
                for j in range(self.__lengthy):
                    self.__table[i].append(Tile(tempTable[i][j], Color.GRAY))
        except Exception:
            print("Something went wrong during parsing the table.")
    
    # Getters
    def GetField(self,x : int,y : int):
        return self.__table[x][y]
    def GetLengthX(self) -> int:
        return self.__lengthx
    def GetLengthY(self) -> int:
        return self.__lengthy
    
    # Returns wether the board has at least one tile that is isolated by black tiles
    def HasIsolated(self) -> bool:
        self.IsolatePoints()
        for i in range(self.__lengthx):
            for j in range(self.__lengthy):
                if not self.GetField(i,j).IsAccessable():
                    return True
        return False
    
    # Returns wether the board has two neighbouring tiles with color BLACK
    def HasNeighbouringBlacks(self) -> bool:
        for i in range(self.__lengthx - 1):
            for j in range(self.__lengthy - 1):
                if self.GetField(i,j).GetColor() is Color.BLACK and (self.GetField(i+1,j).GetColor() is Color.BLACK or self.GetField(i,j+1).GetColor() is Color.BLACK):
                    return True
        return False
    
    def HasTwoSameWhites(self) -> bool:
        for i in range(self.__lengthx - 1):
            for j in range(self.__lengthy - 1):
                if self.GetField(i,j).GetColor() != Color.WHITE:
                    continue
                else:
                    value = self.GetField(i,j).GetValue()
                    for k in range(i+1, self.__lengthx):
                        if self.GetField(k,j).GetValue() == value and self.GetField(k,j).GetColor() == Color.WHITE:
                            return True
                    for l in range(j+1, self.__lengthy):
                        if self.GetField(i,l).GetValue() == value and self.GetField(i,l).GetColor() == Color.WHITE:
                            return True
        return False    
    
    def IsolatePoints(self):
        # Set every tiles accessability to false
        for i in range(self.__lengthx):
            for j in range(self.__lengthy):
                self.GetField(i,j).SetAccessability(False)
        
        # If tile is black, it is accessable, if white or gray, then also call this on the neighbours
        def CheckNeighbours(i,j):
            if i < 0 or j < 0 or i >= self.__lengthx or j >= self.__lengthy:
                return # index was out of bounds
            elif self.GetField(i,j).IsAccessable():
                return # field was already accessable, preventing recursion bomb
            elif self.GetField(i,j).GetColor() == Color.BLACK:
                self.GetField(i,j).SetAccessability(True) 
            elif self.GetField(i,j).GetColor() == Color.WHITE or self.GetField(i,j).GetColor() == Color.GRAY:
                self.GetField(i,j).SetAccessability(True)
                CheckNeighbours(i-1,j)
                CheckNeighbours(i+1,j)
                CheckNeighbours(i,j-1)
                CheckNeighbours(i,j+1)
            else: # invalid color was given
                pass 
        
        # Starting from a non-black field 
        if self.GetField(0,0).GetColor() != Color.BLACK:
            CheckNeighbours(0,0)
        elif self.GetField(0,1).GetColor() != Color.BLACK:
            CheckNeighbours(0,1)
        else:
            return # Two black tiles found next to each other
 

    def IsBoardValid(self) -> bool:
        return not (self.HasIsolated() or self.HasNeighbouringBlacks() or self.HasTwoSameWhites())


class Model:
    # Constructor
    def __init__(self,table: Table, grays = []):
        self.table: Table = table
        self.lengthx: int = table.GetLengthX()
        self.lengthy: int = table.GetLengthY()
        self.remaining: int = self.lengthx * self.lengthy
        self.grays = deepcopy(grays)
        for i in range(self.lengthx):
            for j in range(self.lengthy):
                if self.GetField(i,j).GetColor() == Color.GRAY:
                    self.grays.append((i,j))

    
    # Returns the tiles that are still gray
    def GetRemaining(self) -> int:
        rem = 0
        for i in range(self.lengthx):
            for j in range(self.lengthy):
                if self.GetField(i,j).GetColor() == Color.GRAY:
                    rem += 1
        return rem
    def IsBoardFinished(self) -> bool:
        for i in range(self.lengthx):
            for j in range(self.lengthy):
                if self.GetField(i,j).GetColor() == Color.GRAY:
                    return False
        return True
    
    # Returns boolean, wether the index is in the matrix
    def IsValidIndex(self, x: int, y: int) -> bool:
        return x >= 0 and y >= 0 and x < self.lengthx and y < self.lengthy

    def GetField(self, x,y) -> Tile:
        return self.table.GetField(x,y)
    
    # String representation
    def __repr__(self):
        representation = ""
        for i in range(self.lengthx):
            representation += Back.LIGHTWHITE_EX
            for j in range(self.lengthy):
                if self.GetField(i,j).GetValue() < 10:
                    num = " " + f"{self.GetField(i,j).GetValue()}"
                else:
                    num = f"{self.GetField(i,j).GetValue()}"
                if self.GetField(i,j).GetColor() == Color.WHITE:
                    representation += Fore.LIGHTGREEN_EX + num + " "
                if self.GetField(i,j).GetColor() == Color.GRAY:
                    representation += f"\x1b[38;2;255;255;255;{0.5 * 255}m{Fore.LIGHTBLACK_EX}{num} \x1b[0m"
                if self.GetField(i,j).GetColor() == Color.BLACK:
                    representation += Fore.RED + num + " "
                representation += Back.LIGHTWHITE_EX
            representation += Style.RESET_ALL + "\n"
        representation += f"Remaining tiles: {self.GetRemaining()}\n"
        return representation
    
    # Same as mapf but with upper bounds for both indexes
    def MapF(self, func, toX = -1, toY = -1):
        if toX == -1 and toY == -1:
            toX = self.lengthx
            toY = self.lengthy
        for i in range(toX):
            for j in range(toY):
                    func(i,j)

    # Returns true if the board is valid, returns false otherwise
    def IsBoardValid(self):
        return self.table.IsBoardValid()

    def PrintTable(self):
        if self.IsBoardFinished():
            print(self)
            print(f"The board is valid: {self.IsBoardValid()}")
            print("The board is finished")
        else:
            print(self)

    # Runs the methods to try and solve the table
    def Solve(self):
        self.RunUniqueSolveMethods()
        if self.IsBoardFinished():
            return
        else:
            self.RunRepetitions()

    def RunRepetitions(self):
        self.MapF(self.WhiteSingleton)
        self.Mark2()

    def GetTable(self):
        return self.table
    def RunUniqueSolveMethods(self):
        #UNIQUE 
        self.MapF(self.OneSpaceBetween,toX = self.lengthx, toY = self.lengthy)
        self.MapF(self.TwoInRows) 
        self.MapF(self.TwoInCols)

    def Mark2(self):
        savedTable: Table = deepcopy(self.table)
        for field in self.grays:
            i = field[0]
            j = field[1]

            if self.GetField(i,j).GetColor() == Color.GRAY:
                model1 = Model(deepcopy(savedTable))
                model1.SetColor(i,j,Color.WHITE)
                model1.RunRepetitions()
                if model1.IsBoardFinished() and model1.IsBoardValid():
                    self.table = model1.table
                    return

                model2 = Model(deepcopy(savedTable))
                model2.SetColor(i,j,Color.BLACK)
                model2.RunRepetitions()
                if model2.IsBoardFinished() and model2.IsBoardValid() :
                    self.table = model2.table
                    return
                        



    # If two of the same number appers in a row, every other num in row should be black
    def TwoInRows(self,i,j):
        if self.IsValidIndex(i,j+1) and self.GetField(i,j).GetValue() == self.GetField(i,j+1).GetValue():
            num = self.GetField(i,j).GetValue()
            for y in range(self.lengthy):
                if num == self.GetField(i,y).GetValue() and y != j and y != j+1:
                    self.SetColor(i,y,Color.BLACK)
    # If two of the same number appers in a column, every other num in column should be black
    def TwoInCols(self, i, j):
        if self.IsValidIndex(i+1,j) and self.GetField(i,j).GetValue() == self.GetField(i+1,j).GetValue():
            num = self.GetField(i,j).GetValue()
            for x in range(self.lengthx):
                if num == self.GetField(x,j).GetValue() and x != i and x != i+1:
                    self.SetColor(x,j,Color.BLACK)
       


    def SetColor(self,i: int,j: int,color: Color) -> bool:
        if i < 0 or j < 0:
            return False # index too small
        if i >= self.lengthx or j >= self.lengthy:
            return False # index too large
        if self.GetField(i,j).GetColor() != Color.GRAY:
            return False # cannot recolor non grays
        self.table.GetField(i,j).SetColor(color)
        if color == Color.BLACK:
            if (i,j) in self.grays:
                self.grays.remove((i,j))
            self.OnColoredBlack(i,j)
            return True
        elif color == Color.WHITE:
            if (i,j) in self.grays:
                self.grays.remove((i,j))
            self.OnColoredWhite(i,j)
            return True
        else:
            return False # cannot color to other colors than white or black
    # Sets the field to white, if it is the only non-black number in that row and column
    def WhiteSingleton(self,i,j):
        num = self.GetField(i,j).GetValue()
        noTilesFound = True
        for x in range(self.lengthx):
            if self.GetField(x,j,).GetValue() == num and self.GetField(x,j,).GetColor() != Color.BLACK and i != x:
                noTilesFound = False
                break
        for y in range(self.lengthy):
            if self.GetField(i,y,).GetValue() == num and self.GetField(i,y,).GetColor() != Color.BLACK and j != y:
                noTilesFound = False
                break
        if noTilesFound:
            self.SetColor(i,j,Color.WHITE)
    # Sets the field black in this row and column with the same value
    def BlackSingleton(self,i,j):
        num = self.GetField(i,j).GetValue()
        for x in range(self.lengthx):
            if self.GetField(x,j,).GetValue() == num and self.GetField(x,j,).GetColor() == Color.GRAY and i != x:
                self.SetColor(x,j,Color.BLACK)
        for y in range(self.lengthy):
            if self.GetField(i,y,).GetValue() == num and self.GetField(i,y,).GetColor() == Color.GRAY and j != y:
                self.SetColor(i,y,Color.BLACK)
    # if there are same values with one tile separating them, that tile must be white
    def OneSpaceBetween(self, i, j):
        if self.IsValidIndex(i,j+2) and self.GetField(i,j).GetValue() == self.GetField(i,j+2).GetValue():
            self.SetColor(i,j+1,Color.WHITE)
        if self.IsValidIndex(i+2,j) and self.GetField(i,j).GetValue() == self.GetField(i+2,j).GetValue():
            self.SetColor(i+1,j,Color.WHITE)
    # This should be called when a Field gets colored to white
    def OnColoredWhite(self, x, y):
        self.BlackSingleton(x,y)
    # This should be called to any black's neighbour, prevents enclosing of white
    def PreventObstruction(self, x , y):
        if not self.IsValidIndex(x,y):
            return
        coords = [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]
        coords = list(filter((lambda xy: self.IsValidIndex(xy[0],xy[1])), coords))
        tiles = []
        for c in coords:
            tiles.append(self.GetField(c[0],c[1]))
        cleaned: List[Tile] = list(filter((lambda x: x != None), tiles))
        blackCount = 0
        neighbours = len(cleaned)
        for i in range(neighbours):
            if cleaned[i].GetColor() == Color.BLACK:
                blackCount += 1
        if blackCount + 1 == neighbours:
            self.SetColor(x+1,y,Color.WHITE)
            self.SetColor(x-1,y,Color.WHITE)
            self.SetColor(x,y+1,Color.WHITE)
            self.SetColor(x,y-1,Color.WHITE)
    # This should be called when a Field gets colored to black
    def OnColoredBlack(self, x, y):
        # Checks if it reduced the occurence of a num to 1 in that row or column
        num = self.GetField(x,y,).GetValue()
        for i in range(self.lengthx):
            if self.GetField(i,y,).GetValue() == num and self.GetField(i,y,).GetColor() != Color.BLACK and i != x:
                self.WhiteSingleton(i,y)
        for j in range(self.lengthy):
            if self.GetField(x,j,).GetValue() == num and self.GetField(x,j,).GetColor() != Color.BLACK and j != y:
                self.WhiteSingleton(x,j)

        self.PreventObstruction(x-1,y)
        self.PreventObstruction(x+1,y)
        self.PreventObstruction(x,y-1)
        self.PreventObstruction(x,y+1)
        
        # Set surrounding colors white 
        self.SetColor(x-1,y,Color.WHITE)
        self.SetColor(x+1,y,Color.WHITE)
        self.SetColor(x,y-1,Color.WHITE)
        self.SetColor(x,y+1,Color.WHITE)  



table = Table(f"{sys.argv[1]}")
model = Model(table)
model.Solve()
print(model)
print(model.IsBoardValid())







