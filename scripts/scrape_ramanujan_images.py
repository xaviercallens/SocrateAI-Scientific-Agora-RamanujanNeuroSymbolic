import os
import sys
import asyncio
import aiohttp
import time

async def download_image(session, url, dest_path):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                with open(dest_path, 'wb') as f:
                    while True:
                        chunk = await response.content.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                return True
            elif response.status == 404:
                return False
            else:
                print(f"Failed {url}: HTTP {response.status}")
                return False
    except Exception as e:
        print(f"Error {url}: {e}")
        return False

async def download_notebook(base_url, dest_dir, max_pages=500, max_concurrent=10):
    os.makedirs(dest_dir, exist_ok=True)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    connector = aiohttp.TCPConnector(limit=max_concurrent)
    async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
        page_num = 1
        consecutive_404 = 0
        tasks = []
        
        # Launch workers to download pages concurrently.
        # We don't know the exact end page, so we probe in batches.
        batch_size = max_concurrent
        
        while page_num <= max_pages and consecutive_404 < 3:
            current_batch = []
            for i in range(batch_size):
                url = f"{base_url}/images/page{page_num + i}.jpg"
                dest_path = os.path.join(dest_dir, f"page{page_num + i}.jpg")
                current_batch.append((page_num + i, download_image(session, url, dest_path)))
                
            results = await asyncio.gather(*(t[1] for t in current_batch))
            
            for (p_num, _), success in zip(current_batch, results):
                if success:
                    print(f"Downloaded page {p_num}")
                    consecutive_404 = 0
                else:
                    consecutive_404 += 1
            
            page_num += batch_size
            
            if consecutive_404 >= 3:
                print(f"Hit multiple 404s. Assuming end of notebook around page {page_num - batch_size}.")
                break
                
async def main():
    start = time.time()
    
    print("Downloading Notebook 1 Chapter I (Concurrent)...")
    await download_notebook(
        "https://www.imsc.res.in/~rao/ramanujan/NoteBooks/NoteBook1/chapterI", 
        "data/ramanujan_notebooks/Notebook1/chapterI"
    )
    
    print("\nDownloading Notebook 3 (Concurrent)...")
    await download_notebook(
        "https://www.imsc.res.in/~rao/ramanujan/NoteBooks/NoteBook3", 
        "data/ramanujan_notebooks/Notebook3"
    )
    
    print(f"\nAll downloads completed in {time.time() - start:.2f} seconds.")

if __name__ == "__main__":
    asyncio.run(main())
