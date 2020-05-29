# Gemgem (a Bejeweled clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

"""
This program has "gem data structures", which are basically dictionaries
with the following keys:
  'x' and 'y' - The location of the gem on the board. 0,0 is the top left.
                There is also a ROWABOVEBOARD row that 'y' can be set to,
                to indicate that it is above the board.
  'direction' - one of the four constant variables UP, DOWN, LEFT, RIGHT.
                This is the direction the gem is moving.
  'imageNum'  - The integer index into GEMIMAGES to denote which image
                this gem uses.
"""

import copy
import pygame
import random
import sys
import time

from pygame.locals import *

FPS = 30  # frames per second to update the screen
WINDOW_WIDTH = 600  # width of the program's window, in pixels
WINDOW_HEIGHT = 600  # height in pixels

BOARD_WIDTH = 8  # how many columns in the board
BOARD_HEIGHT = 8  # how many rows in the board
GEM_IMAGE_SIZE = 64  # width & height of each space in pixels

# NUM_GEM_IMAGES is the number of gem types. You will need .png image
# files named gem0.png, gem1.png, etc. up to gem(N-1).png.
NUM_GEM_IMAGES = 7
assert NUM_GEM_IMAGES >= 5  # game needs at least 5 types of gems to work

# NUM_MATCH_SOUNDS is the number of different sounds to choose from when
# a match is made. The .wav files are named match0.wav, match1.wav, etc.
NUM_MATCH_SOUNDS = 6

MOVE_RATE = 25  # 1 to 100, larger num means faster animations
DEDUCT_SPEED = 0.8  # reduces score by 1 point every DEDUCT_SPEED seconds.

#             R    G    B
PURPLE = (255, 0, 255)
LIGHT_BLUE = (170, 190, 255)
BLUE = (0, 0, 255)
RED = (255, 100, 100)
BLACK = (0, 0, 0)
BROWN = (85, 65, 0)
HIGHLIGHT_COLOR = PURPLE  # color of the selected gem's border
BG_COLOR = LIGHT_BLUE  # background color on the screen
GRID_COLOR = BLUE  # color of the game board
GAME_OVER_COLOR = RED  # color of the "Game over" text.
GAME_OVER_BG_COLOR = BLACK  # background color of the "Game over" text.
SCORE_COLOR = BROWN  # color of the text for the player's score

# The amount of space to the sides of the board to the edge of the window
# is used several times, so calculate it once here and store in variables.
X_MARGIN = int((WINDOW_WIDTH - GEM_IMAGE_SIZE * BOARD_WIDTH) / 2)
Y_MARGIN = int((WINDOW_HEIGHT - GEM_IMAGE_SIZE * BOARD_HEIGHT) / 2)

# constants for direction values
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

EMPTY_SPACE = -1  # an arbitrary, non-positive value
ROW_ABOVE_BOARD = 'row above board'  # an arbitrary, non-integer value


def main():
    global FPS_CLOCK, DISPLAY_SURF, GEM_IMAGES, GAME_SOUNDS, BASIC_FONT, BOARD_RECTS

    # Initial set up.
    pygame.init()
    FPS_CLOCK = pygame.time.Clock()
    DISPLAY_SURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Gemgem')
    BASIC_FONT = pygame.font.Font('freesansbold.ttf', 36)

    # Load the images
    GEM_IMAGES = []
    for i in range(1, NUM_GEM_IMAGES + 1):
        gemImage = pygame.image.load('gem%s.png' % i)
        if gemImage.get_size() != (GEM_IMAGE_SIZE, GEM_IMAGE_SIZE):
            gemImage = pygame.transform.smoothscale(gemImage, (GEM_IMAGE_SIZE, GEM_IMAGE_SIZE))
        GEM_IMAGES.append(gemImage)

    # Load the sounds.
    GAME_SOUNDS = {}
    GAME_SOUNDS['bad swap'] = pygame.mixer.Sound('badswap.wav')
    GAME_SOUNDS['match'] = []
    for i in range(NUM_MATCH_SOUNDS):
        GAME_SOUNDS['match'].append(pygame.mixer.Sound('match%s.wav' % i))

    # Create pygame.Rect objects for each board space to
    # do board-coordinate-to-pixel-coordinate conversions.
    BOARD_RECTS = []
    for x in range(BOARD_WIDTH):
        BOARD_RECTS.append([])
        for y in range(BOARD_HEIGHT):
            r = pygame.Rect((X_MARGIN + (x * GEM_IMAGE_SIZE),
                             Y_MARGIN + (y * GEM_IMAGE_SIZE),
                             GEM_IMAGE_SIZE,
                             GEM_IMAGE_SIZE))
            BOARD_RECTS[x].append(r)

    while True:
        runGame()


