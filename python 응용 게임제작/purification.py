import os
import pygame as pg
import math
import time
################

pg.init()

#화면 크기 설정
screen_width = 1280 #가로 1280
screen_height = 720 #세로 720
screen = pg.display.set_mode((screen_width, screen_height))

#화면 타이틀 설정
pg.display.set_caption("edan's purification")

#FPS
clock = pg.time.Clock()
#################

current_path = os.path.dirname(__file__)
image_path = os.path.join(current_path, "images")

#배경 이미지
background = pg.image.load(os.path.join(image_path, "바닥.png"))

'''
#스테이지
stage_left = pg.image.load(os.path.join(image_path, "벽.jpg"))
stage_right = pg.image.load(os.path.join(image_path, "벽.jpg"))
stage_top = pg.image.load(os.path.join(image_path, "벽.jpg"))
stage_botton = pg.image.load(os.path.join(image_path, "벽.jpg"))

stage_left_size = stage_left.get_rect().size
stage_botton_size = stage_botton.get_rect().size
stage_right_size = stage_right.get_rect().size
stage_top_size = stage_top.get_rect().size

stage_height = stage_botton_size[1]
'''

#에단
edan = pg.image.load(os.path.join(image_path, "에단.png"))
edan_size = edan.get_rect().size
edan_width = edan_size[0]
edan_height = edan_size[1]
edan_x_pos = screen_width / 2 - edan_width / 2
edan_y_pos = screen_height / 2 - edan_height / 2

#에단 히트박스
hitbox_color = (0, 255, 0)

#데미지 입은 에단
edan_red = edan.copy()
edan_red.fill((255, 0, 0), special_flags=pg.BLEND_MULT)
edan_red_duration = 200  # 에단이 충돌 후 붉게 변할 시간(ms)
edan_red_timer = 0  # 붉게 변한 상태를 추적할 타이머

#에단 이동 방향
edan_to_x = 0
edan_to_y = 0

#에단 이동 속도
edan_speed = 0.3

#에단 목숨
life = pg.image.load(os.path.join(image_path, '목숨.png'))
edan_lives = 3
imotal_time = 0

#에단 불꽃 공격
fire_image = pg.image.load(os.path.join(image_path, '불꽃.png'))
explosion_image = pg.image.load(os.path.join(image_path, '폭발.png'))
fire_speed = 3
fires = []
explosions = []


#체인유령
chaingoast = pg.image.load(os.path.join(image_path, '체인유령.png'))
max_chaingoast_hp = 50
chaingoast_hp = 50
hp_bar_width = 300
hp_bar_height = 20
hp_bar_color = (255, 0, 0)
chaingoast_size = chaingoast.get_rect().size
chaingoast_width = chaingoast_size[0]
chaingoast_height = chaingoast_size[1]
chaingoast_x_pos = (screen_width / 2) - (chaingoast_width / 2)
chaingoast_y_pos = (screen_height / 2) - (chaingoast_height / 2) - 200

#데미지입은 유령
chaingoast_red = chaingoast.copy()
chaingoast_red.fill((255, 0, 0), special_flags=pg.BLEND_MULT)
chaingoast_red_duration = 200  # 에단이 충돌 후 붉게 변할 시간(ms)
chaingoast_red_timer = 0  # 붉게 변한 상태를 추적할 타이머

#체인유령 이동 속도
chaingoast_speed = 0.1

#체인 공격
chain_image = pg.image.load(os.path.join(image_path,'체인.png'))
attack_interval = 4
last_attack_time = time.time()
projectiles = []
projectile_speed = 7

#적 이동 제한
chaingoast_stop_time = 0
move_restric_time = 0

#폰트 정의
game_font = pg.font.Font(None, 160)#폰트 객체 생성(폰트, 크기)

game_result = 'GAME OVER'

#시작 시간
start_ticks = pg.time.get_ticks()

