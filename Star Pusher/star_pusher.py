# Star Pusher (a Sokoban clone)
# By Al Sweigart
# http://inventwithpython.com/pygame
# Creative Commons BY-NC-SA 3.0 US

import random, sys, copy, os, pygame
from pygame.locals import *

FPS = 30  # frames per second to update the screen
WIN_WIDTH = 800  # width of the program's window, in pixels
WIN_HEIGHT = 600  # height in pixels
HALF_WIN_WIDTH = int(WIN_WIDTH / 2)
HALF_WIN_HEIGHT = int(WIN_HEIGHT / 2)

# The total width and height of each tile in pixels.
TILE_WIDTH = 50
TILE_HEIGHT = 85
TILE_FLOOR_HEIGHT = 45

CAM_MOVE_SPEED = 5  # how many pixels per frame the camera moves

# The percentage of outdoor tiles that have additional decoration on them, such
# as a tree or rock.
OUTSIDE_DECORATION_PCT = 20

BRIGHT_BLUE = (0, 170, 255)
WHITE = (255, 255, 255)
BG_COLOR = BRIGHT_BLUE
TEXT_COLOR = WHITE

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'


def main():
    global FPS_CLOCK, DISPLAY_SURF, IMAGE_DICT, TILE_MAPPING, OUTSIDE_DECO_MAPPING, BASIC_FONT, \
        PLAYER_IMAGES, current_image

    # Pygame initialization and basic set up of the global variables.
    pygame.init()
    FPS_CLOCK = pygame.time.Clock()

    # Because the Surface object stored in DISPLAY_SURF was returned from the
    # pygame.display.set_mode() function, this is the Surface object that is
    # drawn to the actual computer screen when pygame.display.update() is called.
    DISPLAY_SURF = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

    pygame.display.set_caption('Star Pusher')
    BASIC_FONT = pygame.font.Font('freesansbold.ttf', 36)

    # A global dict value that will contain all the Pygame Surface objects
    # returned by pygame.image.load()
    IMAGE_DICT = {'uncovered goal': pygame.image.load('RedSelector.png'),
                  'covered goal': pygame.image.load('Selector.png'),
                  'star': pygame.image.load('Star.png'),
                  'corner': pygame.image.load('Wall_Block_Tall.png'),
                  'wall': pygame.image.load('Wood_Block_Tall.png'),
                  'inside floor': pygame.image.load('Plain_Block.png'),
                  'outside floor': pygame.image.load('Grass_Block.png'),
                  'title': pygame.image.load('star_title.png'),
                  'solved': pygame.image.load('star_solved.png'),
                  'princess': pygame.image.load('princess.png'),
                  'boy': pygame.image.load('boy.png'),
                  'catgirl': pygame.image.load('catgirl.png'),
                  'horngirl': pygame.image.load('horngirl.png'),
                  'pinkgirl': pygame.image.load('pinkgirl.png'),
                  'rock': pygame.image.load('Rock.png'),
                  'short tree': pygame.image.load('Tree_Short.png'),
                  'tall tree': pygame.image.load('Tree_Tall.png'),
                  'ugly tree': pygame.image.load('Tree_Ugly.png')}

    # These dict values are global, and map the character that appears in the
    # level file to the surface object it represents
    TILE_MAPPING = {'x': IMAGE_DICT['corner'],
                    '#': IMAGE_DICT['wall'],
                    'o': IMAGE_DICT['inside floor'],
                    ' ': IMAGE_DICT['outside floor']}
    OUTSIDE_DECO_MAPPING = {'1': IMAGE_DICT['rock'],
                            '2': IMAGE_DICT['short tree'],
                            '3': IMAGE_DICT['tall tree'],
                            '4': IMAGE_DICT['ugly tree']}

    # PLAYER_IMAGES is a list of all possible characters that player can be.
    # current_image is the index of the player's current player image.
    current_image = 0
    PLAYER_IMAGES = [IMAGE_DICT['princess'],
                     IMAGE_DICT['boy'],
                     IMAGE_DICT['catgirl'],
                     IMAGE_DICT['horngirl'],
                     IMAGE_DICT['pinkgirl']]

    start_screen()  # show the title screen until the user presses a key

    # Read in the levels from the text file. See the read_levels_file() for
    # details on the format of this file and how to make your own levels.
    levels = read_levels_file('starPusherLevels.txt')
    current_level_index = 0

    # The main game loop. This loop runs a single level, when the user finishes
    # that level, the next/previous level is loaded.
    while True:  # main game loop
        # Run the level to actually start playing the game:
        result = run_level(levels, current_level_index)

        if result in ('solved', 'next'):
            # Go to the next level.
            current_level_index += 1
            if current_level_index >= len(levels):
                # If there are no more levels, go back to the first one.
                current_level_index = 0
        elif result == 'back':
            # Go to the previous level.
            current_level_index -= 1
            if current_level_index < 0:
                # If there are no previous levels, go to the last one.
                current_level_index = len(levels) - 1
        elif result == 'reset':
            pass  # Do nothing. Loop re-calls run_level() to reset the level