def runGame():
    # Plays through a single game. When the game is over, this function returns.

    # initalize the board
    gameBoard = getBlankBoard()
    score = 0
    fillBoardAndAnimate(gameBoard, [], score)  # Drop the initial gems.

    # initialize variables for the start of a new game
    firstSelectedGem = None
    lastMouseDownX = None
    lastMouseDownY = None
    gameIsOver = False
    lastScoreDeduction = time.time()
    clickContinueTextSurf = None

    while True:  # main game loop
        clickedSpace = None
        for event in pygame.event.get():  # event handling loop
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYUP and event.key == K_BACKSPACE:
                return  # start a new game

            elif event.type == MOUSEBUTTONUP:
                if gameIsOver:
                    return  # after games ends, click to start a new game

                if event.pos == (lastMouseDownX, lastMouseDownY):
                    # This event is a mouse click, not the end of a mouse drag.
                    clickedSpace = checkForGemClick(event.pos)
                else:
                    # this is the end of a mouse drag
                    firstSelectedGem = checkForGemClick((lastMouseDownX, lastMouseDownY))
                    clickedSpace = checkForGemClick(event.pos)
                    if not firstSelectedGem or not clickedSpace:
                        # if not part of a valid drag, deselect both
                        firstSelectedGem = None
                        clickedSpace = None
            elif event.type == MOUSEBUTTONDOWN:
                # this is the start of a mouse click or mouse drag
                lastMouseDownX, lastMouseDownY = event.pos

        if clickedSpace and not firstSelectedGem:
            # This was the first gem clicked on.
            firstSelectedGem = clickedSpace
        elif clickedSpace and firstSelectedGem:
            # Two gems have been clicked on and selected. Swap the gems.
            firstSwappingGem, secondSwappingGem = getSwappingGems(gameBoard, firstSelectedGem,
                                                                  clickedSpace)
            if firstSwappingGem is None and secondSwappingGem is None:
                # If both are None, then the gems were not adjacent
                firstSelectedGem = None  # deselect the first gem
                continue

            # Show the swap animation on the screen.
            boardCopy = getBoardCopyMinusGems(gameBoard, (firstSwappingGem, secondSwappingGem))
            animateMovingGems(boardCopy, [firstSwappingGem, secondSwappingGem], [], score)

            # Swap the gems in the board data structure.
            gameBoard[firstSwappingGem['x']][firstSwappingGem['y']] = secondSwappingGem['imageNum']
            gameBoard[secondSwappingGem['x']][secondSwappingGem['y']] = firstSwappingGem['imageNum']

            # See if this is a matching move.
            matchedGems = findMatchingGems(gameBoard)
            if not matchedGems:
                # Was not a matching move; swap the gems back
                GAME_SOUNDS['bad swap'].play()
                animateMovingGems(boardCopy, [firstSwappingGem, secondSwappingGem], [], score)
                gameBoard[firstSwappingGem['x']][firstSwappingGem['y']] = firstSwappingGem[
                    'imageNum']
                gameBoard[secondSwappingGem['x']][secondSwappingGem['y']] = secondSwappingGem[
                    'imageNum']
            else:
                # This was a matching move.
                scoreAdd = 0
                while matchedGems:
                    # Remove matched gems, then pull down the board.

                    # points is a list of dicts that tells fillBoardAndAnimate()
                    # where on the screen to display text to show how many
                    # points the player got. points is a list because if
                    # the player gets multiple matches, then multiple points text should appear.
                    points = []
                    for gemSet in matchedGems:
                        scoreAdd += (10 + (len(gemSet) - 3) * 10)
                        for gem in gemSet:
                            gameBoard[gem[0]][gem[1]] = EMPTY_SPACE
                        points.append({'points': scoreAdd,
                                       'x': gem[0] * GEM_IMAGE_SIZE + X_MARGIN,
                                       'y': gem[1] * GEM_IMAGE_SIZE + Y_MARGIN})
                    random.choice(GAME_SOUNDS['match']).play()
                    score += scoreAdd

                    # Drop the new gems.
                    fillBoardAndAnimate(gameBoard, points, score)

                    # Check if there are any new matches.
                    matchedGems = findMatchingGems(gameBoard)
            firstSelectedGem = None

            if not canMakeMove(gameBoard):
                gameIsOver = True

        # Draw the board.
        DISPLAY_SURF.fill(BG_COLOR)
        drawBoard(gameBoard)
        if firstSelectedGem is not None:
            highlightSpace(firstSelectedGem['x'], firstSelectedGem['y'])
        if gameIsOver:
            if clickContinueTextSurf is None:
                # Only render the text once. In future iterations, just
                # use the Surface object already in clickContinueTextSurf
                clickContinueTextSurf = BASIC_FONT.render(
                    'Final Score: %s (Click to continue)' % (score), 1, GAME_OVER_COLOR,
                    GAME_OVER_BG_COLOR)
                clickContinueTextRect = clickContinueTextSurf.get_rect()
                clickContinueTextRect.center = int(WINDOW_WIDTH / 2), int(WINDOW_HEIGHT / 2)
            DISPLAY_SURF.blit(clickContinueTextSurf, clickContinueTextRect)
        elif score > 0 and time.time() - lastScoreDeduction > DEDUCT_SPEED:
            # score drops over time
            score -= 1
            lastScoreDeduction = time.time()
        drawScore(score)
        pygame.display.update()
        FPS_CLOCK.tick(FPS)


