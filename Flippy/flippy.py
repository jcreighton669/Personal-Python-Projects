# Fluppy (an Othello or Reversi clone)
# By Al Sweigart
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

# Based on the "reversi.py" code that originally appeared in "Invent Your Own Computer Games with
# Python", chapter 15:
# http://inventwithpython.com/chapter15.html

import copy
import pygame
import random
import sys
import time

from pygame.locals import *

FPS = 10  # frames per second to update the screen
WINDOW_WIDTH = 640  # width of the program's window, in pixels
WINDOW_HEIGHT = 480  # height in pixels
SPACE_SIZE = 50  # width & height of each space on the board, in pixels
BOARD_WIDTH = 8  # how many columns of spaces on the game board
BOARD_HEIGHT = 8  # how many rows of spaces on the game board
WHITE_TILE = 'WHITE_TILE'  # an arbitrary but unique value
BLACK_TILE = 'BLACK_TILE'  # an arbitrary but unique value
EMPTY_SPACE = 'EMPTY_SPACE'  # an arbitrary but unique value
HINT_TILE = 'HINT_TILE'  # an arbitrary but unique value
ANIMATION_SPEED = 25  # integer from 1 to 100, higher is faster animation

# Amount of space on the left & right side (X_MARGIN) or above and below (Y_MARGIN) the game
# board, in pixels.
X_MARGIN = int((WINDOW_WIDTH - (BOARD_WIDTH * SPACE_SIZE)) / 2)
Y_MARGIN = int((WINDOW_HEIGHT - (BOARD_HEIGHT * SPACE_SIZE)) / 2)

#          R    G    B
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 155, 0)
MIDNIGHT_BLUE = (25, 25, 112)
BROWN = (174, 94, 0)

TEXT_BG_COLOR_1 = MIDNIGHT_BLUE
TEXT_BG_COLOR_2 = GREEN
GRID_LINE_COLOR = BLACK
TEXT_COLOR = WHITE
HINT_COLOR = BROWN


def main():
    global MAIN_CLOCK, DISPLAY_SURF, FONT, BIG_FONT, BG_IMAGE

    pygame.init()
    MAIN_CLOCK = pygame.time.Clock()
    DISPLAY_SURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('FLIPPY')
    FONT = pygame.font.Font('freesansbold.ttf', 16)
    BIG_FONT = pygame.font.Font('freesansbold.ttf', 32)

    # Set up the background image.
    board_image = pygame.image.load('flippyboard.png')
    # Use smooth_scale() to stretch the board image to fit the entire board:
    board_image = pygame.transform.smoothscale(board_image, (BOARD_WIDTH * SPACE_SIZE,
                                                             BOARD_HEIGHT * SPACE_SIZE))
    board_image_rect = board_image.get_rect()
    board_image_rect.topleft = (X_MARGIN, Y_MARGIN)
    BG_IMAGE = pygame.image.load('flippybackground.png')
    # Use smooth_scale() to stretch the background image to fit the entire window:
    BG_IMAGE = pygame.transform.smoothscale(BG_IMAGE, (WINDOW_WIDTH, WINDOW_HEIGHT))
    BG_IMAGE.blit(board_image, board_image_rect)

    # Run the main game.
    while True:
        if run_game() is False:
            break


