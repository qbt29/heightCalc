import pygame
import sys
from heightcalc import generate_random_heights, process_matrix
# Инициализация Pygame
pygame.init()

# Константы
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
CELL_SIZE = 60
FONT_SIZE = 24

# Цвета (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (150, 150, 150)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
BLUE = (100, 100, 255)
YELLOW = (255, 255, 100)
PURPLE = (200, 100, 255)
CYAN = (100, 255, 255)
SELECTED_COLOR = (255, 200, 50)  # Цвет выделенной ячейки

# Параметры поля
N = 10000  # Количество строк
M = 10000  # Количество столбцов

# Генерация случайных цветов для ячеек (или можно задать вручную)
# import random
# random.seed(42)  # Для воспроизводимости

heights = generate_random_heights(N, M)
# Создаём матрицу цветов и текстов
matrix = [[{'color': WHITE, 'height': heights[i][j], 'text': str(heights[i][j])} for j in range(M)] for i in range(N)]

# Переменные для хранения выбранной ячейки
selected_cell = None  # (row, col) или None

# Настройка окна
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Интерактивное поле N×M")
clock = pygame.time.Clock()
font = pygame.font.Font(None, FONT_SIZE)

def draw_grid():
    """Отрисовка сетки с ячейками и текстом"""
    # Вычисляем отступы для центрирования поля
    total_width = M * CELL_SIZE
    total_height = N * CELL_SIZE
    offset_x = (WINDOW_WIDTH - total_width) // 2
    offset_y = (WINDOW_HEIGHT - total_height) // 2
    
    # Рисуем каждую ячейку
    for row in range(N):
        for col in range(M):
            x = offset_x + col * CELL_SIZE
            y = offset_y + row * CELL_SIZE
            
            # Определяем цвет ячейки
            if selected_cell == (row, col):
                cell_color = SELECTED_COLOR
            else:
                cell_color = matrix[row][col]['color']
            
            # Рисуем заливку ячейки
            pygame.draw.rect(screen, cell_color, (x, y, CELL_SIZE, CELL_SIZE))
            
            # Рисуем границу ячейки
            pygame.draw.rect(screen, BLACK, (x, y, CELL_SIZE, CELL_SIZE), 2)
            
            # Рисуем текст в центре ячейки
            text_surface = font.render(matrix[row][col]['text'], True, BLACK)
            text_rect = text_surface.get_rect(center=(x + CELL_SIZE//2, y + CELL_SIZE//2))
            screen.blit(text_surface, text_rect)
    
    # Отображаем информацию о выбранной ячейке
    info_text = f"Выбрана ячейка: {selected_cell if selected_cell else 'Нет'}"
    info_surface = font.render(info_text, True, BLACK)
    screen.blit(info_surface, (10, 10))

def get_cell_from_pos(pos):
    """Получить индексы ячейки по позиции мыши"""
    # Вычисляем отступы
    total_width = M * CELL_SIZE
    total_height = N * CELL_SIZE
    offset_x = (WINDOW_WIDTH - total_width) // 2
    offset_y = (WINDOW_HEIGHT - total_height) // 2
    
    x, y = pos
    # Проверяем, что клик в пределах поля
    if (offset_x <= x <= offset_x + total_width and 
        offset_y <= y <= offset_y + total_height):
        col = (x - offset_x) // CELL_SIZE
        row = (y - offset_y) // CELL_SIZE
        if 0 <= row < N and 0 <= col < M:
            return (row, col)
    return None

def reset_selection():
    global selected_cell
    selected_cell = None
    for i in range(N):
        for j in range(M):
            matrix[i][j]['color'] = WHITE

def main():
    global selected_cell
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    cell = get_cell_from_pos(event.pos)
                    if cell is not None:
                        # Если кликнули на уже выбранную ячейку - снимаем выделение
                        if selected_cell == cell:
                            reset_selection()
                        else:
                            selected_cell = cell
                            res = process_matrix(N, M, cell[0], cell[1], matrix)
                            for i in range(N):
                                for j in range(M):
                                    if res[i][j] == 1:
                                        matrix[i][j]['color'] = GREEN
                                    else:
                                        matrix[i][j]['color'] = RED
                        print(f"Выбрана ячейка: {cell} (текст: {matrix[cell[0]][cell[1]]['text']})")
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    reset_selection()
                    print("Выделение снято")
        
        # Отрисовка
        screen.fill(WHITE)
        draw_grid()
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()