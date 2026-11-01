import pygame
import sys
import random
import math
import json
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import colorsys

pygame.init()
pygame.mixer.init()


# --- Screen setup ---
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sipak Game")

# --- Load Background ---
background = pygame.image.load("image/bg.png")

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (60, 130, 255)
PINK = (255, 120, 200)
RED = (255, 0, 0)
YELLOW = (255, 215, 0)
GRAY = (200, 200, 200)

# --- Fonts ---
font = pygame.font.Font(None, 48)
small_font = pygame.font.Font(None, 36)
tiny_font = pygame.font.Font(None, 24)

# --- Game Variables ---
clock = pygame.time.Clock()
state = "menu"  # menu → select → name → play → leaderboard → game_over
previous_state = None
player_name = ""
score = 0
is_kicking = False
kick_timer = 0


# two-player / AI
two_player = False
ai_character = None
ai_char_x = WIDTH // 2 + 140
ai_char_y = HEIGHT - 150
ai_speed = 3.5
ai_facing_right = False
ai_kick_timer = 0
ai_kick_delay = 300  # ms delay when AI prepares a kick
play_owner = "player"  # who currently holds sipa in play ("player" or "ai")
button_width = 120
button_height = 50

# --- Load Images ---
male_kick = pygame.transform.scale(pygame.image.load("image/mkick.png"), (120, 120))
female_kick = pygame.transform.scale(pygame.image.load("image/fkick.png"), (120, 120))
male_idle = pygame.image.load("image/male.png")
female_idle = pygame.image.load("image/female.png")
sipa_img = pygame.image.load("image/sipa.png")
bg_img = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Invisible exit button (Rect lang)
exit_button_rect = pygame.Rect(WIDTH - 100, 10, 80, 40)
back_button_rect_select = pygame.Rect(
    (WIDTH - button_width) // 2,  # centered horizontally
    HEIGHT - 80,                  # y position (from bottom)
    button_width,
    button_height
)

pygame.mixer.music.load("sound/bg_music.mp3")
pygame.mixer.music.set_volume(0.6)  # volume 0.0 - 1.0
pygame.mixer.music.play(-1)  # -1 = loop forever

button_sound = pygame.mixer.Sound("sound/button_sound.mp3")  # o .wav
button_sound.set_volume(0.8)

gameover_sound = pygame.mixer.Sound("sound/game_over.mp3")  # maliit na game over effect
gameover_sound.set_volume(0.9)  # adjust volume



kick_sound = pygame.mixer.Sound("sound/kick.mp3")  # or .wav
kick_sound.set_volume(0.9)  # volume optional

typing_sound = pygame.mixer.Sound("sound/button_sound.mp3")  # maliit na click sound
typing_sound.set_volume(0.9)  # hindi masyadong malakas

 
# Scale idle
male_idle = pygame.transform.scale(male_idle, (120, 120))
female_idle = pygame.transform.scale(female_idle, (120, 120))
# Start screen choice
game_mode = None  # None, "one_player", "multi_player"


# make sipa smaller
SIPA_SIZE = 36
sipa_img = pygame.transform.scale(sipa_img, (SIPA_SIZE, SIPA_SIZE))

# --- Load Walking Animations ---
male_walk_frames = [
    pygame.transform.scale(pygame.image.load(f"image/male_walk{i}.png"), (120, 120))
    for i in range(1, 5)
]
female_walk_frames = [
    pygame.transform.scale(pygame.image.load(f"image/female_walk{i}.png"), (120, 120))
    for i in range(1, 5)
]
# --- Background images ---
bg_images = [
    pygame.transform.scale(pygame.image.load("image/bg.png"), (WIDTH, HEIGHT)),
    pygame.transform.scale(pygame.image.load("image/bg1.jpg"), (WIDTH, HEIGHT)),
    pygame.transform.scale(pygame.image.load("image/bg2.jpg"), (WIDTH, HEIGHT)),
    pygame.transform.scale(pygame.image.load("image/bg3.jpg"), (WIDTH, HEIGHT))
]

# --- Background musics ---
bg_musics = [
    "sound/bg_music.mp3",
    "sound/bg1.mp3",
    "sound/bg2.mp3",
    "sound/bg3.mp3"
]

current_bg_index = 0
current_music_index = 0
pygame.mixer.music.load(bg_musics[current_bg_index])
pygame.mixer.music.play()  # loop

