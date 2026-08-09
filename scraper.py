import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

BASE_URL = "https://www.imsc.res.in/~rao/ramanujan/NoteBooks"
OUTPUT_DIR = "input"

ROMAN_NUMERALS = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII', 'XIV', 'XV', 'XVI', 'XVII', 'XVIII', 'XIX', 'XX', 'XXI']

html_count = 0
image_count = 0
lock = threading.Lock()

def download_page(nb, ch, p):
    url = f"{BASE_URL}/NoteBook{nb}/chapter{ch}/page{p}.htm"
    try:
        resp = requests.get(url, timeout=10)
    except Exception as e:
        return False, 0, 0
        
    if resp.status_code == 200:
        dir_path = os.path.join(OUTPUT_DIR, f"NoteBook{nb}", f"chapter{ch}")
        os.makedirs(dir_path, exist_ok=True)
        file_path = os.path.join(dir_path, f"page{p}.htm")
        with open(file_path, "wb") as f:
            f.write(resp.content)
            
        soup = BeautifulSoup(resp.content, "html.parser")
        images = soup.find_all("img")
        imgs_downloaded = 0
        
        # Download images for this page sequentially
        for img in images:
            src = img.get("src")
            if src:
                img_url = urljoin(url, src)
                if src.startswith("../") or src.startswith("http"):
                    img_filename = os.path.basename(img_url.split("?")[0])
                    img_dir = os.path.join(dir_path, "images_extra")
                else:
                    img_filename = os.path.basename(src)
                    rel_dir = os.path.dirname(src)
                    img_dir = os.path.join(dir_path, rel_dir)
                    
                os.makedirs(img_dir, exist_ok=True)
                img_path = os.path.join(img_dir, img_filename)
                
                if not os.path.exists(img_path):
                    try:
                        img_resp = requests.get(img_url, timeout=10)
                        if img_resp.status_code == 200:
                            with open(img_path, "wb") as f_img:
                                f_img.write(img_resp.content)
                            imgs_downloaded += 1
                    except:
                        pass
        return True, 1, imgs_downloaded
    return False, 0, 0

def scrape_chapter(nb, ch):
    global html_count, image_count
    
    # Check if chapter exists by checking page 1
    exists, h_c, i_c = download_page(nb, ch, 1)
    if not exists:
        return
        
    with lock:
        html_count += h_c
        image_count += i_c
        
    misses = 0
    pages_processed = 1
    # Download subsequent pages up to 300
    for p in range(2, 301):
        exists, h_c, i_c = download_page(nb, ch, p)
        if exists:
            with lock:
                html_count += h_c
                image_count += i_c
            misses = 0
            pages_processed += 1
        else:
            misses += 1
            if misses >= 2: # 2 consecutive misses means end of chapter
                break
    print(f"NoteBook{nb} Chapter{ch}: Downloaded {pages_processed} pages.")

def scrape():
    print("Starting fast scraping...")
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = []
        for nb in range(1, 11):
            for ch in ROMAN_NUMERALS:
                futures.append(executor.submit(scrape_chapter, nb, ch))
        
        for future in as_completed(futures):
            future.result()

if __name__ == "__main__":
    scrape()
    print(f"\n--- Scraping Complete ---")
    print(f"Total HTML files captured: {html_count}")
    print(f"Total Images captured: {image_count}")
