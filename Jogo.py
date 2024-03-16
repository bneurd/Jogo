import pygame
import random
from pylsl import StreamInlet, resolve_stream

# Initialize Pygame
pygame.init()

# Screen dimensions
info = pygame.display.Info()

width = info.current_w
height = info.current_h
screen = pygame.display.set_mode((width - 10, height - 50))
pygame.display.set_caption('Nome do jogo')

# Background image
background = pygame.image.load('Background.png')
background = pygame.transform.scale(background, (width - 10, height - 50))

# Sounds 
barulho_phase2 = pygame.mixer.Sound('smw_kick.wav')

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
yellow = (255, 255, 0)

# Clock and main loop control variables
clock = pygame.time.Clock()
running = True

# Number of trials
num_trials = 4

# Phase durations
phase1_duration = 2  # 2 seconds for phase 1
phase2_duration = 8  # 8 seconds for phase 2

# Flag to track whether music has been played in phase 2
music_played = False

# Get stream on the lab network
streams = resolve_stream('type', 'Markers')

# create a new inlet to read from the stream
inlet = StreamInlet(streams[0])

last_direction = None  # Initialize the last chosen direction

# Function to choose the direction of the triangle
def choose_triangle_direction():
    global last_direction
    
    # Define the options: 1 for pointing up, 2 for pointing down
    options = [1, 2]
    
    # If the last two directions were the same, choose the opposite
    if last_direction is not None:
        options.remove(last_direction)
    
    # Randomly choose between the remaining options
    direction = random.choice(options)
    last_direction = direction
    return direction

# Class for the spaceship
class Foguete(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        original_image = pygame.image.load('Spaceship.png')
        self.image = pygame.transform.scale(original_image, (109 * 1.6, 73 * 1.6))
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (0, height // 2)  # Start at the middle-left of the screen
        self.speed = 2.7 # Set the initial speed

    def update(self, keys):
        # Move the spaceship to the right
        self.rect.x += self.speed

        # Move the spaceship up if W is pressed
        if keys[pygame.K_w]:
            self.rect.y -= self.speed

        # Move the spaceship down if S is pressed
        if keys[pygame.K_s]:
            self.rect.y += self.speed

        # Ensure the spaceship stays within the screen boundaries
        self.rect.y = max(0, min(self.rect.y, height - self.rect.height))

# Main game loop
for trial in range(1, num_trials + 1):

    # Reset phase variables for each trial
    current_phase = 1
    start_time = pygame.time.get_ticks()
    start_phase2_time = 0  # Initialize the start time of phase 2
    music_played = False  # Reset the flag for each trial

    # Create sprite group and object
    all_sprites = pygame.sprite.Group()
    foguete = Foguete()
    all_sprites.add(foguete)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        sample, timestamp = inlet.pull_sample()
        print("got %s at time %s" % (sample[0], timestamp))

        keys = pygame.key.get_pressed()
        foguete.update(keys)

        # Calculate elapsed time
        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - start_time) // 1000  # Convert to seconds

        screen.fill(white)
        screen.blit(background, (0, 0))

        # Check phase transitions
        if current_phase == 1:
            # Draw additional elements only in phase 1 after 2 seconds
            if elapsed_time >= phase1_duration:
                current_phase = 2
                start_phase2_time = pygame.time.get_ticks()  # Record the start time of phase 2

                # Determine the direction of the triangle when phase 2 starts
                triangle_direction = choose_triangle_direction()

        elif current_phase == 2:
            # Calculate time in phase 2 based on the start time of this trial
            time_in_phase2 = (current_time - start_phase2_time) // 1000

            # Play music in phase 2 if it hasn't been played yet
            if not music_played:
                barulho_phase2.play()
                music_played = True  # Set the flag to indicate that music has been played

            # Draw elements during the second phase
            line_color = black
            line_y = height // 2
            line_start = (0, line_y)
            line_end = (width, line_y)
            line_thickness = 2

            pygame.draw.line(screen, line_color, line_start, line_end, line_thickness)

            if time_in_phase2 < 1:  # Display both triangle images for the first 1 second
                if triangle_direction == 1:
                    # Draw the triangle pointing up
                    triangle_vertices = [(width // 2, height // 2 - 60),
                                         (width // 2 - 40, height // 2 + 2),
                                         (width // 2 + 40, height // 2 + 2)]
                else:
                    # Draw the triangle pointing down
                    triangle_vertices = [(width // 2, height // 2 + 60),
                                         (width // 2 - 40, height // 2 - 2),
                                         (width // 2 + 40, height // 2 - 2)]

                pygame.draw.polygon(screen, yellow, triangle_vertices)
            else:
                # Display only the outlined version for the rest of the phase
                if triangle_direction == 1:
                    # Draw the triangle pointing up
                    triangle_vertices = [(width // 2, height // 2 - 60),
                                         (width // 2 - 40, height // 2 + 2),
                                         (width // 2 + 40, height // 2 + 2)]
                else:
                    # Draw the triangle pointing down
                    triangle_vertices = [(width // 2, height // 2 + 60),
                                         (width // 2 - 40, height // 2 - 2),
                                         (width // 2 + 40, height // 2 - 2)]

                pygame.draw.polygon(screen, yellow, triangle_vertices, 5)

            all_sprites.draw(screen)
            all_sprites.update(keys)

            # Check if phase 2 duration has elapsed
            if elapsed_time > phase2_duration:
                running = False  # End the game or transition to the next part

        pygame.display.flip()

        clock.tick(60)

    # Reset running variable for the next trial
    running = True

pygame.quit()
