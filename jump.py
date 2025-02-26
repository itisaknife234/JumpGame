import pygame
import sys
import time
import random

FPS = 60
MAX_WIDTH = 600
MAX_HEIGHT = 400
GAP_SIZE = 120
GRAVITY = 0.5   # 중력 값 (떼면 하강 속도)
FLY_FORCE = -5  # 상승 힘 (스페이스바 누를 때 상승량)

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((MAX_WIDTH, MAX_HEIGHT))

font = pygame.font.Font(None, 36)
button_font = pygame.font.Font(None, 28)

# 배경 이미지 로드
try:
    background_img = pygame.image.load("./background.png")
    background_img = pygame.transform.scale(background_img, (MAX_WIDTH, MAX_HEIGHT))
except:
    background_img = None

# 캐릭터 이미지 로드 및 크기 조정
character_img = pygame.image.load("./호시미미야비01.png")
character_img = pygame.transform.scale(character_img, (35, 35))


class Player():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_y = 0  # 수직 속도 (위아래 이동)
        self.width = 35  # 캐릭터 너비
        self.height = 35  # 캐릭터 높이
        self.image_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.score = 0  # 점수 카운트

    def draw(self):
        self.image_rect.topleft = (self.x, self.y)
        screen.blit(character_img, self.image_rect)

    def move(self, flying):
        if flying:
            self.vel_y = FLY_FORCE  # 상승
        else:
            self.vel_y += GRAVITY  # 중력 적용 (하강)

        self.y += self.vel_y  # 위치 업데이트

        # 충돌 판정 (화면 위/아래 닿으면 게임 오버)
        if self.y <= 0 or self.y + self.height >= MAX_HEIGHT:
            return True  # 게임 오버
        return False  # 계속 진행 가능


class Enemy():
    def __init__(self):
        self.x = MAX_WIDTH
        self.gap_y = random.randint(80, MAX_HEIGHT - GAP_SIZE - 80)  # 장애물 틈 위치 랜덤 설정
        self.speed = 5
        self.passed = False

    def draw(self):
        bottom_rect = pygame.draw.rect(screen, (255, 0, 0), (self.x, self.gap_y + GAP_SIZE, 20, MAX_HEIGHT - (self.gap_y + GAP_SIZE)))
        top_rect = pygame.draw.rect(screen, (255, 0, 0), (self.x, 0, 20, self.gap_y))
        return bottom_rect, top_rect

    def move(self, player_score):
        """장애물 이동 및 속도 증가 로직"""
        self.x -= self.speed

        if player_score >= 4:
            self.speed += 0.01  # 점진적 속도 증가

        # 화면 밖으로 나가면 다시 등장
        if self.x <= -20:
            self.x = MAX_WIDTH
            self.gap_y = random.randint(80, MAX_HEIGHT - GAP_SIZE - 80)
            self.speed += 0.1  # 기본 속도 증가
            self.passed = False  # 새로운 장애물이 나오면 다시 체크 필요


def draw_button(text, x, y, width, height, color, hover_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x < mouse[0] < x + width and y < mouse[1] < y + height:
        pygame.draw.rect(screen, hover_color, (x, y, width, height))
        if click[0] == 1 and action is not None:
            action()
    else:
        pygame.draw.rect(screen, color, (x, y, width, height))

    text_surface = button_font.render(text, True, (255, 255, 255))
    screen.blit(text_surface, (x + 15, y + 10))


def game_over_screen(final_score):
    screen.fill((0, 0, 0, 180))
    game_over_text = font.render("   Game Over!", True, (255, 0, 0))
    screen.blit(game_over_text, (MAX_WIDTH // 2 - 80, MAX_HEIGHT // 2 - 60))

    score_text = font.render(f" Final Score: {final_score}", True, (255, 255, 255))
    screen.blit(score_text, (MAX_WIDTH // 2 - 80, MAX_HEIGHT // 2 - 30))

    draw_button("Restart", MAX_WIDTH // 2 - 90, MAX_HEIGHT // 2, 100, 40, (0, 200, 0), (0, 255, 0), main)
    draw_button("   Quit", MAX_WIDTH // 2 + 10, MAX_HEIGHT // 2, 100, 40, (200, 0, 0), (255, 0, 0), sys.exit)

    pygame.display.update()


def main():
    player = Player(50, MAX_HEIGHT // 2)
    enemy = Enemy()
    game_over = False
    flying = False  # 스페이스바가 눌려있는지 확인

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    flying = True  # 상승 상태로 변경
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE and not game_over:
                    flying = False  # 하강 상태로 변경

        clock.tick(FPS)

        # 배경 표시
        if background_img:
            screen.blit(background_img, (0, 0))
        else:
            screen.fill((255, 255, 255))

        if not game_over:
            player.draw()
            hit_top_or_bottom = player.move(flying)  # 화면 위/아래 충돌 체크
            bottom_rect, top_rect = enemy.draw()
            enemy.move(player.score)  # 점수 기반 속도 증가 적용

            # 장애물을 통과하면 점수 증가
            if enemy.x + 20 < player.x and not enemy.passed:
                player.score += 1
                enemy.passed = True  # 같은 장애물에서 중복 점수 방지

            # 점수 표시
            score_text = font.render(f"Score: {player.score}", True, (255, 255, 255))
            screen.blit(score_text, (10, 10))

            # 충돌 판정 (화면 위/아래 닿거나 장애물 충돌 시 게임 오버)
            if hit_top_or_bottom or player.image_rect.colliderect(bottom_rect) or player.image_rect.colliderect(top_rect):
                game_over = True  # 게임 종료 플래그 설정

        else:
            game_over_screen(player.score)  # 즉시 게임 오버 화면 출력 및 버튼 활성화
            continue

        pygame.display.update()


if __name__ == '__main__':
    main()
