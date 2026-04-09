import pygame, random, sys
pygame.init(); pygame.mixer.init()

W,H = 800,600
screen = pygame.display.set_mode((W,H))
clock = pygame.time.Clock()

difficulty = "medium"
emotion = "neutral"

# LOAD
bg = pygame.transform.scale(pygame.image.load("bg.jpg").convert(), (W,H))
enemy_img = pygame.transform.scale(pygame.image.load("enemy.png").convert_alpha(), (60,60))
boss_img = pygame.transform.scale(pygame.image.load("boss.png").convert_alpha(), (150,150))

WHITE=(255,255,255); GREEN=(0,255,0)
font = pygame.font.Font(None,28)

hit = pygame.mixer.Sound("hit.wav")

def draw_text(txt,x,y):
    screen.blit(font.render(txt,True,WHITE),(x,y))

# 🎭 EMOTION
def update_emotion(lives, score):
    if lives == 1: return "panic"
    elif score > 20: return "happy"
    elif score < 5: return "angry"
    return "neutral"

# 🎬 INTRO
def intro():
    while True:
        screen.fill((0,0,0))
        draw_text("🔥 DEMON INVASION 🔥",220,250)
        draw_text("Press SPACE",300,320)

        for e in pygame.event.get():
            if e.type==pygame.QUIT: sys.exit()
            if e.type==pygame.KEYDOWN and e.key==pygame.K_SPACE: return

        pygame.display.update(); clock.tick(60)

# 🎮 MENU
def menu():
    while True:
        screen.blit(bg,(0,0))

        play = pygame.Rect(300,250,200,50)
        settings_btn = pygame.Rect(300,320,200,50)
        exit_btn = pygame.Rect(300,390,200,50)

        mouse = pygame.mouse.get_pos()

        for btn in [play,settings_btn,exit_btn]:
            pygame.draw.rect(screen,(255,100,0) if btn.collidepoint(mouse) else (0,0,0),btn)

        draw_text("PLAY",360,265)
        draw_text("SETTINGS",340,335)
        draw_text("EXIT",360,405)

        draw_text("← → Move",20,500)
        draw_text("Avoid Enemies",20,530)
        draw_text("Collect Coins 💰",20,560)

        for e in pygame.event.get():
            if e.type==pygame.QUIT: sys.exit()
            if e.type==pygame.MOUSEBUTTONDOWN:
                if play.collidepoint(e.pos): return "play"
                if settings_btn.collidepoint(e.pos): return "settings"
                if exit_btn.collidepoint(e.pos): sys.exit()

        pygame.display.update()

# ⚙️ SETTINGS
def settings():
    global difficulty
    while True:
        screen.fill((20,20,20))

        easy = pygame.Rect(300,220,200,50)
        med = pygame.Rect(300,300,200,50)
        hard = pygame.Rect(300,380,200,50)

        mouse = pygame.mouse.get_pos()

        for btn in [easy,med,hard]:
            pygame.draw.rect(screen,(255,100,0) if btn.collidepoint(mouse) else (50,50,50),btn)

        draw_text("EASY",360,235)
        draw_text("MEDIUM",340,315)
        draw_text("HARD",360,395)
        draw_text(f"CURRENT: {difficulty}",300,150)

        for e in pygame.event.get():
            if e.type==pygame.QUIT: sys.exit()
            if e.type==pygame.MOUSEBUTTONDOWN:
                if easy.collidepoint(e.pos): difficulty="easy"; return
                if med.collidepoint(e.pos): difficulty="medium"; return
                if hard.collidepoint(e.pos): difficulty="hard"; return

        pygame.display.update()

