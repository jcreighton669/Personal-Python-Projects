import random
import sys
import webbrowser
import copy
import pygame
from pygame.locals import *

# There are different box sizes, number of boxes, and life depending on the "board size" setting
# selected.
SMALL_BOX_SIZE = 60  # size is in pixels
MEDIUM_BOX_SIZE = 20
LARGE_BOX_SIZE = 11

SMALL_BOARD_SIZE = 6  # size is in boxes
MEDIUM_BOARD_SIZE = 17
LARGE_BOARD_SIZE = 30

SMALL_MAX_LIFE = 10  # size is in boxes
MEDIUM_MAX_LIFE = 30
LARGE_MAX_LIFE = 64

FPS = 30
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
box_size = MEDIUM_BOX_SIZE
PALETTE_GAP_SIZE = 10
PALETTE_SIZE = 45
EASY = 0  # arbitrary but unique value
MEDIUM = 1  # arbitrary but unique value
HARD = 2  # arbitrary but unique value

difficulty = MEDIUM
max_life = MEDIUM_MAX_LIFE
board_width = MEDIUM_BOARD_SIZE
board_height = MEDIUM_BOARD_SIZE

#         (R, G, B)
WHITE = (255, 255, 255)
DARK_GRAY = (70, 70, 70)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 128, 0)
PURPLE = (255, 0, 255)

# The first color in each scheme is the background color, the next six are the palette colors.
COLOR_SCHEMES = (((150, 200, 255), RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE),
                 ((0, 155, 104), (97, 215, 164), (228, 0, 69), (0, 125, 50), (204, 246, 0),
                  (148, 0, 45), (241, 109, 149)),
                 ((195, 179, 0), (255, 239, 115), (255, 226, 0), (147, 3, 167), (24, 38, 176),
                  (166, 147, 0), (197, 97, 211)),
                 ((85, 0, 0), (155, 39, 102), (0, 201, 13), (255, 118, 0), (206, 0, 113),
                  (0, 130, 9), (255, 180, 115)),
                 ((191, 159, 64), (183, 182, 208), (4, 31, 183), (167, 184, 45), (122, 128, 212),
                  (37, 204, 7), (88, 155, 213)),
                 ((200, 33, 205), (116, 252, 185), (68, 56, 56), (52, 238, 83), (23, 149, 195),
                  (222, 157, 227), (212, 86, 185)))

for i in range(len(COLOR_SCHEMES)):
    assert len(COLOR_SCHEMES[i]) == 7, 'Color scheme %s does not have exactly 7 colors.' % (i)
bg_color = COLOR_SCHEMES[0][0]
palette_colors = COLOR_SCHEMES[0][1:]