def run_game():
    # Plays a single game of reversi each time this function is called.

    # Reset the board and game.
    main_board = get_new_board()
    reset_board(main_board)
    show_hints = False
    turn = random.choice(['computer', 'player'])

    # Draw the starting board and ask the player what color they want.
    draw_board(main_board)
    player_tile, computer_tile = enter_player_tile()

    # Make the Surface and Rect objects for the "New Game" and "Hints" buttons
    new_game_surf = FONT.render('New Game', True, TEXT_COLOR, TEXT_BG_COLOR_2)
    new_game_rect = new_game_surf.get_rect()
    new_game_rect.topright = (WINDOW_WIDTH - 8, 10)
    hints_surf = FONT.render('Hints', True, TEXT_COLOR, TEXT_BG_COLOR_2)
    hints_rect = hints_surf.get_rect()
    hints_rect.topright = (WINDOW_WIDTH - 8, 40)

    while True:  # main game loop
        # Keep looping for player and computer's turns.
        if turn == 'player':
            # Player's turn:
            if get_valid_moves(main_board, player_tile) == []:
                # If it's the player's turn but they can't move, then end the game.
                break
            move_x_y = None
            while move_x_y == None:
                # Keep looping until the player clicks on a valid space.

                # Determine which board data structure to use for display.
                if show_hints:
                    board_to_draw = get_board_with_valid_moves(main_board, player_tile)
                else:
                    board_to_draw = main_board

                check_for_quit()
                for event in pygame.event.get():  # event handling loop
                    if event.type == MOUSEBUTTONUP:
                        # Handle mouse click events
                        mouse_x, mouse_y = event.pos
                        if new_game_rect.collidepoint((mouse_x, mouse_y)):
                            # start a new game
                            return True
                        elif hints_rect.collidepoint((mouse_x, mouse_y)):
                            # Toggle hints mode
                            show_hints = not show_hints
                        # move_x_y is set to a two-item tuple XY coordinate, or None value
                        move_x_y = get_space_clicked(mouse_x, mouse_y)
                        if move_x_y != None and not is_valid_move(main_board, player_tile,
                                                                  move_x_y[0], move_x_y[1]):
                            move_x_y = None

                # Draw the game board.
                draw_board(board_to_draw)
                draw_info(board_to_draw, player_tile, computer_tile, turn)

                # Draw the "New Game" and "Hints" buttons.
                DISPLAY_SURF.blit(new_game_surf, new_game_rect)
                DISPLAY_SURF.blit(hints_surf, hints_rect)

                MAIN_CLOCK.tick(FPS)
                pygame.display.update()

            # Make the move and end the turn.
            make_move(main_board, player_tile, move_x_y[0], move_x_y[1], True)
            if get_valid_moves(main_board, computer_tile) != []:
                # Only set for the computer's turn if it can make a move.
                turn = 'computer'

        else:
            # Computer's turn:
            if get_valid_moves(main_board, computer_tile) == []:
                # If it was set to be the computer's turn but they can't move, then end the game.
                break

            # Draw the board.
            draw_board(main_board)
            draw_info(main_board, player_tile, computer_tile, turn)

            # Draw the "New Game" and "Hints" buttons.
            DISPLAY_SURF.blit(new_game_surf, new_game_rect)
            DISPLAY_SURF.blit(hints_surf, hints_rect)

            # Make it look like the computer is thinking by pausing a bit.
            pause_until = time.time() + random.randint(5, 15) * 0.1
            while time.time() < pause_until:
                pygame.display.update()

            # Make the move and end the turn.
            x, y = get_computer_move(main_board, computer_tile)
            make_move(main_board, computer_tile, x, y, True)
            if get_valid_moves(main_board, player_tile) != []:
                # Only set for the player's turn if they can make a move.
                turn = 'player'

    # Display the final score.
    draw_board(main_board)
    scores = get_score_of_board(main_board)

    # Determine the text of the message to display.
    if scores[player_tile] > scores[computer_tile]:
        text = 'You beat the computer by %s points! Congratulations!' % (scores[player_tile] -
                                                                         scores[computer_tile])
    elif scores[player_tile] < scores[computer_tile]:
        text = 'You lost. The computer beat you by %s points.' % (scores[computer_tile] - scores[
            player_tile])
    else:
        text = 'The game was a tie!'

    text_surf = FONT.render(text, True, TEXT_COLOR, TEXT_BG_COLOR_1)
    text_rect = text_surf.get_rect()
    text_rect.center = (int(WINDOW_WIDTH / 2), int(WINDOW_HEIGHT / 2))
    DISPLAY_SURF.blit(text_surf, text_rect)

    # Display the "Play again?" text with Yes and No buttons.
    text_2_surf = BIG_FONT.render('Play again?', True, TEXT_COLOR, TEXT_BG_COLOR_1)
    text_2_rect = text_2_surf.get_rect()
    text_2_rect.center = (int(WINDOW_WIDTH / 2), int(WINDOW_HEIGHT / 2) + 50)

    # Make "Yes" button.
    yes_surf = BIG_FONT.render('Yes', True, TEXT_COLOR, TEXT_BG_COLOR_1)
    yes_rect = yes_surf.get_rect()
    yes_rect.center = (int(WINDOW_WIDTH / 2) - 60, int(WINDOW_HEIGHT / 2) + 90)

    # Make "No" button.
    no_surf = BIG_FONT.render('No', True, TEXT_COLOR, TEXT_BG_COLOR_1)
    no_rect = no_surf.get_rect()
    no_rect.center = (int(WINDOW_WIDTH / 2) + 60, int(WINDOW_HEIGHT / 2) + 90)

    while True:
        # Process events until the user clicks on Yes or No.
        check_for_quit()
        for event in pygame.event.get():  # event handling loop
            if event.type == MOUSEBUTTONUP:
                mouse_x, mouse_y = event.pos
                if yes_rect.collidepoint((mouse_x, mouse_y)):
                    return True
                elif no_rect.collidepoint((mouse_x, mouse_y)):
                    return False
        DISPLAY_SURF.blit(text_surf, text_rect)
        DISPLAY_SURF.blit(text_2_surf, text_2_rect)
        DISPLAY_SURF.blit(yes_surf, yes_rect)
        DISPLAY_SURF.blit(no_surf, no_rect)
        pygame.display.update()
        MAIN_CLOCK.tick(FPS)