def run_level(levels, level_num):
    global current_image
    level_obj = levels[level_num]
    map_obj = decorate_map(level_obj['map_obj'], level_obj['start_state']['player'])
    game_state_obj = copy.deepcopy(level_obj['start_state'])
    map_needs_redraw = True  # set to True to call draw_map()
    level_surf = BASIC_FONT.render('Level %s of %s' % (level_num + 1, len(levels)),
                                   1, TEXT_COLOR)
    level_rect = level_surf.get_rect()
    level_rect.bottomleft = (20, WIN_HEIGHT - 35)
    map_width = len(map_obj) * TILE_WIDTH
    map_height = (len(map_obj[0]) - 1) * TILE_FLOOR_HEIGHT + TILE_HEIGHT
    MAX_CAM_X_PAN = abs(HALF_WIN_HEIGHT - int(map_height / 2)) + TILE_WIDTH
    MAX_CAM_Y_PAN = abs(HALF_WIN_WIDTH - int(map_width / 2)) + TILE_HEIGHT

    level_is_complete = False
    # Track how much the camera has moved:
    camera_offset_x = 0
    camera_offset_y = 0
    # Track if the keys to move the camera are being held down:
    camera_up = False
    camera_down = False
    camera_left = False
    camera_right = False

    while True:  # main game loop
        # Reset these variables:
        player_move_to = None
        key_pressed = False

        for event in pygame.event.get():  # event handling loop
            if event.type == QUIT:
                # Player clicked the "X" at the corer of the window.
                terminate()

            elif event.type == KEYDOWN:
                # Handle key presses
                key_pressed = True
                if event.key == K_LEFT:
                    player_move_to = LEFT
                elif event.key == K_RIGHT:
                    player_move_to = RIGHT
                elif event.key == K_UP:
                    player_move_to = UP
                elif event.key == K_DOWN:
                    player_move_to = DOWN

                # Set the camera move mode.
                elif event.key == K_a:
                    camera_left = True
                elif event.key == K_d:
                    camera_right = True
                elif event.key == K_w:
                    camera_up = True
                elif event.key == K_s:
                    camera_down = True

                elif event.key == K_n:
                    return 'next'
                elif event.key == K_b:
                    return 'back'

                elif event.key == K_ESCAPE:
                    terminate()
                elif event.key == K_BACKSPACE:
                    return 'reset'
                elif event.key == K_p:
                    # Change the player image to the next one.
                    current_image += 1
                    if current_image >= len(PLAYER_IMAGES):
                        # After the last player image, use the first one.
                        current_image = 0
                    map_needs_redraw = True

            elif event.type == KEYUP:
                # Unset the camera move mode.
                if event.key == K_a:
                    camera_left = False
                elif event.key == K_d:
                    camera_right = False
                elif event.key == K_w:
                    camera_up = False
                elif event.key == K_s:
                    camera_down = False

        if player_move_to != None and not level_is_complete:
            # If the player pushed a key to move, make the move (if possible)
            # and push any stars that are pushable.
            moved = make_move(map_obj, game_state_obj, player_move_to)

            if moved:
                # increment the step counter.
                game_state_obj['step_counter'] += 1
                map_needs_redraw = True

            if is_level_finished(level_obj, game_state_obj):
                # level is solved, we should show the "Solved!" image.
                level_is_complete = True
                key_pressed = False

        DISPLAY_SURF.fill(BG_COLOR)

        if map_needs_redraw:
            map_surf = draw_map(map_obj, game_state_obj, level_obj['goals'])
            map_needs_redraw = False

        if camera_up and camera_offset_y < MAX_CAM_X_PAN:
            camera_offset_y += CAM_MOVE_SPEED
        elif camera_down and camera_offset_y > -MAX_CAM_X_PAN:
            camera_offset_y -= CAM_MOVE_SPEED
        if camera_left and camera_offset_x < MAX_CAM_Y_PAN:
            camera_offset_x += CAM_MOVE_SPEED
        elif camera_right and camera_offset_x > -MAX_CAM_Y_PAN:
            camera_offset_x -= CAM_MOVE_SPEED

        # Adjust map_surf's Rect object based on the camera offset.
        map_surf_rect = map_surf.get_rect()
        map_surf_rect.center = (HALF_WIN_WIDTH + camera_offset_x, HALF_WIN_HEIGHT + camera_offset_y)

        # Draw map_surf to the DISPLAY_SURF Surface object.
        DISPLAY_SURF.blit(map_surf, map_surf_rect)

        DISPLAY_SURF.blit(level_surf, level_rect)
        step_surf = BASIC_FONT.render('Steps: %s' % (game_state_obj['step_counter']), 1, TEXT_COLOR)
        step_rect = step_surf.get_rect()
        step_rect.bottomleft = (20, WIN_HEIGHT - 10)
        DISPLAY_SURF.blit(step_surf, step_rect)

        if level_is_complete:
            # is solved, show the "Solved!" image until the player has pressed a key.
            solved_rect = IMAGE_DICT['solved'].get_rect()
            solved_rect.center = (HALF_WIN_WIDTH, HALF_WIN_HEIGHT)
            DISPLAY_SURF.blit(IMAGE_DICT['solved'], solved_rect)

            if key_pressed:
                return 'solved'

        pygame.display.update()
        FPS_CLOCK.tick()


