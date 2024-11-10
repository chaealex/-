import os
import pygame as pg
import math
import time


# 초기 설정
pg.init()
screen_width = 1280  # 화면의 너비
screen_height = 720   # 화면의 높이
screen = pg.display.set_mode((screen_width, screen_height))  # 화면 크기 설정
pg.display.set_caption("Ethan's Purification")  # 창 제목 설정
clock = pg.time.Clock()  # FPS를 조절하기 위한 클락 객체 생성

# 이미지 경로 설정
current_path = os.path.dirname(__file__)  # 현재 파일 경로
image_path = os.path.join(current_path, "images")  # 이미지 파일들이 위치할 경로


# 배경 이미지 로드
backgrounds = [pg.image.load(os.path.join(image_path, f"바닥{i}.png")) for i in range(1, 3)]
current_stage = 0

class Portal:
    def __init__(self, x, y, width, height):
        self.rect = pg.Rect(x, y, width, height)
        self.color = (255, 0, 255)  # 포탈 색상
        self.active = False
        self.last_active_time = 0
        self.active_delay = 2000

    def draw_portal(self, screen):
        current_time = pg.time.get_ticks()
        # 일정 시간이 지나면 포탈 표시
        if current_time - self.last_active_time >= self.active_delay:
            self.active = True
            self.last_active_time = current_time  # 시간 갱신
        if self.active:
            pg.draw.rect(screen, self.color, self.rect)  # 포탈 그리기

portal = Portal(600, 400, 50, 50)  # 포탈 위치 및 크기 설정

# 스테이지 전환 시 함수
def load_next_stage():
    global current_stage
    current_stage += 1
    if current_stage >= len(backgrounds):
        current_stage = 0  # 첫 스테이지로 돌아감
        print("모든 스테이지를 클리어하고 처음으로 돌아갑니다.")
    else:
        print(f"스테이지 {current_stage + 1}로 이동했습니다.")

class Character:
    def __init__(self, image_path, x, y, speed, lives=3):
        # 캐릭터의 기본 속성 초기화
        self.image = pg.image.load(image_path)  # 캐릭터 이미지 로드
        self.rect = self.image.get_rect(center=(x, y))  # 캐릭터의 사각형 영역 생성
        self.speed = speed  # 캐릭터의 이동 속도
        self.lives = lives  # 캐릭터의 생명
        self.red_image = self.image.copy()  # 캐릭터의 붉은 이미지 복사
        self.red_image.fill((255, 0, 0), special_flags=pg.BLEND_MULT)  # 붉은 이미지 생성
        self.hit_timer = 0  # 맞았을 때의 타이머

    def move(self, dx, dy, dt):
        # 캐릭터 이동 메서드
        if self.hit_timer > 0:  # 맞은 상태라면
            self.hit_timer -= dt  # 타이머 감소
        self.rect.x += dx * self.speed * dt  # x축 이동
        self.rect.y += dy * self.speed * dt  # y축 이동
        self.rect.clamp_ip(screen.get_rect())  # 화면 경계에서 벗어나지 않도록 조정

    def draw(self):
        # 캐릭터 그리기 메서드
        if self.hit_timer > 0:  # 맞은 상태라면
            screen.blit(self.red_image, self.rect)  # 붉은 이미지로 그리기
        else:
            screen.blit(self.image, self.rect)  # 일반 이미지로 그리기

    def hit(self):
        # 캐릭터가 맞았을 때의 처리
        if self.hit_timer <= 0:  # 무적 시간이 아닐 때만
            self.hit_timer = 1000  # 1초간 무적 상태 설정
            self.lives -= 1  # 생명 감소

