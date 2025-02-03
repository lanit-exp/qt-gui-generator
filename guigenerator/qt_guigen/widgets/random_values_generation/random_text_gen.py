# -*- coding: utf-8 -*-

from abc import ABC
from enum import Enum
from random import choice, sample, randint, random
from string import punctuation, whitespace
from typing import Dict, Callable, List

from guigenerator.http_requests import FishTextWebsiteHttpRequest
from guigenerator.utils import Utils


class TextGenerationStrategy(Enum):
    RAND_CHARS = "rand_chars"
    RAND_WORDS = "rand_words"


# Facade for different RandTextMixin strategies

class RandomTextGeneration(object):
    def __init__(self, default_strategy: TextGenerationStrategy):
        self.__default_strat = default_strategy
        self.__gen_engine = self.__init_engine(default_strategy)

    def __init_engine(self, strat: TextGenerationStrategy) -> 'RandTextMixin':
        if strat == TextGenerationStrategy.RAND_WORDS:
            return RandTextFishWebsite()
        elif strat == TextGenerationStrategy.RAND_CHARS:
            return RandTextChars()
        else:
            RuntimeError("Shouldn't come here")

    def gen_random_str_of_words(self, min_words: int, max_words: int,
                                strategy: TextGenerationStrategy = None):
        gen_engine = self.__apply_method_strategy(strategy)
        words_count = randint(min_words, max_words)
        words = [gen_engine.get_word() + " " for _ in range(words_count - 1)]
        words.append(gen_engine.get_word())

        n = randint(3, 7)
        new_lines_count = len(words) // n
        while new_lines_count > 0:
            pos = randint(0, len(words) - 1)
            if words[pos] and words[pos][-1] == " ":
                words[pos] = words[pos].strip() + "\n"
                new_lines_count -= 1

        return "".join(words)

    def gen_random_str_of_words_starting_with_letter(
            self,
            min_words: int,
            max_words: int,
            letter: str,
            strategy: TextGenerationStrategy = None):
        gen_engine = self.__apply_method_strategy(strategy)
        words_count = randint(min_words, max_words)
        letter_word = gen_engine.get_word_staring_with_letter(letter)
        words = [letter_word] \
                + [gen_engine.get_word() for _ in range(words_count - 1)]
        return " ".join(words)

    def gen_random_paragraph(self,
                             strategy: TextGenerationStrategy = None) -> str:
        gen_engine = self.__apply_method_strategy(strategy)
        return gen_engine.get_paragraph()

    def gen_random_sentence(self,
                            strategy: TextGenerationStrategy = None) -> str:
        gen_engine = self.__apply_method_strategy(strategy)
        return gen_engine.get_sentence()

    def gen_random_title(self, strategy: TextGenerationStrategy = None) -> str:
        gen_engine = self.__apply_method_strategy(strategy)
        return gen_engine.get_title()

    def gen_random_html_doc(self, text_blocks_count: int = 5) -> str:
        def _gen_title() -> str:
            h_type = randint(1, 3)
            title_text = self.gen_random_title()
            return f"<h{h_type}>{title_text}</h{h_type}"

        def _gen_paragraph() -> str:
            return f"<p>{self.gen_random_paragraph()}</p>"

        def _gen_href() -> str:
            href_text = self.gen_random_sentence()
            return f'<a href="https://schoolsw3.com/html">{href_text}</a>'

        def _gen_list_item() -> str:
            list_item_text = self.gen_random_str_of_words(1, 3)
            return f"<li> {list_item_text} \n</li>"

        def _gen_ulist() -> str:
            n_list_items = randint(2, 5)
            return '\n'.join([_gen_list_item() for _ in range(n_list_items)])

        def try_gen_text_sub_block(possibility: float, gen_func: Callable,
                                   gen_text_list: List[str]):
            if random() <= possibility:
                gen_text_list.append(gen_func())

        if text_blocks_count < 0:
            raise RuntimeError("text_block_count must NOT be negative")

        text_list = []
        while (text_blocks_count):
            try_gen_text_sub_block(0.5, _gen_title, text_list)
            try_gen_text_sub_block(1, _gen_paragraph, text_list)
            try_gen_text_sub_block(0.5, _gen_href, text_list)
            try_gen_text_sub_block(0.5, _gen_paragraph, text_list)
            try_gen_text_sub_block(0.5, _gen_ulist, text_list)
            text_blocks_count -= 1

        return "\n".join(text_list)

    def get_possible_starting_letters(self,
                                      strategy: TextGenerationStrategy =
                                      None) \
            -> List[str]:
        gen_engine = self.__apply_method_strategy(strategy)
        return gen_engine.get_possible_starting_letters()

    def __apply_method_strategy(self, strategy):
        if strategy is not None \
                and strategy != self.__default_strat:
            gen_engine = self.__init_engine(strategy)
        else:
            gen_engine = self.__gen_engine
        return gen_engine


