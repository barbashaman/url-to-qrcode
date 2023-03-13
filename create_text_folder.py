import os
import re
import argparse
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter


class FileParser:
    def __init__(self, input_file, output_folder):
        self.input_file = input_file
        self.output_folder = output_folder
        self.section = None
        self.description = None
        self.url = None
        self.regex_section = re.compile(r'^P\d+')
        self.regex_description = re.compile(r'^\d+\.\s')
        self.regex_url = re.compile(r'^(http(s)?://|www\.)\S+')

    def parse_file(self):
        with open(self.input_file, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if self.regex_section.match(line):
                    self._create_section(line)
                elif self.regex_description.match(line):
                    self._create_description(line)
                elif self.regex_url.match(line):
                    self._create_url(line)

    def _create_section(self, line):
        self.section = line
        self.description = None
        self.url = None

    def _create_description(self, line):
        self.description = line
        self.url = None

    def _create_url(self, line):
        self.url = line
        self._save_to_file()

    def _sanitize_filename(self,section,description):
        replacements = [
            (" ", ""),
            (".",""),
            (" ","")
        ]
        
        for old, new in replacements:
            section.replace(old,new)
            description.replace(old,new)
        
        return section +"_"+ re.sub(r'[^\w\s-]', '', description).strip() + '.txt'

    def _save_to_file(self):
        if not all((self.section, self.description, self.url)):
            return

        section_folder = os.path.join(self.output_folder, self.section)
        if not os.path.exists(section_folder):
            os.makedirs(section_folder)

        filename = self._sanitize_filename(self.section, self.description)
        print(f"the file name is:{filename}" )
        file_path = os.path.join(section_folder, filename)

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(f"{self.description}\n{self.url}\n")    


def main():
    input_file = prompt("Enter input file path: ")
    output_folder = prompt("Enter output folder path: ")
    completer = WordCompleter(['parse'])

    while True:
        action = prompt('Enter action (parse or exit): ', completer=completer)
        if action == 'exit':
            break
        elif action == 'parse':
            file_parser = FileParser(input_file, output_folder)
            file_parser.parse_file()
            print('Parsing complete!')

if __name__ == '__main__':
    main()