def is_wall(map_obj, x, y):
    """Returns True if the (x, y) position on the map is a wall, otherwise return False."""
    if x < 0 or x >= len(map_obj) or y < 0 or y >= len(map_obj[x]):
        return False  # x and y aren't actually on the map.
    elif map_obj[x][y] in ('#', 'x'):
        return True  # wall is blocking
    return False


def decorate_map(map_obj, startxy):
    """Makes a copy of the given map object and modifies it.
    Here is what is done to it:
        * Walls that are corners are turned into corner pieces.
        * The outside/inside floor tile distinction is make.
        * Tree/rock decorations are randomly added to the outside tiles.

    Returns the decorated map object."""

    start_x, start_y = startxy  # Syntactic sugar

    # Copy the map object so we don't modify the original passed
    map_obj_copy = copy.deepcopy(map_obj)

    # Remove the non-wall characters from the map data
    for x in range(len(map_obj_copy)):
        for y in range(len(map_obj_copy[0])):
            if map_obj_copy[x][y] in ('$', '.', '@', '+', '*'):
                map_obj_copy[x][y] = ' '

    # Flood fill to determine inside.outside floor tiles.
    flood_fill(map_obj_copy, start_x, start_y, ' ', 'o')

    # Convert the adjoined walls into corner tiles.
    for x in range(len(map_obj_copy)):
        for y in range(len(map_obj_copy[0])):

            if map_obj_copy[x][y] == '#':
                if (is_wall(map_obj_copy, x, y-1) and is_wall(map_obj_copy, x+1, y)) or \
                   (is_wall(map_obj_copy, x+1, y) and is_wall(map_obj_copy, x, y+1)) or \
                   (is_wall(map_obj_copy, x, y+1) and is_wall(map_obj_copy, x-1, y)) or \
                   (is_wall(map_obj_copy, x-1, y) and is_wall(map_obj_copy, x, y-1)):
                    map_obj_copy[x][y] = 'x'
                elif map_obj_copy[x][y] == ' ' and random.randint(0, 99) < OUTSIDE_DECORATION_PCT:
                    map_obj_copy[x][y] = random.choice(list(OUTSIDE_DECO_MAPPING.keys()))

    return map_obj_copy