def translate_board_to_pixel_coord(x, y):
    return X_MARGIN + x * SPACE_SIZE + int(SPACE_SIZE / 2), Y_MARGIN + y * SPACE_SIZE + int(
        SPACE_SIZE / 2)


def animate_tile_change(tiles_to_flip, tile_color, additional_tile):
    # Draw the additional tile that was just laid down. (Otherwise we'd have to completely redraw
    # the board & the board info.)
    if tile_color == WHITE_TILE:
        additional_tile_color = WHITE
    else:
        additional_tile_color = BLACK
    additional_tile_x, additional_tile_y = translate_board_to_pixel_coord(additional_tile[0],
                                                                          additional_tile[1])
    pygame.draw.circle(DISPLAY_SURF, additional_tile_color,
                       (additional_tile_x, additional_tile_y), int(SPACE_SIZE / 2) - 4)
    pygame.display.update()

    for rgb_values in range(0, 255, int(ANIMATION_SPEED * 2.55)):
        if rgb_values > 255:
            rgb_values = 255
        elif rgb_values < 0:
            rgb_values = 0

        if tile_color == WHITE_TILE:
            color = tuple([rgb_values] * 3)  # rgb_values goes from 0 to 255
        elif tile_color == BLACK_TILE:
            color = tuple([255 - rgb_values] * 3)  # rgb_values goes from 255 to 0

        for x, y in tiles_to_flip:
            center_x, center_y = translate_board_to_pixel_coord(x, y)
            pygame.draw.circle(DISPLAY_SURF, color, (center_x, center_y), int(SPACE_SIZE / 2) - 4)

        pygame.display.update()
        MAIN_CLOCK.tick(FPS)
        check_for_quit()


def draw_board(board):
    # Draw background of board.
    DISPLAY_SURF.blit(BG_IMAGE, BG_IMAGE.get_rect())

    # Draw grid lines of the board.
    for x in range(BOARD_WIDTH + 1):
        # Draw the horizontal lines.
        start_x = (x * SPACE_SIZE) + X_MARGIN
        start_y = Y_MARGIN
        end_x = (x * SPACE_SIZE) + X_MARGIN
        end_y = Y_MARGIN + (BOARD_HEIGHT * SPACE_SIZE)
        pygame.draw.line(DISPLAY_SURF, GRID_LINE_COLOR, (start_x, start_y), (end_x, end_y))
    for y in range(BOARD_HEIGHT + 1):
        # Draw the vertical lines
        start_x = X_MARGIN
        start_y = (y * SPACE_SIZE) + Y_MARGIN
        end_x = X_MARGIN + (BOARD_WIDTH * SPACE_SIZE)
        end_y = (y * SPACE_SIZE) + Y_MARGIN
        pygame.draw.line(DISPLAY_SURF, GRID_LINE_COLOR, (start_x, start_y), (end_x, end_y))

    # Draw the black & white tiles or hint spots.
    for x in range(BOARD_WIDTH):
        for y in range(BOARD_HEIGHT):
            center_x, center_y = translate_board_to_pixel_coord(x, y)
            if board[x][y] == WHITE_TILE or board[x][y] == BLACK_TILE:
                if board[x][y] == WHITE_TILE:
                    tile_color = WHITE
                else:
                    tile_color = BLACK
                pygame.draw.circle(DISPLAY_SURF, tile_color, (center_x, center_y), int(SPACE_SIZE
                                                                                       / 2) - 4)
            if board[x][y] == WHITE_TILE:
                pygame.draw.rect(DISPLAY_SURF, HINT_COLOR, (center_x - 4, center_y - 4, 8, 8))


