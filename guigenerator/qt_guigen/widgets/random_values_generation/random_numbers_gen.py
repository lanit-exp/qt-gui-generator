from random import sample, randint
from string import digits
from typing import Tuple

from guigenerator.dto.tree_dto import NodeDto
from guigenerator.qt_guigen.widgets.widget_names import WidgetNames


class RandNumbersGeneration(object):
    @classmethod
    def generate_widget_size_values_for_grid(cls, node: NodeDto, max_w: int,
                                             max_h: int, side_size: int = 3) \
            -> Tuple[int, int]:

        grid_children \
            = [child for child in node.children if
               WidgetNames(child.name).is_central_widget_child]
        widgets_count_in_1st_grid = side_size ** 2

        # calculate min width and min height of 1st 3x3 grid (by default)
        # ----------------------------------------------
        row_widths = [0] * side_size
        col_heights = [0] * side_size
        for i in range(min(widgets_count_in_1st_grid, len(grid_children))):
            child = grid_children[i]
            if child.name == WidgetNames.GROUP_BOX:
                w, h = cls.__generate_groupbox_size_values(child)
            else:
                w, h = WidgetNames(child.name).min_width, WidgetNames(
                    child.name).min_height

            row_widths[i // side_size] += w
            col_heights[i % side_size] += h

        width_1st = max(row_widths)
        height_1st = max(col_heights)

        # calculate min width and min height of 2nd additional grid
        # ----------------------------------------------------
        width_2nd = 0
        height_2nd = 0
        if len(grid_children) > widgets_count_in_1st_grid:
            from math import ceil
            additional_col_count = int(ceil(
                (len(grid_children) - widgets_count_in_1st_grid) / side_size))
            row_widths = [0] * side_size
            col_heights = [0] * additional_col_count
            for i in range(widgets_count_in_1st_grid, len(grid_children)):
                child = grid_children[i]
                if child.name == WidgetNames.GROUP_BOX:
                    w, h = cls.__generate_groupbox_size_values(child)
                else:
                    w, h = WidgetNames(child.name).min_width, WidgetNames(
                        child.name).min_height
                row_widths[(i - widgets_count_in_1st_grid) % side_size] += w
                col_heights[(i - widgets_count_in_1st_grid) // side_size] += h

            width_2nd = max(row_widths)
            height_2nd = max(col_heights)

        # calculate final width and height
        # -----------------------------------------------------------------------------
        width = min(max_w, width_1st + width_2nd)
        height = min(max_h, max(height_1st, height_2nd))

        return width, height

    @classmethod
    def __generate_groupbox_size_values(cls, node: NodeDto) -> Tuple[int, int]:
        width = 0
        height = 0
        for i, child in enumerate(node.children):
            child_width, child_height = WidgetNames(
                child.name).min_width, WidgetNames(child.name).min_height
            width += child_width
            height = max(height, child_height)

        return width, height

    @classmethod
    def generate_random_number(cls, length: int) -> str:
        return ''.join(sample(digits, length))

    @classmethod
    def generate_random_line_of_numbers(cls, min_number_of_words: int,
                                        max_number_of_words: int,
                                        min_word_len: int,
                                        max_word_len: int) -> str:

        number_of_words = randint(min_number_of_words, max_number_of_words)
        words = [
            cls.generate_random_number(randint(min_word_len, max_word_len))
            for _ in range(number_of_words)]
        return ' '.join(words)