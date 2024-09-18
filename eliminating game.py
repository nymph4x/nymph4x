import pygame
import random
import os

# 初始化 Pygame
pygame.init()

# 屏幕尺寸（根据背景图来适应）
WIDTH, HEIGHT = 600, 800  # 你可以根据实际情况调整
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("鱼了个鱼")

# 加载并缩放图像
def load_and_scale_image(path, target_size):
    image = pygame.image.load(path)
    return pygame.transform.scale(image, target_size)

# 加载背景图并缩放到屏幕大小
bg_main = load_and_scale_image(os.path.join('images', 'background.png'), (WIDTH, HEIGHT))
bg_game = load_and_scale_image(os.path.join('images', 'background2.png'), (WIDTH, HEIGHT))
bg_win = load_and_scale_image(os.path.join('images', 'win.jpg'), (WIDTH, HEIGHT))
bg_lose = load_and_scale_image(os.path.join('images', 'lose.jpg'), (WIDTH, HEIGHT))

# 加载卡片图案并缩放到合适尺寸
CARD_WIDTH, CARD_HEIGHT = 100, 100  # 设置卡片尺寸
cards = [load_and_scale_image(os.path.join('images', f'pattern_{i}.png'), (CARD_WIDTH, CARD_HEIGHT)) for i in range(1,10)]

# 设置字体
font = pygame.font.SysFont(None, 50)
small_font = pygame.font.SysFont(None, 30)

# 颜色定义
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
PINK = (255, 192, 203)

# 游戏状态
STATE_MAIN = 0
STATE_GAME = 1
STATE_END = 2

# 定义卡片类
class Card:
    def __init__(self, image, x, y, z):
        self.image = image
        self.rect = image.get_rect(topleft=(x, y))
        self.z = z  # z 代表堆叠层数
        self.selected = False  # 用来判断卡片是否被选中
        self.cleared = False   # 用来判断卡片是否被消除
        

    def draw(self, surface):
        # 如果卡片被选中，将边缘变为红色
        if self.selected:
            pygame.draw.rect(surface, RED, self.rect, 5)  # 绘制红色边框
        if not self.cleared:
            surface.blit(self.image, self.rect)

    

def draw_button(surface, x, y, width, height, text):
    # 绘制圆角矩形框
    border_radius = 15
    button_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, PINK, button_rect, border_radius=border_radius)
    pygame.draw.rect(surface, WHITE, button_rect, 2, border_radius=border_radius)
    
    # 绘制按钮文本
    text_surf = font.render(text, True, WHITE)
    text_rect = text_surf.get_rect(center=button_rect.center)
    surface.blit(text_surf, text_rect.topleft)
    return text_rect

# 主界面
def main_menu():
    screen.blit(bg_main, (0, 0))
    draw_button(screen, WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50, 'Start Game')
    start_easy_rect = draw_button(screen, WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50, 'Easy Mode')
    start_hard_rect = draw_button(screen, WIDTH // 2 - 100, HEIGHT // 2 + 90, 200, 50, 'Hard Mode')

    return start_easy_rect, start_hard_rect

# 游戏结束界面
def game_over(win):
    screen.fill((0, 0, 0))
    if win:
        screen.blit(bg_win, (0, 0))
    else:
        screen.blit(bg_lose, (0, 0))
    replay_button_rect = draw_button(screen, WIDTH // 2, HEIGHT // 2 + 100, 200, 50, "Replay")
    return replay_button_rect

# 游戏界面
def game_screen(card_list, pending_list, clear_list, time_left):
    screen.blit(bg_game, (0, 0))

    # 绘制未消除的卡片
    for card in card_list:
        if not card.cleared:
            card.draw(screen)
    
    # 绘制选中的卡片
    for card in pending_list:
        card.draw(screen)
    
    # 绘制已消除的卡片
    for card in clear_list:
        card.draw(screen)

    # 倒计时显示
    time_text = small_font.render(f"Time Left: {time_left} sec", True, (255, 255, 255))
    screen.blit(time_text, (WIDTH - 200, 10))




# 主游戏逻辑
def game_loop(level):
    card_list = []
    clear_list = []

    # 简单模式卡片数量，困难模式更多
    card_count = 30 if level == 'easy' else 48
    total_time = 60  # 设置为60秒的倒计时

    # 确保卡片的数量为3的倍数
    card_per_count = card_count // 3

    # 确保每种类型的卡片数量是3的倍数
    cards_to_use = []
    for i in range(card_per_count):
        j = random.randint(1,9)
        cards_to_use.extend([cards[j]] * 3) 

    # 随机打乱卡片列表
    random.shuffle(cards_to_use)

    # 随机分配卡片，每种类型的卡片数量必须为3的倍数
    for z in range(2):  # 两层卡片
        for i in range(card_count // 2 ):
            x = random.randint(100, WIDTH - CARD_WIDTH - 50)
            y = random.randint(100, HEIGHT - CARD_HEIGHT - 50)
            
            card_image = cards_to_use.pop()
            card = Card(card_image, x, y, z)
            card_list.append(card)
            

    selected_cards = []
    game_running = True
    game_won = False
    start_ticks = pygame.time.get_ticks()

    while game_running:
        seconds = (pygame.time.get_ticks() - start_ticks) // 1000  # 计算经过的秒数
        time_left = total_time - seconds

        if time_left <= 0:
            game_running = False
            game_won = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # 卡片点击事件
            if event.type == pygame.MOUSEBUTTONDOWN:
                for card in card_list:
                    if card.rect.collidepoint(event.pos)  and not card.cleared:
                        if not card.selected:
                            card.selected = True
                            selected_cards.append(card)
                        break

                # 当选中三张卡片时
                if len(selected_cards) == 3:
                    if selected_cards[0].image == selected_cards[1].image == selected_cards[2].image:
                        for card in selected_cards:
                            card.cleared = True
                        selected_cards = []

                    else:
                        # 重置已选卡片
                        for card in selected_cards:
                            card.selected = False
                        selected_cards = []

                # 如果卡片全部消除，游戏胜利
                if all(card.cleared for card in card_list):
                    game_running = False
                    game_won = True

        game_screen(card_list, selected_cards, clear_list, time_left)
        pygame.display.update()

    return game_won

# 主程序
def main():
    state = STATE_MAIN
    level = 'easy'
    game_won = False

    while True:
        screen.fill((0, 0, 0))

        if state == STATE_MAIN:
            start_easy_rect, start_hard_rect = main_menu()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if start_easy_rect.collidepoint(event.pos):
                        level = 'easy'
                        state = STATE_GAME
                    elif start_hard_rect.collidepoint(event.pos):
                        level = 'hard'
                        state = STATE_GAME

        elif state == STATE_GAME:
            game_won = game_loop(level)
            state = STATE_END

        elif state == STATE_END:
            replay_button_rect = game_over(game_won)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if replay_button_rect.collidepoint(event.pos):
                        state = STATE_MAIN

        pygame.display.update()

if __name__ == '__main__':
    main()
