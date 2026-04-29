#!/usr/bin/env python3
"""Apple ][ GR-style 40x40 matrix Snake game in a dedicated window.

Controls:
  i = up
  m = down
  j = left
  k = right
  q = quit
"""

from __future__ import annotations

import random
import tkinter as tk
from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    y: int
    x: int


GRID_SIZE = 40
CELL_SIZE = 12
INITIAL_LENGTH = 3
FRAME_DELAY_MS = 120

UP = Point(-1, 0)
DOWN = Point(1, 0)
LEFT = Point(0, -1)
RIGHT = Point(0, 1)

KEY_TO_DIRECTION = {
    "i": UP,
    "m": DOWN,
    "j": LEFT,
    "k": RIGHT,
}

OPPOSITE_DIRECTION = {
    UP: DOWN,
    DOWN: UP,
    LEFT: RIGHT,
    RIGHT: LEFT,
}


class SnakeGame:
    def __init__(self) -> None:
        mid = GRID_SIZE // 2
        self.snake: list[Point] = [
            Point(mid, mid),
            Point(mid, mid - 1),
            Point(mid, mid - 2),
        ]
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.score = 0
        self.dot = self.spawn_dot()
        self.game_over = False

    def spawn_dot(self) -> Point:
        snake_cells = set(self.snake)
        candidates = [
            Point(y, x)
            for y in range(GRID_SIZE)
            for x in range(GRID_SIZE)
            if Point(y, x) not in snake_cells
        ]
        return random.choice(candidates)

    def turn(self, new_direction: Point) -> None:
        if new_direction != OPPOSITE_DIRECTION[self.direction]:
            self.next_direction = new_direction

    def tick(self) -> None:
        if self.game_over:
            return

        self.direction = self.next_direction
        head = self.snake[0]
        new_head = Point(head.y + self.direction.y, head.x + self.direction.x)

        if (
            new_head.x < 0
            or new_head.x >= GRID_SIZE
            or new_head.y < 0
            or new_head.y >= GRID_SIZE
            or new_head in self.snake
        ):
            self.game_over = True
            return

        self.snake.insert(0, new_head)
        if new_head == self.dot:
            self.score += 1
            self.dot = self.spawn_dot()
        else:
            self.snake.pop()


class SnakeApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("snakebyte - Apple ][ GR 40x40")
        self.root.resizable(False, False)

        canvas_px = GRID_SIZE * CELL_SIZE
        self.canvas = tk.Canvas(root, width=canvas_px, height=canvas_px, bg="black", highlightthickness=0)
        self.canvas.pack(padx=10, pady=(10, 4))

        self.info_label = tk.Label(root, text="", font=("Courier", 11), anchor="w")
        self.info_label.pack(fill="x", padx=10, pady=(0, 2))

        self.help_label = tk.Label(root, text="Controls: i/m/j/k, q=quit, r=restart", font=("Courier", 10), anchor="w")
        self.help_label.pack(fill="x", padx=10, pady=(0, 10))

        self.game = SnakeGame()

        self.root.bind("<KeyPress>", self.on_key)
        self.running = True
        self.draw()
        self.loop()

    def on_key(self, event: tk.Event) -> None:
        key = event.keysym.lower()

        if key == "q":
            self.running = False
            self.root.destroy()
            return

        if key == "r" and self.game.game_over:
            self.game = SnakeGame()
            self.draw()
            return

        if key in KEY_TO_DIRECTION and not self.game.game_over:
            self.game.turn(KEY_TO_DIRECTION[key])

    def grid_to_px(self, p: Point) -> tuple[int, int, int, int]:
        x0 = p.x * CELL_SIZE
        y0 = p.y * CELL_SIZE
        x1 = x0 + CELL_SIZE
        y1 = y0 + CELL_SIZE
        return x0, y0, x1, y1

    def draw(self) -> None:
        self.canvas.delete("all")

        # Apple ][ GR 느낌: 검은 바탕 + 단색 블록
        for y in range(0, GRID_SIZE * CELL_SIZE, CELL_SIZE):
            self.canvas.create_line(0, y, GRID_SIZE * CELL_SIZE, y, fill="#111111")
        for x in range(0, GRID_SIZE * CELL_SIZE, CELL_SIZE):
            self.canvas.create_line(x, 0, x, GRID_SIZE * CELL_SIZE, fill="#111111")

        # food
        self.canvas.create_rectangle(*self.grid_to_px(self.game.dot), fill="#00FF66", outline="")

        # snake
        head = self.game.snake[0]
        self.canvas.create_rectangle(*self.grid_to_px(head), fill="#FFFFFF", outline="")
        for seg in self.game.snake[1:]:
            self.canvas.create_rectangle(*self.grid_to_px(seg), fill="#33AAFF", outline="")

        status = f"Score: {self.game.score}   Length: {len(self.game.snake)}"
        if self.game.game_over:
            status += "   GAME OVER (r=restart)"
            self.canvas.create_text(
                GRID_SIZE * CELL_SIZE // 2,
                GRID_SIZE * CELL_SIZE // 2,
                text="GAME OVER",
                fill="#FF5555",
                font=("Courier", 26, "bold"),
            )
        self.info_label.config(text=status)

    def loop(self) -> None:
        if not self.running:
            return

        if not self.game.game_over:
            self.game.tick()
        self.draw()
        self.root.after(FRAME_DELAY_MS, self.loop)


def main() -> None:
    root = tk.Tk()
    SnakeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