def is_blocked(map_obj, game_state_obj, x, y):
    """Returns True if the (x, y) position on the map is blocked by a wall or star, otherwise
    return False."""

    if is_wall(map_obj, x, y):
        return True

    elif x < 0 or x >= len(map_obj) or y < 0 or y >= len(map_obj[x]):
        return True  # x and y aren't actually on the map.

    elif (x, y) in game_state_obj['stars']:
        return True  # a star is blocking

    return False


def make_move(map_obj, game_state_obj, player_move_to):
    """Given a map and game state object, see if it is possible for the player to make the given
    move. If it is, then change the player's position (and the position of any pusher star). If
    not, do nothing.

    Returns True if the player moved, otherwise False."""

    # Make sure the player can move in the direction they want.
    player_x, player_y = game_state_obj['player']

    # This variable is "syntactic sugar". Typing "stars" is more readable than typing
    # "game_state_obj['stars']" in our code.
    stars = game_state_obj['stars']

    # The code for handling each of the directions is so similar aside from adding or subtracting
    # 1 to the x/y coordinates. We can simplify it by using the x_offset and y_offset variables.
    if player_move_to == UP:
        x_offset = 0
        y_offset = -1
    elif player_move_to == RIGHT:
        x_offset = 1
        y_offset = 0
    elif player_move_to == DOWN:
        x_offset = 0
        y_offset = 1
    elif player_move_to == LEFT:
        x_offset = -1
        y_offset = 0

    # See if the player can move in that direction.
    if is_wall(map_obj, player_x + x_offset, player_y + y_offset):
        return False
    else:
        if (player_x + x_offset, player_y + y_offset) in stars:
            # There is a star in the way, see if the player can push it.
            if not is_blocked(map_obj, game_state_obj, player_x + (x_offset*2), player_y + (
                    y_offset*2)):
                # Move the star.
                ind = stars.index((player_x + x_offset, player_y + y_offset))
                stars[ind] = (stars[ind][0] + x_offset, stars[ind][1] + y_offset)
            else:
                return False
        # Move the player upwards.
        game_state_obj['player'] = (player_x + x_offset, player_y + y_offset)
        return True

def start_screen():
    """Display the start screen (which has the title and instructions) until the player presses a key. Return None."""

    # Position the title image.
    title_rect = IMAGE_DICT['title'].get_rect()
    top_coord = 50  # top_coord tracks where to position the top of the text
    title_rect.top = top_coord
    title_rect.centerx = HALF_WIN_WIDTH
    top_coord += title_rect.height

    # Unfortunately, Pygame's font & text system only shows one line at a time, so we can't use
    # strings with \n newline characters in them. So we will use a list with each line in it.
    instruction_text = ['Push the stars over the marks.',
                        'Arrow keys to move, WASD for camera control, P to change character.',
                        'Backspace to rest level, Esc to quit.',
                        'N for next level, B to go back a level.']

    # Start with drawing a blank color to the entire window:
    DISPLAY_SURF.fill(BG_COLOR)

    # Draw the title image to the window:
    DISPLAY_SURF.blit(IMAGE_DICT['title'], title_rect)

    # Position and draw the text.
    for i in range(len(instruction_text)):
        inst_surf = BASIC_FONT.render(instruction_text[i], 1, TEXT_COLOR)
        inst_rect = inst_surf.get_rect()
        top_coord += 10  # 10 pixels will go in between each line of text.
        inst_rect.top = top_coord
        inst_rect.centerx = HALF_WIN_WIDTH
        top_coord += inst_rect.height  # Adjust for the height of the line.
        DISPLAY_SURF.blit(inst_surf, inst_rect)

    while True:  # Main loop for the start screen.
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                return  # user has pressed a key, so return.

        # Display the DISPLAY_SURF contents to the actual screen.
        pygame.display.update()
        FPS_CLOCK.tick()


