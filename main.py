import pygame
import sys
import numpy as np
from heightcalc import generate_random_heights, compute_visibility

pygame.init()

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
MIN_CELL_SIZE = 5
MAX_CELL_SIZE = 120
FONT_SIZE = 24

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
SELECTED_COLOR = (255, 200, 50)

# Размеры поля
N, M = 10000, 10000

heights = generate_random_heights(N, M)
visibility = None
selected_cell = None
cell_size = 40  # начальный размер ячейки

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Visibility Demo (Scroll to zoom)")
clock = pygame.time.Clock()
font = pygame.font.Font(None, FONT_SIZE)


def get_cell_size_for_font(size):
	"""Возвращает подходящий размер шрифта в зависимости от размера ячейки"""
	if size < 15:
		return 10
	elif size < 25:
		return 14
	elif size < 40:
		return 18
	elif size < 60:
		return 24
	else:
		return 32


def draw_grid():
	total_w = M * cell_size
	total_h = N * cell_size

	# Центрируем поле
	off_x = (WINDOW_WIDTH - total_w) // 2
	off_y = (WINDOW_HEIGHT - total_h) // 2

	# Определяем размер шрифта
	font_size = get_cell_size_for_font(cell_size)
	current_font = pygame.font.Font(None, font_size)

	for row in range(N):
		for col in range(M):
			x = off_x + col * cell_size
			y = off_y + row * cell_size

			# Выбор цвета
			if selected_cell == (row, col):
				color = SELECTED_COLOR
			elif visibility is not None:
				color = GREEN if visibility[row, col] else RED
			else:
				color = WHITE

			pygame.draw.rect(screen, color, (x, y, cell_size, cell_size))
			pygame.draw.rect(screen, BLACK, (x, y, cell_size, cell_size), max(1, cell_size // 30))

			# Отображаем высоту только если ячейка достаточно большая
			if cell_size >= 20:
				text = current_font.render(str(heights[row, col]), True, BLACK)
				text_rect = text.get_rect(center=(x + cell_size // 2, y + cell_size // 2))
				screen.blit(text, text_rect)

	# Информация вверху экрана
	info_texts = [
		f"Selected: {selected_cell if selected_cell else 'None'}",
		f"Zoom: {cell_size}px",
		f"Scroll to zoom | ESC to clear"
	]
	for i, text in enumerate(info_texts):
		surf = font.render(text, True, BLACK)
		screen.blit(surf, (10, 10 + i * 25))


def get_cell_from_pos(pos):
	total_w = M * cell_size
	total_h = N * cell_size
	off_x = (WINDOW_WIDTH - total_w) // 2
	off_y = (WINDOW_HEIGHT - total_h) // 2
	px, py = pos
	if off_x <= px <= off_x + total_w and off_y <= py <= off_y + total_h:
		col = (px - off_x) // cell_size
		row = (py - off_y) // cell_size
		if 0 <= row < N and 0 <= col < M:
			return (row, col)
	return None


def reset_selection():
	global selected_cell, visibility
	selected_cell = None
	visibility = None


def main():
	global selected_cell, visibility, cell_size

	running = True

	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

			elif event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:  # Левая кнопка
					cell = get_cell_from_pos(event.pos)
					if cell is not None:
						if selected_cell == cell:
							reset_selection()
						else:
							selected_cell = cell
							row, col = cell
							visibility = compute_visibility(N, M, row, col, heights)

				elif event.button == 4:  # Колёсико вверх (увеличение)
					new_size = min(cell_size + 5, MAX_CELL_SIZE)
					if new_size != cell_size:
						cell_size = new_size

				elif event.button == 5:  # Колёсико вниз (уменьшение)
					new_size = max(cell_size - 5, MIN_CELL_SIZE)
					if new_size != cell_size:
						cell_size = new_size

			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					reset_selection()
				elif event.key == pygame.K_r:
					cell_size = 40

		screen.fill(WHITE)
		draw_grid()
		pygame.display.flip()
		clock.tick(60)

	pygame.quit()
	sys.exit()


if __name__ == "__main__":
	main()