class Ethan(Character):
    def __init__(self, x, y):
        super().__init__(os.path.join(image_path, "에단.png"), x, y, 0.3)  # Ethan 초기화
        self.lives = 3  # 생명 수
        self.life_image = pg.image.load(os.path.join(image_path, '목숨.png'))  # 생명 이미지 로드
        self.life_width = self.life_image.get_width()  # 생명 이미지의 너비
        self.fires = []  # 발사한 불꽃 리스트
        self.fire_image = pg.image.load(os.path.join(image_path, '빛.png'))  # 불꽃 이미지 로드
        self.last_shoot_time = 0  # 마지막 발사 시간 저장
        self.shoot_delay = 200  # 200ms(0.2초) 간격으로 발사 가능

    def shoot(self, direction, angle):
        # 불꽃 발사 메서드 (0.2초 딜레이 체크 추가)
        current_time = pg.time.get_ticks()
        if current_time - self.last_shoot_time >= self.shoot_delay:
            self.fires.append({"pos": [(self.rect.centerx) + 30, self.rect.centery], "dir": direction, "angle": angle})
            self.last_shoot_time = current_time  # 마지막 발사 시간 업데이트

    def update_fires(self, dt):
        # 발사한 불꽃 업데이트
        for fire in self.fires[:]:
            fire["pos"][0] += fire["dir"][0] * 0.3 * dt  # x축 이동
            fire["pos"][1] += fire["dir"][1] * 0.3 * dt  # y축 이동
            if not screen.get_rect().collidepoint(fire["pos"]):  # 화면을 벗어나면 삭제
                self.fires.remove(fire)

    def draw_fires(self):
        # 발사한 불꽃 그리기
        for fire in self.fires:
            rotated_fire = pg.transform.rotate(self.fire_image, fire["angle"])  # 불꽃 회전
            fire_rect = rotated_fire.get_rect(center=fire["pos"])  # 불꽃의 사각형 영역 생성
            screen.blit(rotated_fire, fire_rect)  # 불꽃 그리기

    def draw_lives(self, screen):
        # 오른쪽 상단에 Ethan의 목숨을 그림
        for i in range(self.lives):
            x = screen.get_width() - (i + 1) * (self.life_width + 10)  # 목숨 이미지 간격 설정
            y = 10  # 화면 상단에서 약간 띄운 위치
            screen.blit(self.life_image, (x, y))  # 목숨 이미지 그리기

class enemy(Character):
    def __init__(self, image_path, x, y):
        super().__init__([pg.image.load(os.path.join(image_path, f"잡몹{i}.png")) for i in range(1, 3)])
        self.hp = 5
        self.red_duration = 1000
        self.red_timer = 0
        self.self.knockback_distance = 10  # 넉백 거리
    def update(self, dt):
        # 붉은 상태 업데이트
        if self.red_timer > 0:
            self.red_timer -= dt  # 타이머 감소

    def knockback(self, dx, dy):
        # 넉백 처리
        self.rect.x += dx  # x축으로 넉백
        self.rect.y += dy  # y축으로 넉백

    def update_position(self, target, dt):
        # Ethan을 추적하여 위치 업데이트
        dx, dy = target.rect.x - self.rect.x, target.rect.y - self.rect.y  # 목표와의 거리 계산
        distance = math.hypot(dx, dy)  # 거리 계산
        if distance != 0:
            self.rect.x += (dx / distance) * self.speed * dt  # 목표 방향으로 이동
            self.rect.y += (dy / distance) * self.speed * dt  # 목표 방향으로 이동
        self.rect.clamp_ip(screen.get_rect())  # 화면 경계에서 벗어나지 않도록 조정

    def draw(self):
        # Chaingoast 그리기 메서드
        if self.red_timer > 0:  # 붉은 상태라면
            screen.blit(self.red_image, self.rect)  # 붉은 유령 이미지 그리기
        else:
            screen.blit(self.image, self.rect)  # 일반 유령 이미지 그리기
            
    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            return True
        return False

