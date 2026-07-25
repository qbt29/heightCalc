import pyglet
from pyglet.gl import *
from pyglet.window import key, mouse
import numpy as np
from heightcalc import generate_random_heights, compute_visibility

# ----------------------------
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
MIN_CELL_SIZE = 5
MAX_CELL_SIZE = 120

# Цвета в формате (R, G, B) целые 0..255
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 102, 102)
GREEN = (102, 255, 102)
SELECTED = (255, 204, 51)   # жёлтый

# Размеры поля (можно менять, например 1000, 1000)
N, M = 10000, 10000
heights = generate_random_heights(N, M)
visibility = None
selected_cell = None
cell_size = 20   # начальный размер ячейки в пикселях

window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT,
                              caption="Visibility Demo (Texture)")

# ----------------------------
# Глобальные объекты для рендеринга
color_array = None          # numpy (N, M, 3) uint8
sprite = None               # pyglet.sprite.Sprite

def create_sprite():
    """Создаёт спрайт из текущего color_array с настройкой фильтрации."""
    global sprite
    if color_array is None:
        return
    # Переворачиваем по вертикали для OpenGL
    flipped = np.flipud(color_array)
    data = flipped.tobytes()
    image = pyglet.image.ImageData(M, N, 'RGB', data, pitch=M * 3)
    texture = image.get_texture()
    # Чёткие пиксели без размытия
    glBindTexture(GL_TEXTURE_2D, texture.id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glBindTexture(GL_TEXTURE_2D, 0)
    sprite = pyglet.sprite.Sprite(texture)
    update_sprite_position_and_size()

def update_sprite_position_and_size():
    """Центрирует спрайт и устанавливает размер согласно cell_size."""
    if sprite is None:
        return
    total_w = M * cell_size
    total_h = N * cell_size
    sprite.width = total_w
    sprite.height = total_h
    sprite.x = (WINDOW_WIDTH - total_w) // 2
    sprite.y = (WINDOW_HEIGHT - total_h) // 2

def update_colors():
    """Пересчитывает color_array на основе visibility и selected_cell."""
    global color_array
    if visibility is None:
        color_array = np.full((N, M, 3), WHITE, dtype=np.uint8)
    else:
        # Зелёные видимые, красные невидимые
        color_array = np.where(visibility[..., None],
                               np.array(GREEN, dtype=np.uint8),
                               np.array(RED, dtype=np.uint8))
    if selected_cell is not None:
        row, col = selected_cell
        color_array[row, col] = SELECTED

def update_visuals():
    """Обновляет цвета и пересоздаёт спрайт."""
    update_colors()
    create_sprite()

def get_cell_from_pos(px, py):
    """Определяет индекс ячейки по координатам окна."""
    if sprite is None:
        return None
    x0, y0 = sprite.x, sprite.y
    w, h = sprite.width, sprite.height
    if x0 <= px <= x0 + w and y0 <= py <= y0 + h:
        col = int((px - x0) // cell_size)
        # Инвертируем Y, так как экранные координаты идут сверху вниз,
        # а массив heights индексируется снизу вверх?
        # В оригинале row считался инвертированным: row = N-1 - (py - y0)//cell_size
        row = int((N - 1) - (py - y0) // cell_size)
        if 0 <= row < N and 0 <= col < M:
            return (row, col)
    return None

def reset_selection():
    global selected_cell, visibility
    selected_cell = None
    visibility = None
    update_visuals()

# ----------------------------
# Инициализация
update_visuals()

# ----------------------------
@window.event
def on_draw():
    window.clear()
    if sprite is not None:
        sprite.draw()

    # Информационная панель
    info_lines = [
        f"Selected: {selected_cell if selected_cell else 'None'}",
        f"Zoom: {cell_size}px",
        "Scroll to zoom | ESC to clear | R reset zoom"
    ]
    for i, line in enumerate(info_lines):
        label = pyglet.text.Label(line,
                                  font_name='Arial',
                                  font_size=14,
                                  x=10,
                                  y=WINDOW_HEIGHT - 10 - i * 25,
                                  anchor_x='left', anchor_y='top',
                                  color=(0, 0, 0, 255))
        label.draw()

    # Текст высот только для небольших полей
    if cell_size >= 25 and N * M <= 500:
        total_w = M * cell_size
        total_h = N * cell_size
        off_x = (WINDOW_WIDTH - total_w) // 2
        off_y = (WINDOW_HEIGHT - total_h) // 2
        font_size = 12 if cell_size < 40 else 18
        for row in range(N):
            for col in range(M):
                x = off_x + col * cell_size + cell_size // 2
                y = off_y + (N - 1 - row) * cell_size + cell_size // 2
                label = pyglet.text.Label(str(heights[row, col]),
                                          font_name='Arial',
                                          font_size=font_size,
                                          x=x, y=y,
                                          anchor_x='center', anchor_y='center',
                                          color=(0, 0, 0, 255))
                label.draw()

# ----------------------------
@window.event
def on_mouse_press(x, y, button, modifiers):
    global selected_cell, visibility
    if button == mouse.LEFT:
        cell = get_cell_from_pos(x, y)
        if cell is not None:
            if selected_cell == cell:
                reset_selection()
            else:
                selected_cell = cell
                row, col = cell
                print(f"Computing visibility from ({row}, {col})...")
                visibility = compute_visibility(N, M, row, col, heights)
                print("Done.")
                update_visuals()

@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    global cell_size
    new_size = min(cell_size + 5, MAX_CELL_SIZE) if scroll_y > 0 else max(cell_size - 5, MIN_CELL_SIZE)
    if new_size != cell_size:
        cell_size = new_size
        update_sprite_position_and_size()
        print(f"Zoom: {cell_size}px")

@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.ESCAPE:
        reset_selection()
    elif symbol == key.R:
        global cell_size
        cell_size = 40
        update_sprite_position_and_size()

# ----------------------------
if __name__ == "__main__":
    pyglet.app.run()