#!/usr/bin/python3

from pyglet import shapes
import pyglet
import psutil

import io
import sys
import base64


# Config
WIDTH = 1000  # width of the window
HEIGHT = 200  # height of the window
MIN_UPPER_VALUE = 1  # upper value of horizontal lines will not go below this (must be > 0)
HOR_LINE_NUM = 6  # number of horizontal lines
REFRESH_INTERVAL = 1  # refresh rate in seconds

# GUI Colors (Red, Green, Blue[, Alpha])
C_BACKGROUND = (60, 60, 60)
C_DOWNLOAD = (255, 90, 90)
C_UPLOAD = (10, 200, 35)
C_OVERLAP = (220, 220, 50)
C_CURSOR = (255, 255, 255)
C_T_CURSOR = (220, 180, 220, 255)
C_HORIZON = (120, 230, 230)
C_T_HORIZON = (120, 230, 230, 255)

# 24x24 png icon blob
_ICON_BLOB = \
    'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAN1wAADdcBQiibeAAAABl0RVh0U29mdHdh' \
    'cmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAAOdEVYdFRpdGxlAFRlcm1pbmFs1fugkQAAABd0RVh0QXV0aG9yAExhcG8gQ2FsYW1hbmRyZWnfkRoq' \
    'AAAAKXRFWHREZXNjcmlwdGlvbgBCYXNlZCBvZiBKYWt1YiBTdGVpbmVyJ3Mgd29yayfTJ5kAAAWsSURBVFjD7ZfLb1xJFcZ/p6pud9/b7rZju91+' \
    'xYwDSZxkMiMyPFYjSDSwQBFoWLJAGiQ2s+Iv4J9AQoIRSCzYDIw0KxBiUBYskIJmYJIJTIhoZ9xO/Gy33U6/7r1VxaIfbmcMO3s2lHR065Zu1fnu' \
    '951zqkq893yWTfEZt/8DMABv/PD739JK/8JZO3vaDrXSO3j35ltv/eq3QwBGm59c/Pzl2ZlS+dT/eLe2U3r48B8/BY4A2MTOf+O1b5LJZNBao7XG' \
    'GIMx5tj76HNgIoK1ljRNsdYe6580liQJHz24VzomgfcOgK/dunXqDNx5772hvyEA5x2DehCWn7F+vwXA4vWI9fstROD8SxG1JzEi8OVXX2Rcluh2' \
    'OozNw1//9E+q61UWrkZQn+TKylXys561B3Xa7TbjS1D5W43E9fw4545ngXN+CGDgXGnYeNjChGAi2Flr89qP5rh8c5y0kUWMQwJPbb3NQatGEArb' \
    'qx0uX7uIBI7dagu0A3FsfNwaOnXO4ZznBAl6gzrTcy4alBZEgyjIFTQv354kyCpad0OcSvA6oR03SFWbIIL52QWiQpZOpwvaoowDY5HAIsZBqvDe' \
    'H5NghIHewOdu5DGhEITC0hcjghAyebjx3WnykwHlyzkWVgo4FeNUjCk3CCIIIuErt1bwOsZJl6kLCqtixFjKKwFoS+9n/TEG1ICWAQNblRYmByaE' \
    'nU96EmSLiiu3JnCpo7RYpLZ5iJUuVrqsfvyUIBTmz8/SbKRceDXE65ittQZexVgds1Fp4HUydPqpGOjR0tckN2J9JqJJxfxKnod/rlMoRljdIZU2' \
    'z+I9yCRk8sLi8hzXbxdYeiVDajo9gCrG0us7FXPk6wQGBoOL1yNMTjA5YeFaRCYv3Pj2DC713PvDFplswPiiJ6XDYbzH/JWI6dIk+QnN+VeymKLF' \
    'S5uJJUhoY1VM6ZLBm2REgufT0NmhBLtrbUwOlIHakxaZouLq16dY/eCAJLbY1GODLqlqkaomBzuwND/H9dtFEtdBsjGJ6lCvdrASk9JlYzXFZIX0' \
    'v0lgR4JQ5yBXVIQFRTiuKX8hT34qw0d3tkB7Os2E4nlPrA7IjgvnSnnGZhTTlxR/v7OG1TGp6uAzXch2CSJHrqjQOU4MwmOVEGDppTFe//ElRI6q' \
    'V2O3S3hO6HQ8jYMmE0vC+AvC62+8TFblEYTdrTqb69tcJOSFr2b50neWh/M98PMffEh38P6pSmiPAmOz8oxfvvkhOgM6ABWA6H6NyAm17Trl5TFe' \
    'vFmmWUv43a/fJ4ktSZIiKJJ0jms3Z9h53OSPP6sQtxw2Bmv/Zxp6/KAQGcHjjkw8onvSmAzsbx+SKxhK5/M8en+DlC5eJSjjMVlIY0dYNPzr7i7W' \
    '2uE62siJQThMw75/yhdClOkFYWk5Qge96lhaClFZz36thQkUNnVsP20wtRAO03VqMUunlZLGjm4rRvrrzCz31hxK4p+PgZE03H3SxmR6E+ubbUy2' \
    'J0Vjr43JCKm1OOd4WtlDZRzNVpsgBJvAYb1LpxnT3O+yt9lGafAG9p62Ec2JhWi4Gw6aqIHJcE8QDcoIKgBlPM2DLp882sHkwDvBJh4EvPUc7ses' \
    'P9gDHEqDU4IojyhOlkBEZHQ3nF6IwAvihXPlXh8vTExH4ASXeCr3trGJxWSEwrkIofd9oRhS+WCX+kabiVKE768zOR8hXo4FoUgPkgG0758HtNY8' \
    'encMGANgA4A8ABUAIgDuAzA5cswInzt2FPrP/Mg6Y2h9LA2NiKQGyDnXg/fuO++c+oloJA1DoGWAgrNu/+3fvF2em507dQDbO9t4758B40BsgGzl' \
    '36u/T9P0e6IkcwYMJI8rjx/09dkzQFKtVv9SrVYdkD2Du4gD6kBKL0tpAXeBtUFangGAFrAPpALk+nRkz+iq5oEEOARi6TtVgJzhldD3zf0HUIX2' \
    'plJ47ToAAAAASUVORK5CYII='