#이벤트 루프
running = True
while running:
    dt = clock.tick(60)    #초당 프레임 수 설정
    
    #무적 & 움직임 제한
    if imotal_time > 0:
        imotal_time -= dt
    if move_restric_time > 0:
        move_restric_time -= dt
    if chaingoast_stop_time > 0:
        chaingoast_stop_time -= dt
    if edan_red_timer > 0:
        edan_red_timer -= dt
    if chaingoast_red_timer > 0:
        chaingoast_red_timer -= dt
    #이벤트 처리
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        
        if event.type == pg.KEYDOWN:#키 입력 확인
            if event.key == pg.K_LEFT:
                edan_to_x -= edan_speed
            elif event.key == pg.K_RIGHT:
                edan_to_x += edan_speed
            elif event.key == pg.K_UP:
                edan_to_y -= edan_speed
            elif event.key == pg.K_DOWN:
                edan_to_y += edan_speed
            elif event.key == pg.K_w:
                fires.append({"pos": [edan_x_pos, edan_y_pos], "dir": (0, -1), 'angle': 90})
            elif event.key == pg.K_s:  # 아래쪽 발사
                fires.append({"pos": [edan_x_pos, edan_y_pos], "dir": (0, 1), 'angle': 270})
            elif event.key == pg.K_a:  # 왼쪽 발사
                fires.append({"pos": [edan_x_pos, edan_y_pos], "dir": (-1, 0), 'angle': 180})
            elif event.key == pg.K_d:  # 오른쪽 발사
                fires.append({"pos": [edan_x_pos, edan_y_pos], "dir": (1, 0), 'angle': 0})
            
        if event.type == pg.KEYUP:#방향키 때면 멈춤
            if event.key == pg.K_LEFT or event.key == pg.K_RIGHT:
                edan_to_x = 0
            elif event.key == pg.K_UP or event.key == pg.K_DOWN:
                edan_to_y = 0
    
    for fire in fires[:]:
        fire["pos"][0] += fire["dir"][0] * fire_speed
        fire["pos"][1] += fire["dir"][1] * fire_speed
        
        # 화면 밖으로 나가면 삭제
        if fire["pos"][0] < 0 or fire["pos"][0] > screen_width or fire["pos"][1] < 0 or fire["pos"][1] > screen_height:
            fires.remove(fire)
    
    #게임 캐릭터 위치 정의
    #에단
    edan_x_pos += edan_to_x * dt
    edan_y_pos += edan_to_y * dt
    
    
    #적이 에단 따라가는 로직
    if  chaingoast_stop_time <= 0:
        dx = edan_x_pos - chaingoast_x_pos
        dy = edan_y_pos - chaingoast_y_pos
        distance = math.hypot(dx, dy)
        if distance != 0:
            dx, dy = dx / distance, dy / distance
            chaingoast_x_pos += dx * chaingoast_speed * dt
            chaingoast_y_pos += dy * chaingoast_speed * dt
    
    #10초마다 6방향으로 체인 발사체 생성
    if time.time() - last_attack_time >= attack_interval:
        last_attack_time = time.time()
        move_restric_time = 2000
        chaingoast_restriction_time = 2000
        for i in range(6):
            angle = 60 * i  # 6방향 각도 설정 (0°, 45°, 90°, ..., 315°)
            radians = math.radians(angle)
            dir_x = math.cos(radians)
            dir_y = math.sin(radians)
            rotated_chain = pg.transform.rotate(chain_image, -angle)  # 방향에 따라 체인 회전
            projectiles.append({
                "pos": [chaingoast_x_pos, chaingoast_y_pos],
                "dir": [dir_x, dir_y],
                "image": rotated_chain
            })
    
    # 발사체 위치 업데이트
    for projectile in projectiles:
        projectile["pos"][0] += projectile["dir"][0] * projectile_speed
        projectile["pos"][1] += projectile["dir"][1] * projectile_speed
    
    
    #가로세로 경계값 처리
    #에단
    if edan_x_pos < 0:
        edan_x_pos = 0
    elif edan_x_pos > screen_width - edan_width:
        edan_x_pos = screen_width - edan_width
    elif edan_y_pos < 0:
        edan_y_pos = 0
    elif edan_y_pos > screen_height - edan_height:
        edan_y_pos = screen_height - edan_height
    
    #체인유령
    if chaingoast_x_pos < 0:
        chaingoast_x_pos = 0
    elif chaingoast_x_pos > screen_width - chaingoast_width:
        chaingoast_x_pos = screen_width - chaingoast_width
    elif chaingoast_y_pos < 0:
        chaingoast_y_pos = 0
    elif chaingoast_y_pos > screen_height - chaingoast_height:
        chaingoast_y_pos = screen_height - chaingoast_height
    
    #에단 정보 업데이트
    edan_rect = edan.get_rect(centerx = edan_width / 2, centery = edan_height / 2)
    edan_rect.left = edan_x_pos
    edan_rect.top = edan_y_pos   
    
    #체인유령 정보 업데이트
    chaingoast_rect = chaingoast.get_rect()
    chaingoast_rect.left = chaingoast_x_pos
    chaingoast_rect.top = chaingoast_y_pos 
    
    #충돌처리
    if edan_rect.colliderect(chaingoast_rect) and imotal_time <= 0:
        imotal_time = 2000
        edan_lives -= 1
        edan_red_timer = edan_red_duration
        if edan_lives <=- 0:
            running = False
            break
    
    for projectile in projectiles:
        projectile_rect = projectile["image"].get_rect(topleft=(projectile["pos"][0], projectile["pos"][1]))
        if edan_rect.colliderect(projectile_rect) and imotal_time <= 0:
            imotal_time = 2000  # 충돌 시 2초 동안 무적
            edan_lives -= 1  # 목숨 감소
            edan_red_timer = edan_red_duration  # 붉게 변한 상태 유지 시간 설정
            if edan_lives <= 0:
                running = False  # 목숨이 다하면 게임 종료
    
    # 불꽃과 적의 충돌 체크
    chaingoast_rect = chaingoast.get_rect(center=(chaingoast_x_pos, chaingoast_y_pos))
    for fire in fires[:]:
        rotated_fire_image = pg.transform.rotate(fire_image, fire["angle"])
        fire_rect = rotated_fire_image.get_rect(center=fire["pos"])
        if fire_rect.colliderect(chaingoast_rect):
            chaingoast_hp -= 1  # 체력 감소
            fires.remove(fire)  # 불꽃 삭제
            chaingoast_red_timer = chaingoast_red_duration
            if chaingoast_hp <= 0:
                game_result = 'COMPLITE'
                running = False  # 적 처치 시 게임 종료
        elif fire["pos"][0] < 0 or fire["pos"][0] > screen_width or fire["pos"][1] < 0 or fire["pos"][1] > screen_height:
            explosions.append({"pos": fire["pos"], "time": pg.time.get_ticks()})  # 폭발 추가
            fires.remove(fire)
    
    #폭발 지속시간 
    # 폭발 효과 지속 시간 설정 (예: 500ms 동안 표시)
    current_time = pg.time.get_ticks()
    explosions = [explosion for explosion in explosions if current_time - explosion["time"] < 500]
    
    #유령 체력 게이지 계산
    current_hp_ratio = chaingoast_hp / max_chaingoast_hp  # 현재 HP 비율
    current_hp_bar_width = hp_bar_width * current_hp_ratio  # 비율에 따른 게이지 길이 계산
    
    #화면에 그리기
    
    #배경
    screen.blit(background, (0,0))
    
    
    #에단
    if edan_red_timer > 0:
        screen.blit(edan_red, (edan_x_pos, edan_y_pos))  # 붉은 색 에단
    else:
        screen.blit(edan, (edan_x_pos, edan_y_pos))  # 일반 에단
        
    #히트박스
    edan_hitbox = pg.Rect(edan_x_pos, edan_y_pos, edan_width, edan_height)
    pg.draw.rect(screen, hitbox_color, edan_hitbox, 2)
    
    #사슬유령
    if chaingoast_red_timer > 0:
        screen.blit(chaingoast_red, (chaingoast_x_pos, chaingoast_y_pos)) # 데미지 입은 체인유령
    else:
        screen.blit(chaingoast, (chaingoast_x_pos, chaingoast_y_pos)) # 일반 체인유령
    
    #사슬
    for projectile in projectiles:#발사체
        screen.blit(projectile["image"], (projectile["pos"][0], projectile["pos"][1]))
    
    #에단 목숨
    for i in range(edan_lives):
        screen.blit(life, (screen_width - (i + 1) * (life.get_rect().width + 10), 10))
    
    hp_bar_x = (screen_width - hp_bar_width) / 2  # 화면 중앙에 배치
    hp_bar_y = 30  # 상단에 위치 설정
    pg.draw.rect(screen, (100, 100, 100), (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))  # 회색 배경
    pg.draw.rect(screen, hp_bar_color, (hp_bar_x, hp_bar_y, current_hp_bar_width, hp_bar_height))  # 현재 HP 게이지
    
    #불꽃
    for fire in fires:
        rotated_fire_image = pg.transform.rotate(fire_image, fire["angle"])
        screen.blit(rotated_fire_image, (fire["pos"][0] - rotated_fire_image.get_width() / 2, fire["pos"][1] - rotated_fire_image.get_height() / 2))
    
    # 폭발
    for explosion in explosions:
        screen.blit(explosion_image, (explosion["pos"][0] - explosion_image.get_width() / 2, explosion["pos"][1] - explosion_image.get_height() / 2))
    pg.display.update()

msg = game_font.render(game_result, True, (255,0,0))
msg_rect = msg.get_rect(center=(int(screen_width / 2), int(screen_height / 2)))
screen.blit(msg, msg_rect)
pg.display.update()

pg.time.delay(2000)
pg.quit()