def get_space_clicked(mouse_x, mouse_y):
    # Return a tuple of two integers of the board space coordinates where the mouse was clicked.
    # (or returns None not in any space.)
    for x in range(BOARD_WIDTH):
        for y in range(BOARD_HEIGHT):
            if x * SPACE_SIZE + X_MARGIN < mouse_x < (x + 1) * SPACE_SIZE + X_MARGIN \
                    and y * SPACE_SIZE + Y_MARGIN < mouse_y < (y + 1) * SPACE_SIZE + \
                    Y_MARGIN:
                return x, y
    return None


def draw_info(board, player_tile, computer_tile, turn):
    # Draws scores and whose turn it is at the bottom of the screen.
    scores = get_score_of_board(board)
    score_surf = FONT.render("Player Score: %s Computer Score: %s %s's Turn" % (str(scores[
                                                                                        player_tile]), str(scores[computer_tile]), turn.title()), True, TEXT_COLOR)
    score_rect = score_surf.get_rect()
    score_rect.bottomleft = (10, WINDOW_HEIGHT - 5)
    DISPLAY_SURF.blit(score_surf, score_rect)


def reset_board(board):
    # Blanks out the board it is passed, and sets up starting tiles.
    for x in range(BOARD_WIDTH):
        for y in range(BOARD_HEIGHT):
            board[x][y] = EMPTY_SPACE

    # Add starting pieces to the center
    board[3][3] = WHITE_TILE
    board[3][4] = BLACK_TILE
    board[4][3] = BLACK_TILE
    board[4][4] = WHITE_TILE


def get_new_board():
    # Creates a brand new, empty board data structure.
    board = []
    for i in range(BOARD_WIDTH):
        board.append([EMPTY_SPACE] * BOARD_HEIGHT)

    return board


def is_valid_move(board, tile, x_start, y_start):
    # Returns False if the player's move is invalid. If it is a valid move, returns a list of
    # spaces of the captured pieces.
    if board[x_start][y_start] != EMPTY_SPACE or not is_on_board(x_start, y_start):
        return False

    board[x_start][y_start] = tile  # temporarily set the tile on the board.

    if tile == WHITE_TILE:
        other_tile = BLACK_TILE
    else:
        other_tile = WHITE_TILE

    tiles_to_flip = []
    # check each of the eight directions:
    for x_direction, y_direction in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0],
                                     [-1, 1]]:
        x, y = x_start, y_start
        x += x_direction
        y += y_direction
        if is_on_board(x, y) and board[x][y] == other_tile:
            # The piece belongs to the other player next to our piece.
            x += x_direction
            y += y_direction
            if not is_on_board(x, y):
                continue
            while board[x][y] == other_tile:
                x += x_direction
                y += y_direction
                if not is_on_board(x, y):
                    break  # break out of while loop, continue in for loop
            if not is_on_board(x, y):
                continue
            if board[x][y] == tile:
                # There are pieces to flip over. Go in the reverse direction until we reach the
                # original space, noting all the tiles along the way.
                while True:
                    x -= x_direction
                    y -= y_direction
                    if x == x_start and y == y_start:
                        break
                    tiles_to_flip.append([x, y])

    board[x_start][y_start] = EMPTY_SPACE  # make space empty
    if len(tiles_to_flip) == 0:  # If no tiles flipped, this move is invalid
        return False
    return tiles_to_flip


def is_on_board(x, y):
    # Returns True if the coordinates are located on the board.
    return 0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT


def get_board_with_valid_moves(board, tile):
    # Returns a new board with hint markings.
    dupe_board = copy.deepcopy(board)

    for x, y in get_valid_moves(dupe_board, tile):
        dupe_board[x][y] = HINT_TILE
    return dupe_board


