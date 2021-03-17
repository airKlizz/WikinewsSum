import base64
import concurrent.futures as cf
from pathlib import Path

import requests
import savepagenow
from tqdm import tqdm


class Source:

    archive_url_template = "https://web.archive.org/web/{}/{}"

    def __init__(self, url):
        self.url = url

    def get(self, folder="sources", year=1990, user_agent="getweb agent", timeout=10, retry=False):
        path = Path(folder)
        path.mkdir(parents=True, exist_ok=True)
        if (path / "urls" / base64.b64encode(self.url.encode(), b"qw").decode("utf-8")[:254]).exists():
            if not retry:
                return "cached"
            else:
                with open(path / "urls" / base64.b64encode(self.url.encode(), b"qw").decode("utf-8")[:254]) as f:
                    if not f.read() == "error":
                        return "cached"
        try:
            print(f"Get archive {self.url}")
            self.response = self.get_archive(year=year, user_agent=user_agent, timeout=timeout)
        except:
            try:
                print(f"Archive {self.url}")
                self.response = self.archive(user_agent=user_agent, timeout=timeout)
            except:
                print(f"Error {self.url}")
                urls_path = path / "urls"
                urls_path.mkdir(parents=True, exist_ok=True)
                with open(urls_path / base64.b64encode(self.url.encode(), b"qw").decode("utf-8")[:254], "w") as f:
                    f.write("error")
                return "error"

        pages_path = path / "pages"
        pages_path.mkdir(parents=True, exist_ok=True)
        with open(pages_path / base64.b64encode(self.response.url.encode(), b"qw").decode("utf-8")[:254], "w") as f:
            f.write(self.response.text)

        urls_path = path / "urls"
        urls_path.mkdir(parents=True, exist_ok=True)
        with open(urls_path / base64.b64encode(self.url.encode(), b"qw").decode("utf-8")[:254], "w") as f:
            f.write(self.response.url)
        print(f"Success {self.url}")
        return "success"

    def get_archive(self, year=1900, user_agent="getweb agent", timeout=10):
        url = self.archive_url_template.format(year, self.url)
        response = requests.get(url, headers={"User-Agent": user_agent}, timeout=timeout)
        assert response.ok, f"Response from {url} not valid"
        return response

    def archive(self, user_agent="getweb agent", timeout=10):
        url = savepagenow.capture(self.url, accept_cache=True)
        response = requests.get(url, headers={"User-Agent": user_agent}, timeout=timeout)
        assert response.ok, f"Response from {url} not valid"
        return response


class Sources:
    @staticmethod
    def save(file, folder="sources", max_workers=5, timeout=10, retry=False):
        with open(file) as f:
            sources = f.read().split("\n")

        path = Path(folder)
        path.mkdir(parents=True, exist_ok=True)

        success = 0
        error = 0
        cached = 0
        total = len(sources)
        with cf.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for url in sources:
                source = Source(url)
                futures.append(
                    executor.submit(
                        source.get,
                        folder=folder,
                        timeout=timeout,
                        retry=retry,
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
                print(
                    f"[{success + error + cached}/{total}]   \tsuccess {success}   \t   error {error}   \t   cached {cached}"
                )
