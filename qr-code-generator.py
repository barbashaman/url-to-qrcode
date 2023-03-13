import os
import re
import qrcode
import qrcode.image.svg
import datetime
from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter
from pathlib import Path

class QRCodeGenerator:
    def __init__(self, url, input_file_name, method='basic'):
        self.url = url
        self.qr = qrcode
        self.input_file_name = input_file_name
        if method == 'basic':
            # Simple factory, just a set of rects.
            self.factory = qrcode.image.svg.SvgImage
        elif method == 'fragment':
            # Fragment factory (also just a set of rects)
            self.factory = qrcode.image.svg.SvgFragmentImage
        elif method == 'path':
            # Combined path factory, fixes white space that may occur when zooming
            self.factory = qrcode.image.svg.SvgPathImage

    def generate(self):
        img = self.qr.make(self.url, image_factory=self.factory)
        return img

    def get_svg_filename(self):
        
        return f"{self.input_file_name}.svg"

    def save(self, folder):
        if not os.path.exists(folder):
            os.makedirs(folder)
        filename = os.path.join(folder, self.get_svg_filename())
        img = self.generate()
        img.save(filename)
        print(f"QR code for {self.url} saved to {filename}")

class QRCodeBatchGenerator:
    def __init__(self, urls, input_file_name,folder, method):
        self.input_file_name = input_file_name
        self.urls = urls
        self.folder = folder
        self.method = method

    def generate_qrcodes(self):
        for url in self.urls:
            generator = QRCodeGenerator(url, self.input_file_name, method=self.method)
            generator.save(self.folder)

class QRCodeGeneratorMenu:
    def __init__(self):
        print("QR Code Generator")
    
    def prompt_generic_confirmation(self):
        self.confirmation = input("Do you want to continue? (y/n): ")
        while self.confirmation.lower() not in ['y', 'n']:
            self.confirmation = input("Please enter 'y' or 'n': ")
        return self.confirmation.lower() == 'y'
    
    def prompt_for_confirmation(self):
        
        confirmation = input("Generate QR codes for all URLs in input folder? (y/n): ")
        while confirmation.lower() not in ['y', 'n']:
            confirmation = input("Please enter 'y' or 'n': ")
        return confirmation.lower() == 'y'
    
    def prompt_file_found(self,file):
        print(f"FILE FOUND: {file}")
        self.prompt_generic_confirmation()
    
    def read_files_from_input_folder(self):
        files = []
        for dirpath, _, filenames in os.walk(self.input_folder):
            for filename in filenames:
                if filename.endswith('.txt'):
                    files.append(os.path.join(dirpath, filename))
        return files
    
    def read_urls_from_file(self, file_path):
        urls = []
        with open(file_path, 'r') as f:
            for line in f:
                matches = re.findall(r'(https?://\S+)', line)
                urls.extend(matches)
        return urls
      
    def prompt_for_input_folder(self):
        input_folder = prompt("Enter the path to the input folder: ", completer=PathCompleter())
        while not os.path.isdir(input_folder):
            print("Invalid input folder path.")
            input_folder = prompt("Enter the path to the input folder: ", completer=PathCompleter())
        return input_folder
    
    def search_files_from_input_folder(self):
        files = list(Path(self.input_folder).rglob("*.[tT][xX][tT]"))
        print(f"\n{len(files)} files found in {self.input_folder}.\n")
        for file in files:
            print(file)
        print("")
        
    def prompt_for_files_in_folder(self):
        self.search_files_from_input_folder()
        

    def prompt_for_output_folder(self):
        output_folder = input("Enter the path to the output folder: ")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        while not os.path.isdir(output_folder):
            print("Invalid output folder path.")
            output_folder = input("Enter the path to the output folder: ")
        return output_folder

    def prompt_found_urls(self):
        for file_name in self.files:
            urls = self.read_urls_from_file(file_path=file_name)
            print(f"\n{len(urls)} URLs detected in file in {file_name}.\n")
            for url in urls:
                print(url)
            print("")
    
    def prompt_urls_in_file(self, file,urls):
        print("URLS IN FILE:\n")
        print(f"File Name:{file} \n")
        for url in urls:
            print(f"Found URL: {url} \n")
    
    def generate_qrcodes_for_urls(self):
        for file_path in self.files:
            input_file_name = os.path.basename(file_path).split('.')[0]
            urls = self.read_urls_from_file(file_path)
            self.prompt_urls_in_file(input_file_name,urls)
            
            batch_generator = QRCodeBatchGenerator(urls, input_file_name, self.output_folder, self.method)
            batch_generator.generate_qrcodes()
        print("\nQR codes generated successfully.\n")

    def prompt_for_factory_method(self):
        method = input("Generate QR codes using what factory method? (basic/fragment/path): ")
        while method.lower() not in ['basic', 'fragment','path' ]:
            method = input("Please enter 'basic', 'fragment' or 'path': ")
        return method.lower()

    def confirm_qrcode_generation(self, confirmation):
        if confirmation:
            self.method = self.prompt_for_factory_method()
            self.generate_qrcodes_for_urls()
        else:
            print("\nOperation cancelled.\n")

def main():
    menu = QRCodeGeneratorMenu()
    menu.input_folder = menu.prompt_for_input_folder()
    
    menu.prompt_for_files_in_folder()
    
    menu.output_folder = menu.prompt_for_output_folder()
    
    menu.files = menu.read_files_from_input_folder()
    
    # menu.prompt_found_urls()
    
    menu.confirm_qrcode_generation(menu.prompt_for_confirmation())

if __name__ == '__main__':
    main()