# --- Timer variables ---
bg_change_interval = 30000  # 30 seconds in milliseconds
last_bg_change = pygame.time.get_ticks()



# --- Character variables ---
character = None
char_x = WIDTH // 2 - 60
char_y = HEIGHT - 150
char_speed = 9
walk_index = 0
walking = False
facing_right = True

# --- Sipa variables ---
sipa_x = WIDTH // 2
sipa_y = HEIGHT - 200
sipa_dx = 0
sipa_dy = 0
gravity = 0.30
on_air = False
spin_angle = 0
rotation_speed = 0

# --- Menu demo sipa (auto animation on Start screen) ---
menu_char_y = HEIGHT - 150
menu_left_char_x = WIDTH // 2 - 200
menu_right_char_x = WIDTH // 2 + 80

# Shared demo sipa (rally back-and-forth)
menu_sipa_x = menu_left_char_x + 80
menu_sipa_y = menu_char_y + 65
menu_sipa_dx = 0
menu_sipa_dy = 0
menu_on_air = False
menu_owner = "left"   # "left" or "right" -- who currently holds / will kick
menu_spin = 0

# --- Multiplayer variables ---
ai_x = WIDTH//2 + 140
ai_y = HEIGHT - 150
ai_speed = 5
ai_facing_right = False
ai_kick_delay = 600   # ms
ai_next_kick = 0
player_score = 0
ai_score = 0
net_y = HEIGHT - 180

# per-character kick state (for brief kick frame)
menu_left_is_kicking = False
menu_left_kick_timer = 0
menu_right_is_kicking = False
menu_right_kick_timer = 0

# rally control
menu_last_action = pygame.time.get_ticks()
menu_kick_delay = 420          # ms between catch and next kick
menu_next_kick_time = menu_last_action + 600
menu_rally_count = 0
menu_rally_target = random.randint(3, 7)  # how many successful passes before a miss
menu_reset_time = 0

# --- Leaderboard file ---
LEADERBOARD_FILE = "leaderboard.json"
def rainbow_color(speed=0.002):
    # Gumagawa ng shifting hue (rainbow)
    time_now = pygame.time.get_ticks() * speed
    hue = time_now % 1.0
    r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
    return int(r * 255), int(g * 255), int(b * 255)

def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "r") as f:
            return json.load(f)
    return []

def save_leaderboard(leaderboard):
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(leaderboard, f, indent=2)

def update_leaderboard(name, score):
    leaderboard = load_leaderboard()
    leaderboard.append({"name": name, "score": score})
    leaderboard = sorted(leaderboard, key=lambda x: x["score"], reverse=True)[:5]
    save_leaderboard(leaderboard)

def draw_leaderboard(x, y, title_text="Leaderboard (Top 5)", font_to_use=None):
    if font_to_use is None:
        font_to_use = small_font
    leaderboard = load_leaderboard()
    title = font_to_use.render(title_text, True, BLACK)
    screen.blit(title, (x, y))
    y += 30

    if not leaderboard:
        screen.blit(font_to_use.render("Wala pang record.", True, BLACK), (x, y))
    else:
        for i, entry in enumerate(leaderboard):
            color = RED if i == 0 else BLACK
            text = font_to_use.render(f"{i+1}. {entry['name']} - {entry['score']}", True, color)
            screen.blit(text, (x, y))
            y += 25
gameover_played = False
def reset_game():
    global sipa_x, sipa_y, sipa_dx, sipa_dy, score, state, on_air, char_x, spin_angle
    global gameover_played
    sipa_x = WIDTH // 2
    sipa_y = HEIGHT - 200
    sipa_dx = 0
    sipa_dy = 0
    on_air = False
    score = 0
    spin_angle = 0
    char_x = WIDTH // 2 - 60
    state = "play"
    gameover_played = False  # reset for next game

