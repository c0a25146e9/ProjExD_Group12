import math
import os
import pygame as pg
import sys
import random

# 画面サイズ
WIDTH = 800
HEIGHT = 600
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 色
WHITE = (255, 255, 255)
BLUE = (100, 200, 255)
GREEN = (0, 200, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

# 重力
GRAVITY = 0.8
# ジャンプ力
JUMP_POWER = -15


class Player:
    def __init__(self):
        self.image = pg.Surface((40, 50))
        self.image.fill(BLUE)
        self.image = pg.image.load("photo/3.png").convert_alpha()
        self.image = pg.transform.scale(self.image, (40, 50))
        self.image = pg.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = 400
        self.vy = 0
        self.speed = 5
        self.on_ground = False

    def update(self, keys, blocks):
        # 左移動
        if keys[pg.K_LEFT]:
            self.rect.x -= self.speed
        # 右移動
        if keys[pg.K_RIGHT]:
            self.rect.x += self.speed
        # ジャンプ
        if keys[pg.K_SPACE] and self.on_ground:
            self.vy = JUMP_POWER
            self.on_ground = False
        # 重力
        self.vy += GRAVITY
        self.rect.y += self.vy
        # 地面判定
        self.on_ground = False

        for block in blocks:
            if self.rect.colliderect(block.rect):
                # 上から乗った場合
                if self.vy > 0:
                    self.rect.bottom = block.rect.top
                    self.vy = 0
                    self.on_ground = True

    def draw(self, screen, scroll_x):
        screen.blit(self.image, (self.rect.x - scroll_x, self.rect.y))


class Block:
    def __init__(self, x, y, w, h):
        self.rect = pg.Rect(x, y, w, h)

    def draw(self, screen, scroll_x):
        pg.draw.rect(screen, GREEN, (self.rect.x - scroll_x, self.rect.y, self.rect.width, self.rect.height))


class Enemy:
    def __init__(self, x, y):
        self.rect = pg.Rect(x, y, 40, 40)

        self.image = pg.image.load("photo/kyomutomato.png").convert_alpha()
        self.image = pg.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self, screen, scroll_x):
        screen.blit(
            self.image,
            (self.rect.x - scroll_x, self.rect.y)
        )


class Goal:
    def __init__(self, x, y):
        self.rect = pg.Rect(x, y, 40, 120)

    def draw(self, screen, scroll_x):
        # 棒
        pg.draw.rect(screen, BLACK, (self.rect.x - scroll_x, self.rect.y, 5, self.rect.height))
        # 旗
        pg.draw.polygon(screen, YELLOW, [(self.rect.x - scroll_x + 5, self.rect.y), (self.rect.x - scroll_x + 60, self.rect.y + 20), (self.rect.x - scroll_x + 5, self.rect.y + 40)])


class Life:
    """
    残機数に関するクラス
    """
    def __init__(self, num):
        """
        引数 num：初期残機数
        """
        self.num = num
        self.image = pg.Surface((40, 40))
        self.image.set_colorkey((0, 0, 0))
        points = [(16*math.sin(t/100)**3 +20,
                   -(13*math.cos(t/100)-5*math.cos(2*t/100)-2*math.cos(3*t/100)-math.cos(4*t/100)) +20
                   ) for t in range(0,628) ]
        pg.draw.polygon(self.image, RED, points)
        self.rect = self.image.get_rect()
        self.rect.center = +50, HEIGHT-50
    
    def draw(self, screen, y):
        """
        残機を画面に表示する

        y：表示位置
        """
        total_width = self.num * 50
        start_x = (WIDTH - total_width) // 2

        for i in range (self.num):
                screen.blit(self.image, (start_x + i * 50, y))


class Score:
    """
    ゲーム中のスコアを表示させるクラス
    引数1:game_startの真偽
    引数2:game_overの真偽
    引数3:game_clearの真偽

    敵：10点
    """
    def __init__(self, game_start, game_over, game_clear):
        self.game_start = game_start
        self.game_over = game_over
        self.game_clear = game_clear
        self.font = pg.font.Font(None, 50)
        self.color = BLACK
        self.value = 0
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 100, HEIGHT-550

    def update(self, screen: pg.Surface, game_start, game_over, game_clear):
        if not game_start:
            return()
        
        if game_over or game_clear:  # ゲーム中とゲーム後のScoreの位置の変化
            self.rect.center = 370, 400
        else:
            self.rect.center = 100, HEIGHT-550

        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        screen.blit(self.image, self.rect)


def draw_text(screen, text, size, x, y, color=BLACK):
    font = pg.font.SysFont("yugothic", size)
    img = font.render(text, True, color)
    rect = img.get_rect(center=(x, y))
    screen.blit(img, rect)