def read_levels_file(filename):
    assert os.path.exists(filename), 'Cannot find the level file: %s' % (filename)
    map_file = open(filename, 'r')
    # Each level must end with a blank line
    content = map_file.readlines() + ['\r\n']
    map_file.close()

    levels = []  # Will contain a list of level objects.
    level_num = 0
    map_text_lines = []  # contains the lines for a single level's map.
    map_obj = []  # the map object made from the data in map_text_lines
    for line_num in range(len(content)):
        # Process each line that was in the level file.
        line = content[line_num].rstrip('\r\n')

        if ';' in line:
            # Ignore the ; lines, they're comments in the level file.
            line = line[:line.find(';')]

        if line != '':
            # This line is part of the map.
            map_text_lines.append(line)
        elif line == '' and len(map_text_lines) > 0:
            # A blank line indicates the end of a level's map in the file. Convert the text in
            # map_text_lines into a level object.

            # Find the longest row in the map.
            max_width = -1
            for i in range(len(map_text_lines)):
                if len(map_text_lines[i]) > max_width:
                    max_width = len(map_text_lines[i])
            # Add spaces to the ends of the shorter rows. This ensures the map will be rectangular.
            for i in range(len(map_text_lines)):
                map_text_lines[i] += ' ' * (max_width - len(map_text_lines[i]))

            # Convert map_text_lines to a map object.
            for x in range(len(map_text_lines[0])):
                map_obj.append([])
            for y in range(len(map_text_lines)):
                for x in range(max_width):
                    map_obj[x].append(map_text_lines[y][x])

            # Loop through the spaces in the map and find the @, ., and $ characters for the
            # starting game state.
            start_x = None  # The x and y for the player's starting position
            start_y = None
            goals = []  # list of (x, y) tuples for each goal.
            stars = []  # list of (x, y) for each star's starting position.
            for x in range(max_width):
                for y in range(len(map_obj[x])):
                    if map_obj[x][y] in ('@', '+'):
                        # '@' is player, '+' is player & goal
                        start_x = x
                        start_y = y
                    if map_obj[x][y] in ('.', '+', '*'):
                        # '.' is goal, '*' is star & goal
                        goals.append((x, y))
                    if map_obj[x][y] in ('$', '*'):
                        # '$' is star
                        stars.append((x, y))
            # Basic level design sanity checks:
            assert start_x != None and start_y != None, 'Level %s (around line %s) in %s is ' \
                                                        'missing a "@" or "+" to mark the start ' \
                                                        'point.' % (level_num + 1, line_num, filename)
            assert len(goals) > 0, 'Level %s (around line %s) in %s must have at least one goal.'\
                                   % (level_num + 1, line_num, filename)
            assert len(stars) >= len(goals), 'Level %s (around line %s) in %s is impossible to ' \
                                             'solve. It has %s goals but only %s stars.' % (
                level_num + 1, line_num, filename, len(goals), len(stars))

            # Create level object and starting game state object.
            game_state_obj = {'player': (start_x, start_y),
                              'step_counter': 0,
                              'stars': stars}
            level_obj = {'width': max_width,
                         'height': len(map_obj),
                         'map_obj': map_obj,
                         'goals': goals,
                         'start_state': game_state_obj}
            levels.append(level_obj)

            # Reset the variables for reading the next map.
            map_text_lines = []
            map_obj = []
            game_state_obj = {}
            level_num += 1
    return levels


