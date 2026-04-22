#!/usr/bin/env python3
"""Terminal Snake game inspired by Apple ][ GR-style block graphics.

Controls:
  i = up
  m = down
  j = left
  k = right
  q = quit
"""

from __future__ import annotations

import curses
import random
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    y: int
    x: int


BOARD_WIDTH = 40
BOARD_HEIGHT = 24
INITIAL_LENGTH = 3
FRAME_DELAY = 0.12

UP = Point(-1, 0)
DOWN = Point(1, 0)
LEFT = Point(0, -1)
RIGHT = Point(0, 1)

KEY_TO_DIRECTION = {
    ord("i"): UP,
    ord("m"): DOWN,
    ord("j"): LEFT,
    ord("k"): RIGHT,
}

OPPOSITE_DIRECTION = {
    UP: DOWN,
    DOWN: UP,
    LEFT: RIGHT,
    RIGHT: LEFT,
}


class SnakeGame:
    def __init__(self) -> None:
        mid_y = BOARD_HEIGHT // 2
        mid_x = BOARD_WIDTH // 2
        self.snake: list[Point] = [
            Point(mid_y, mid_x),
            Point(mid_y, mid_x - 1),
            Point(mid_y, mid_x - 2),
        ]
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.score = 0
        self.dot = self._spawn_dot()
        self.game_over = False

    def _spawn_dot(self) -> Point:
        snake_cells = set(self.snake)
        candidates = [
            Point(y, x)
            for y in range(1, BOARD_HEIGHT + 1)
            for x in range(1, BOARD_WIDTH + 1)
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
            new_head.x < 1
            or new_head.x > BOARD_WIDTH
            or new_head.y < 1
            or new_head.y > BOARD_HEIGHT
        ):
            self.game_over = True
            return

        if new_head in self.snake:
            self.game_over = True
            return

        self.snake.insert(0, new_head)
        if new_head == self.dot:
            self.score += 1
            self.dot = self._spawn_dot()
        else:
            self.snake.pop()


def draw(stdscr: curses.window, game: SnakeGame) -> None:
    stdscr.erase()

    # GR 느낌의 사각형 화면 테두리
    top = "+" + "-" * BOARD_WIDTH + "+"
    bottom = top
    stdscr.addstr(0, 0, top)
    for row in range(1, BOARD_HEIGHT + 1):
        stdscr.addstr(row, 0, "|")
        stdscr.addstr(row, BOARD_WIDTH + 1, "|")
    stdscr.addstr(BOARD_HEIGHT + 1, 0, bottom)

    # 점(먹이)
    stdscr.addstr(game.dot.y, game.dot.x, ".")

    # 뱀 머리/몸
    head = game.snake[0]
    stdscr.addstr(head.y, head.x, "@")
    for segment in game.snake[1:]:
        stdscr.addstr(segment.y, segment.x, "#")

    stdscr.addstr(
        BOARD_HEIGHT + 3,
        0,
        f"Score: {game.score}  Length: {len(game.snake)}  Controls: i/m/j/k, q=quit",
    )

    if game.game_over:
        stdscr.addstr(
            BOARD_HEIGHT // 2,
            max(2, (BOARD_WIDTH // 2) - 6),
            " GAME OVER ",
            curses.A_REVERSE,
        )
        stdscr.addstr(BOARD_HEIGHT + 4, 0, "Press r to restart or q to quit")

    stdscr.refresh()


def run(stdscr: curses.window) -> None:
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(0)

    game = SnakeGame()
    last_tick = time.monotonic()

    while True:
        key = stdscr.getch()

        if key == ord("q"):
            break

        if game.game_over and key == ord("r"):
            game = SnakeGame()
            last_tick = time.monotonic()

        if key in KEY_TO_DIRECTION and not game.game_over:
            game.turn(KEY_TO_DIRECTION[key])

        now = time.monotonic()
        if now - last_tick >= FRAME_DELAY:
            game.tick()
            last_tick = now

        draw(stdscr, game)
        time.sleep(0.01)


def main() -> None:
    curses.wrapper(run)


if __name__ == "__main__":
    main()
