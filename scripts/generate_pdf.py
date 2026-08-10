import os
import re
from pathlib import Path
from PIL import Image

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    '''
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', text)]

def generate_pdf():
    print("Collecting downloaded images...")
    
    # Collect all jpgs
    input_dir = Path("input")
    image_paths = []
    
    for ext in ["*.jpg", "*.jpeg", "*.png"]:
        image_paths.extend(list(input_dir.rglob(ext)))
        
    if not image_paths:
        print("No images found.")
        return
        
    # Sort files naturally so NoteBook1 comes before NoteBook2, page2 comes before page10, etc.
    image_paths_str = [str(p) for p in image_paths]
    image_paths_str.sort(key=natural_keys)
    
    print(f"Found {len(image_paths_str)} images. Preparing PDF generation...")
    
    # Open images and convert to RGB (required for PDF)
    images = []
    first_image = None
    
    for i, p in enumerate(image_paths_str):
        if i % 50 == 0:
            print(f"Processing image {i+1}/{len(image_paths_str)}...")
            
        try:
            img = Image.open(p)
            if img.mode != 'RGB':
                img = img.convert('RGB')
                
            if first_image is None:
                first_image = img
            else:
                images.append(img)
        except Exception as e:
            print(f"Failed to process {p}: {e}")
            
    output_filename = "Ramanujan_Notebooks_Complete_Scans.pdf"
    
    if first_image:
        print(f"Saving to {output_filename}...")
        first_image.save(
            output_filename, "PDF" ,resolution=100.0, save_all=True, append_images=images
        )
        print("PDF generated successfully!")
    else:
        print("Failed to load any valid images.")

if __name__ == "__main__":
    generate_pdf()