def main():
    global FPS_CLOCK, DISPLAY_SURF, LOGO_IMAGE, SPOT_IMAGE, SETTINGS_IMAGE, \
        SETTINGS_BUTTON_IMAGE, RESET_BUTTON_IMAGE

    pygame.init()
    FPS_CLOCK = pygame.time.Clock()
    DISPLAY_SURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    # Load images
    LOGO_IMAGE = pygame.image.load('inkspilllogo.png')
    SPOT_IMAGE = pygame.image.load('inkspillspot.png')
    SETTINGS_IMAGE = pygame.image.load('inkspillsettings.png')
    SETTINGS_BUTTON_IMAGE = pygame.image.load('inkspillsettingsbutton.png')
    RESET_BUTTON_IMAGE = pygame.image.load('inkspillresetbutton.png')

    pygame.display.set_caption('Ink Spill')
    mouse_x = 0
    mouse_y = 0
    main_board = generate_random_board(board_width, board_height, difficulty)
    life = max_life
    last_palette_clicked = None

    while True:  # main game loop
        palette_clicked = None
        reset_game = False

        # Draw the screen.
        DISPLAY_SURF.fill(bg_color)
        draw_logo_and_buttons()
        draw_board(main_board)
        draw_life_meter(life)
        draw_palettes()

        check_for_quit()
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                mouse_x, mouse_y = event.pos
                if pygame.Rect(WINDOW_WIDTH - SETTINGS_BUTTON_IMAGE.get_width(),
                               WINDOW_HEIGHT - SETTINGS_BUTTON_IMAGE.get_height(),
                               SETTINGS_BUTTON_IMAGE.get_width(),
                               SETTINGS_BUTTON_IMAGE.get_height()).collidepoint(mouse_x, mouse_y):
                    reset_game = show_settings_screen()  # clicked on settings button
                elif pygame.Rect(WINDOW_WIDTH - RESET_BUTTON_IMAGE.get_width(),
                                 WINDOW_HEIGHT - SETTINGS_BUTTON_IMAGE.get_height() -
                                 RESET_BUTTON_IMAGE.get_height(),
                                 RESET_BUTTON_IMAGE.get_width(),
                                 RESET_BUTTON_IMAGE.get_height()).collidepoint(mouse_x, mouse_y):
                    reset_game = True  # clicked on reset button
                else:
                    # Check if a palette button was clicked
                    palette_clicked = get_color_of_palette_at(mouse_x, mouse_y)

            if palette_clicked != None and palette_clicked != last_palette_clicked:
                # a palette button was clicked that is different from the last palette button
                # clicked (this check prevents the player from accidentally clicking the same
                # palette twice)
                last_palette_clicked = palette_clicked
                flood_animation(main_board, palette_clicked)
                life -= 1

                reset_game = False
                if has_won(main_board):
                    for i in range(4):  # flash border 4 times
                        flash_border_animation(WHITE, main_board)
                    reset_game = True
                    pygame.time.wait(2000)  # pause so the player can bask in their glory of victory
                elif life == 0:
                    # life is zero, so player has lost
                    draw_life_meter(0)
                    pygame.display.update(400)
                    for i in range(4):
                        flash_border_animation(BLACK, main_board)
                    reset_game = True
                    pygame.time.wait(2000)  # pause so the player can suffer from their loss

            if reset_game:
                # start a new game
                main_board = generate_random_board(board_width, board_height, difficulty)
                life = max_life
                last_palette_clicked = None

            pygame.display.update()
            FPS_CLOCK.tick(FPS)


def check_for_quit():
    # Terminates the program if there are any QUIT or escape key events.
    for event in pygame.event.get(QUIT):  # get all the QUIT events
        pygame.quit()  # terminate if any QUIT events are present
        sys.exit()
    for event in pygame.event.get(KEYUP):  # get all the KEYUP events
        if event.key == K_ESCAPE:
            pygame.quit()  # terminate if the KEYUP event was for the Esc

            sys.exit()
        pygame.event.post(event)  # put the other KEYUP event objects back


def has_won(board):
    # if the entire board is the same color, player has won
    for x in range(board_width):
        for y in range(board_height):
            if board[x][y] != board[0][0]:
                return False  # found a different color, player has not won
    return True


