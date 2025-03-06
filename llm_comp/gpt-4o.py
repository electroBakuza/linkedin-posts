import pygame
import sys
from pygame.locals import *
import imageio  # For saving GIFs

# Constants for colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (192, 192, 192)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Maze representation
maze_text = '''
+---+---+---+---+---+---+---+---+---+
| S |   |   | # |   |   |   | # | E |
+---+---+---+---+---+---+---+---+---+
| # | # |   | # |   | # |   | # |   |
+---+---+---+---+---+---+---+---+---+
|   |   |   |   |   | # |   |   |   |
+---+---+---+---+---+---+---+---+---+
|   | # | # | # |   | # | # | # |   |
+---+---+---+---+---+---+---+---+---+
|   |   |   | # |   |   |   |   |   |
+---+---+---+---+---+---+---+---+---+
'''

# Parsing the maze text to a grid
def parse_maze(maze_text):
    maze = []
    for line in maze_text.strip().splitlines():
        if '+' in line:  # Skip lines with "+"
            continue
        row = []
        for char in line.split('|'):
            char = char.strip()
            if char == '':
                continue
            if char == 'S':
                start = (len(maze), len(row))
            if char == 'E':
                end = (len(maze), len(row))
            row.append(char)
        maze.append(row)
    return maze, start, end

def draw_maze(screen, maze):
    block_size = 50
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            rect = pygame.Rect(x * block_size, y * block_size, block_size, block_size)
            if cell == '#':
                pygame.draw.rect(screen, BLACK, rect)
            else:
                pygame.draw.rect(screen, WHITE, rect)
                pygame.draw.rect(screen, GRAY, rect, 1)
            if cell == 'S':
                pygame.draw.circle(screen, RED, rect.center, block_size // 4)
            if cell == 'E':
                pygame.draw.circle(screen, GREEN, rect.center, block_size // 4)

def main():
    pygame.init()
    
    # Setup the maze and find start and end points
    maze, start, end = parse_maze(maze_text)

    # Setup Pygame window
    block_size = 50
    width = len(maze[0]) * block_size
    height = len(maze) * block_size
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Maze Solver Animation")
    clock = pygame.time.Clock()

    # Hardcoded solution path (each tuple is (row, column))
    path = [
        (0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 1), (2, 0), (3, 0), (4, 0), (4, 1),
        (4, 2), (3, 2), (2, 2), (2, 3), (2, 4), (1, 4), (0, 4), (0, 5), (1, 5), (2, 5),
        (2, 6), (3, 6), (4, 6), (4, 7), (4, 8), (3, 8), (2, 8), (1, 8), (0, 8)
    ]

    # List to store frames for the GIF
    frames = []

    step_count = 0
    # Iterate over the path positions
    for pos in path:
        if step_count>20:
            break
        # Allow quitting during animation
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(WHITE)
        draw_maze(screen, maze)

        # Update player's position from the current step in the path
        player_pos = pos
        step_count += 1

        # Draw player (note the swap: x is column, y is row)
        rect = pygame.Rect(player_pos[1] * block_size, player_pos[0] * block_size, block_size, block_size)
        pygame.draw.circle(screen, RED, rect.center, block_size // 4)

        # Display step count at the bottom of the screen
        font = pygame.font.SysFont(None, 36)
        text = font.render(f'Steps: {step_count}', True, BLACK)
        screen.blit(text, (10, height - 40))

        pygame.display.flip()

        # Capture the current frame (transpose to correct orientation)
        frame = pygame.surfarray.array3d(screen).transpose(1, 0, 2)
        frames.append(frame)

        clock.tick(2)  # Control animation speed (2 frames per second)

    # Optional: hold the final frame for a moment before exiting
    pygame.time.wait(2000)
    final_frame = pygame.surfarray.array3d(screen).transpose(1, 0, 2)
    frames.append(final_frame)

    # Save all frames as an animated GIF
    imageio.mimsave('maze_output_gpt4o.gif', frames, fps=2)
    print("Saved animation to maze_output.gif")

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
