import pygame
from .settings import *
from .data_manager import DataManager
from .sprites import Enemy, Player, Bullet

class GameManager:
    """
    게임의 전체 상태(메뉴, 플레이, 게임오버)를 관리하는 핵심 클래스
    """
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(FONT_NAME, 30)
        
        self.data_manager = DataManager()
        self.running = True
        self.state = "MENU" # 초기 상태: 메뉴
        
        # 게임 관련 변수
        self.selected_language = None
        self.score = 0
        self.input_text = "" # 사용자가 현재 타이핑 중인 글자
        self.lives = 3  # 생명력 (하트 3개)
        
        # 카운트다운 관련
        self.countdown_timer = 0
        self.countdown_number = 3
        
        # 스프라이트 그룹
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.player = Player()
        self.all_sprites.add(self.player)

        # 적 생성 타이머
        self.spawn_timer = 0
        
        # 용어 공부 스크롤 관련
        self.study_scroll_offset = 0
        self.study_max_scroll = 0
        
        # 입력 커서 관련
        self.cursor_timer = 0
        self.cursor_visible = True

    def run(self):
        """게임 메인 루프"""
        while self.running:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def events(self):
        """키보드 및 마우스 입력 처리"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if self.state == "MENU":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_menu_click(event.pos)
            
            elif self.state == "GAMEOVER":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        # 메뉴로 복귀
                        self.state = "MENU"
            
            elif self.state == "STUDY_MENU":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_study_menu_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = "MENU"
            
            elif self.state == "STUDY":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        self.state = "STUDY_MENU"
                elif event.type == pygame.MOUSEWHEEL:
                    # 마우스 휠로 스크롤
                    self.study_scroll_offset -= event.y * 30  # 스크롤 속도 조절
                    # 스크롤 범위 제한
                    self.study_scroll_offset = max(0, min(self.study_scroll_offset, self.study_max_scroll))
            
            elif self.state == "PLAYING":
                if event.type == pygame.KEYDOWN:
                    # 방향키는 단어 입력에서 제외 (WASD는 단어 입력 가능)
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                        # 방향키는 무시 (플레이어 이동도 안 함)
                        pass
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    elif event.key == pygame.K_RETURN:
                        self.check_input() # 엔터 치면 정답 확인
                        self.input_text = ""
                    elif event.unicode and event.unicode.isprintable():
                        # 글자 입력 추가 (WASD 포함, 모든 문자 입력 가능)
                        self.input_text += event.unicode

    def handle_menu_click(self, pos):
        """메뉴 화면에서 언어 선택 및 용어 공부 처리"""
        langs = self.data_manager.get_language_list()
        # 버튼 영역 계산 (draw와 동일하게)
        button_width = 250
        button_height = 50
        button_spacing = 60
        start_y = 180
        button_x = (SCREEN_WIDTH - button_width) // 2
        
        # 언어 선택 버튼들
        for i, lang in enumerate(langs):
            button_y = start_y + (i * button_spacing)
            rect = pygame.Rect(button_x, button_y, button_width, button_height)
            if rect.collidepoint(pos):
                self.selected_language = lang
                self.start_game()
                return
        
        # "용어 공부" 버튼 체크
        study_button_y = start_y + len(langs) * button_spacing + 20
        study_rect = pygame.Rect(button_x, study_button_y, button_width, button_height)
        if study_rect.collidepoint(pos):
            self.state = "STUDY_MENU"  # 용어 공부 언어 선택 메뉴

    def handle_study_menu_click(self, pos):
        """용어 공부 언어 선택 메뉴 처리"""
        langs = self.data_manager.get_language_list()
        button_width = 250
        button_height = 50
        button_spacing = 60
        start_y = 150
        button_x = (SCREEN_WIDTH - button_width) // 2
        
        for i, lang in enumerate(langs):
            button_y = start_y + (i * button_spacing)
            rect = pygame.Rect(button_x, button_y, button_width, button_height)
            if rect.collidepoint(pos):
                self.selected_language = lang
                self.study_scroll_offset = 0  # 스크롤 초기화
                self.state = "STUDY"
                break
    
    def draw_study_screen(self):
        """용어 공부 화면 그리기"""
        # 제목
        title_font = pygame.font.SysFont(FONT_NAME, 40, bold=True)
        title_text = f"{self.selected_language} 용어집"
        title_surf = title_font.render(title_text, True, WHITE)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH//2, 30))
        self.screen.blit(title_surf, title_rect)
        
        # 용어 목록 가져오기
        if self.selected_language in self.data_manager.data:
            words = self.data_manager.data[self.selected_language]
            
            word_font = pygame.font.SysFont(FONT_NAME, 28, bold=True)
            desc_font = pygame.font.SysFont(FONT_NAME, 20)
            
            start_y = 80
            line_height = 60
            content_area_height = SCREEN_HEIGHT - 150  # 제목과 안내 문구 제외한 높이
            
            # 전체 콘텐츠 높이 계산
            total_content_height = len(words) * line_height
            self.study_max_scroll = max(0, total_content_height - content_area_height)
            
            # 스크롤 범위 제한
            self.study_scroll_offset = max(0, min(self.study_scroll_offset, self.study_max_scroll))
            
            # 스크롤 가능한 영역 설정
            scroll_area_top = start_y
            scroll_area_bottom = SCREEN_HEIGHT - 100
            
            # 용어 목록 그리기 (스크롤 오프셋 적용)
            for i, word_data in enumerate(words):
                y_pos = start_y + (i * line_height) - self.study_scroll_offset
                
                # 화면에 보이는 범위 내에만 그리기
                if scroll_area_top <= y_pos <= scroll_area_bottom + line_height:
                    # 단어 (빨간색, 굵게)
                    word_surf = word_font.render(word_data['word'], True, RED)
                    self.screen.blit(word_surf, (50, y_pos))
                    
                    # 설명 (회색)
                    desc_surf = desc_font.render(word_data['desc'], True, GRAY)
                    self.screen.blit(desc_surf, (300, y_pos + 5))
            
            # 스크롤바 그리기 (스크롤이 필요한 경우만)
            if self.study_max_scroll > 0:
                scrollbar_width = 10
                scrollbar_x = SCREEN_WIDTH - 30
                scrollbar_height = content_area_height
                scrollbar_y = scroll_area_top
                
                # 스크롤바 배경
                pygame.draw.rect(self.screen, GRAY, 
                                (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height))
                
                # 스크롤바 핸들 (현재 위치 표시)
                handle_height = max(20, int(scrollbar_height * (content_area_height / total_content_height)))
                handle_y = scrollbar_y + int((self.study_scroll_offset / self.study_max_scroll) * 
                                            (scrollbar_height - handle_height)) if self.study_max_scroll > 0 else scrollbar_y
                
                pygame.draw.rect(self.screen, WHITE, 
                                (scrollbar_x, handle_y, scrollbar_width, handle_height))
        
        # 안내 문구
        hint_font = pygame.font.SysFont(FONT_NAME, 20)
        hint_text = "ESC 또는 ENTER: 뒤로가기 | 마우스 휠: 스크롤"
        hint_surf = hint_font.render(hint_text, True, GRAY)
        hint_rect = hint_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 30))
        self.screen.blit(hint_surf, hint_rect)
    
    def start_game(self):
        """게임을 시작 상태로 변경 (카운트다운부터)"""
        self.state = "COUNTDOWN"
        self.score = 0
        self.input_text = ""
        self.lives = 3  # 생명력 초기화
        self.enemies.empty()
        self.bullets.empty()
        # 플레이어 위치 초기화
        self.player.rect.centerx = SCREEN_WIDTH // 2
        # 카운트다운 초기화
        self.countdown_timer = 0
        self.countdown_number = 3

    def update(self):
        """게임 상태 업데이트"""
        if self.state == "COUNTDOWN":
            # 카운트다운 처리
            self.countdown_timer += 1
            if self.countdown_timer >= FPS:  # 1초마다 숫자 감소
                self.countdown_timer = 0
                self.countdown_number -= 1
                if self.countdown_number <= 0:
                    self.state = "PLAYING"
                    self.countdown_number = 0
        
        elif self.state == "PLAYING":
            # 1. 적 생성 (약 2초마다)
            self.spawn_timer += 1
            if self.spawn_timer >= 120:
                self.spawn_timer = 0
                word_data = self.data_manager.get_random_word(self.selected_language)
                if word_data:
                    enemy = Enemy(word_data, speed=1 + (self.score // 100)) # 점수 높으면 빨라짐
                    self.all_sprites.add(enemy)
                    self.enemies.add(enemy)
            
            # 2. 충돌 체크 (총알 -> 적)
            hits = pygame.sprite.groupcollide(self.enemies, self.bullets, True, True)
            for hit in hits:
                self.score += 10
                # 적이 총알에 맞아서 제거됨
            
            # 3. 게임 오버 체크 (적이 바닥에 닿았는지)
            for enemy in self.enemies:
                if enemy.rect.bottom > SCREEN_HEIGHT:
                    enemy.kill()  # 적 제거
                    self.lives -= 1  # 생명력 감소
                    if self.lives <= 0:
                        # 게임 오버
                        self.state = "GAMEOVER"
                        break

            # 플레이어 업데이트 (방향키 이동 비활성화)
            self.player.update()
            
            # 나머지 스프라이트 업데이트
            self.enemies.update()
            self.bullets.update()
            
            # 커서 깜빡임 업데이트 (약 0.5초마다)
            self.cursor_timer += 1
            if self.cursor_timer >= FPS // 2:  # 0.5초마다 토글
                self.cursor_timer = 0
                self.cursor_visible = not self.cursor_visible

    def _draw_broken_heart(self, screen, x, y, size):
        """깨진 하트 그리기"""
        # 회색 하트 배경
        heart_font = pygame.font.SysFont('Arial', size, bold=True)
        heart_surf = heart_font.render('♥', True, GRAY)
        screen.blit(heart_surf, (x, y))
        
        # 깨진 효과 (지그재그 크랙)
        center_x = x + size // 2
        center_y = y + size // 2
        
        # 지그재그 크랙 그리기
        crack_points = [
            (center_x - size // 3, center_y - size // 4),
            (center_x - size // 6, center_y),
            (center_x, center_y + size // 6),
            (center_x + size // 6, center_y),
            (center_x + size // 3, center_y - size // 4),
        ]
        pygame.draw.lines(screen, BLACK, False, crack_points, 2)
        
        # 추가 크랙 라인
        pygame.draw.line(screen, BLACK, 
                        (center_x - size // 4, center_y - size // 6),
                        (center_x + size // 4, center_y + size // 6), 2)

    def check_input(self):
        """입력한 단어가 화면의 적과 일치하는지 확인"""
        for enemy in self.enemies:
            if self.input_text == enemy.word:
                # 일치하면 총알 발사 (적은 총알이 맞출 때까지 살아있음)
                bullet = Bullet(self.player.rect.centerx, self.player.rect.top, enemy)
                self.all_sprites.add(bullet)
                self.bullets.add(bullet)
                break # 한 번에 하나만 발사

    def draw(self):
        """화면 그리기"""
        self.screen.fill(BLACK)
        
        if self.state == "MENU":
            title_surf = self.font.render("언어를 선택하세요", True, WHITE)
            title_rect = title_surf.get_rect(center=(SCREEN_WIDTH//2, 100))
            self.screen.blit(title_surf, title_rect)
            
            langs = self.data_manager.get_language_list()
            # 버튼을 중앙에 배치하고 모든 버튼이 화면에 보이도록 조정
            button_width = 250
            button_height = 50
            button_spacing = 60
            start_y = 180
            total_height = len(langs) * button_spacing - (button_spacing - button_height)
            
            # 중앙 정렬
            button_x = (SCREEN_WIDTH - button_width) // 2
            
            for i, lang in enumerate(langs):
                button_y = start_y + (i * button_spacing)
                # 버튼 그리기
                pygame.draw.rect(self.screen, GRAY, (button_x, button_y, button_width, button_height))
                text_surf = self.font.render(lang, True, BLACK)
                text_rect = text_surf.get_rect(center=(button_x + button_width//2, button_y + button_height//2))
                self.screen.blit(text_surf, text_rect)
            
            # "용어 공부" 버튼 추가
            study_button_y = start_y + len(langs) * button_spacing + 20
            pygame.draw.rect(self.screen, BLUE, (button_x, study_button_y, button_width, button_height))
            study_text = self.font.render("용어 공부", True, WHITE)
            study_text_rect = study_text.get_rect(center=(button_x + button_width//2, study_button_y + button_height//2))
            self.screen.blit(study_text, study_text_rect)
        
        elif self.state == "STUDY_MENU":
            # 용어 공부 언어 선택 메뉴
            title_surf = self.font.render("용어 공부 - 언어를 선택하세요", True, WHITE)
            title_rect = title_surf.get_rect(center=(SCREEN_WIDTH//2, 80))
            self.screen.blit(title_surf, title_rect)
            
            langs = self.data_manager.get_language_list()
            button_width = 250
            button_height = 50
            button_spacing = 60
            start_y = 150
            button_x = (SCREEN_WIDTH - button_width) // 2
            
            for i, lang in enumerate(langs):
                button_y = start_y + (i * button_spacing)
                pygame.draw.rect(self.screen, GRAY, (button_x, button_y, button_width, button_height))
                text_surf = self.font.render(lang, True, BLACK)
                text_rect = text_surf.get_rect(center=(button_x + button_width//2, button_y + button_height//2))
                self.screen.blit(text_surf, text_rect)
            
            # 안내 문구
            hint_text = self.font.render("ESC: 뒤로가기", True, GRAY)
            hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50))
            self.screen.blit(hint_text, hint_rect)
        
        elif self.state == "STUDY":
            # 용어 공부 화면
            self.draw_study_screen()

        elif self.state == "PLAYING":
            # 스프라이트 그리기 (적과 총알 먼저)
            self.enemies.draw(self.screen)
            self.bullets.draw(self.screen)
            # 플레이어는 마지막에 그려서 위에 표시
            self.screen.blit(self.player.image, self.player.rect)
            
            # UI 그리기 (점수, 입력창)
            score_surf = self.font.render(f"Score: {self.score}", True, WHITE)
            self.screen.blit(score_surf, (10, 10))
            
            # 생명력 표시 (하트) - 화면 오른쪽
            heart_size = 30
            heart_x = SCREEN_WIDTH - 110
            heart_y = 10
            for i in range(3):
                if i < self.lives:
                    # 빨간 하트 (♥)
                    heart_font = pygame.font.SysFont('Arial', heart_size, bold=True)
                    heart_surf = heart_font.render('♥', True, RED)
                    self.screen.blit(heart_surf, (heart_x + i * 35, heart_y))
                else:
                    # 깨진 하트 그리기
                    self._draw_broken_heart(self.screen, heart_x + i * 35, heart_y, heart_size)
            
            input_surf = self.font.render(f"Target: {self.input_text}", True, YELLOW)
            self.screen.blit(input_surf, (10, SCREEN_HEIGHT - 40))
            
            # 깜빡이는 커서 그리기
            if self.cursor_visible:
                input_text_width = self.font.size(f"Target: {self.input_text}")[0]
                cursor_x = 10 + input_text_width
                cursor_y = SCREEN_HEIGHT - 40
                cursor_height = self.font.get_height()
                # 커서를 세로선으로 그리기
                pygame.draw.line(self.screen, YELLOW, 
                (cursor_x, cursor_y), 
                (cursor_x, cursor_y + cursor_height), 3)
        
        elif self.state == "COUNTDOWN":
            # 카운트다운 화면
            countdown_font = pygame.font.SysFont(FONT_NAME, 120, bold=True)
            countdown_text = str(self.countdown_number) if self.countdown_number > 0 else "GO!"
            countdown_color = RED if self.countdown_number > 0 else GREEN
            countdown_surf = countdown_font.render(countdown_text, True, countdown_color)
            countdown_rect = countdown_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(countdown_surf, countdown_rect)
            
            # 플레이어 표시 (준비 상태)
            self.screen.blit(self.player.image, self.player.rect)
        
        elif self.state == "GAMEOVER":
            # 게임 오버 화면
            gameover_font = pygame.font.SysFont(FONT_NAME, 60, bold=True)
            score_font = pygame.font.SysFont(FONT_NAME, 40)
            instruction_font = pygame.font.SysFont(FONT_NAME, 25)
            
            # "Game Over" 텍스트
            gameover_surf = gameover_font.render("Game Over", True, RED)
            gameover_rect = gameover_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
            self.screen.blit(gameover_surf, gameover_rect)
            
            # 스코어 표시
            score_text = f"Final Score: {self.score}"
            score_surf = score_font.render(score_text, True, WHITE)
            score_rect = score_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(score_surf, score_rect)
            
            # 안내 문구
            instruction_text = "Press ENTER or SPACE to return to menu"
            instruction_surf = instruction_font.render(instruction_text, True, GRAY)
            instruction_rect = instruction_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80))
            self.screen.blit(instruction_surf, instruction_rect)

        pygame.display.flip()