def show_settings_screen():
    global difficulty, box_size, board_width, board_height, max_life, palette_colors, bg_color

    # The pixel coordinates in this function were obtained by loading the inkspillingsettings.png
    # image into a graphics editor and reading the pixel coordinates from there. Handy trick.

    original_difficulty = difficulty
    original_box_size = box_size
    screen_needs_redraw = True

    while True:
        if screen_needs_redraw:
            DISPLAY_SURF.fill(bg_color)
            DISPLAY_SURF.blit(SETTINGS_IMAGE, (0, 0))

            # place the ink spot marker next to the selected difficulty
            if difficulty == EASY:
                DISPLAY_SURF.blit(SPOT_IMAGE, (30, 4))
            if difficulty == MEDIUM:
                DISPLAY_SURF.blit(SPOT_IMAGE, (8, 41))
            if difficulty == HARD:
                DISPLAY_SURF.blit(SPOT_IMAGE, (30, 76))

            # place the ink spot marker next to the selected size
            if box_size == SMALL_BOX_SIZE:
                DISPLAY_SURF.blit(SPOT_IMAGE, (22, 150))
            if box_size == MEDIUM_BOX_SIZE:
                DISPLAY_SURF.blit(SPOT_IMAGE, (11, 185))
            if box_size == LARGE_BOX_SIZE:
                DISPLAY_SURF.blit(SPOT_IMAGE, (24, 220))

            for i in range(len(COLOR_SCHEMES)):
                draw_color_scheme_boxes(500, i * 60 + 30, i)

            pygame.display.update()

        screen_needs_redraw = False  # by default, don't redraw the screen
        for event in pygame.event.get():  # event handling loop
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYUP:
                if event.key == K_ESCAPE:
                    # Esc key on settings screen goes back to game
                    return not (original_difficulty == difficulty and original_box_size == box_size)
            elif event.type == MOUSEBUTTONUP:
                screen_needs_redraw = True  # screen should be redrawn
                mouse_x, mouse_y = event.pos  # syntactic sugar

                # check for clicks on the difficulty buttons
                if pygame.Rect(74, 16, 111, 30).collidepoint(mouse_x, mouse_y):
                    difficulty = EASY
                elif pygame.Rect(53, 50, 104, 29).collidepoint(mouse_x, mouse_y):
                    difficulty = MEDIUM
                elif pygame.Rect(72, 85, 65, 31).collidepoint(mouse_x, mouse_y):
                    difficulty = HARD

                # check for clicks on the size buttons
                elif pygame.Rect(63, 156, 84, 31).collidepoint(mouse_x, mouse_y):
                    # small board size setting:
                    box_size = SMALL_BOX_SIZE
                    board_width = SMALL_BOARD_SIZE
                    board_height = SMALL_BOARD_SIZE
                    max_life = SMALL_MAX_LIFE
                elif pygame.Rect(52, 192, 106, 32).collidepoint(mouse_x, mouse_y):
                    # medium board size setting:
                    box_size = MEDIUM_BOX_SIZE
                    board_width = MEDIUM_BOARD_SIZE
                    board_height = MEDIUM_BOARD_SIZE
                    max_life = MEDIUM_MAX_LIFE
                elif pygame.Rect(67, 228, 58, 37).collidepoint(mouse_x, mouse_y):
                    # large board size setting:
                    box_size = LARGE_BOX_SIZE
                    board_width = LARGE_BOARD_SIZE
                    board_height = LARGE_BOARD_SIZE
                    max_life = LARGE_MAX_LIFE
                elif pygame.Rect(14, 299, 371, 97).collidepoint(mouse_x, mouse_y):
                    # clicked on the "learn programming" ad
                    webbrowser.open('http://inventwithpython.com')  #opens a web browser
                elif pygame.Rect(178, 418, 215, 34).collidepoint(mouse_x, mouse_y):
                    # clicked on the "back to game" button
                    return not (original_difficulty == difficulty and original_box_size == box_size)

                for i in range(len(COLOR_SCHEMES)):
                    # clicked on a color scheme button
                    if pygame.Rect(500, 30 + i * 60, MEDIUM_BOX_SIZE * 3,
                                   MEDIUM_BOX_SIZE * 2).collidepoint(mouse_x, mouse_y):
                        bg_color = COLOR_SCHEMES[i][0]
                        palette_colors = COLOR_SCHEMES[i][1:]


def draw_color_scheme_boxes(x, y, scheme_num):
    # Draws the color scheme boxes that appear on the "Settings" screen.
    for box_y in range(2):
        for box_x in range(3):
            pygame.draw.rect(DISPLAY_SURF, COLOR_SCHEMES[scheme_num][3 * box_y + box_x + 1],
                             (x + MEDIUM_BOX_SIZE * box_x, y + MEDIUM_BOX_SIZE * box_y,
                              MEDIUM_BOX_SIZE, MEDIUM_BOX_SIZE))
            if palette_colors == COLOR_SCHEMES[scheme_num][1:]:
                # put the ink spot next to the selected color scheme
                DISPLAY_SURF.blit(SPOT_IMAGE, (x - 50, y))