def getSwappingGems(board, firstXY, secondXY):
    # If the gems at the (X, Y) coordinates of the two gems are adjacent,
    # then their 'direction' keys are set to the appropriate direction
    # value to be swapped with each other.
    # Otherwise, (None, None) is returned.
    firstGem = {'imageNum': board[firstXY['x']][firstXY['y']],
                'x': firstXY['x'],
                'y': firstXY['y']}
    secondGem = {'imageNum': board[secondXY['x']][secondXY['y']],
                 'x': secondXY['x'],
                 'y': secondXY['y']}
    highlightedGem = None
    if firstGem['x'] == secondGem['x'] + 1 and firstGem['y'] == secondGem['y']:
        firstGem['direction'] = LEFT
        secondGem['direction'] = RIGHT
    elif firstGem['x'] == secondGem['x'] - 1 and firstGem['y'] == secondGem['y']:
        firstGem['direction'] = RIGHT
        secondGem['direction'] = LEFT
    elif firstGem['y'] == secondGem['y'] + 1 and firstGem['x'] == secondGem['x']:
        firstGem['direction'] = UP
        secondGem['direction'] = DOWN
    elif firstGem['y'] == secondGem['y'] - 1 and firstGem['x'] == secondGem['x']:
        firstGem['direction'] = DOWN
        secondGem['direction'] = UP
    else:
        # These gems are not adjacent and can't be swapped.
        return None, None
    return firstGem, secondGem


def getBlankBoard():
    # Create and return a blank board data structure.
    board = []
    for x in range(BOARD_WIDTH):
        board.append([EMPTY_SPACE] * BOARD_HEIGHT)
    return board


