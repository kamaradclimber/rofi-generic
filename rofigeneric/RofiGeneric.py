#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import fnmatch
import os
import shlex
import sys
from subprocess import run
from typing import List, Tuple

import configargparse
from xdg import BaseDirectory

from rofigeneric.Clipboarder import Clipboarder
from rofigeneric.Typer import Typer


class RofiGeneric:
    def __init__(self) -> None:
        self.args = self.parse_arguments()
        self.typer = Typer.best_option(self.args.typer)
        self.clipboarder = Clipboarder.best_option(self.args.clipboarder)
        self.active_window = self.typer.get_active_window()

        returncode, stdout = self.open_main_rofi_window()

        if returncode == 1:
            sys.exit()
        else:
            if 10 <= returncode <= 19:
                self.default_handle_recent_character(returncode - 9)
            else:
                # for now we assume stdout is a single line
                assert len(stdout.splitlines()) == 1

                output=stdout.split(self.args.seperator)[0]

                # TODO(g.seux): deal with history
                # self.save_characters_to_recent_file(characters)

                if returncode == 0:
                    self.default_handle(output)
                #elif returncode == 20:
                #    self.clipboarder.copy_characters_to_clipboard(characters)
                #elif returncode == 21:
                #    self.typer.type_characters(characters, self.active_window)
                #elif returncode == 22:
                #    self.clipboarder.copy_paste_characters(characters, self.active_window, self.typer)
                #elif returncode == 23:
                #    self.default_handle(self.get_codepoints(characters))
                #elif returncode == 24:
                #    self.clipboarder.copy_characters_to_clipboard(self.get_codepoints(characters))

    def parse_arguments(self) -> argparse.Namespace:
        parser = configargparse.ArgumentParser(
            description='Select, insert or copy Unicode characters using rofi.',
            default_config_files=[os.path.join(directory, 'rofigeneric.rc') for directory in
                                  BaseDirectory.xdg_config_dirs]
        )
        parser.add_argument('--version', action='version', version='rofi-generic 0.1.0')
        parser.add_argument(
            '--insert-with-clipboard',
            '-p',
            dest='insert_with_clipboard',
            action='store_true',
            help='Do not type the character directly, but copy it to the clipboard, insert it from '
                 'there and then restore the clipboard\'s original value '
        )
        parser.add_argument(
            '--copy-only',
            '-c',
            dest='copy_only',
            action='store_true',
            help='Only copy the character to the clipboard but do not insert it'
        )
        parser.add_argument(
            '--input-files',
            '-f',
            dest='files',
            action='store',
            default=[],
            nargs='+',
            metavar='FILE',
            help='Read text from files'
        )
        parser.add_argument(
            '--seperator',
            '-s',
            dest='seperator',
            action='store',
            default=" ",
            help='Text seperator'
        )
        parser.add_argument(
            '--prompt',
            '-r',
            dest='prompt',
            action='store',
            default='😀 ',
            help='Set rofi-generic\'s  prompt'
        )
        parser.add_argument(
            '--rofi-args',
            dest='rofi_args',
            action='store',
            default='',
            help='A string of arguments to give to rofi'
        )
        parser.add_argument(
            '--max-recent',
            dest='max_recent',
            action='store',
            type=int,
            default=10,
            help='Show at most this number of recently used words (cannot be larger than 10)'
        )
        parser.add_argument(
            '--clipboarder',
            dest='clipboarder',
            action='store',
            type=str,
            default=None,
            help='Choose the application to access the clipboard with'
        )
        parser.add_argument(
            '--typer',
            dest='typer',
            action='store',
            type=str,
            default=None,
            help='Choose the application to type with'
        )

        parsed_args = parser.parse_args()
        parsed_args.rofi_args = shlex.split(parsed_args.rofi_args)

        return parsed_args

    def read_input_files(self) -> str:
        entries = []

        for file_name in self.args.files:
            entries = entries + self.load_from_file(file_name)

        return entries

    def load_from_file(self, file_name: str) -> str:
        if os.path.isfile(file_name):
            actual_file_name = file_name
        else:
            raise FileNotFoundError(f"Couldn't find file {file_name}")

        with open(actual_file_name, "r") as file:
            return file.readlines()

    def load_all_characters(self) -> str:
        characters = ""

        directory = os.path.join(os.path.dirname(__file__), "data")
        for filename in os.listdir(directory):
            with open(os.path.join(directory, filename), "r") as file:
                characters = characters + file.read()
        return characters

    def load_recent_characters(self, max: int) -> List[str]:
        try:
            with open(os.path.join(BaseDirectory.xdg_data_home, 'rofi-generic', 'recent'), 'r') as file:
                return file.read().strip().split('\n')[:max]
        except FileNotFoundError:
            return []

    def format_recent_characters(self) -> str:
        pairings = [f'{(index + 1) % 10}: {character}' for index, character in
                    enumerate(self.load_recent_characters(self.args.max_recent))]

        return ' | '.join(pairings)

    def open_main_rofi_window(self) -> Tuple[int, str]:
        rofi_args = self.args.rofi_args
        lines = self.read_input_files()
        prompt = self.args.prompt

        parameters = [
            'rofi',
            '-dmenu',
            '-markup-rows',
            '-i',
            '-multi-select',
            '-p',
            prompt,
            '-kb-custom-11',
            'Alt+c',
            '-kb-custom-12',
            'Alt+t',
            '-kb-custom-13',
            'Alt+p',
            '-kb-custom-14',
            'Alt+u',
            '-kb-custom-15',
            'Alt+i',
            *rofi_args
        ]

        # TODO(g.seux): deal with recent selections
        #recent_characters = self.format_recent_characters()
        #if len(recent_characters) > 0:
        #    parameters.extend(['-mesg', recent_characters])

        rofi = run(
            parameters,
            input=''.join(lines),
            capture_output=True,
            encoding='utf-8'
        )
        return rofi.returncode, rofi.stdout

    def process_chosen_characters(
            self,
            chosen_characters: List[str]
    ) -> str:

        result = ""
        for line in chosen_characters:
            character = line.split(" ")[0]

            characters_with_skin_tone = ''
            for element in character:
                if element in self.skin_tone_selectable_emojis:
                    characters_with_skin_tone += self.select_skin_tone(element)
                else:
                    characters_with_skin_tone += element

            result += characters_with_skin_tone

        return result

    def save_characters_to_recent_file(self, characters: str):
        max_recent_from_conf = self.args.max_recent

        old_file_name = os.path.join(BaseDirectory.xdg_data_home, 'rofi-generic', 'recent')
        new_file_name = os.path.join(BaseDirectory.xdg_data_home, 'rofi-generic', 'recent_temp')

        max_recent = min(max_recent_from_conf, 10)

        os.makedirs(os.path.dirname(new_file_name), exist_ok=True)
        with open(new_file_name, 'w+') as new_file:
            new_file.write(characters + '\n')

            try:
                with open(old_file_name, 'r') as old_file:
                    index = 0
                    for line in old_file:
                        if characters == line.strip():
                            continue
                        if index == max_recent - 1:
                            break
                        new_file.write(line)
                        index = index + 1

                os.remove(old_file_name)
            except FileNotFoundError:
                pass

        os.rename(new_file_name, old_file_name)

    def append_to_favorites_file(self, characters: str):
        file_name = os.path.join(BaseDirectory.xdg_data_home, 'rofi-generic', 'favorites')

        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        with open(file_name, 'a+') as file:
            file.write(characters + '\n')

    def default_handle(self, output: str):
        if self.args.copy_only:
            self.clipboarder.copy_characters_to_clipboard(output)
        elif self.args.insert_with_clipboard:
            self.clipboarder.copy_paste_characters(output, self.active_window, self.typer)
        else:
            self.typer.type_characters(output, self.active_window)

    def default_handle_recent_character(self, position: int):
        recent_characters = self.load_recent_characters(position)

        self.default_handle(recent_characters[position - 1].strip())


def main():
    RofiGeneric()


if __name__ == "__main__":
    main()