def flash_border_animation(color, board, animation_speed=30):
    original_surface = DISPLAY_SURF.copy()
    flash_surface = pygame.Surface(DISPLAY_SURF.get_size())
    flash_surface = flash_surface.convert_alpha()
    for start, end, step in ((0, 256, 1), (255, 0, -1)):
        # the first iteration on the outer loop will set the inner loop to have transparency fo
        # from 0 to 255, the second iteration will have it go from 255 to 0, This is the "flash".
        for transparency in range(start, end, animation_speed * step):
            DISPLAY_SURF.blit(original_surface, (0, 0))
            r, g, b = color
            flash_surface.fill((r, g, b, transparency))
            DISPLAY_SURF.blit(flash_surface, (0, 0))
            draw_board(board)  # draw board ON TOP OF the transparency layer
            pygame.display.update()
            FPS_CLOCK.tick(FPS)
    DISPLAY_SURF.blit(original_surface, (0, 0))  # redraw the original surface


def flood_animation(board, palette_clicked, animation_speed = 25):
    original_board = copy.deepcopy(board)
    flood_fill(board, board[0][0], palette_clicked, 0, 0)

    for transparency in range(0, 255, animation_speed):
        # The "new" board slowly become opaque over the original board.
        draw_board(original_board)
        draw_board(board, transparency)
        pygame.display.update()
        FPS_CLOCK.tick(FPS)


def generate_random_board(width, height, difficulty=MEDIUM):
    # Creates a board data structure with random colors for each box.
    board = []
    for x in range(width):
        column = []
        for y in range(height):
            column.append(random.randint(0, len(palette_colors) - 1))
        board.append(column)

    # Make board easier by setting some boxes to same color as a neighbor.

    # determine how many boxes to change.
    if difficulty == EASY:
        if box_size == SMALL_BOX_SIZE:
            boxes_to_change = 100
        else:
            boxes_to_change = 1500
    elif difficulty == MEDIUM:
        if box_size == SMALL_BOX_SIZE:
            boxes_to_change = 5
        else:
            boxes_to_change = 200
    else:
        boxes_to_change = 0

    # Change neighbor's colors:
    for i in range(boxes_to_change):
        # Randomly choose a box whose color to copy
        x = random.randint(1, width - 2)
        y = random.randint(1, height - 2)

        # Randomly choose neighbors to change.
        direction = random.randint(0, 3)
        if direction == 0:  # change left and up neighbor
            board[x-1][y] = board[x][y]
            board[x][y-1] = board[x][y]
        elif direction == 1:  # change right and down neighbor
            board[x+1][y] = board[x][y]
            board[x][y+1] = board[x][y]
        elif direction == 2:  # change right and up neighbor
            board[x][y-1] = board[x][y]
            board[x+1][y] = board[x][y]
        elif direction == 3:  # change left and down neighbor
            board[x][y+1] = board[x][y]
            board[x-1][y] = board[x][y]
    return board


def draw_logo_and_buttons():
    # draw the Ink Spill logo and settings and reset buttons.
    DISPLAY_SURF.blit(LOGO_IMAGE, (WINDOW_WIDTH - LOGO_IMAGE.get_width(), 0))
    DISPLAY_SURF.blit(SETTINGS_BUTTON_IMAGE, (WINDOW_WIDTH - SETTINGS_BUTTON_IMAGE.get_width(),
                                              WINDOW_HEIGHT - SETTINGS_BUTTON_IMAGE.get_height()))
    DISPLAY_SURF.blit(RESET_BUTTON_IMAGE, (WINDOW_WIDTH - RESET_BUTTON_IMAGE.get_width(),
                                           WINDOW_HEIGHT - SETTINGS_BUTTON_IMAGE.get_height() -
                                           RESET_BUTTON_IMAGE.get_height()))