def canMakeMove(board):
    # Return True if the board is in a state where a matching
    # move can be made on it. Otherwise return False.

    # The patterns in oneOffPatterns represent gems that are configured
    # in a way where it only takes one move to make a triplet.
    oneOffPatterns = (((0, 1), (1, 0), (2, 0)),
                      ((0, 1), (1, 1), (2, 0)),
                      ((0, 0), (1, 1), (2, 0)),
                      ((0, 1), (1, 0), (2, 1)),
                      ((0, 0), (1, 0), (2, 1)),
                      ((0, 0), (1, 1), (2, 1)),
                      ((0, 0), (0, 2), (0, 3)),
                      ((0, 0), (0, 1), (0, 3)))

    # The x and y variables iterate over each space on the board.
    # If we use + to represent the currently iterated space on the
    # board, then this pattern: ((0,1), (1,0), (2,0))refers to identical
    # gems being set up like this:
    #
    #     +A
    #     B
    #     C
    #
    # That is, gem A is offset from the + by (0,1), gem B is offset
    # by (1,0), and gem C is offset by (2,0). In this case, gem A can
    # be swapped to the left to form a vertical three-in-a-row triplet.
    #
    # There are eight possible ways for the gems to be one move
    # away from forming a triple, hence oneOffPattern has 8 patterns.

    for x in range(BOARD_WIDTH):
        for y in range(BOARD_HEIGHT):
            for pat in oneOffPatterns:
                # check each possible pattern of "match in next move" to
                # see if a possible move can be made.
                if (getGemAt(board, x + pat[0][0], y + pat[0][1]) == \
                    getGemAt(board, x + pat[1][0], y + pat[1][1]) == \
                    getGemAt(board, x + pat[2][0], y + pat[2][1]) is not None) or \
                        (getGemAt(board, x + pat[0][1], y + pat[0][0]) == \
                         getGemAt(board, x + pat[1][1], y + pat[1][0]) == \
                         getGemAt(board, x + pat[2][1], y + pat[2][0]) is not None):
                    return True  # return True the first time you find a pattern
    return False


def drawMovingGem(gem, progress):
    # Draw a gem sliding in the direction that its 'direction' key
    # indicates. The progress parameter is a number from 0 (just
    # starting) to 100 (slide complete).
    move_x = 0
    move_y = 0
    progress *= 0.01

    if gem['direction'] == UP:
        move_y = -int(progress * GEM_IMAGE_SIZE)
    elif gem['direction'] == DOWN:
        move_y = int(progress * GEM_IMAGE_SIZE)
    elif gem['direction'] == RIGHT:
        move_x = int(progress * GEM_IMAGE_SIZE)
    elif gem['direction'] == LEFT:
        move_x = -int(progress * GEM_IMAGE_SIZE)

    base_x = gem['x']
    base_y = gem['y']
    if base_y == ROW_ABOVE_BOARD:
        base_y = -1

    pixel_x = X_MARGIN + (base_x * GEM_IMAGE_SIZE)
    pixel_y = Y_MARGIN + (base_y * GEM_IMAGE_SIZE)
    r = pygame.Rect((pixel_x + move_x, pixel_y + move_y, GEM_IMAGE_SIZE, GEM_IMAGE_SIZE))
    DISPLAY_SURF.blit(GEM_IMAGES[gem['imageNum']], r)


def pullDownAllGems(board):
    # pulls down gems on the board to the bottom to fill in any gaps
    for x in range(BOARD_WIDTH):
        gemsInColumn = []
        for y in range(BOARD_HEIGHT):
            if board[x][y] != EMPTY_SPACE:
                gemsInColumn.append(board[x][y])
        board[x] = ([EMPTY_SPACE] * (BOARD_HEIGHT - len(gemsInColumn))) + gemsInColumn


def getGemAt(board, x, y):
    if x < 0 or y < 0 or x >= BOARD_WIDTH or y >= BOARD_HEIGHT:
        return None
    else:
        return board[x][y]