class MainWindow(pyglet.window.Window):
    def __init__(self, net_if):
        super().__init__(WIDTH, HEIGHT, f'Net Meter [{net_if}]')

        self.graph = [[0.0, 0.0] for _ in range(WIDTH)]
        self.batch = pyglet.graphics.Batch()
        self.upper_value = MIN_UPPER_VALUE
        self.shift = self.cursor = -1

        self.set_icon(pyglet.image.load('icon.png', file=io.BytesIO(base64.b64decode(_ICON_BLOB))))
        pyglet.gl.glClearColor(*[x / 255 for x in C_BACKGROUND], 1)

        kwargs = dict(x=0, y=0, x2=0, y2=0, width=1, batch=self.batch)
        self.dl_lines = [shapes.Line(color=C_DOWNLOAD, **kwargs) for _ in range(WIDTH)]
        self.ul_lines = [shapes.Line(color=C_UPLOAD, **kwargs) for _ in range(WIDTH)]
        self.ol_lines = [shapes.Line(color=C_OVERLAP, **kwargs) for _ in range(WIDTH)]
        self.cs_line = shapes.Line(color=C_CURSOR, **kwargs)
        self.cs_line.opacity = 120

        self.cursor_label = pyglet.text.Label(
            'Starting ...', font_size=8, batch=self.batch, color=C_T_CURSOR, bold=True,
            x=WIDTH / 2, anchor_x='center',
            y=HEIGHT - 10, anchor_y='center')

        self.horizontal_lines = []
        self.horizontal_labels = []
        for i in range(HOR_LINE_NUM):
            y = (HEIGHT - 20) * (i + 1) / HOR_LINE_NUM
            line = shapes.Line(0, y, WIDTH, y, width=1, color=C_HORIZON, batch=self.batch)
            line.opacity = 80
            self.horizontal_lines.append(line)

            label = pyglet.text.Label(
                human_bytes(0) + '/s', font_size=8, batch=self.batch, color=C_T_HORIZON,
                x=WIDTH - 5, anchor_x='right',
                y=y, anchor_y='top')
            self.horizontal_labels.append(label)

        self.net_if = net_if
        self.tx, self.rx = self.get_net_io()

    def on_draw(self):
        self.clear()
        self.batch.draw()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.cursor = x
        self.update_cursor_label(x)
        self.cs_line.position = (x, 0, x, HEIGHT - 20)

    def on_mouse_release(self, x, y, button, modifiers):
        self.cursor = -1
        self.cursor_label.x = WIDTH // 2
        self.cs_line.position = (0, 0, 0, 0)

    def get_net_io(self):
        net_io = psutil.net_io_counters(pernic=True)[self.net_if]
        return net_io.bytes_recv, net_io.bytes_sent

    def update_cursor_label(self, x, update_pos=True):
        if x < 0:
            x = 0
        elif x >= WIDTH:
            x = WIDTH - 1

        self.cursor_label.text = 'DL: {}/s, UL: {}/s'.format(
            *(human_bytes(y) for y in self.graph[(self.shift - x) % WIDTH])
        )

        if update_pos:
            self.cursor_label.x = x
            m = self.cursor_label.content_width // 2 + 5
            if x < m:
                self.cursor_label.x = m
            elif x > WIDTH - m:
                self.cursor_label.x = WIDTH - m

    def update_lines(self):
        for x in range(WIDTH):
            down, up = self.graph[(self.shift - x) % WIDTH]
            down_h = down / self.upper_value * (HEIGHT - 20)
            up_h = up / self.upper_value * (HEIGHT - 20)

            if down_h > up_h:
                self.dl_lines[x].position = (x, 0, x, down_h)
                self.ul_lines[x].position = (0, 0, 0, 0)
                self.ol_lines[x].position = (x, 0, x, up_h)
            elif down_h < up_h:
                self.dl_lines[x].position = (0, 0, 0, 0)
                self.ul_lines[x].position = (x, 0, x, up_h)
                self.ol_lines[x].position = (x, 0, x, down_h)
            else:
                self.dl_lines[x].position = (0, 0, 0, 0)
                self.ul_lines[x].position = (0, 0, 0, 0)
                self.ol_lines[x].position = (x, 0, x, down_h)

    def update_horizontal_labels(self):
        for i, label in enumerate(self.horizontal_labels):
            label.text = human_bytes(self.upper_value * (i + 1) / HOR_LINE_NUM) + '/s'

    def update(self, dt):
        self.shift += 1

        i = self.shift % WIDTH
        if any(x == self.upper_value for x in self.graph[i]):
            self.upper_value = max(
                max(
                    y for j, x in enumerate(self.graph) if j != i for y in x
                ), MIN_UPPER_VALUE
            )

        tx, rx = self.get_net_io()
        self.graph[i][0], self.graph[i][1] = (tx - self.tx) / dt, (rx - self.rx) / dt
        self.tx, self.rx = tx, rx

        self.upper_value = max(*self.graph[i], self.upper_value, MIN_UPPER_VALUE)

        self.update_lines()
        self.update_horizontal_labels()

        if self.cursor >= 0:
            self.update_cursor_label(self.cursor)
        else:
            self.update_cursor_label(0, False)


def human_bytes(n):
    for k, u in enumerate(['KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB']):
        if n < 1024 ** (k + 2):
            return '{:.2f} {}'.format(n / 1024 ** (k + 1), u)
    else:
        return '{:.2f} YiB'.format(n / 1024 ** 8)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print(f'Usage: {sys.argv[0]} NET_INTERFACE')
        print('NET_INTERFACE = Name of the network interface to monitor')
        exit(1)

    main = MainWindow(sys.argv[1])
    pyglet.clock.schedule_interval(main.update, REFRESH_INTERVAL)
    pyglet.app.run()
