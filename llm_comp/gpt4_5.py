import pygame
import sys
import imageio  # Import imageio for saving GIFs

# Define maze as text
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

# Maze parsing
def parse_maze(maze_text):
    maze, start, end = [], None, None
    lines = [line for line in maze_text.split('\n') if '|' in line]
    for y, line in enumerate(lines):
        row = []
        cells = line.split('|')[1:-1]
        for x, cell in enumerate(cells):
            char = cell.strip()
            if char == 'S':
                start = (x, y)
                row.append(' ')
            elif char == 'E':
                end = (x, y)
                row.append(' ')
            elif char == '#':
                row.append('#')
            else:
                row.append(' ')
        maze.append(row)
    return maze, start, end

# Manually determined solution path (as coordinate positions)
solution_path = [
    (0, 0), (1, 0), (2, 0), (2, 1), (2, 2),
    (3, 2), (4, 2), (4, 1), (4, 0), (5, 0),
    (6, 0), (6, 1), (6, 2), (7, 2), (8, 2),
    (8, 1), (8, 0)
]

# Visualization parameters
TILE_SIZE = 50
FPS = 4

# Colors
WHITE, BLACK = (255,255,255), (0,0,0)
GREEN, RED, BLUE, GRAY = (0,255,0), (255,0,0), (0,0,255), (200,200,200)

# Initialize pygame
pygame.init()
maze, start, end = parse_maze(maze_text)
width, height = len(maze[0]), len(maze)
screen = pygame.display.set_mode((width*TILE_SIZE, height*TILE_SIZE + 40))
pygame.display.set_caption('Maze Solver (GPT4.5)')
font = pygame.font.SysFont(None, 28)
clock = pygame.time.Clock()

def draw_maze():
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
            color = WHITE if cell == ' ' else BLACK
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, GRAY, rect, 1)
    # Start and end positions
    pygame.draw.rect(screen, GREEN, (start[0]*TILE_SIZE, start[1]*TILE_SIZE, TILE_SIZE, TILE_SIZE))
    pygame.draw.rect(screen, RED, (end[0]*TILE_SIZE, end[1]*TILE_SIZE, TILE_SIZE, TILE_SIZE))

def display_steps(steps):
    step_text = font.render(f"GPT 4.5 - Steps: {steps}", True, BLACK)
    screen.blit(step_text, (8, height*TILE_SIZE + 10))
        
def main():
    frames = []  # List to store frames for the GIF
    steps = 0
    for pos in solution_path:
        steps += 1
        screen.fill(WHITE)
        draw_maze()
        pygame.draw.circle(screen, BLUE, (pos[0]*TILE_SIZE + TILE_SIZE//2, pos[1]*TILE_SIZE + TILE_SIZE//2), TILE_SIZE//3)
        display_steps(steps)
        pygame.display.flip()
        
        # Capture the frame (transpose to get correct orientation)
        frame = pygame.surfarray.array3d(screen).transpose(1, 0, 2)
        frames.append(frame)
        
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if pos == end:
            break

    # Final screen with completion message
    complete_text = font.render(f"Maze solved in {steps} steps!", True, BLUE)
    screen.blit(complete_text, (width*TILE_SIZE//2 - 30, height*TILE_SIZE + 7))
    pygame.display.flip()
    frame = pygame.surfarray.array3d(screen).transpose(1, 0, 2)
    frames.append(frame)

    # Save the collected frames as a GIF
    imageio.mimsave('maze_output_gpt4-5.gif', frames, fps=FPS)
    print("Saved animation to maze_output.gif")

    # Optionally, exit after a short delay instead of an infinite loop
    pygame.time.wait(3000)
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
