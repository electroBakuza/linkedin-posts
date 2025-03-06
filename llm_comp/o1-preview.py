import pygame
import sys
import imageio  # For saving GIFs

# Maze text representation
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

def parse_maze(maze_text):
    """
    Parses the maze text and returns the maze grid along with start and exit positions.
    """
    maze = []
    start_pos = None
    exit_pos = None

    # Split the text into lines and filter out empty lines
    lines = [line for line in maze_text.split('\n') if line.strip()]
    # We only need the lines that contain the maze data (lines with '|')
    maze_lines = [line for line in lines if '|' in line and '+' not in line]

    for y, line in enumerate(maze_lines):
        # Split the line by '|' and remove empty strings
        cells = [cell.strip() for cell in line.strip().split('|')[1:-1]]
        maze_row = []
        for x, cell in enumerate(cells):
            if cell == 'S':
                start_pos = (x, y)
                maze_row.append(' ')
            elif cell == 'E':
                exit_pos = (x, y)
                maze_row.append(' ')
            elif cell == '#':
                maze_row.append('#')
            else:
                maze_row.append(' ')
        maze.append(maze_row)

    return maze, start_pos, exit_pos

def draw_maze(screen, maze, tile_size):
    """
    Draws the maze grid on the screen.
    """
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
            if cell == '#':
                pygame.draw.rect(screen, (0, 0, 0), rect)  # Black for walls
            else:
                pygame.draw.rect(screen, (255, 255, 255), rect)  # White for paths
                pygame.draw.rect(screen, (200, 200, 200), rect, 1)  # Gray grid lines

def animate_path(screen, maze, path, start_pos, exit_pos, tile_size):
    """
    Animates the character moving along the path and captures frames for a GIF.
    """
    clock = pygame.time.Clock()
    character_pos = start_pos
    steps_taken = 0
    font = pygame.font.SysFont(None, 24)

    frames = []  # List to store frames for the GIF

    # Animate movement along the path (skip the starting position)
    for pos in path[1:]:
        # Handle events to allow quitting
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Draw the maze
        draw_maze(screen, maze, tile_size)

        # Draw the start and exit positions
        pygame.draw.rect(screen, (0, 255, 0), (start_pos[0] * tile_size, start_pos[1] * tile_size, tile_size, tile_size))  # Green for start
        pygame.draw.rect(screen, (255, 0, 0), (exit_pos[0] * tile_size, exit_pos[1] * tile_size, tile_size, tile_size))  # Red for exit

        # Update character position and step count
        character_pos = pos
        steps_taken += 1

        # Draw the character as a blue circle
        pygame.draw.circle(screen, (0, 0, 255), 
                           (character_pos[0] * tile_size + tile_size // 2, character_pos[1] * tile_size + tile_size // 2), 
                           tile_size // 3)

        # Display steps taken
        steps_text = font.render(f"Steps Taken: {steps_taken}", True, (0, 0, 0))
        screen.blit(steps_text, (10, 10))

        pygame.display.flip()
        # Capture the current frame (transpose for correct orientation)
        frame = pygame.surfarray.array3d(screen).transpose(1, 0, 2)
        frames.append(frame)

        clock.tick(2)  # Control animation speed (2 frames per second)

    # Final display: Show the character at the exit for a few seconds
    final_display_time = 3000  # milliseconds
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < final_display_time:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        draw_maze(screen, maze, tile_size)
        pygame.draw.rect(screen, (0, 255, 0), (start_pos[0] * tile_size, start_pos[1] * tile_size, tile_size, tile_size))
        pygame.draw.rect(screen, (255, 0, 0), (exit_pos[0] * tile_size, exit_pos[1] * tile_size, tile_size, tile_size))
        # Draw the character at the exit
        pygame.draw.circle(screen, (0, 0, 255), 
                           (exit_pos[0] * tile_size + tile_size // 2, exit_pos[1] * tile_size + tile_size // 2), 
                           tile_size // 3)
        steps_text = font.render(f"Total Steps Taken: {steps_taken}", True, (0, 0, 0))
        screen.blit(steps_text, (10, 10))
        pygame.display.flip()
        frame = pygame.surfarray.array3d(screen).transpose(1, 0, 2)
        frames.append(frame)
        clock.tick(30)

    # Save the captured frames as an animated GIF
    imageio.mimsave('maze_output_o1-preview.gif', frames, fps=2)
    print("Saved animation to maze_output.gif")
    
    pygame.quit()
    sys.exit()

def main():
    # Initialize Pygame
    pygame.init()

    # Parse the maze and get start and exit positions
    maze, start_pos, exit_pos = parse_maze(maze_text)

    # Define the path (list of positions)
    path = [
        (0, 0), (1, 0), (2, 0), (2, 1),
        (2, 2), (3, 2), (4, 2), (4, 1),
        (4, 0), (5, 0), (6, 0), (6, 1),
        (6, 2), (7, 2), (8, 2), (8, 1),
        (8, 0)
    ]

    # Adjust the path to match the maze coordinates (x, y)
    adjusted_path = [(x, y) for y, x in path]

    # Set the size of each tile and the window dimensions
    tile_size = 60
    width = len(maze[0]) * tile_size
    height = len(maze) * tile_size

    # Set up the Pygame window
    screen = pygame.display.set_mode([width, height])
    pygame.display.set_caption('Maze Solver o1-preview')

    # Run the animation and record frames
    animate_path(screen, maze, adjusted_path, start_pos, exit_pos, tile_size)

if __name__ == "__main__":
    main()