def getDropSlots(board):
    # Creates a "drop slot" for each column and fills the slot with a
    # number of gems that that column is lacking. This function assumes
    # that the gems have been gravity dropped already.
    boardCopy = copy.deepcopy(board)
    pullDownAllGems(boardCopy)

    dropSlots = []
    for i in range(BOARD_WIDTH):
        dropSlots.append([])

    # count the number of empty spaces in each column on the board
    for x in range(BOARD_WIDTH):
        for y in range(BOARD_HEIGHT - 1, -1, -1):  # start from bottom, going up
            if boardCopy[x][y] == EMPTY_SPACE:
                possibleGems = list(range(len(GEM_IMAGES)))
                for offsetX, offsetY in ((0, -1), (1, 0), (0, 1), (-1, 0)):
                    # Narrow down the possible gems we should put in the
                    # blank space so we don't end up putting an two of
                    # the same gems next to each other when they drop.
                    neighborGem = getGemAt(boardCopy, x + offsetX, y + offsetY)
                    if neighborGem is not None and neighborGem in possibleGems:
                        possibleGems.remove(neighborGem)

                newGem = random.choice(possibleGems)
                boardCopy[x][y] = newGem
                dropSlots[x].append(newGem)
    return dropSlots


def findMatchingGems(board):
    gemsToRemove = []  # a list of lists of gems in matching triplets that should be removed
    boardCopy = copy.deepcopy(board)

    # loop through each space, checking for 3 adjacent identical gems
    for x in range(BOARD_WIDTH):
        for y in range(BOARD_HEIGHT):
            # look for horizontal matches
            if getGemAt(boardCopy, x, y) == getGemAt(boardCopy, x + 1, y) == getGemAt(boardCopy,
                                                                                      x + 2,
                                                                                      y) and getGemAt(
                    boardCopy, x, y) != EMPTY_SPACE:
                targetGem = boardCopy[x][y]
                offset = 0
                removeSet = []
                while getGemAt(boardCopy, x + offset, y) == targetGem:
                    # keep checking if there's more than 3 gems in a row
                    removeSet.append((x + offset, y))
                    boardCopy[x + offset][y] = EMPTY_SPACE
                    offset += 1
                gemsToRemove.append(removeSet)

            # look for vertical matches
            if getGemAt(boardCopy, x, y) == getGemAt(boardCopy, x, y + 1) == getGemAt(boardCopy, x,
                                                                                      y + 2) and getGemAt(
                    boardCopy, x, y) != EMPTY_SPACE:
                targetGem = boardCopy[x][y]
                offset = 0
                removeSet = []
                while getGemAt(boardCopy, x, y + offset) == targetGem:
                    # keep checking, in case there's more than 3 gems in a row
                    removeSet.append((x, y + offset))
                    boardCopy[x][y + offset] = EMPTY_SPACE
                    offset += 1
                gemsToRemove.append(removeSet)

    return gemsToRemove


def highlightSpace(x, y):
    pygame.draw.rect(DISPLAY_SURF, HIGHLIGHT_COLOR, BOARD_RECTS[x][y], 4)


def getDroppingGems(board):
    # Find all the gems that have an empty space below them
    boardCopy = copy.deepcopy(board)
    droppingGems = []
    for x in range(BOARD_WIDTH):
        for y in range(BOARD_HEIGHT - 2, -1, -1):
            if boardCopy[x][y + 1] == EMPTY_SPACE and boardCopy[x][y] != EMPTY_SPACE:
                # This space drops if not empty but the space below it is
                droppingGems.append(
                    {'imageNum': boardCopy[x][y], 'x': x, 'y': y, 'direction': DOWN})
                boardCopy[x][y] = EMPTY_SPACE
    return droppingGems