def flood_fill(map_obj, x, y, old_character, new_character):
    """Changes any values matching old_character on the map object to new_character at the
    (x,y) position, and does the same for the positions to the left, right, down and up of
    (x, y) recursively."""

    # In this game, the flood fill algorithm creates the inside/outside floor distinction. This
    # is a "recursive" function.
    if map_obj[x][y] == old_character:
        map_obj[x][y] = new_character

    if x < len(map_obj) - 1 and map_obj[x+1][y] == old_character:
        flood_fill(map_obj, x+1, y, old_character, new_character)  # call right
    if x > 0 and map_obj[x-1][y] == old_character:
        flood_fill(map_obj, x-1, y, old_character, new_character)  # call left
    if y < len(map_obj[x]) - 1 and map_obj[x][y+1] == old_character:
        flood_fill(map_obj, x, y+1, old_character, new_character)  # call down
    if y > 0 and map_obj[x][y-1] == old_character:
        flood_fill(map_obj, x, y-1, old_character, new_character)  # call up


def draw_map(map_obj, game_state_obj, goals):
    """Draws the map to a Surface object, including the player and stars. This function does not
    call pygame.display.update(), nor does it draw the "Level" and "Steps" text in the corner."""

    # map_surf will be the single surface object that the tiles are drawn on, so that it is easy
    # to position the entire map on the DISPLAY_SURF Surface object. First, the width and height
    # must be calculated.
    map_surf_width = len(map_obj) * TILE_WIDTH
    map_surf_height = (len(map_obj[0]) - 1) * (TILE_HEIGHT - TILE_FLOOR_HEIGHT) + TILE_HEIGHT
    map_surf = pygame.Surface((map_surf_width, map_surf_height))
    map_surf.fill(BG_COLOR)  # start with a blank color on the surface.

    # Draw the tile sprites onto this surface.
    for x in range(len(map_obj)):
        for y in range(len(map_obj[x])):
            space_rect = pygame.Rect((x * TILE_WIDTH, y * (TILE_HEIGHT - TILE_FLOOR_HEIGHT),
                                      TILE_WIDTH, TILE_HEIGHT))
            if map_obj[x][y] in TILE_MAPPING:
                base_tile = TILE_MAPPING[map_obj[x][y]]
            elif map_obj[x][y] in OUTSIDE_DECO_MAPPING:
                base_tile = TILE_MAPPING[' ']

            # First draw the base ground/wall tile.
            map_surf.blit(base_tile, space_rect)

            if map_obj[x][y] in OUTSIDE_DECO_MAPPING:
                # Draw any tree/rock decorations that are on this tile.
                map_surf.blit(OUTSIDE_DECO_MAPPING[map_obj[x][y]], space_rect)
            elif (x, y) in game_state_obj['stars']:
                if (x, y) in goals:
                    # A goal AND star are on this space, draw goal first.
                    map_surf.blit(IMAGE_DICT['star'], space_rect)
                # Then draw the star sprite.
                map_surf.blit(IMAGE_DICT['star'], space_rect)
            elif (x, y) in goals:
                # Draw a goal without a star on it.
                map_surf.blit(IMAGE_DICT['uncovered goal'], space_rect)
            # Last draw the player on the board.
            if (x, y) == game_state_obj['player']:
                # Note: The value "current_image" refers to a key in "PLAYER_IMAGES" which has
                # the specific player image we want to show.
                map_surf.blit(PLAYER_IMAGES[current_image], space_rect)

    return map_surf


def is_level_finished(level_obj, game_state_obj):
    """Returns True if all the goals have stars in them."""
    for goal in level_obj['goals']:
        if goal not in game_state_obj['stars']:
            # Found a space with a goal but no star on it.
            return False
    return True


def terminate():
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()