class Chaingoast(Character):
    def __init__(self, x, y):
        super().__init__(os.path.join(image_path, '체인유령.png'), x, y, 0.1, 50)  # Chaingoast 초기화
        self.hp = 50  # 체력
        self.red_duration = 1000  # 붉은 상태 지속 시간(ms)
        self.red_timer = 0  # 붉은 상태 타이머
        self.knockback_distance = 10  # 넉백 거리
        self.chains = []  # 체인 리스트
        self.chain_image = pg.image.load(os.path.join(image_path, '체인.png'))  # 체인 이미지 로드
        self.attack_interval = 4  # 공격 간격(초)
        self.last_attack_time = time.time()  # 마지막 공격 시간

    def update(self, dt):
        # 붉은 상태 업데이트
        if self.red_timer > 0:
            self.red_timer -= dt  # 타이머 감소
    
    def knockback(self, dx, dy):
        # 넉백 처리
        self.rect.x += dx  # x축으로 넉백
        self.rect.y += dy  # y축으로 넉백

    def update_position(self, target, dt):
        # Ethan을 추적하여 위치 업데이트
        dx, dy = target.rect.x - self.rect.x, target.rect.y - self.rect.y  # 목표와의 거리 계산
        distance = math.hypot(dx, dy)  # 거리 계산
        if distance != 0:
            self.rect.x += (dx / distance) * self.speed * dt  # 목표 방향으로 이동
            self.rect.y += (dy / distance) * self.speed * dt  # 목표 방향으로 이동
        self.rect.clamp_ip(screen.get_rect())  # 화면 경계에서 벗어나지 않도록 조정

    def attack(self):
        # 체인 공격 메서드
        if time.time() - self.last_attack_time >= self.attack_interval:  # 공격 가능 시간 체크
            self.last_attack_time = time.time()  # 현재 시간을 마지막 공격 시간으로 설정
            for i in range(6):  # 6개의 체인 발사
                angle = 60 * i  # 각도 설정
                radians = math.radians(angle)  # 라디안 변환
                dir_x = math.cos(radians)  # x 방향
                dir_y = math.sin(radians)  # y 방향
                rotated_chain = pg.transform.rotate(self.chain_image, -angle)  # 체인 회전
                self.chains.append({
                    "pos": [self.rect.centerx, self.rect.centery],  # 체인 시작 위치
                    "dir": [dir_x, dir_y],  # 체인 방향
                    "image": rotated_chain  # 체인 이미지
                })

    def update_chains(self, dt):
        # 체인 업데이트
        for chain in self.chains:
            chain["pos"][0] += chain["dir"][0] * 0.3 * dt  # x축 이동
            chain["pos"][1] += chain["dir"][1] * 0.3 * dt  # y축 이동

    def draw_chains(self):
        # 체인 그리기
        for chain in self.chains:
            screen.blit(chain["image"], chain["pos"])  # 체인 이미지 그리기

    def draw(self):
        # Chaingoast 그리기 메서드
        if self.red_timer > 0:  # 붉은 상태라면
            screen.blit(self.red_image, self.rect)  # 붉은 유령 이미지 그리기
        else:
            screen.blit(self.image, self.rect)  # 일반 유령 이미지 그리기
            
    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            return True
        return False

