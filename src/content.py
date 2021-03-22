import json
from pathlib import Path

from newsplease import NewsPlease
from tqdm import tqdm
import concurrent.futures as cf



class Content:
    
    @classmethod
    def save(cls, filename, contents_path):
        content_path = contents_path / filename.name
        if content_path.exists() and content_path.is_file():
            return "cached"
        try:
            with open(filename) as f:
                html = f.read()
            article = NewsPlease.from_html(html, url=None)
            content = {
                "title": article.title,
                "maintext": article.maintext,
                "language": article.language,
            }
            with open(content_path, "w") as f:
                json.dump(content, f, sort_keys=True, indent=4)
            return "success"
        except Exception as e:
            print(e)
            return "error"
    
    @classmethod
    def extract(cls, folder="sources", max_workers=30):
        pages_path = Path(folder) / "pages"
        contents_path = Path(folder) / "contents"
        contents_path.mkdir(parents=True, exist_ok=True)
        files = list(pages_path.glob("*"))
        success = 0
        error = 0
        cached = 0
        total = len(files)
        with cf.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for filename in files:
                futures.append(
                    executor.submit(
                        cls.save,
                        filename=filename,
                        contents_path=contents_path,
                    )
                )
            for future in cf.as_completed(futures):
                status = future.result()
                if status == "success":
                    success += 1
                elif status == "error":
                    error += 1
                elif status == "cached":
                    cached += 1
                else:
                    raise ValueError("Should not append.")
                print(f"[{success+error+cached}/{total}]  \tsuccess {success}   \terror {error}   \tcached {cached}")
