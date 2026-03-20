import pygame
import random
import time
import sys
import pyttsx3  # offline TTS

#  SETTINGS 
start_number = 1000
decrement = 7
end_number = 6
base_pause = 0.15      # starting pause between numbers
min_pause = 0.03       # fastest pause
acceleration = 0.002   # decrease in pause per number


#INITIALIZE PYGAME 
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # full screen
screen_width, screen_height = screen.get_size()
pygame.display.set_caption("Kaneki Countdown")
clock = pygame.time.Clock()
pygame.font.init()

# INITIALIZE TTS
engine = pyttsx3.init()
engine.say("1000 minus 7")  # say it once
engine.runAndWait()

# MAIN LOOP 
num = start_number
pause = base_pause
numbers = []  # list of tuples: (text, font, color, position)
shake_offset = 0

running = True
while num >= end_number and running:
    screen.fill((0, 0, 0))  # black background
    
    # Create random font size and color for dramatic effect
    font_size = random.randint(50, 120)
    font = pygame.font.SysFont("Arial", font_size, bold=True)
    color = random.choice([(255, 0, 0), (255, 255, 255), (255, 255, 0)])
    
    # Random position with optional screen shake
    x = random.randint(0, screen_width - font_size) + shake_offset
    y = random.randint(0, screen_height - font_size) + shake_offset
    
    numbers.append((str(num), font, color, (x, y)))
    
    # Draw all numbers
    for text, fnt, clr, pos in numbers:
        label = fnt.render(text, True, clr)
        screen.blit(label, pos)
    
    pygame.display.flip()
    
    # Event check
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    time.sleep(pause)
    
    # Gradually accelerate
    pause = max(min_pause, pause - acceleration)
    
    # Slight shake effect
    shake_offset = random.randint(-5, 5)
    
    num -= decrement
    clock.tick(60)

# Optional: final number dramatic display
if running:
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont("Arial", 150, bold=True)
    label = font.render(str(end_number), True, (255, 0, 0))
    screen.blit(label, ((screen_width - label.get_width())//2, (screen_height - label.get_height())//2))
    pygame.display.flip()
    time.sleep(2)

# BLACK SCREEN LOCKDOWN
typed = ""
locked = True
black = True

while locked:
    screen.fill((0, 0, 0))
    pygame.display.flip()
    
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.unicode and event.unicode.isprintable():
                typed += event.unicode
                # Only keep last 6 characters
                if len(typed) > 6:
                    typed = typed[-6:]
                if typed == "your_code_here":
                    locked = False

pygame.quit()
sys.exit()