# 게임 루프 및 충돌 처리
def main():
    global current_stage

    ethan = Ethan(screen_width / 2, screen_height / 2)  # Ethan 객체 생성
    chaingoast = Chaingoast(screen_width / 2, screen_height / 2 - 200)  # Chaingoast 객체 생성
    running = True  # 게임 루프 플래그

    while running:
        map_move = 0
        dt = clock.tick(60)  # 초당 프레임 설정
        screen.blit(backgrounds[current_stage], (0, 0))  # 배경 그리기

        # 이벤트 처리
        for event in pg.event.get():
            if event.type == pg.QUIT:  # 종료 이벤트 처리
                running = False
            elif event.type == pg.KEYDOWN:  # 키 눌림 이벤트 처리
                if event.key == pg.K_w:  # W 키를 누르면 위쪽으로 발사
                    ethan.shoot((0, -1), 90)
                elif event.key == pg.K_s:  # S 키를 누르면 아래쪽으로 발사
                    ethan.shoot((0, 1), 270)
                elif event.key == pg.K_a:  # A 키를 누르면 왼쪽으로 발사
                    ethan.shoot((-1, 0), 180)
                elif event.key == pg.K_d:  # D 키를 누르면 오른쪽으로 발사
                    ethan.shoot((1, 0), 0)
                elif event.key == pg.K_y: # Y 키를 누르면 이동
                    map_move = 1

        keys = pg.key.get_pressed()  # 현재 눌린 키 확인
        ethan.move((keys[pg.K_RIGHT] - keys[pg.K_LEFT]), (keys[pg.K_DOWN] - keys[pg.K_UP]), dt)  # 캐릭터 이동

        # 불꽃 이동 및 충돌 처리
        ethan.update_fires(dt)  # 불꽃 업데이트
        ethan.draw_fires()  # 불꽃 그리기

        if chaingoast.hp > 0:
            chaingoast.draw()  # Chaingoast 그리기
            
            # Chaingoast 체력 게이지
            hp_bar_width = 300 * (chaingoast.hp / 50)  # 체력 비율에 따른 게이지 너비 계산
            pg.draw.rect(screen, (100, 100, 100), ((screen_width - 300) / 2, 30, 300, 20))  # 배경 게이지
            pg.draw.rect(screen, (255, 0, 0), ((screen_width - 300) / 2, 30, hp_bar_width, 20))  # 체력 게이지
            
            # Chaingoast 행동 및 공격
            chaingoast.update(dt)  # Chaingoast 업데이트
            chaingoast.update_position(ethan, dt)  # Chaingoast가 Ethan을 추적
            chaingoast.attack()  # Chaingoast 공격
            chaingoast.update_chains(dt)  # 체인 업데이트
            chaingoast.draw_chains()  # 체인 그리기

            # 충돌 처리
            if ethan.rect.colliderect(chaingoast.rect):  # Ethan과 Chaingoast 충돌 처리
                ethan.hit()  # Ethan의 hit 메서드 호출
            for fire in ethan.fires[:]:  # Ethan의 불꽃에 대해 충돌 처리
                if chaingoast.rect.collidepoint(fire["pos"]):  # Chaingoast에 불꽃이 맞으면
                    chaingoast.hit()  # Chaingoast의 체력 감소
                    ethan.fires.remove(fire)  # 불꽃 삭제

                    # 넉백 효과 추가
                    knockback_x = (chaingoast.rect.centerx - ethan.rect.centerx) / math.hypot(chaingoast.rect.centerx - ethan.rect.centerx, chaingoast.rect.centery - ethan.rect.centery) * chaingoast.knockback_distance
                    knockback_y = (chaingoast.rect.centery - ethan.rect.centery) / math.hypot(chaingoast.rect.centerx - ethan.rect.centerx, chaingoast.rect.centery - ethan.rect.centery) * chaingoast.knockback_distance
                    chaingoast.knockback(knockback_x, knockback_y)  # Chaingoast의 넉백 처리

                    chaingoast.red_timer = chaingoast.red_duration  # Chaingoast를 붉은 상태로 설정



            # 체인에 의한 충돌 처리
            for chain in chaingoast.chains:
                if ethan.rect.collidepoint(chain["pos"]) and ethan.hit_timer <= 0:  # Ethan이 체인에 맞으면
                    ethan.hit()  # Ethan의 hit 메서드 호출

        #포탈
        # 캐릭터와 포탈 충돌 검사
        else :
            portal.active = True
            portal.draw_portal(screen)
        #포탈 그리기
        if portal.active and ethan.rect.colliderect(portal.rect):
            if map_move == 1:
                load_next_stage()
                portal.active = False
                map_move = 0
        
        # 캐릭터 그리기
        ethan.draw()  # Ethan 그리기
        
        # Ethan 체력 게이지
        ethan.draw_lives(screen)  # Ethan의 목숨 그리기
        
        pg.display.update()  # 화면 업데이트
    pg.quit()  # Pygame 종료



main()  # 게임 실행
