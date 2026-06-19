import requests
import zipfile
import os
import shutil
from pathlib import Path
from dotenv import load_dotenv
import re 
# Getting all env's
load_dotenv()
# Настройки
API_KEY =  os.getenv("CURSEFORGE_API_KEY")
SLUG =  os.getenv("MODPACK_URL")
match = re.search(r'/modpacks/([^/]+)', SLUG)
result = match.group(1)
print(result)
OUTPUT_DIR = "./mod_pack"  
ZIP_NAME = "modpack.zip"   

def download_modpack():
    headers = {"x-api-key": API_KEY}
    
    # Search for id
    search_url = f"https://api.curseforge.com/v1/mods/search?slug={result}&gameId=432"
    resp = requests.get(search_url, headers=headers)
    resp.raise_for_status()
    mod_id = resp.json()["data"][0]["id"]
    
    # Getting all modpack specific id's
    files_url = f"https://api.curseforge.com/v1/mods/{mod_id}/files"
    resp = requests.get(files_url, headers=headers)
    resp.raise_for_status()
    files = resp.json()["data"]
    
    # Searching for serverpack
    for f in files:
        servepack_id = f.get("serverPackFileId")
        if servepack_id is not None:
            print(servepack_id)
            break
    

    
    download_url_req = f"https://api.curseforge.com/v1/mods/{mod_id}/files/{servepack_id}/download-url"
    resp = requests.get(download_url_req, headers=headers)
    resp.raise_for_status()
    download_url = resp.json()["data"]
    
    
    print(f"Скачиваю с {download_url}...")
    with requests.get(download_url, stream=True) as r:
        r.raise_for_status()
        with open(ZIP_NAME, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print("Скачивание завершено.")
    
    
    if os.path.exists(OUTPUT_DIR):
        
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"Распаковываю в {OUTPUT_DIR}...")
    with zipfile.ZipFile(ZIP_NAME, 'r') as zip_ref:
        zip_ref.extractall(OUTPUT_DIR)
    print("Распаковка завершена.")
    
    # 6. Удаляем временный ZIP
    os.remove(ZIP_NAME)
    print("Временный файл удалён.")

if __name__ == "__main__":
    download_modpack()