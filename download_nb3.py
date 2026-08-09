import os
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://www.imsc.res.in/~rao/ramanujan/NoteBooks/NoteBook3"
OUTPUT_DIR = "input/NoteBook3"

async def download_image(session, img_url, img_path):
    if os.path.exists(img_path):
        return
    try:
        async with session.get(img_url, timeout=10) as resp:
            if resp.status == 200:
                content = await resp.read()
                with open(img_path, "wb") as f_img:
                    f_img.write(content)
    except:
        pass

async def download_page(session, p):
    url = f"{BASE_URL}/page{p}.htm"
    try:
        async with session.get(url, timeout=10) as resp:
            if resp.status != 200:
                return False
            content = await resp.read()
    except Exception:
        return False
        
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    file_path = os.path.join(OUTPUT_DIR, f"page{p}.htm")
    with open(file_path, "wb") as f:
        f.write(content)
        
    soup = BeautifulSoup(content, "html.parser")
    images = soup.find_all("img")
    
    tasks = []
    for img in images:
        src = img.get("src")
        if src:
            img_url = urljoin(url, src)
            if src.startswith("../") or src.startswith("http"):
                img_filename = os.path.basename(img_url.split("?")[0])
                img_dir = os.path.join(OUTPUT_DIR, "images_extra")
            else:
                img_filename = os.path.basename(src)
                rel_dir = os.path.dirname(src)
                img_dir = os.path.join(OUTPUT_DIR, rel_dir)
                
            os.makedirs(img_dir, exist_ok=True)
            img_path = os.path.join(img_dir, img_filename)
            tasks.append(download_image(session, img_url, img_path))
            
    if tasks:
        await asyncio.gather(*tasks)
    return True

async def scrape_async():
    print("Starting NoteBook3 scraping asynchronously...")
    pages_processed = 0
    
    async with aiohttp.ClientSession() as session:
        # We process in batches of 10 to not overwhelm the server, but still fast
        for batch_start in range(1, 400, 10):
            batch_end = batch_start + 10
            tasks = [download_page(session, p) for p in range(batch_start, batch_end)]
            results = await asyncio.gather(*tasks)
            
            success_count = sum(1 for r in results if r)
            pages_processed += success_count
            print(f"Processed batch up to page {batch_end-1}. Successful this batch: {success_count}")
            
            # If an entire batch fails, we've likely reached the end
            if success_count == 0:
                break
                
    print(f"NoteBook3: Downloaded {pages_processed} pages.")

def scrape():
    asyncio.run(scrape_async())

if __name__ == "__main__":
    scrape()