def reset_game():
    # プレイヤー
    player = Player()
    # 地面
    blocks = [
        # Block(0, 500, 2500, 100),
        Block(400, 400, 200, 30),
        Block(700, 300, 200, 30),
        Block(1200, 350, 200, 30),
        # 仕掛け床用
        Block(0, 500, 1000, 100),
        Block(1200, 500, 2500, 100),
        Block(1000, 500, 1200, 100),
    ]
    # 敵

    enemies = []
    for i in range(5):
        x = random.randint(300, 2200)
        y = random.choice([260, 460])
        enemies.append(Enemy(x, y))


    # ゴール旗
    goal = Goal(2200, 380)
    # スクロール量
    scroll_x = 0
    return player, blocks, enemies, goal, scroll_x

def main():
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("こうかとんのアクション")
    life = Life(3)
    clock = pg.time.Clock()

    # 初期化
    player, blocks, enemies, goal, scroll_x = reset_game()
    score = 0

    # ゲーム状態
    game_start = False
    game_over = False
    game_clear = False
    game_miss = False

    score = Score(game_start, game_over, game_clear)

    while True:
        keys = pg.key.get_pressed()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    # タイトル画面
                    if not game_start:
                        game_start = True
                    # ミス後の再開
                    elif game_miss:
                        player, blocks, enemies, goal, scroll_x = reset_game()
                        game_miss = False
                        game_start = True
                    # リスタート
                    elif game_over or game_clear:
                        player, blocks, enemies, goal, scroll_x = reset_game()
                        life.num = 3
                        game_over = False
                        game_clear = False
                        game_start = False
                        score.value = 0  # スコアをリセット

        # 背景
        screen.fill(WHITE)

        # タイトル画面
        if not game_start:
            draw_text(screen, "こうかとんのアクション", 60, WIDTH // 2, 180)
            life.draw(screen, 260)
            draw_text(screen, "PRESS ENTER TO START", 45,WIDTH // 2, 350)
        # ゲーム中
        elif not game_over and not game_clear and not game_miss:
            # プレイヤー更新
            player.update(keys, blocks)
            # 横スクロール
            scroll_x = player.rect.x - 200
            if scroll_x < 0:
                scroll_x = 0
            # 奈落判定
            if player.rect.y > HEIGHT:
                life.num -= 1

                if life.num <= 0:
                    game_over = True
                else:
                    game_miss = True
            # 敵判定
            for enemy in enemies[:]:
                if player.rect.colliderect(enemy.rect):
                    # 上から踏んだ
                    if (player.vy > 0 and player.rect.bottom < enemy.rect.centery):
                        enemies.remove(enemy)
                        # score += 100
                        score.value += 10  # スコアに10点追加

                        # 跳ねる
                        player.vy = -10
                    else:
                        life.num -= 1
                        if life.num <= 0:
                            game_over = True
                        else:
                            game_miss = True

            # ゴール判定
            if player.rect.colliderect(goal.rect):
                game_clear = True
            # 地面描画
            for block in blocks:
                block.draw(screen, scroll_x)

            # 仕掛け床判定
            cou = 0
            for block in blocks[:]:
                if cou == 5:  # blocksリストの何個目が仕掛け床になるか
                    if player.on_ground and player.rect.bottom == block.rect.top and player.rect.right > block.rect.left and player.rect.left < block.rect.right:
                       block.rect.y += 100
                       player.rect.y += 100
                cou += 1

            # 敵描画
            for enemy in enemies:
                enemy.draw(screen, scroll_x)
            # ゴール描画
            goal.draw(screen, scroll_x)
            # プレイヤー描画
            player.draw(screen, scroll_x)

            # #敵討伐スコア
            # draw_text(screen,f"SCORE : {score}",40,100,20)

        # ゲームオーバー
        elif game_over:
            draw_text(screen, "GAME OVER", 80, WIDTH // 2, 220, RED)
            draw_text(screen, "PRESS ENTER", 50, WIDTH // 2, 320)
        # ミス画面
        elif game_miss:
            draw_text(screen, "MISS", 80, WIDTH // 2, 180, RED)
            life.draw(screen, 260)
            draw_text(screen, "PRESS ENTER", 50, WIDTH // 2, 350)
        # ゲームクリア
        elif game_clear:
            draw_text(screen, "GAME CLEAR!", 80, WIDTH // 2, 220, BLUE)
            draw_text(screen, "PRESS ENTER", 50, WIDTH // 2, 320)

        score.update(screen, game_start, game_over, game_clear)
        pg.display.update()
        clock.tick(60)


if __name__ == "__main__":
    main()