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


def safe_addstr(stdscr: curses.window, y: int, x: int, text: str, attr: int = 0) -> None:
    max_y, max_x = stdscr.getmaxyx()
    if y < 0 or y >= max_y or x >= max_x:
        return

    if x < 0:
        text = text[-x:]
        x = 0

    if not text:
        return

    allowed = max_x - x
    if allowed <= 0:
        return

    clipped = text[:allowed]
    try:
        stdscr.addstr(y, x, clipped, attr)
    except curses.error:
        # 터미널 리사이즈 순간 발생할 수 있는 addstr 에러를 무시
        pass


def draw_too_small(stdscr: curses.window, max_y: int, max_x: int) -> None:
    required_y = BOARD_HEIGHT + 5
    required_x = BOARD_WIDTH + 2
    stdscr.erase()
    safe_addstr(stdscr, 0, 0, "Terminal window is too small for snakebyte.")
    safe_addstr(stdscr, 1, 0, f"Current: {max_x}x{max_y}, Required: {required_x}x{required_y}")
    safe_addstr(stdscr, 2, 0, "Resize terminal or reduce font size.")
    safe_addstr(stdscr, 3, 0, "Press q to quit.")
    stdscr.refresh()


def draw(stdscr: curses.window, game: SnakeGame) -> bool:
    stdscr.erase()
    max_y, max_x = stdscr.getmaxyx()

    required_y = BOARD_HEIGHT + 5
    required_x = BOARD_WIDTH + 2
    if max_y < required_y or max_x < required_x:
        draw_too_small(stdscr, max_y, max_x)
        return False

    # GR 느낌의 사각형 화면 테두리
    top = "+" + "-" * BOARD_WIDTH + "+"
    bottom = top
    safe_addstr(stdscr, 0, 0, top)
    for row in range(1, BOARD_HEIGHT + 1):
        safe_addstr(stdscr, row, 0, "|")
        safe_addstr(stdscr, row, BOARD_WIDTH + 1, "|")
    safe_addstr(stdscr, BOARD_HEIGHT + 1, 0, bottom)

    # 점(먹이)
    safe_addstr(stdscr, game.dot.y, game.dot.x, ".")

    # 뱀 머리/몸
    head = game.snake[0]
    safe_addstr(stdscr, head.y, head.x, "@")
    for segment in game.snake[1:]:
        safe_addstr(stdscr, segment.y, segment.x, "#")

    safe_addstr(
        stdscr,
        BOARD_HEIGHT + 3,
        0,
        f"Score: {game.score}  Length: {len(game.snake)}  Controls: i/m/j/k, q=quit",
    )

    if game.game_over:
        safe_addstr(
            stdscr,
            BOARD_HEIGHT // 2,
            max(2, (BOARD_WIDTH // 2) - 6),
            " GAME OVER ",
            curses.A_REVERSE,
        )
        safe_addstr(stdscr, BOARD_HEIGHT + 4, 0, "Press r to restart or q to quit")

    stdscr.refresh()
    return True


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

        rendered = draw(stdscr, game)

        now = time.monotonic()
        if rendered and now - last_tick >= FRAME_DELAY:
            game.tick()
            last_tick = now

        time.sleep(0.01)


def main() -> None:
    curses.wrapper(run)


if __name__ == "__main__":
    main()
