import pygame
import pygame.freetype
import random
import sys
import math

GRIDSIZE = 16
MINEPERCENTAGE = 0.15

if len(sys.argv) > 1:
  GRIDSIZE = int(sys.argv[1])
if len(sys.argv) > 2:
  MINEPERCENTAGE = float(sys.argv[2])

CELLSIZE = 32
CELLAMOUNT = GRIDSIZE * GRIDSIZE
WIDTH = CELLSIZE * GRIDSIZE
HEIGHT = WIDTH
FPS = 30

MINES = math.floor(GRIDSIZE*GRIDSIZE * MINEPERCENTAGE)

GREY = (128, 128, 128)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

class Cell:
  def __init__(self, row, col) -> None:
    self.row = row
    self.col = col
    self.cords = (row, col)
    self.isMine = False
    self.isFound = False
    self.isFoundChanged = False
    self.value = 0
    self.isFlagged = False
  def toggleIsFound(self):
    if not self.isFoundChanged:
      self.isFound = not self.isFound
      self.isFoundChanged = True
  def toggleIsFlagged(self):
    self.isFlagged = not self.isFlagged
  def draw(self, surface):
    x = CELLSIZE * self.row
    y = CELLSIZE * self.col
    rect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    rectIcon = pygame.Rect(x + CELLSIZE / 4, y + CELLSIZE / 4, CELLSIZE / 2, CELLSIZE / 2)
    if self.isFound:
      if self.isMine:
        pygame.draw.rect(surface, RED, rectIcon, 0, CELLSIZE)
      else:
        pygame.draw.rect(surface, WHITE, rect)
        if self.value > 0:
          textSurface = FONT.render(str(self.value), True, BLACK)
          textRect = textSurface.get_rect(center=(x + rect.height / 2, y + rect.width /2))
          surface.blit(textSurface, textRect)
    else:
      pygame.draw.rect(surface, GREY, rect)
      if self.isFlagged:
        pygame.draw.rect(surface, RED, rectIcon, 0, CELLSIZE)
    pygame.draw.rect(surface, BLACK, rect, 1)

class Grid:
  def __init__(self) -> None:
    self.isComplete = False
    self.isLost = False
    self.isWon = False
    self.foundCells = 0
    self.fillGrid()
    self.generateMineLocations()
    self.assignMines()
    self.assignValues()

  def fillGrid(self):
    self.grid = []
    self.flags = []
    for i in range(GRIDSIZE):
      self.grid.append([])
      for j in range(GRIDSIZE):
        self.grid[i].append(Cell(i, j))

  def generateMineLocations(self):
    self.mines = []
    def uniqueTuple(list, aMin, aMax, bMin, bMax):
      randomTuple = (random.randint(aMin, aMax), random.randint(bMin, bMax))
      if randomTuple in list:
        return uniqueTuple(list, aMin, aMax, bMin, bMax)
      else:
        return randomTuple
    for i in range(MINES):
      self.mines.append(uniqueTuple(
        self.mines,
        0,
        len(self.grid)-1,
        0,
        len(self.grid[0])-1
        ))
  def assignMines(self):
    for i in range(len(self.grid)):
      for j in range(len(self.grid[i])):
        if (i, j) in self.mines:
          self.grid[i][j].isMine = True
          self.grid[i][j].value = -1
  def assignValues(self):
    for i in self.mines:
      for j in range(-1,2,1):
        for k in range(-1,2,1):
          if j == 0 and k == 0:
            continue

          x = list(i)[0] + j
          y = list(i)[1] + k
          if 0 <= x < GRIDSIZE and 0 <= y < GRIDSIZE:
            if not self.grid[x][y].isMine:
              self.grid[x][y].value += 1
  def find(self, x, y):
    if self.isComplete:
      return
    if self.grid[x][y].isFoundChanged or self.grid[x][y].isFlagged:
      return
    self.grid[x][y].toggleIsFound()
    self.foundCells = self.foundCells + 1
    if self.grid[x][y].value == 0:
      self.findNeighbours(x, y)
    if self.grid[x][y].isMine:
      self.lost()
    if self.foundCells + MINES == CELLAMOUNT:
      self.isComplete = True
      self.isWon = True

  
  def findNeighbours(self, x, y):
    for i in range(-1, 2, 1):
      for j in range(-1, 2, 1):
          if i == 0 and j == 0:
            continue
          cX = x + i
          cY = y + j
          if 0 <= cX < GRIDSIZE and 0 <= cY < GRIDSIZE:
            if not self.grid[cX][cY].isFoundChanged:
              self.find(cX, cY)

  def findNumberNeighbours(self, x, y):
    if self.isComplete:
      return
    flagsFound = 0
    for i in range(-1, 2, 1):
      for j in range(-1, 2, 1):
          if i == 0 and j == 0:
            continue
          cX = x + i
          cY = y + j
          if 0 <= cX < GRIDSIZE and 0 <= cY < GRIDSIZE:
            if self.grid[cX][cY].isFlagged:
              flagsFound = flagsFound + 1
    if flagsFound == self.grid[x][y].value:
      for i in range(-1, 2, 1):
        for j in range(-1, 2, 1):
          if i == 0 and j == 0:
            continue
          cX = x + i
          cY = y + j
          if 0 <= cX < GRIDSIZE and 0 <= cY < GRIDSIZE:
            if not self.grid[cX][cY].isFlagged:
              self.findNeighbours(x, y)


  def flag(self,x,y):
    if self.isComplete:
      return
    if not self.grid[x][y].isFoundChanged:
      self.grid[x][y].toggleIsFlagged()
      if self.grid[x][y].cords in self.flags:
        self.flags.pop(self.flags.index(tuple(self.grid[x][y].cords)))
        return
      self.flags.append(self.grid[x][y].cords)
      return
    self.findNumberNeighbours(x, y)


  def draw(self, surface):
    for i in range(len(self.grid)):
      for j in range(len(self.grid[i])):
        self.grid[i][j].draw(surface)
    
  def lost(self):
    self.isComplete = True
    self.isLost = True
    for i in self.mines:
      x = list(i)[0]
      y = list(i)[1]
      self.grid[x][y].toggleIsFound()


pygame.init()
FONT = pygame.font.SysFont("Arial", 32)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

grid = Grid()

running = True
while running:
  clock.tick(FPS)
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_r:
          grid = Grid()
    if event.type == pygame.MOUSEBUTTONUP:
      pos = list(pygame.mouse.get_pos())
      x = math.floor(pos[0] / CELLSIZE)
      y = math.floor(pos[1] / CELLSIZE)

      if event.button == 1:
        grid.find(x, y)
      if event.button == 3:
        grid.flag(x, y)
  caption = "{} flags left".format(len(grid.mines) - len(grid.flags))
  if grid.isComplete:
    if grid.isWon:
      caption = "You won! | R to restart"
    if grid.isLost:
      caption = "You lost! | R to restart"

  pygame.display.set_caption(caption)
  screen.fill(WHITE)
  grid.draw(screen)


  pygame.display.flip()