def animateMovingGems(board, gems, points_text, score):
    # pointsText is a dictionary with keys 'x', 'y', and 'points'
    progress = 0  # progress at 0 represents beginning, 100 means finished.
    while progress < 100:  # animation loop
        DISPLAY_SURF.fill(BG_COLOR)
        drawBoard(board)
        for gem in gems:  # Draw each gem.
            drawMovingGem(gem, progress)
        drawScore(score)
        for pointText in points_text:
            pointsSurf = BASIC_FONT.render(str(pointText['points']), 1, SCORE_COLOR)
            pointsRect = pointsSurf.get_rect()
            pointsRect.center = (pointText['x'], pointText['y'])
            DISPLAY_SURF.blit(pointsSurf, pointsRect)

        pygame.display.update()
        FPS_CLOCK.tick(FPS)
        progress += MOVE_RATE  # progress the animation a little bit more for the next frame


def moveGems(board, moving_gems):
    # movingGems is a list of dicts with keys x, y, direction, imageNum
    for gem in moving_gems:
        if gem['y'] != ROW_ABOVE_BOARD:
            board[gem['x']][gem['y']] = EMPTY_SPACE
            move_x = 0
            move_y = 0
            if gem['direction'] == LEFT:
                move_x = -1
            elif gem['direction'] == RIGHT:
                move_x = 1
            elif gem['direction'] == DOWN:
                move_y = 1
            elif gem['direction'] == UP:
                move_y = -1
            board[gem['x'] + move_x][gem['y'] + move_y] = gem['imageNum']
        else:
            # gem is located above the board (where new gems come from)
            board[gem['x']][0] = gem['imageNum']  # move to top row


def fillBoardAndAnimate(board, points, score):
    dropSlots = getDropSlots(board)
    while dropSlots != [[]] * BOARD_WIDTH:
        # do the dropping animation as long as there are more gems to drop
        movingGems = getDroppingGems(board)
        for x in range(len(dropSlots)):
            if len(dropSlots[x]) != 0:
                # cause the lowest gem in each slot to begin moving in the DOWN direction
                movingGems.append(
                    {'imageNum': dropSlots[x][0], 'x': x, 'y': ROW_ABOVE_BOARD, 'direction': DOWN})

        boardCopy = getBoardCopyMinusGems(board, movingGems)
        animateMovingGems(boardCopy, movingGems, points, score)
        moveGems(board, movingGems)

        # Make the next row of gems from the drop slots
        # the lowest by deleting the previous lowest gems.
        for x in range(len(dropSlots)):
            if len(dropSlots[x]) == 0:
                continue
            board[x][0] = dropSlots[x][0]
            del dropSlots[x][0]


def checkForGemClick(pos):
    # See if the mouse click was on the board
    for x in range(BOARD_WIDTH):
        for y in range(BOARD_HEIGHT):
            if BOARD_RECTS[x][y].collidepoint(pos[0], pos[1]):
                return {'x': x, 'y': y}
    return None  # Click was not on the board.


def drawBoard(board):
    for x in range(BOARD_WIDTH):
        for y in range(BOARD_HEIGHT):
            pygame.draw.rect(DISPLAY_SURF, GRID_COLOR, BOARD_RECTS[x][y], 1)
            gemToDraw = board[x][y]
            if gemToDraw != EMPTY_SPACE:
                DISPLAY_SURF.blit(GEM_IMAGES[gemToDraw], BOARD_RECTS[x][y])


def getBoardCopyMinusGems(board, gems):
    # Creates and returns a copy of the passed board data structure,
    # with the gems in the "gems" list removed from it.
    #
    # Gems is a list of dicts, with keys x, y, direction, imageNum

    boardCopy = copy.deepcopy(board)

    # Remove some of the gems from this board data structure copy.
    for gem in gems:
        if gem['y'] != ROW_ABOVE_BOARD:
            boardCopy[gem['x']][gem['y']] = EMPTY_SPACE
    return boardCopy


def drawScore(score):
    scoreImg = BASIC_FONT.render(str(score), 1, SCORE_COLOR)
    scoreRect = scoreImg.get_rect()
    scoreRect.bottomleft = (10, WINDOW_HEIGHT - 6)
    DISPLAY_SURF.blit(scoreImg, scoreRect)


if __name__ == '__main__':
    main()
