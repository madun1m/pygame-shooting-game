
import pygame
import random
import time
import os

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("슈팅 게임 개선판")
clock = pygame.time.Clock()

current_path = os.path.dirname(__file__)
bg_img = pygame.image.load(os.path.join(current_path, "background.png"))

try:
    pygame.mixer.music.load(os.path.join(current_path, "music.mp3"))
    pygame.mixer.music.play(-1)
except:
    print("배경음악 로드 실패")

font = pygame.font.SysFont("malgungothic", 30)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
GRAY = (100, 100, 100)

start_button = pygame.Rect(300, 250, 200, 60)
shop_button = pygame.Rect(300, 330, 200, 60)

player = pygame.Rect(375, 500, 50, 50)
bullets = []
enemy_bullets = []
enemy = pygame.Rect(random.randint(0, 750), random.randint(50, 200), 50, 50)
boss = None
boss_bullets = []

money = 0
score = 0
stage = 1
player_hp = 3
boss_hp = 10
weapon = "single"
last_shot_time = 0
game_state = "menu"
weapon_unlocked = False

enemy_dx = random.choice([-1, 1])
enemy_dy = random.choice([-1, 1])
enemy_move_timer = 0
enemy_attack_timer = 0
boss_direction = 3
boss_attack_timer = 0

def draw_text(text, x, y, color=BLACK):
    txt = font.render(text, True, color)
    screen.blit(txt, (x, y))

running = True
while running:
    dt = clock.tick(60)
    screen.fill(WHITE)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    game_state = "play"
                elif shop_button.collidepoint(event.pos):
                    game_state = "shop"

        if game_state in ["game_over", "win"]:
            if keys[pygame.K_r]:
                player_hp = 3
                score = 0
                boss = None
                boss_hp = 10
                bullets.clear()
                boss_bullets.clear()
                enemy_bullets.clear()
                game_state = "menu"

    if game_state == "menu":
        screen.blit(bg_img, (0, 0))
        draw_text("슈팅 게임 개선판", 270, 150)
        pygame.draw.rect(screen, RED, start_button)
        pygame.draw.rect(screen, GREEN, shop_button)
        draw_text("게임 시작", 340, 265, WHITE)
        draw_text("상점", 370, 345, WHITE)

    elif game_state == "shop":
        screen.fill(WHITE)
        draw_text("현재 돈: {}원".format(money), 270, 200)
        draw_text("10원: 다발총 구매", 270, 240)
        draw_text("Enter 키: 구매하기", 270, 280)
        draw_text("B키: 돌아가기", 270, 320)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    game_state = "menu"
                elif event.key == pygame.K_RETURN:
                    if money >= 10 and not weapon_unlocked:
                        weapon = "multi"
                        money -= 10
                        weapon_unlocked = True

    elif game_state in ["game_over", "win"]:
        msg = "게임 승리!" if game_state == "win" else "게임 오버"
        draw_text(msg, 320, 250, RED)
        draw_text("R 키로 메뉴로 돌아가기", 260, 300)

    elif game_state == "play":
        screen.blit(bg_img, (0, 0))

        if keys[pygame.K_LEFT] and player.x > 0:
            player.x -= 5
        if keys[pygame.K_RIGHT] and player.x < 750:
            player.x += 5
        if keys[pygame.K_UP] and player.y > 0:
            player.y -= 5
        if keys[pygame.K_DOWN] and player.y < 550:
            player.y += 5

        if keys[pygame.K_SPACE] and time.time() - last_shot_time > 0.4:
            if weapon == "single":
                bullets.append(pygame.Rect(player.x + 22, player.y, 6, 10))
            elif weapon == "multi":
                bullets.append(pygame.Rect(player.x + 10, player.y, 6, 10))
                bullets.append(pygame.Rect(player.x + 22, player.y, 6, 10))
                bullets.append(pygame.Rect(player.x + 34, player.y, 6, 10))
            last_shot_time = time.time()

        for b in bullets:
            b.y -= 8
        bullets = [b for b in bullets if b.y > 0]

        if score >= 10:
            stage = 3
        elif score >= 5:
            stage = 2

        if stage < 3:
            enemy_move_timer += 1
            if enemy_move_timer > 20:
                enemy.x += enemy_dx * (1 + stage)
                enemy.y += enemy_dy * (1 + stage)
                if enemy.x <= 0 or enemy.x >= 750:
                    enemy_dx *= -1
                if enemy.y <= 0 or enemy.y >= 550:
                    enemy_dy *= -1
                enemy_move_timer = 0

            enemy_attack_timer += 1
            if enemy_attack_timer > 120:
                enemy_bullets.append(pygame.Rect(enemy.x + 22, enemy.y + 50, 5, 12))
                enemy_attack_timer = 0

        if stage == 3 and not boss:
            boss = pygame.Rect(300, 50, 100, 80)

        if boss:
            boss.x += boss_direction
            if boss.x <= 0 or boss.x >= 700:
                boss_direction *= -1
            boss_attack_timer += 1
            if boss_attack_timer > 60:
                boss_bullets.append(pygame.Rect(boss.x + 45, boss.y + 80, 8, 15))
                boss_attack_timer = 0

        for bb in boss_bullets:
            bb.y += 5
        boss_bullets = [bb for bb in boss_bullets if bb.y < 600]

        for eb in enemy_bullets:
            eb.y += 5
        enemy_bullets = [eb for eb in enemy_bullets if eb.y < 600]

        for b in bullets[:]:
            if boss and b.colliderect(boss):
                bullets.remove(b)
                boss_hp -= 1
                if boss_hp <= 0:
                    game_state = "win"
            elif not boss and b.colliderect(enemy):
                bullets.remove(b)
                score += 1
                money += 1
                enemy = pygame.Rect(random.randint(0, 750), random.randint(50, 200), 50, 50)

        for bb in boss_bullets[:]:
            if bb.colliderect(player):
                boss_bullets.remove(bb)
                player_hp -= 1
        for eb in enemy_bullets[:]:
            if eb.colliderect(player):
                enemy_bullets.remove(eb)
                player_hp -= 1
        if not boss and enemy.colliderect(player):
            player_hp -= 1
            enemy = pygame.Rect(random.randint(0, 750), random.randint(50, 200), 50, 50)

        if player_hp <= 0:
            game_state = "game_over"

        # 그리기
        pygame.draw.rect(screen, GREEN, player)
        if not boss:
            pygame.draw.rect(screen, RED, enemy)
        else:
            pygame.draw.rect(screen, RED, boss)
            pygame.draw.rect(screen, RED, (600, 10, boss_hp * 15, 20))

        for b in bullets:
            pygame.draw.rect(screen, BLACK, b)
        for bb in boss_bullets:
            pygame.draw.rect(screen, GRAY, bb)
        for eb in enemy_bullets:
            pygame.draw.rect(screen, GRAY, eb)

        for i in range(player_hp):
            pygame.draw.rect(screen, RED, (10 + i * 35, 10, 30, 20))

        draw_text(f"점수: {score}", 10, 40)
        draw_text(f"돈: {money}", 10, 70)
        draw_text(f"무기: {'다발총' if weapon == 'multi' else '단발총'}", 10, 100)

    pygame.display.update()

pygame.quit()
