import pygame as pg
import sys
import os
import time

# 画面サイズ
WIDTH = 800
HEIGHT = 600

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

os.chdir(os.path.dirname(os.path.abspath(__file__)))
class Player:
    def __init__(self):

        self.image = pg.Surface((40, 50))
        self.image.fill(BLUE)

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

        screen.blit(
            self.image,
            (self.rect.x - scroll_x, self.rect.y)
        )


class Block:
    def __init__(self, x, y, w, h):

        self.rect = pg.Rect(x, y, w, h)

    def draw(self, screen, scroll_x):

        pg.draw.rect(
            screen,
            GREEN,
            (
                self.rect.x - scroll_x,
                self.rect.y,
                self.rect.width,
                self.rect.height
            )
        )


class Enemy:
    def __init__(self, x, y):

        self.rect = pg.Rect(x, y, 40, 40)

    def draw(self, screen, scroll_x):

        pg.draw.rect(
            screen,
            RED,
            (
                self.rect.x - scroll_x,
                self.rect.y,
                self.rect.width,
                self.rect.height
            )
        )


class Goal:
    def __init__(self, x, y):

        self.rect = pg.Rect(x, y, 40, 120)

    def draw(self, screen, scroll_x):

        # 棒
        pg.draw.rect(
            screen,
            BLACK,
            (
                self.rect.x - scroll_x,
                self.rect.y,
                5,
                self.rect.height
            )
        )

        # 旗
        pg.draw.polygon(
            screen,
            YELLOW,
            [
                (self.rect.x - scroll_x + 5, self.rect.y),
                (self.rect.x - scroll_x + 60, self.rect.y + 20),
                (self.rect.x - scroll_x + 5, self.rect.y + 40)
            ]
        )

class Item:
    """
    アイテムの位置を設定しているクラス
    引数 x(x座標), y(y座標)でアイテムの位置を指定する
    
    """
    def __init__(self, x, y):
        self.image = pg.Surface((20, 20))
        pg.draw.circle(self.image, (0, 255, 230), (10, 10), 10)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
            
    def draw(self, screen, scroll_x):
        screen.blit(self.image,(self.rect.x-scroll_x,self.rect.y))

def draw_text(screen, text, size, x, y, color=BLACK):

    font = pg.font.Font(None, size)

    img = font.render(text, True, color)

    screen.blit(img, (x, y))

def draw_text_J(screen, text, size, x, y, color=BLACK):

    
    font = pg.font.SysFont("Meiryo", size)

    img = font.render(text, True, color)

    screen.blit(img, (x, y))


def reset_game():

    # プレイヤー
    player = Player()

    # 地面
    blocks = [
        Block(0, 500, 2500, 100),
        Block(400, 400, 200, 30),
        Block(700, 300, 200, 30),
        Block(1200, 350, 200, 30),
    ]

    # 敵
    enemies = [
        Enemy(850, 260),
        Enemy(1200, 460),
    ]

    # アイテム
    items = [Item(400, 380),]

    # ゴール旗
    goal = Goal(2200, 380)

    # スクロール量
    scroll_x = 0

    return player, blocks, enemies, items, goal, scroll_x


def main():

    pg.init()

    screen = pg.display.set_mode((WIDTH, HEIGHT))

    pg.display.set_caption("Mario Style Game")

    clock = pg.time.Clock()

    # 初期化
    player, blocks, enemies, items, goal, scroll_x = reset_game()

    # ゲーム状態
    game_start = False
    game_over = False
    game_clear = False

    

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

                    # リスタート
                    elif game_over or game_clear:

                        player, blocks, enemies, items, goal, scroll_x = reset_game()

                        game_over = False
                        game_clear = False
                        game_start = False

                        state = "inactive"  # 初期状態はinactive
        # 背景
        screen.fill(WHITE)

        # タイトル画面
        if not game_start:

            draw_text(
                screen,
                "PRESS ENTER TO START",
                60,
                170,
                250
            )

        # ゲーム中
        elif not game_over and not game_clear:

            # プレイヤー更新
            player.update(keys, blocks)

            # 横スクロール
            scroll_x = player.rect.x - 200

            if scroll_x < 0:
                scroll_x = 0

            # 奈落判定
            if player.rect.y > HEIGHT:
                game_over = True

            # 敵判定
            for enemy in enemies[:]:

                if player.rect.colliderect(enemy.rect):

                    # 上から踏んだ
                    if (
                        player.vy > 0 and
                        player.rect.bottom < enemy.rect.centery
                    ):

                        enemies.remove(enemy)

                        # 跳ねる
                        player.vy = -10

                    else:
                        if state != "active":
                            game_over = True

            now = int(time.time())  # 現在の時間を取得
            
            
                
            
            # アイテム判定
            # アイテムを拾った時、無敵状態となるようにする
            for item in items[:]:
                # for文の外で使えるように変数をここで定義
                end = 0   # アイテムの効果終了時間を保管 
                s_time = 0  # アイテムの効果開始時間を保管
                state = ""   # アイテムが効果中か否かの状態を示す

                if player.rect.colliderect(item.rect):  # プレイヤーとアイテムの衝突判定
                    items.remove(item)
                    s_time = int(time.time())  # 現在の時間を一度保存
                    end = s_time + 5  # 五秒後にアイテムの効果が切れるように調整
                    state = "active"  # アイテムをとった時active状態にする    
                
            l_time = end - now 
            
            if state == "active":
                draw_text_J(screen, f"効果時間:{l_time}sec", 40, 0, 0, (0,255,255)) 
            
            if now >= end:  # アイテムの効果時間が切れたらinactiveに戻す
                draw_text_J(screen, "効果時間:0sec", 40, 0, 0, BLACK)
                state = "inactive"

            
            
            for item in items:
                item.draw(screen, scroll_x)

            # ゴール判定
            if player.rect.colliderect(goal.rect):
                game_clear = True

            # 地面描画
            for block in blocks:
                block.draw(screen, scroll_x)

            # 敵描画
            for enemy in enemies:
                enemy.draw(screen, scroll_x)

            # ゴール描画
            goal.draw(screen, scroll_x)

            # プレイヤー描画
            player.draw(screen, scroll_x)

        # ゲームオーバー
        elif game_over:
            if state != "active":
                draw_text(
                    screen,
                    "GAME OVER",
                    80,
                    230,
                    220,
                    RED
                )

            draw_text(
                screen,
                "PRESS ENTER",
                50,
                250,
                320
            )

        # ゲームクリア
        elif game_clear:

            draw_text(
                screen,
                "GAME CLEAR!",
                80,
                210,
                220,
                BLUE
            )

            draw_text(
                screen,
                "PRESS ENTER",
                50,
                250,
                320
            )

        pg.display.update()

        clock.tick(60)


if __name__ == "__main__":
    main()