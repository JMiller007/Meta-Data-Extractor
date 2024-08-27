import tkinter as tk
from tkinter import filedialog, Text, messagebox
from PIL import Image
from PIL.ExifTags import TAGS
import mutagen
import exifread
import os
import PyPDF2
import docx
import chardet

root = tk.Tk()
root.title("Metadata Extractor")
root.geometry("600x500")

def extract_metadata(file_path):
    metadata = {}
    
    # Extract image metadata using Pillow and ExifRead
    if file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff')):
        try:
            with Image.open(file_path) as img:
                exif_data = img._getexif()
                if exif_data:
                    metadata['Pillow EXIF'] = {TAGS.get(tag): value for tag, value in exif_data.items()}
                with open(file_path, 'rb') as f:
                    exif_tags = exifread.process_file(f)
                    metadata['ExifRead'] = {tag: str(exif_tags[tag]) for tag in exif_tags}
        except Exception as e:
            metadata['Error'] = str(e)
    
    # Extract audio metadata using mutagen
    elif file_path.lower().endswith(('.mp3', '.flac', '.wav')):
        try:
            audio = mutagen.File(file_path)
            metadata['Mutagen'] = dict(audio)
        except Exception as e:
            metadata['Error'] = str(e)
    
    # Extract text file content or encoding details
    elif file_path.lower().endswith('.txt'):
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                encoding = chardet.detect(raw_data)['encoding']
                text = raw_data.decode(encoding)
                metadata['Encoding'] = encoding
                metadata['Content'] = text[:1000]  # Display the first 1000 characters
        except Exception as e:
            metadata['Error'] = str(e)

    # Extract PDF metadata using PyPDF2
    elif file_path.lower().endswith('.pdf'):
        try:
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                pdf_info = pdf_reader.metadata
                metadata['PDF Metadata'] = {key: pdf_info[key] for key in pdf_info}
                metadata['Page Count'] = len(pdf_reader.pages)
        except Exception as e:
            metadata['Error'] = str(e)

    # Extract Word document metadata using python-docx
    elif file_path.lower().endswith('.docx'):
        try:
            doc = docx.Document(file_path)
            core_properties = doc.core_properties
            metadata['Word Metadata'] = {
                'Title': core_properties.title,
                'Author': core_properties.author,
                'Subject': core_properties.subject,
                'Keywords': core_properties.keywords,
                'Last Modified By': core_properties.last_modified_by,
                'Created': core_properties.created,
                'Last Printed': core_properties.last_printed,
                'Modified': core_properties.modified,
                'Revision': core_properties.revision,
            }
            # Extracting text content from the document
            metadata['Content'] = '\n'.join([para.text for para in doc.paragraphs][:1000])  # First 1000 characters
        except Exception as e:
            metadata['Error'] = str(e)

    # Handle unsupported file types
    else:
        metadata['Error'] = "Unsupported file type. Only image, audio, text, PDF, and Word files are supported."
    
    return metadata

def open_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        metadata = extract_metadata(file_path)
        display_metadata(metadata)

def display_metadata(metadata):
    output.delete(1.0, tk.END)  # Clear the output area
    if metadata:
        for category, data in metadata.items():
            output.insert(tk.END, f"{category}:\n")
            if isinstance(data, list):
                for line in data:
                    output.insert(tk.END, f"{line}\n")
            elif isinstance(data, dict):
                for key, value in data.items():
                    output.insert(tk.END, f"{key}: {value}\n")
            else:
                output.insert(tk.END, f"{data}\n")
            output.insert(tk.END, "\n")
    else:
        output.insert(tk.END, "No metadata found or unable to process the file.")

open_button = tk.Button(root, text="Open File", padx=10, pady=5, command=open_file)
open_button.pack()

output = Text(root, wrap=tk.WORD)
output.pack(expand=True, fill='both')

root.mainloop()
