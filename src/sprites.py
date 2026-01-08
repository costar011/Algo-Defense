import pygame
import random
import math
from .settings import *

class Enemy(pygame.sprite.Sprite):
    """화면 위에서 떨어지는 버그(단어) 클래스"""
    def __init__(self, data, speed):
        super().__init__()
        self.word = data['word']  # 타이핑해야 할 단어
        self.desc = data['desc']  # 단어 설명 (게임에서는 표시 안 함)
        self.speed = speed
        
        # 폰트 설정
        self.font_main = pygame.font.SysFont(FONT_NAME, FONT_SIZE_MAIN, bold=True)
        
        # 텍스트 렌더링 (게임에서는 word만 표시)
        text_surf = self.font_main.render(self.word, True, RED)
        
        # 적의 전체 크기 계산 (word만)
        self.image = pygame.Surface((text_surf.get_width() + 20, 
                                     text_surf.get_height() + 20))
        self.image.fill(BLACK) # 배경 투명 대신 검정 (가독성 위함)
        
        # 이미지 위에 텍스트 그리기 (word만)
        self.image.blit(text_surf, (10, 10))
        
        self.rect = self.image.get_rect()
        
        # 랜덤한 X 위치, 화면 맨 위 Y 위치에서 시작
        self.rect.x = random.randint(50, SCREEN_WIDTH - self.rect.width - 50)
        self.rect.y = -self.rect.height

    def update(self):
        """매 프레임마다 아래로 이동"""
        self.rect.y += self.speed
        # 화면 밖으로 나가면 제거
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Bullet(pygame.sprite.Sprite):
    """플레이어가 발사하는 미사일"""
    def __init__(self, x, y, target_enemy):
        super().__init__()
        # 총알 크기를 더 크게 (20x30)
        self.image = pygame.Surface((20, 30), pygame.SRCALPHA)  # 투명도 지원
        # 반투명한 초록색 (단어가 가려지지 않도록)
        self.image.fill((GREEN[0], GREEN[1], GREEN[2], 128))  # 알파값 128 (50% 투명)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        
        # 타겟 정보 저장
        self.target = target_enemy
        self.target_pos = (target_enemy.rect.centerx, target_enemy.rect.centery) if target_enemy else None
        
        # 기본 속도에 약간의 랜덤성 추가 (각 총알이 조금씩 다르게)
        base_speed = 12
        self.speed = base_speed + random.uniform(-2, 2)
        
        # 타겟을 향한 방향 벡터 계산
        if self.target_pos:
            dx = self.target_pos[0] - self.rect.centerx
            dy = self.target_pos[1] - self.rect.centery
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0:
                # 정규화된 방향 벡터
                self.velocity_x = (dx / distance) * self.speed
                self.velocity_y = (dy / distance) * self.speed
            else:
                self.velocity_x = 0
                self.velocity_y = -self.speed
        else:
            self.velocity_x = 0
            self.velocity_y = -self.speed
        
        # 약간의 곡선 경로를 위한 랜덤 오프셋
        self.curve_offset = random.uniform(-0.3, 0.3)
        self.frame = 0

    def update(self):
        # 타겟이 여전히 존재하면 위치 업데이트
        if self.target and self.target.alive():
            self.target_pos = (self.target.rect.centerx, self.target.rect.centery)
            # 방향 재계산 (타겟이 움직이므로)
            dx = self.target_pos[0] - self.rect.centerx
            dy = self.target_pos[1] - self.rect.centery
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0:
                # 부드러운 추적을 위해 현재 속도와 새 방향을 섞음
                new_vx = (dx / distance) * self.speed
                new_vy = (dy / distance) * self.speed
                # 선형 보간으로 부드럽게 방향 전환
                self.velocity_x = self.velocity_x * 0.7 + new_vx * 0.3
                self.velocity_y = self.velocity_y * 0.7 + new_vy * 0.3
        
        # 곡선 효과를 위한 약간의 수평 오프셋
        curve_x = math.sin(self.frame * 0.1) * self.curve_offset
        
        # 위치 업데이트
        self.rect.centerx += self.velocity_x + curve_x
        self.rect.centery += self.velocity_y
        self.frame += 1
        
        # 화면 밖으로 나가면 제거
        if (self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT or 
            self.rect.right < 0 or self.rect.left > SCREEN_WIDTH):
            self.kill()

class Player(pygame.sprite.Sprite):
    """하단에 위치한 플레이어 캐릭터"""
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = 5  # 플레이어 이동 속도
    
    def update(self, keys=None):
        """플레이어 업데이트 (방향키 이동 비활성화)"""
        # 방향키로 움직이지 않음 - 총알 발사 시 반동 효과만 사용
        # 화면 밖으로 나가지 않도록 제한만 유지
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)
    
    def add_recoil(self, direction):
        """총알 발사 시 반동 효과"""
        # 총알 발사 시 약간의 반동 효과 (선택적)
        pass