def draw_board(board, transparency = 255):
    # The colored squares are drawn to a temporary surface which is then drawn to the
    # DISPLAY_SURF surface. This is done so we can draw the squares with tranparency on top of
    # DISPLAY_SURF as it currently is.
    temp_surf = pygame.Surface(DISPLAY_SURF.get_size())
    temp_surf = temp_surf.convert_alpha()
    temp_surf.fill((0, 0, 0, 0))

    for x in range(board_width):
        for y in range(board_height):
            left, top = left_top_pixel_coord_of_box(x, y)
            r, g, b = palette_colors[board[x][y]]
            pygame.draw.rect(temp_surf, (r, g, b, transparency), (left, top, box_size, box_size))
    left, top = left_top_pixel_coord_of_box(0, 0)

    pygame.draw.rect(temp_surf, BLACK, (left-1, top-1, box_size * board_width + 1, box_size *
                                        board_height + 1), 1)
    DISPLAY_SURF.blit(temp_surf, (0, 0))


def draw_palettes():
    # Draws the six color palettes at the bottom of the screen.
    num_colors = len(palette_colors)
    x_margin = int((WINDOW_WIDTH - ((PALETTE_SIZE * num_colors) +
                                    (PALETTE_GAP_SIZE * (num_colors - 1)))) / 2)
    for i in range(num_colors):
        left = x_margin + (i * PALETTE_SIZE) + (i * PALETTE_GAP_SIZE)
        top = WINDOW_HEIGHT - PALETTE_SIZE - 10
        pygame.draw.rect(DISPLAY_SURF, palette_colors[i], (left, top, PALETTE_SIZE, PALETTE_SIZE))
        pygame.draw.rect(DISPLAY_SURF, bg_color, (left + 2, top + 2, PALETTE_SIZE - 4,
                                                  PALETTE_SIZE - 4), 2)


def draw_life_meter(current_life):
    life_box_size = int((WINDOW_HEIGHT - 40) / max_life)

    # Draw background color of life meter.
    pygame.draw.rect(DISPLAY_SURF, bg_color, (20, 20, 20, 20 + (max_life * life_box_size)))

    for i in range(max_life):
        if current_life >= (max_life - i):  # draw a solid red box
            pygame.draw.rect(DISPLAY_SURF, RED, (20, 20 + (i * life_box_size), 20, life_box_size))
        pygame.draw.rect(DISPLAY_SURF, WHITE, (20, 20 + (i * life_box_size), 20, life_box_size),
                         1)  # draw white outline


def get_color_of_palette_at(x, y):
    # Returns the index of the color in palette_colors that the x and y parameters are over.
    # Returns None if x and y are not over any palette.
    num_colors = len(palette_colors)
    x_margin = int((WINDOW_WIDTH - ((PALETTE_SIZE * num_colors) +
                                    (PALETTE_GAP_SIZE * (num_colors - 1)))) / 2)
    top = WINDOW_HEIGHT - PALETTE_SIZE - 10
    for i in range(num_colors):
        # Find out if the mouse click is inside any of the palettes.
        left = x_margin + (i * PALETTE_SIZE) + (i * PALETTE_GAP_SIZE)
        r = pygame.Rect(left, top, PALETTE_SIZE, PALETTE_SIZE)
        if r.collidepoint(x, y):
            return i
    return None  # no palette exists at these x, y coordinates


def flood_fill(board, old_color, new_color, x, y):
    # This is the flood fill algorithm.
    if old_color == new_color or board[x][y] != old_color:
        return

    board[x][y] = new_color  # change the color of the current box

    # Make the recursive call for any neighboring boxes:
    if x > 0:
        flood_fill(board, old_color, new_color, x - 1, y)  # on box to the left

    if x < board_width - 1:
        flood_fill(board, old_color, new_color, x + 1, y)  # on box to the right

    if y > 0:
        flood_fill(board, old_color, new_color, x, y - 1)  # on box to up

    if y < board_height - 1:
        flood_fill(board, old_color, new_color, x, y + 1)  # on box to down


def left_top_pixel_coord_of_box(box_x, box_y):
    # Returns the x and y of the left-topmost pixel of the xth & yth box.
    x_margin = int((WINDOW_WIDTH - (board_width * box_size)) / 2)
    y_margin = int((WINDOW_HEIGHT - (board_height * box_size)) / 2)
    return (box_x * box_size + x_margin, box_y * box_size + y_margin)


if __name__ == '__main__':
    main()
