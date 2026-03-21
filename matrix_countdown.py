import pygame
import random
import time
import sys
import pyttsx3

# --- SETTINGS ---
NORMAL_DURATION   = 8    # seconds of normal rain
OVERLOAD_DURATION = 4    # seconds of overload before flash
UNLOCK_CODE       = "redpill"

# --- INITIALIZE PYGAME ---
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Matrix Override")
clock = pygame.font.init() or pygame.time.Clock()
pygame.font.init()
clock = pygame.time.Clock()

# --- TTS ---
engine = pyttsx3.init()
engine.say("1000 minus 7")
engine.runAndWait()

# --- COLORS ---
BLACK  = (0, 0, 0)
GREEN  = (0, 255, 100)
DIM    = (0, 80, 0)
BRIGHT = (200, 255, 200)
RED    = (255, 0, 0)

# --- CHARACTERS ---
katakana = [chr(i) for i in range(0x30A0, 0x30FF)]
chars    = katakana + list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*")

# --- FONTS ---
font_size    = 18
font         = pygame.font.SysFont("courier", font_size, bold=True)
overlay_font = pygame.font.SysFont("courier", 72, bold=True)
small_font   = pygame.font.SysFont("courier", 32, bold=True)


# ── Helper: make a stream ────────────────────

def make_stream(x, fast=False):
    length = random.randint(15, 35)
    return {
        "x":     x,
        "y":     random.randint(-HEIGHT, 0),
        "speed": random.randint(8, 18) if fast else random.randint(3, 7),
        "chars": [random.choice(chars) for _ in range(length)],
        "len":   length,
    }


def draw_streams(streams):
    for s in streams:
        for i, ch in enumerate(s["chars"]):
            cy = s["y"] + i * font_size
            if -font_size < cy < HEIGHT:
                if i == len(s["chars"]) - 1:
                    color = BRIGHT
                elif i > len(s["chars"]) - 4:
                    color = GREEN
                else:
                    color = DIM
                screen.blit(font.render(ch, True, color), (s["x"], cy))
        s["y"] += s["speed"]
        if s["y"] > HEIGHT:
            s["y"]     = random.randint(-200, -50)
            s["chars"] = [random.choice(chars) for _ in range(s["len"])]
        if random.random() > 0.95:
            idx = random.randint(0, len(s["chars"]) - 1)
            s["chars"][idx] = random.choice(chars)


# ── Phase 1: Normal rain ─────────────────────

columns = WIDTH // font_size
streams = [make_stream(i * font_size) for i in range(columns)]

start = time.time()
while time.time() - start < NORMAL_DURATION:
    screen.fill(BLACK)
    draw_streams(streams)
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
    clock.tick(30)


# ── Phase 2: Overload ────────────────────────

# Add 3x fast streams at random positions
for _ in range(columns * 3):
    streams.append(make_stream(random.randint(0, WIDTH), fast=True))

start = time.time()
while time.time() - start < OVERLOAD_DURATION:
    progress = (time.time() - start) / OVERLOAD_DURATION

    
    screen.fill((0, 0, 0))

    # Speeds up continuously
    for s in streams:
        s["speed"] = min(s["speed"] * 1.008, 35)

    draw_streams(streams)
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
    clock.tick(30)


# ── Phase 3: Flash → Black ───────────────────

for color in [(255, 255, 255), (180, 180, 180), (80, 80, 80), (0, 0, 0)]:
    screen.fill(color)
    pygame.display.flip()
    time.sleep(0.07)


# ── Phase 4: ACCESS DENIED lockscreen ────────

# Sparse slow background streams
bg_streams = [make_stream(i * font_size * 3) for i in range(columns // 3)]
for s in bg_streams:
    s["speed"] = random.randint(1, 2)

input_text  = ""
blink       = True
blink_timer = 0
running     = True

while running:
    screen.fill(BLACK)

    # Faint background rain
    for s in bg_streams:
        for i, ch in enumerate(s["chars"]):
            cy = s["y"] + i * font_size
            if -font_size < cy < HEIGHT:
                color = (0, 30, 0) if i < len(s["chars"]) - 1 else (0, 60, 0)
                screen.blit(font.render(ch, True, color), (s["x"], cy))
        s["y"] += s["speed"]
        if s["y"] > HEIGHT:
            s["y"]     = random.randint(-200, -50)
            s["chars"] = [random.choice(chars) for _ in range(s["len"])]

    # Blink timer
    blink_timer += 1
    if blink_timer >= 20:
        blink       = not blink
        blink_timer = 0

    # Semi-transparent overlay box
    overlay_rect = pygame.Surface((600, 260))
    overlay_rect.set_alpha(200)
    overlay_rect.fill(BLACK)
    rx = WIDTH  // 2 - 300
    ry = HEIGHT // 2 - 130
    screen.blit(overlay_rect, (rx, ry))
    pygame.draw.rect(screen, GREEN, (rx, ry, 600, 260), 2)

    # ACCESS DENIED — blinking red
    denied_color = RED if blink else (150, 0, 0)
    title_surf   = overlay_font.render("ACCESS DENIED", True, denied_color)
    screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, HEIGHT // 2 - 100))

    # Prompt
    prompt_surf = small_font.render("ENTER OVERRIDE CODE:", True, GREEN)
    screen.blit(prompt_surf, (WIDTH // 2 - prompt_surf.get_width() // 2, HEIGHT // 2 - 10))

    # Asterisks + blinking cursor
    asterisks    = ">" + "*" * len(input_text) + ("|" if blink else " ")
    entered_surf = small_font.render(asterisks, True, BRIGHT)
    screen.blit(entered_surf, (WIDTH // 2 - entered_surf.get_width() // 2, HEIGHT // 2 + 45))

    pygame.display.flip()

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if input_text == UNLOCK_CODE:
                    running = False
                else:
                    input_text = ""
            elif event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]
            elif event.unicode and event.unicode.isprintable():
                input_text += event.unicode

    clock.tick(30)

pygame.quit()
sys.exit()