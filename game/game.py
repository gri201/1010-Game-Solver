from __future__ import print_function

import os
import time
import json
import numpy as np


class Game:
    def __init__(self):
        self.field = np.zeros((10, 10), dtype=int)
        self.figures = [
            np.array([[1, 1, 1, 1, 1]], dtype=int),
            np.array([[1], [1], [1], [1], [1]], dtype=int),
            np.array([[1, 1, 1, 1]], dtype=int),
            np.array([[1], [1], [1], [1]], dtype=int),
            np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]], dtype=int),
            np.array([[1, 0, 0], [1, 0, 0], [1, 1, 1]], dtype=int),
            np.array([[0, 0, 1], [0, 0, 1], [1, 1, 1]], dtype=int),
            np.array([[1, 1, 1], [0, 0, 1], [0, 0, 1]], dtype=int),
            np.array([[1, 1, 1], [1, 0, 0], [1, 0, 0]], dtype=int),
            np.array([[1, 1, 1]], dtype=int),
            np.array([[1], [1], [1]], dtype=int),
            np.array([[1, 1], [1, 1]], dtype=int),
            np.array([[1, 0], [1, 1]], dtype=int),
            np.array([[0, 1], [1, 1]], dtype=int),
            np.array([[1, 1], [0, 1]], dtype=int),
            np.array([[1, 1], [1, 0]], dtype=int),
            np.array([[1], [1]], dtype=int),
            np.array([[1, 1]], dtype=int),
            np.array([[1]], dtype=int)
        ]
        self.score = 0
        self.settings = {}

        self.load_settings()

    def load_settings(self, filename='../settings.json'):
        with open(filename) as f:
            settings = json.loads(f.read())
            print(type(settings), settings)
            self.settings = settings

    def show_field(self):
        os.system('clear')
        print('-' * 4, 'YOUR SCORE: {}'.format(self.score), '-' * 4)
        print(' ', '_ ' * 10)
        for i in range(self.field.shape[0]):
            print('|', end='')
            for j in range(self.field.shape[1]):
                if self.field[i, j] == 1:
                    print('*', end=' ')
                else:
                    print(' ', end=' ')
            print(' |')
        print(' ', '_ ' * 10)

    def show_figures(self, figs):
        for f, fig in enumerate(figs):
            print('Figure {}:'.format(f))
            for i in range(fig.shape[0]):
                for j in range(fig.shape[1]):
                    if fig[i, j] == 1:
                        print('*', end=' ')
                    else:
                        print(' ', end=' ')
                print('')

    def show_game_over(self):
        os.system('clear')
        print(
            '''
             #####     #    #     # #######    ####### #     # ####### ######  
            #     #   # #   ##   ## #          #     # #     # #       #     # 
            #        #   #  # # # # #          #     # #     # #       #     # 
            #  #### #     # #  #  # #####      #     # #     # #####   ######  
            #     # ####### #     # #          #     #  #   #  #       #   #   
            #     # #     # #     # #          #     #   # #   #       #    #  
             #####  #     # #     # #######    #######    #    ####### #     # 
            '''
        )
        print(' ' * 35, 'YOUR SCORE: {}'.format(self.score), '' * 35, '\n')

    def get_next_figures(self, count=None):
        if not count:
            count = self.settings['default_figures_count']

        return np.random.choice(self.figures, count)

    def check_ready_lines(self, field):
        ready_rows_idx = []
        ready_cols_idx = []

        for i, row in enumerate(field):
            if row.sum() == 10:
                ready_rows_idx.append(i)
        for i, col in enumerate(field.T):
            if col.sum() == 10:
                ready_cols_idx.append(i)

        return ready_rows_idx, ready_cols_idx

    def clean_ready_lines(self, rows_idx, cols_idx):
        for row in rows_idx:
            self.field[row, :] = 0
        for col in cols_idx:
            self.field[:, col] = 0

        self.score = self.score + (len(rows_idx) + len(cols_idx)) * 10

    def count_neighbor_pixels(self, field, fig, x, y):
        count = 0
        local_coordinates = set()
        global_coordinates = set()

        for i in range(fig.shape[0]):
            for j in range(fig.shape[1]):
                if fig[i, j] == 1:
                    local_coordinates.add((i - 1, j))
                    local_coordinates.add((i + 1, j))
                    local_coordinates.add((i, j + 1))
                    local_coordinates.add((i, j - 1))

        for i in range(fig.shape[0]):
            for j in range(fig.shape[1]):
                if fig[i, j] == 1:
                    local_coordinates.discard((i, j))

        for coordinate in local_coordinates:
            global_coordinates.add((coordinate[0] + x, coordinate[1] + y))

        for pixel in global_coordinates:
            if pixel[0] < 0 or pixel[0] > 9 or pixel[1] < 0 or pixel[1] > 9:
                count += 1
            elif field[pixel[0], pixel[1]] == 1:
                count += 1

        return count

    def fit_figure(self, fig, pos_x, pos_y):
        d_x = fig.shape[0]
        d_y = fig.shape[1]

        if pos_x + d_x > 10 or pos_y + d_y > 10:
            return None

        tmp_field = self.field.copy()
        tmp_field[pos_x:pos_x + d_x, pos_y:pos_y + d_y] += fig

        if tmp_field.max() > 1:
            return None

        neighbors_count = self.count_neighbor_pixels(tmp_field, fig, pos_x, pos_y)
        ready_lines = self.check_ready_lines(tmp_field)

        return tmp_field, neighbors_count, ready_lines

    def place_figure(self, fig, pos_x, pos_y):
        try:
            new_field, neighbors_count, ready_lines = self.fit_figure(fig, pos_x, pos_y)
        except:
            return False
        else:
            self.field = new_field
            self.score += fig.sum()
            self.clean_ready_lines(ready_lines[0], ready_lines[1])

            return True

    def check_game_over(self, figs):
        for fig in figs:
            for x in range(self.field.shape[0]):
                for y in range(self.field.shape[1]):
                    if self.fit_figure(fig, x, y) is not None:
                        return False
        return True

    def choose_best_move(self, next_figures):
        max_neighbors = 0
        max_ready_lines = 0
        best_fig = 0
        best_x = 0
        best_y = 0

        for i, fig in enumerate(next_figures):
            for x in range(self.field.shape[0]):
                for y in range(self.field.shape[1]):
                    try:
                        tmp_field, neighbors_count, ready_lines = self.fit_figure(fig, x, y)
                    except:
                        pass
                    else:
                        count_ready_lines = len(ready_lines[0]) +  len(ready_lines[1])
                        if count_ready_lines > max_ready_lines:
                            best_fig = i
                            best_x = x
                            best_y = y
                            max_ready_lines = count_ready_lines
                            max_neighbors = neighbors_count
                        elif count_ready_lines == max_ready_lines:
                            if neighbors_count > max_neighbors:
                                best_fig = i
                                best_x = x
                                best_y = y
                                max_ready_lines = count_ready_lines
                                max_neighbors = neighbors_count

        return best_fig, best_x, best_y

    def process(self):
        while True:
            next_figures = self.get_next_figures()

            while len(next_figures) > 0:
                if self.check_game_over(next_figures):
                    if self.settings['show_game_over']:
                        self.show_game_over()
                    return False

                if self.settings['show_field']:
                    self.show_field()
                if self.settings['show_figures']:
                    self.show_figures(next_figures)

                if self.settings['mode'] == 'MANUAL':
                    chosen_figure = int(input('Figure No.: '))
                    y = int(input('x: '))
                    x = int(input('y: '))
                elif self.settings['mode'] == 'RANDOM':
                    chosen_figure = np.random.randint(len(next_figures))
                    x = np.random.randint(10)
                    y = np.random.randint(10)
                elif self.settings['mode'] == 'SMART':
                    chosen_figure, x, y = self.choose_best_move(next_figures)

                try:
                    self.place_figure(next_figures[chosen_figure], x, y)
                except:
                    pass
                else:
                    next_figures = [fig for i, fig in enumerate(next_figures) if i != chosen_figure]
                    time.sleep(self.settings['latency'])


if __name__ == '__main__':
    g = Game()
    g.process()