def draw_button(text, x, y, w, h, color, hover_color, mouse_pos):
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, hover_color if rect.collidepoint(mouse_pos) else color, rect, border_radius=10)
    pygame.draw.rect(screen, BLACK, rect, 2)
    label = small_font.render(text, True, BLACK)
    screen.blit(label, (x + (w - label.get_width()) // 2, y + (h - label.get_height()) // 2))
    return rect
# --- Feather variables (for menu animation) ---
feathers = []
for _ in range(20):  # dami ng feather
    feather = {
        "x": random.randint(100, WIDTH-100),
        "y": random.randint(50, HEIGHT-200),
        "dx": random.uniform(-2, 2),
        "dy": random.uniform(-2, 2),
        "size": random.randint(20, 40)
    }
    feathers.append(feather)



# --- Game Loop ---
while True:
    screen.blit(bg_images[current_bg_index], (0, 0))
    keys = pygame.key.get_pressed()
    mouse_pos = pygame.mouse.get_pos()

    # center helpers
    select_center_y = HEIGHT // 2 - 40

    # --- Precompute clickable rects ---
    start_button_rect = pygame.Rect(WIDTH//2 - 100, 250, 200, 60)
    leaderboard_button_rect = pygame.Rect(WIDTH//2 - 100, 340, 200, 60)
    exit_button_rect = pygame.Rect(WIDTH//2 - 100, 430, 200, 60)
    back_button_rect = pygame.Rect(WIDTH // 2 - 60, 480, 120, 50)
    # centered character selection rects (match select rendering positions)
    male_rect = pygame.Rect((WIDTH//2 - 160) - 80, select_center_y - 80, 160, 160)
    female_rect = pygame.Rect((WIDTH//2 + 160) - 80, select_center_y - 80, 160, 160)
    play_again_rect = pygame.Rect(WIDTH // 2 - 220, 380, 200, 60)
    home_rect = pygame.Rect(WIDTH // 2 + 20, 380, 200, 60)
    leaderboard_rect2 = pygame.Rect(WIDTH // 2 - 100, 460, 200, 60)
    # start button for name entry screen
    start_name_rect = pygame.Rect(WIDTH//2 - 100, 340, 200, 60)

    # mode select rects (used for click handling)
    mode_one_rect = pygame.Rect(WIDTH//2 - 120, 250, 240, 60)
    mode_multi_rect = pygame.Rect(WIDTH//2 - 120, 340, 240, 60)
    mode_back_rect = pygame.Rect(WIDTH//2 - 60, 430, 120, 50)

    now = pygame.time.get_ticks()
    if now - last_bg_change >= bg_change_interval:
        current_bg_index = (current_bg_index + 1) % len(bg_images)
        last_bg_change = now
    if not pygame.mixer.music.get_busy():  # kapag tapos na ang current track
        current_music_index = (current_music_index + 1) % len(bg_musics)
        pygame.mixer.music.load(bg_musics[current_music_index])
        pygame.mixer.music.play()


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # --- MENU STATE ---
        if state == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button_rect.collidepoint(event.pos):
                    button_sound.play()
                    state = "mode_select"
                elif leaderboard_button_rect.collidepoint(event.pos):
                    button_sound.play()
                    previous_state = "menu"
                    state = "leaderboard"
                if exit_button_rect.collidepoint(event.pos):
                    button_sound.play()
                    pygame.time.delay(500)  # para marinig muna bago mag-quit
                    pygame.quit()
                    sys.exit()

        # --- LEADERBOARD STATE ---
        elif state == "leaderboard":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button_rect.collidepoint(event.pos):
                    if previous_state == "game_over":
                        button_sound.play()
                        state = "game_over"
                    else:
                        state = "menu"
                        button_sound.play()

        # --- SELECT CHARACTER ---
        elif state == "select":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if male_rect.collidepoint(event.pos):
                    character = "male"
                    if game_mode == "multi_player":
                        ai_character = "female"
                    button_sound.play()
                    state = "name"
                elif female_rect.collidepoint(event.pos):
                    character = "female"
                    if game_mode == "multi_player":
                        ai_character = "male"
                    button_sound.play()
                    state = "name"
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if male_rect.collidepoint(event.pos):
                    character = "male"
                    player_name = ""
                    state = "name"
                elif female_rect.collidepoint(event.pos):
                    character = "female"
                    player_name = ""
                    state = "name"
                elif back_button_rect_select.collidepoint(event.pos):
                    button_sound.play()
                    state = "mode_select"

        # --- MODE SELECT (click handling only) ---
        elif state == "mode_select":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if mode_one_rect.collidepoint(event.pos):
                    button_sound.play()
                    game_mode = "one_player"
                    state = "select"
                elif mode_multi_rect.collidepoint(event.pos):
                    button_sound.play()
                    game_mode = "multi_player"
                    state = "select"
                elif mode_back_rect.collidepoint(event.pos):
                    button_sound.play()
                    state = "menu"

        # --- ENTER NAME ---
        elif state == "name":
            if event.type == pygame.KEYDOWN:
                typing_sound.play()
                if event.key == pygame.K_RETURN and player_name.strip() != "":
                    reset_game()
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    # avoid control characters
                    if event.unicode.isprintable():
                        player_name += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # allow clicking the Start button when a name is present
                if start_name_rect.collidepoint(event.pos) and player_name.strip() != "":
                    reset_game()
                    button_sound.play()


        # --- GAME OVER ---
        elif state == "game_over":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_rect.collidepoint(event.pos):
                    typing_sound.play()
                    reset_game()
                elif home_rect.collidepoint(event.pos):
                    button_sound.play()
                    state = "menu"
                elif leaderboard_rect2.collidepoint(event.pos):
                    button_sound.play()
                    previous_state = "game_over"
                    state = "leaderboard"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    typing_sound.play()
                    reset_game()
                    state = "play"
                    
                    


        # --- PLAY STATE ---
      

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            is_kicking = True
            kick_timer = pygame.time.get_ticks()  # start timer
            
            # --- PLAY KICK SOUND FOR 2 SECONDS ---
            kick_sound.play()          # play sound
            kick_sound.fadeout(2000)   # automatically stops after 2 sec with fadeout

            if not on_air:
                on_air = True
                sipa_dy = -10
                sipa_dx = random.uniform(-2, 2)
                rotation_speed = random.uniform(-5, 5)
            else:
                # use SIPA_SIZE/2 for center-based collision math
                if abs((char_x + 60) - (sipa_x + SIPA_SIZE/2)) < 70 and abs(char_y - sipa_y) < 40:
                    score += 1
                    diff = (sipa_x + SIPA_SIZE/2) - (char_x + 60)
                    if abs(diff) < 10:
                        power = -15
                        sipa_dx = random.uniform(-1.5, 1.5)
                        rotation_speed = random.uniform(-5, 5)
                    elif abs(diff) < 30:
                        power = -10
                        sipa_dx = diff / 8
                        rotation_speed = random.uniform(-7, 7)
                    else:
                        power = -7
                        sipa_dx = diff / 5
                        rotation_speed = random.uniform(-10, 10)
                    sipa_dy = power


    # --- RENDERING SECTIONS ---
    if state == "menu":
        now = pygame.time.get_ticks()
        # subtle walk wobble for liveliness
        walk_index += 0.06
        if walk_index >= 4:
            walk_index = 0

        # compute hand positions
        left_hand_x = menu_left_char_x + 80
        left_hand_y = menu_char_y + 65
        right_hand_x = menu_right_char_x + 40
        right_hand_y = menu_char_y + 65

        # If an automatic reset is scheduled (after miss/ground), do it
        if menu_reset_time and now >= menu_reset_time:
            menu_rally_count = 0
            menu_rally_target = random.randint(3, 7)
            menu_owner = "left"
            menu_on_air = False
            menu_sipa_x = left_hand_x - (SIPA_SIZE // 2)
            menu_sipa_y = left_hand_y - (SIPA_SIZE // 2)
            menu_reset_time = 0
            menu_next_kick_time = now + 1000
        # --- Update feather positions ---
        for feather in feathers:
            feather["x"] += feather["dx"]
            feather["y"] += feather["dy"]

            # bounce sa screen edges
            if feather["x"] <= 0 or feather["x"] >= WIDTH:
                feather["dx"] *= -1
            if feather["y"] <= 0 or feather["y"] >= HEIGHT-50:
                feather["dy"] *= -1

            # draw rainbow feather
            rainbow = rainbow_color()
            feather_surf = pygame.Surface((feather["size"], feather["size"]), pygame.SRCALPHA)
            pygame.draw.circle(feather_surf, (*rainbow, 200), (feather["size"]//2, feather["size"]//2), feather["size"]//2)
            screen.blit(feather_surf, (feather["x"], feather["y"]))

        # If sipa is in air, update physics
        if menu_on_air:
            menu_sipa_x += menu_sipa_dx
            menu_sipa_y += menu_sipa_dy
            menu_sipa_dy += gravity
            menu_spin = (menu_spin + 6) % 360

            # bounce off sides a little
            if menu_sipa_x <= 0 or menu_sipa_x >= WIDTH - SIPA_SIZE:
                menu_sipa_dx *= -0.7

            # if it hits ground
            if menu_sipa_y >= HEIGHT - (SIPA_SIZE + 30):
                menu_sipa_y = HEIGHT - (SIPA_SIZE + 30)
                menu_on_air = False
                # check if it landed near a hand to be "caught"
                # determine nearest hand
                dist_left = abs((menu_sipa_x + SIPA_SIZE//2) - left_hand_x)
                dist_right = abs((menu_sipa_x + SIPA_SIZE//2) - right_hand_x)
                catch_threshold = 60
                if dist_left < catch_threshold:
                    # caught by left
                    menu_owner = "left"
                    menu_rally_count += 1
                    menu_left_is_kicking = False
                    menu_left_kick_timer = now
                    # schedule next kick unless we've reached target
                    if menu_rally_count < menu_rally_target:
                        menu_next_kick_time = now + menu_kick_delay
                    else:
                        # this time they miss -> let it sit and then reset
                        menu_reset_time = now + 900
                elif dist_right < catch_threshold:
                    # caught by right
                    menu_owner = "right"
                    menu_rally_count += 1
                    menu_right_is_kicking = False
                    menu_right_kick_timer = now
                    if menu_rally_count < menu_rally_target:
                        menu_next_kick_time = now + menu_kick_delay
                    else:
                        menu_reset_time = now + 900
                else:
                    # not near either hand -> it just sits on ground, reset later
                    menu_reset_time = now + 900

        else:
            # anchored to current owner's hand
            if menu_owner == "left":
                menu_sipa_x = left_hand_x - (SIPA_SIZE // 2)
                menu_sipa_y = left_hand_y - (SIPA_SIZE // 2)
            else:
                menu_sipa_x = right_hand_x - (SIPA_SIZE // 2)
                menu_sipa_y = right_hand_y - (SIPA_SIZE // 2)
            menu_spin = 0

            # time to auto-kick?
            if now >= menu_next_kick_time and menu_reset_time == 0:
                # perform kick by current owner toward the other side
                if menu_owner == "left":
                    menu_sipa_dx = random.uniform(2.0, 4.0)  # send to right
                    menu_sipa_dy = -9
                    menu_owner = "left"
                    menu_left_is_kicking = True
                    menu_left_kick_timer = now
                else:
                    menu_sipa_dx = -random.uniform(2.0, 4.0)  # send to left
                    menu_sipa_dy = -9
                    menu_owner = "right"
                    menu_right_is_kicking = True
                    menu_right_kick_timer = now

                menu_on_air = True
                menu_spin = random.uniform(-8, 8)

        # draw left character (kick frame briefly)
        left_frame = male_kick if menu_left_is_kicking and now - menu_left_kick_timer < 300 else (male_walk_frames[int(walk_index)] if character == "male" else male_idle)

        # draw right character (kick frame briefly)
        right_frame = female_kick if menu_right_is_kicking and now - menu_right_kick_timer < 300 else (female_walk_frames[int(walk_index)] if character == "female" else female_idle)

        # Make them face each other: left faces RIGHT (flip), right faces LEFT (no flip)
        draw_left = pygame.transform.flip(left_frame, True, False)
        draw_right = right_frame

        screen.blit(draw_left, (menu_left_char_x, menu_char_y))
        screen.blit(draw_right, (menu_right_char_x, menu_char_y))

        # draw shared menu sipa
        rotated = pygame.transform.rotate(sipa_img, menu_spin)
        rrect = rotated.get_rect(center=(menu_sipa_x + SIPA_SIZE // 2, menu_sipa_y + SIPA_SIZE // 2))
        screen.blit(rotated, rrect.topleft)

        # Draw menu UI (center)
        title = font.render("SIPAK GAME", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 120))
        draw_button("Start Game", WIDTH//2 - 100, 250, 200, 60, BLUE, (100,180,255), mouse_pos)
        draw_button("Leaderboard", WIDTH//2 - 100, 340, 200, 60, YELLOW, (255,230,150), mouse_pos)
        # Sa loob ng rendering section (halimbawa sa lahat ng state o menu)
        exit_button_rect = draw_button("Exit", WIDTH//2 - 100, 430, 200, 60, RED, (220,220,220), mouse_pos)
    
    # --- RENDER MODE SELECT ---
    elif state == "mode_select":
        title = font.render("Choose Mode", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 120))

        # Buttons (rendered here; click handling uses the precomputed rects)
        draw_button("One Player", WIDTH//2 - 120, 250, 240, 60, BLUE, (100,180,255), mouse_pos)
        draw_button("Multiplayer", WIDTH//2 - 120, 340, 240, 60, YELLOW, (255,230,150), mouse_pos)
        draw_button("Back", WIDTH//2 - 60, 430, 120, 50, WHITE, GRAY, mouse_pos)

    elif state == "leaderboard":
        title = font.render("LEADERBOARD", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
        draw_leaderboard(WIDTH // 2 - 100, 180)
        draw_button("Back", WIDTH // 2 - 60, 480, 120, 50, WHITE, GRAY, mouse_pos)

    elif state == "select":
        # --- Title ---
        title = font.render("Select Character", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

        # --- Walking animation frame update ---
        walk_index += 0.15
        if walk_index >= 4:
            walk_index = 0

        # --- Animated bounce effect ---
        bounce = math.sin(pygame.time.get_ticks() * 0.005) * 5

        # compute centered positions for the two characters
        left_center_x = WIDTH // 2 - 160
        right_center_x = WIDTH // 2 + 160

        # --- Male animation ---
        male_frame = male_walk_frames[int(walk_index)]
        male_scaled = pygame.transform.scale(male_frame, (160, 160))  # larger
        male_rect = male_scaled.get_rect(center=(left_center_x, select_center_y + bounce))
        screen.blit(male_scaled, male_rect)

        # --- Female animation ---
        female_frame = female_walk_frames[int(walk_index)]
        female_scaled = pygame.transform.scale(female_frame, (160, 160))
        female_rect = female_scaled.get_rect(center=(right_center_x, select_center_y + bounce))
        screen.blit(female_scaled, female_rect)

        # --- Glowing labels ---
        glow = abs(math.sin(pygame.time.get_ticks() * 0.004)) * 80

        male_color = (int(min(255, 175 + glow)), int(min(255, 175 + glow)), 0)  # gold glow
        female_color = (255, int(min(200 + glow, 255)), int(min(220 + glow, 255)))  # pink glow

        male_label = small_font.render("Male", True, male_color)
        female_label = small_font.render("Female", True, female_color)
        screen.blit(male_label, (male_rect.centerx - male_label.get_width() // 2, male_rect.bottom + 10))
        screen.blit(female_label, (female_rect.centerx - female_label.get_width() // 2, female_rect.bottom + 10))
        draw_button("Back",back_button_rect_select.x,back_button_rect_select.y,back_button_rect_select.width,back_button_rect_select.height,WHITE,GRAY,mouse_pos)


    elif state == "name":
        # draw prompt
        text = font.render("Enter Name:", True, BLACK)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 200))
        

        # input box
        box_w, box_h = 400, 60
        box_x = WIDTH // 2 - box_w // 2
        box_y = 250
        input_box = pygame.Rect(box_x, box_y, box_w, box_h)
        pygame.draw.rect(screen, WHITE, input_box, border_radius=8)

        # placeholder or typed name
        display_name = player_name if player_name.strip() != "" else "Type your name..."
        name_surf = small_font.render(display_name, True, BLACK if player_name.strip() != "" else (120,120,120))
        screen.blit(name_surf, (box_x + 12, box_y + (box_h - name_surf.get_height()) // 2))

        # Start button (enabled only when name is non-empty)
        start_enabled = player_name.strip() != ""
        btn_color = BLUE if start_enabled else GRAY
        btn_hover = (100,180,255) if start_enabled else (220,220,220)
        draw_button("Start", start_name_rect.x, start_name_rect.y, start_name_rect.width, start_name_rect.height, btn_color, btn_hover, mouse_pos)


    elif state == "play":
        # Movement
        walking = False
        if keys[pygame.K_LEFT]:
            char_x -= char_speed
            facing_right = False
            walking = True
        if keys[pygame.K_RIGHT]:
            char_x += char_speed
            facing_right = True
            walking = True
        char_x = max(0, min(char_x, WIDTH - 120))

        # Animation
        if walking:
            walk_index += 0.2
            if walk_index >= 4:
                walk_index = 0
        else:
            walk_index = 0

        # Physics
        if on_air:
            # --- GRAVITY & POSITION UPDATE ---
            sipa_y += sipa_dy
            sipa_dy += gravity
            sipa_x += sipa_dx

            # --- REALISTIC ROTATION (pabigat behavior) ---
            if sipa_dy < 0:
                # Paakyat — umiikot paakyat (pabigat nasa baba umaangat)
                spin_angle += abs(sipa_dy) * 1.5
            else:
                # Pababa — umiikot pabalik (pabigat bumababa)
                spin_angle -= abs(sipa_dy) * 1.5

            spin_angle %= 360  # limit rotation overflow

            # --- FEATHER-LIKE DRIFT (rotation affects fall direction) ---
            drift_strength = 0.25
            sipa_x += math.sin(math.radians(spin_angle)) * drift_strength

            # --- EDGE COLLISION WITH LIGHT BOUNCE ---
            if sipa_x <= 0:
                sipa_x = 0
                sipa_dx *= -0.7
                rotation_speed *= -1
            elif sipa_x >= WIDTH - SIPA_SIZE:
                sipa_x = WIDTH - SIPA_SIZE
                sipa_dx *= -0.7
                rotation_speed *= -1

            # --- GROUND COLLISION (GAME OVER) ---
            if sipa_y >= HEIGHT - (SIPA_SIZE + 30):
                sipa_y = HEIGHT - (SIPA_SIZE + 30)
                sipa_dy = 0
                on_air = False
                spin_angle = 0
                rotation_speed = 0

                # 🔊 Game over sound (play once)
                if 'gameover_played' not in globals() or not gameover_played:
                    gameover_sound.play()
                    gameover_played = True

                # 🧾 Update leaderboard & switch state
                update_leaderboard(player_name, score)
                state = "game_over"

        else:
            # position sipa to match character's hand (center-based)
            # tuned offsets: smaller and a bit higher
            hand_offset_x_right = 80   # horizontal hand position when facing right (from char_x)
            hand_offset_x_left  = 40   # horizontal hand position when facing left (from char_x)
            hand_offset_y = 65         # smaller -> sipa raised a bit

            # sipa image is SIPA_SIZE; store top-left in sipa_x/sipa_y but want its center at the hand
            sipa_center_x = char_x + (hand_offset_x_right if facing_right else hand_offset_x_left)
            sipa_center_y = char_y + hand_offset_y

            sipa_x = sipa_center_x - (SIPA_SIZE // 2)
            sipa_y = sipa_center_y - (SIPA_SIZE // 2)
            spin_angle = 0

        # Draw character
        frame = (male_walk_frames if character == "male" else female_walk_frames)[int(walk_index)] if walking else (male_idle if character == "male" else female_idle)
        # determine what frame to draw
        if is_kicking and pygame.time.get_ticks() - kick_timer < 200:
            frame = male_kick if character == "male" else female_kick
        else:
            is_kicking = False
            if walking:
                frame = (male_walk_frames if character == "male" else female_walk_frames)[int(walk_index)]
            else:
                frame = male_idle if character == "male" else female_idle

        if facing_right:
            frame = pygame.transform.flip(frame, True, False)
        screen.blit(frame, (char_x, char_y))

        # Draw sipa (use SIPA_SIZE for correct centering)
        rotated_sipa = pygame.transform.rotate(sipa_img, spin_angle)
        rect = rotated_sipa.get_rect(center=(sipa_x + SIPA_SIZE // 2, sipa_y + SIPA_SIZE // 2))
        screen.blit(rotated_sipa, rect.topleft)

        # UI
        screen.blit(font.render(f"Score: {score}", True, BLACK), (20, 20))
        screen.blit(small_font.render(player_name, True, BLACK), (20, 60))

        # Live leaderboard (right corner, small)
        draw_leaderboard(WIDTH - 240, 20, "Live Leaderboard", tiny_font)

    elif state == "game_over":
        title = font.render("SIPAK GAME", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
        over_text = font.render("GAME OVER!", True, RED)
        screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, 200))
        name_text = small_font.render(f"Player: {player_name}", True, WHITE)
        screen.blit(name_text, (WIDTH // 2 - name_text.get_width() // 2, 250))
        score_text = small_font.render(f"Final Score: {score}", True, YELLOW)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 280))
        draw_button("Play Again", WIDTH // 2 - 220, 380, 200, 60, BLUE, (100,180,255), mouse_pos)
        draw_button("Home", WIDTH // 2 + 20, 380, 200, 60, WHITE, GRAY, mouse_pos)
        draw_button("Leaderboard", WIDTH // 2 - 100, 460, 200, 60, YELLOW, (255,230,150), mouse_pos)

    pygame.display.flip()
    clock.tick(60)