class RandTextMixin(ABC):
    def get_word(self) -> str:
        pass

    def get_sentence(self) -> str:
        pass

    def get_title(self) -> str:
        pass

    def get_paragraph(self) -> str:
        pass

    def get_word_staring_with_letter(self, letter: str) -> str:
        pass

    def get_possible_starting_letters(self) -> List[str]:
        pass


class RandTextChars(RandTextMixin):
    __LTTRS \
        = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяAБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    __MIN_WORD_LEN, __MAX_WORD_LEN = 3, 10
    __MIN_WORDS_IN_SENTENCE, __MAX_WORDS_IN_SENTENCE = 1, 10
    __MIN_SENTENCES_IN_PARAGRAPH, __MAX_SENTENCES_IN_PARAGRAPH = 1, 15

    def get_word(self) -> str:
        word_len = randint(self.__MIN_WORDS_IN_SENTENCE,
                           self.__MAX_WORDS_IN_SENTENCE)
        return ''.join(sample(self.__LTTRS, word_len))

    def get_sentence(self) -> str:
        sentence_length = randint(self.__MIN_WORD_LEN, self.__MAX_WORD_LEN)
        words = [self.get_word() for _ in range(sentence_length)]
        return ' '.join(words)

    def get_title(self) -> str:
        return self.get_sentence().capitalize()

    def get_paragraph(self) -> str:
        sentences_count = randint(self.__MIN_SENTENCES_IN_PARAGRAPH,
                                  self.__MAX_SENTENCES_IN_PARAGRAPH)
        sentences = [self.get_sentence() for _ in range(sentences_count)]
        return '\n'.join(sentences)

    def get_word_staring_with_letter(self, letter: str) -> str:
        word = self.get_word()
        return letter + word

    def get_possible_starting_letters(self) -> List[str]:
        return self.__LTTRS.split(sep="")


class RandTextFishWebsite(RandTextMixin):
    __sentences: List[str] = []
    __titles: List[str] = []
    __paragraphs: List[str] = []
    __words: List[str] = []
    __same_first_letter_words: Dict[str, List[str]] = {}

    REQUEST_COUNT = 1
    LOCAL_WORDS_DICT_PATH = Utils.RESOURCES_DIR / "words.json"

    def __init__(self):
        website = FishTextWebsiteHttpRequest()
        self.__init_words_from_local_file()
        self.__init_text_from_request(website)
        self.__init_words_from_request(website)

    def __init_words_from_local_file(self):
        word_lists = Utils.read_from_json(str(self.LOCAL_WORDS_DICT_PATH),
                                          None)
        for letter, joint_words in word_lists.items():
            splitted_words = joint_words.split(",")
            self.__same_first_letter_words[letter] = splitted_words
            self.__words.extend(splitted_words)

    def __init_text_from_request(self, website: FishTextWebsiteHttpRequest):
        for _ in range(self.REQUEST_COUNT):
            self.__sentences.extend(website.request_sentences(100))
            self.__titles.extend(website.request_titles(100))
            self.__paragraphs.extend(website.request_paragraphs(100))

    def __init_words_from_request(self, website: FishTextWebsiteHttpRequest):
        sentences = website.request_sentences(100)
        for sentence in sentences:
            words = sentence.split()
            for word in words:
                self.__words.append(word.strip(punctuation).strip(whitespace))

    def get_word(self) -> str:
        return choice(self.__words)

    def get_sentence(self) -> str:
        return choice(self.__sentences)

    def get_title(self) -> str:
        return choice(self.__titles)

    def get_paragraph(self) -> str:
        return choice(self.__paragraphs)

    def get_word_staring_with_letter(cls, letter: str) -> str:
        if letter not in cls.__same_first_letter_words.keys():
            raise RuntimeError("No words starting with such letter")
        return choice(cls.__same_first_letter_words[letter])

    def get_possible_starting_letters(cls) -> List[str]:
        return list(cls.__same_first_letter_words.keys())
