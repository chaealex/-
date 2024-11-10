import os
import pygame as pg
import math
import time

# 초기 설정
pg.init()
screen_width = 1280
screen_height = 720
screen = pg.display.set_mode((screen_width, screen_height))
pg.display.set_caption("Ethan's Purification")
clock = pg.time.Clock()

# 이미지 경로 설정
current_path = os.path.dirname(__file__)
image_path = os.path.join(current_path, "images")

# 배경 이미지 로드
backgrounds = [pg.image.load(os.path.join(image_path, f"바닥{i}.png")) for i in range(1, 3)]
current_stage = 0

class Portal:
    def __init__(self, x, y, width, height):
        self.rect = pg.Rect(x, y, width, height)
        self.color = (255, 0, 255)
        self.active = False

    def draw_portal(self, screen):
        if self.active:
            pg.draw.rect(screen, self.color, self.rect)

class Character:
    def __init__(self, image_path, x, y, speed, lives=3):
        self.image = pg.image.load(image_path)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.lives = lives
        self.hit_timer = 0

    def move(self, dx, dy, dt):
        if self.hit_timer > 0:
            self.hit_timer -= dt
        self.rect.x += dx * self.speed * dt
        self.rect.y += dy * self.speed * dt
        self.rect.clamp_ip(screen.get_rect())

    def draw(self):
        screen.blit(self.image, self.rect)

    def hit(self):
        if self.hit_timer <= 0:
            self.hit_timer = 1000
            self.lives -= 1

class Ethan(Character):
    def __init__(self, x, y):
        super().__init__(os.path.join(image_path, "에단.png"), x, y, 0.3)
        self.lives = 3
        self.life_image = pg.image.load(os.path.join(image_path, '목숨.png'))
        self.life_width = self.life_image.get_width()
        self.fires = []
        self.fire_image = pg.image.load(os.path.join(image_path, '빛.png'))
        self.last_shoot_time = 0
        self.shoot_delay = 200

    def shoot(self, direction, angle):
        current_time = pg.time.get_ticks()
        if current_time - self.last_shoot_time >= self.shoot_delay:
            self.fires.append({"pos": [(self.rect.centerx) + 30, self.rect.centery], "dir": direction, "angle": angle})
            self.last_shoot_time = current_time

    def update_fires(self, dt):
        for fire in self.fires[:]:
            fire["pos"][0] += fire["dir"][0] * 0.3 * dt
            fire["pos"][1] += fire["dir"][1] * 0.3 * dt
            if not screen.get_rect().collidepoint(fire["pos"]):
                self.fires.remove(fire)

    def draw_fires(self):
        for fire in self.fires:
            rotated_fire = pg.transform.rotate(self.fire_image, fire["angle"])
            fire_rect = rotated_fire.get_rect(center=fire["pos"])
            screen.blit(rotated_fire, fire_rect)

    def draw_lives(self, screen):
        for i in range(self.lives):
            x = screen.get_width() - (i + 1) * (self.life_width + 10)
            y = 10
            screen.blit(self.life_image, (x, y))

class Chaingoast(Character):
    def __init__(self, x, y):
        super().__init__(os.path.join(image_path, '체인유령.png'), x, y, 0.1)
        self.hp = 50
        self.chains = []
        self.chain_image = pg.image.load(os.path.join(image_path, '체인.png'))
        self.attack_interval = 4
        self.last_attack_time = time.time()

    def attack(self):
        if time.time() - self.last_attack_time >= self.attack_interval:
            self.last_attack_time = time.time()
            for i in range(6):
                angle = 60 * i
                radians = math.radians(angle)
                dir_x = math.cos(radians)
                dir_y = math.sin(radians)
                rotated_chain = pg.transform.rotate(self.chain_image, -angle)
                self.chains.append({
                    "pos": [self.rect.centerx, self.rect.centery],
                    "dir": [dir_x, dir_y],
                    "image": rotated_chain
                })

    def update_chains(self, dt):
        for chain in self.chains:
            chain["pos"][0] += chain["dir"][0] * 0.3 * dt
            chain["pos"][1] += chain["dir"][1] * 0.3 * dt

    def draw_chains(self):
        for chain in self.chains:
            screen.blit(chain["image"], chain["pos"])

    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            return True
        return False

# 게임 루프 및 충돌 처리
def main():
    global current_stage

    ethan = Ethan(screen_width / 2, screen_height / 2)
    chaingoasts = [
        Chaingoast(screen_width / 4, screen_height / 4),
        Chaingoast(screen_width / 2, screen_height / 3),
        Chaingoast(screen_width * 3 / 4, screen_height / 4),
        Chaingoast(screen_width / 2, screen_height * 3 / 4)
    ]
    portal = Portal(600, 400, 50, 50)
    running = True
    start_time = time.time()
    while running:
        dt = clock.tick(60)
        screen.blit(backgrounds[current_stage], (0, 0))

        # 이벤트 처리
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_w:
                    ethan.shoot((0, -1), 90)
                elif event.key == pg.K_s:
                    ethan.shoot((0, 1), 270)
                elif event.key == pg.K_a:
                    ethan.shoot((-1, 0), 180)
                elif event.key == pg.K_d:
                    ethan.shoot((1, 0), 0)

        keys = pg.key.get_pressed()
        ethan.move((keys[pg.K_RIGHT] - keys[pg.K_LEFT]), (keys[pg.K_DOWN] - keys[pg.K_UP]), dt)

        # 불꽃 이동 및 그리기
        ethan.update_fires(dt)
        ethan.draw_fires()

        # Chaingoasts 처리
        for chaingoast in chaingoasts[:]:
            if chaingoast.hp > 0:
                chaingoast.attack()
                chaingoast.update_chains(dt)
                chaingoast.draw_chains()
                if ethan.rect.colliderect(chaingoast.rect):
                    ethan.hit()
                for fire in ethan.fires[:]:
                    if chaingoast.rect.collidepoint(fire["pos"]):
                        chaingoast.hit()
                        ethan.fires.remove(fire)

        # 포탈 활성화
        elapsed_time = time.time() - start_time
        if all(c.hp <= 0 for c in chaingoasts) or elapsed_time >= 240:
            portal.active = True
            portal.draw_portal(screen)

        if portal.active and ethan.rect.colliderect(portal.rect):
            load_next_stage()
            portal.active = False

        ethan.draw()
        ethan.draw_lives(screen)

        pg.display.update()

    pg.quit()

def load_next_stage():
    global current_stage
    current_stage += 1
    if current_stage >= len(backgrounds):
        current_stage = 0
        print("모든 스테이지를 클리어하고 처음으로 돌아갑니다.")
    else:
        print(f"스테이지 {current_stage + 1}로 이동했습니다.")

main()