def get_valid_moves(board, tile):
    # Returns a list of (x, y) tuples of all valid moves.
    valid_moves = []

    for x in range(BOARD_WIDTH):
        for y in range(BOARD_HEIGHT):
            if is_valid_move(board, tile, x, y):
                valid_moves.append((x, y))
    return valid_moves


def get_score_of_board(board):
    # Determine the score by counting the tiles.
    x_score = 0
    o_score = 0
    for x in range(BOARD_WIDTH):
        for y in range(BOARD_HEIGHT):
            if board[x][y] == WHITE_TILE:
                x_score += 1
            if board[x][y] == BLACK_TILE:
                o_score += 1
    return {WHITE_TILE: x_score, BLACK_TILE: o_score}


def enter_player_tile():
    # Draws the text and handles the mouse click events for letting the player choose which color
    # they want to be. Returns [WHITE_TILE, BLACK_TILE] if the player chooses to be White,
    # [BLACK_TILE, WHITE_TILE] if Black.

    # # Create the text
    text_surf = FONT.render('Do you want to be white or black?', True, TEXT_COLOR, TEXT_BG_COLOR_1)
    text_rect = text_surf.get_rect()
    text_rect.center = (int(WINDOW_WIDTH / 2), int(WINDOW_HEIGHT / 2))

    x_surf = BIG_FONT.render('White', True, TEXT_COLOR, TEXT_BG_COLOR_1)
    x_rect = x_surf.get_rect()
    x_rect.center = (int(WINDOW_WIDTH / 2) - 60, int(WINDOW_HEIGHT / 2) + 40)

    o_surf = BIG_FONT.render('Black', True, TEXT_COLOR, TEXT_BG_COLOR_1)
    o_rect = o_surf.get_rect()
    o_rect.center = (int(WINDOW_WIDTH / 2) + 60, int(WINDOW_HEIGHT / 2) + 40)

    while True:
        # Keep looping until the player has clicked on a color.
        check_for_quit()
        for event in pygame.event.get():  # event handling loop
            if event.type == MOUSEBUTTONUP:
                mouse_x, mouse_y = event.pos
                if x_rect.collidepoint((mouse_x, mouse_y)):
                    return [WHITE_TILE, BLACK_TILE]
                elif o_rect.collidepoint((mouse_x, mouse_y)):
                    return [BLACK_TILE, WHITE_TILE]

        # Draw the screen.
        DISPLAY_SURF.blit(text_surf, text_rect)
        DISPLAY_SURF.blit(x_surf, x_rect)
        DISPLAY_SURF.blit(o_surf, o_rect)
        pygame.display.update()
        MAIN_CLOCK.tick(FPS)


def make_move(board, tile, x_start, y_start, real_move=False):
    # Place the tile on the board at x_start, y_start, and flip tiles Returns False if this is an
    # invalid move, True if it is valid.
    tile_to_flip = is_valid_move(board, tile, x_start, y_start)

    if not tile_to_flip:
        return False

    board[x_start][y_start] = tile

    if real_move:
        animate_tile_change(tile_to_flip, tile, (x_start, y_start))

    for x, y, in tile_to_flip:
        board[x][y] = tile
    return True


def is_on_corner(x, y):
    # Returns True if the position is in one of the four corners.
    return (x == 0 and y == 0) or (x == BOARD_WIDTH and y == 0) or (x == 0 and y == BOARD_HEIGHT)\
           or (x == BOARD_WIDTH and y == BOARD_HEIGHT)


def get_computer_move(board, computer_tile):
    # Given a board and the computer's tile, determine where to move and return that move as a
    # [x, y] list.
    possible_moves = get_valid_moves(board, computer_tile)

    # randomize the order of the possible moves
    random.shuffle(possible_moves)

    # always go for a corner if available.
    for x, y in possible_moves:
        if is_on_corner(x, y):
            return [x, y]

    # Go through all possible moves and remember the best scoring move
    best_score = -1
    for x, y in possible_moves:
        dupe_board = copy.deepcopy(board)
        make_move(dupe_board, computer_tile, x, y)
        score = get_score_of_board(dupe_board)[computer_tile]
        if score > best_score:
            best_move = [x, y]
            best_score = score
    return best_move


def check_for_quit():
    for event in pygame.event.get((QUIT, KEYUP)):  # event handling loop
        if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()


if __name__ == '__main__':
    main()