# 🎮 GAME
def game():
    global emotion

    player = pygame.Rect(375,500,50,50)
    lives,score,timer = 3,0,0

    enemies=[]; coins=[]
    shake=flash=0

    # 🔥 INITIAL DRAGONS
    for _ in range(5):
        enemies.append(pygame.Rect(random.randint(0,W-60),random.randint(-300,0),60,60))

    # 👾 BOSS
    boss=None
    boss_health=20
    boss_active=False
    boss_fire=[]
    boss_dir=4

    while True:
        clock.tick(60); timer+=1

        emotion = update_emotion(lives, score)

        # difficulty via emotion
        if emotion=="angry": enemy_speed,spawn_rate = 6,25
        elif emotion=="happy": enemy_speed,spawn_rate = 2,60
        elif emotion=="panic": enemy_speed,spawn_rate = 3,40
        else: enemy_speed,spawn_rate = 4,35

        # background
        if emotion=="panic": screen.fill((50,0,0))
        elif emotion=="happy": screen.fill((0,50,0))
        else: screen.blit(bg,(0,0))

        offx,offy = random.randint(-shake,shake),random.randint(-shake,shake)

        for e in pygame.event.get():
            if e.type==pygame.QUIT: sys.exit()

        keys=pygame.key.get_pressed()
        player.x += (keys[pygame.K_RIGHT]-keys[pygame.K_LEFT])*6

        # 👾 ENEMY SPAWN
        if not boss_active and random.randint(1,spawn_rate)==1:
            enemies.append(pygame.Rect(random.randint(0,W-60),0,60,60))

        # 👾 ENEMY
        for en in enemies[:]:
            en.y+=enemy_speed

            if en.colliderect(player):
                lives-=1; hit.play(); shake=8; flash=5
                if random.randint(1,3)==1:
                    coins.append(pygame.Rect(en.x,en.y,15,15))
                enemies.remove(en)

            elif en.y>H:
                score+=1
                if random.randint(1,3)==1:
                    coins.append(pygame.Rect(en.x,en.y,15,15))
                enemies.remove(en)

        # 💰 COINS
        for c in coins[:]:
            c.y+=3
            pygame.draw.circle(screen,(255,215,0),(c.x+7,c.y+7),7)

            if c.colliderect(player):
                score+=5
                coins.remove(c)
            elif c.y>H:
                coins.remove(c)

        # 🔥 BOSS SPAWN
        if score > 15 and not boss_active:
            boss = pygame.Rect(300,50,150,150)
            boss_active = True
            enemies.clear()

        # 🔥 BOSS
        if boss_active:
            boss.x += boss_dir
            if boss.x <= 0 or boss.x >= W-150:
                boss_dir *= -1

            screen.blit(boss_img,(boss.x,boss.y))

            # 🔥 FIRE SHOOT
            if timer % 40 == 0:
                boss_fire.append([boss.x+75,boss.y+80])

            # 🔥 FIRE MOVE
            for f in boss_fire[:]:
                f[1]+=6
                pygame.draw.circle(screen,(255,80,0),(int(f[0]),int(f[1])),10)

                if pygame.Rect(f[0]-10,f[1]-10,20,20).colliderect(player):
                    lives-=1; hit.play(); boss_fire.remove(f)
                elif f[1]>H:
                    boss_fire.remove(f)

            # collision
            if player.colliderect(boss):
                lives-=1; hit.play()

            pygame.draw.rect(screen,(255,0,0),(250,20,boss_health*10,15))

            if boss_health<=0:
                screen.fill((0,0,0))
                draw_text("YOU WIN 🏆",300,250)
                pygame.display.update()
                pygame.time.delay(2000)
                return

        # PLAYER
        pygame.draw.circle(screen,(0,255,100),player.center,40,2)
        pygame.draw.rect(screen,GREEN,player)

        # DRAW ENEMY
        for en in enemies:
            screen.blit(enemy_img,(en.x+offx,en.y+offy))

        # EFFECTS
        if flash>0:
            overlay=pygame.Surface((W,H))
            overlay.fill((255,0,0))
            overlay.set_alpha(80)
            screen.blit(overlay,(0,0))
            flash-=1

        if shake>0: shake-=1

        # UI
        draw_text(f"LIVES:{lives}",10,10)
        draw_text(f"SCORE:{score}",10,30)
        draw_text(f"EMOTION:{emotion}",600,10)

        pygame.display.update()

        if lives<=0:
            screen.fill((0,0,0))
            draw_text("GAME OVER",300,250)
            pygame.display.update()
            pygame.time.delay(1500)
            return

# 🔁 FLOW
while True:
    intro()
    choice = menu()

    if choice=="play":
        game()
    else:
        settings()