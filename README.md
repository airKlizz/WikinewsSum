# WikinewsSum

Code used to create the WikinewsSum dataset presented in **Generating Extended and Multilingual Summaries with Pre-trained Transformers**.

## Data

WikinewsSum is based on [Wikinews](https://www.wikinews.org).
The Wikinews articles are used as summaries and the source texts as input texts for the summaries.

The dataset is ditributed via the European Language Grid: https://live.european-language-grid.eu/catalogue/corpus/18633

## Usage

First you need to download the dataset [here](https://live.european-language-grid.eu/catalogue/corpus/18633).
Then you can load the dataset using the [`datasets`](https://github.com/huggingface/datasets) library:

```python
from datasets import load_dataset

dataset = load_dataset("json", data_files={"train": "train.json", "test": "test.json", "validation": "validation.json"})
```

## Structure

Each sample of the dataset follows the following structure:

```json
{
    "language": "en",
    "title": "This is the title",
    "news": "This is the 1st passage of the news.\nThis is the second one.\n...",
    "sources": [
        {
            "language": "en",
            "text": "This is the raw text from the source",
            "url": "url of the source",
            "archive_url": "archive url of the source"
        },
        {
            "language": "en",
            "text": "This is the raw text from the source",
            "url": "url of the source",
            "archive_url": "archive url of the source"
        }
    ]
}
```

## Statistics

| Languages     | # samples | # cross-lingual samples | Input Documents # words | Input Documents  # sentences | Summaries # words | Summaries # sentences |
|---------------|-----------|-------------------------|-------------------------|------------------------------|-------------------|-----------------------|
| English       | 11,616    | 641 (5.5%)              | 1,466                   | 57                           | 300               | 13                    |
| German        | 8,126     | 2,796 (34.4%)           | 1,179                   | 58                           | 241               | 13                    |
| French        | 6,200     | 1,932 (31.2%)           | 884                     | 29                           | 176               | 7                     |
| Spanish       | 6,116     | 2,137 (34.9%)           | 1,215                   | 42                           | 276               | 10                    |
| Portuguese    | 3,843     | 1,971 (51.3%)           | 1,037                   | 38                           | 221               | 8                     |
| Polish        | 3,630     | 1,214 (33.4%)           | 734                     | 35                           | 173               | 10                    |
| Italian       | 95        | 46 (48.4%)              | 1,021                   | 35                           | 224               | 8                     |
| All languages | 39,626    | 10,737 (27.1%)          | 1,168                   | 47                           | 245               | 11                    |



## Steps to create the WikinewsSum dataset

```bash
cd wikinewssum
```

### Step 1: Wikinews Dump

First you need to download the Wikinews dump you want to create the dataset from.

> Replace with the language you want

```bash
cd dumps
wget https://dumps.wikimedia.org/enwikinews/latest/enwikinews-latest-pages-meta-current.xml.bz2
cd ..
```

### Step 2: Extract docs from dump

```python
from src import Wikinews
Wikinews.save(dump_path="dumps/enwikinews-latest-pages-meta-current.xml.bz2", max_doc_count=0, folder="enwikinews")
```

This will create 2 files in the `enwikinews` folder: `docs.json` that information of the Wikinews articles, and `sources.txt` that contains all the sources (1 per line).

### Step 3: Get sources

```python
from src import Sources
Sources.save(file="enwikinews/sources.txt", folder="sources", max_workers=5, timeout=10, retry=False)
```

> Can takes hours. You can stop it when you want and run it again, it will reuse the sources already saved if the folder parameter is the same. The sources didn't find will be skipped unless the retry parameter is set to True.

### Step 4: Extract content from sources

```python
from src import Content
Content.extract(folder="sources")
```

### Step 5: Create the dataset

```python
from src import Dataset
Dataset.create(wikinews_folder="enwikinews", sources_folder="sources", dataset_folder="endataset")
```

### (optional) Zip everything

```bash
zip -r enwikinewssum.zip endataset/ sources/ enwikinews/
```

### Step 6: Create one big json file

```python
import json
from pathlib import Path

dataset_folder = Path("endataset")
files = list(dataset_folder.glob("**/*.json"))
with open("endataset.json", "w") as output_file:
    for filename in files:
        with open(filename) as f:
            entry = json.load(f)
        output_file.write(json.dumps(entry))
        output_file.write("\n")
```

### Step 7: Clean the texts by using another text extraction method (which removed the sources, this is why it was not used in the first place)

```bash
python -m gensim.scripts.segment_wiki -i -f dumps/enwikinews-latest-pages-meta-current.xml.bz2 -o dumps/enwikinews-latest.json.gz
```

```python
from src import Clean
Clean.clean("endataset.json", "dumps/enwikinews-latest.json.gz", "cleaned_endataset.json")
```

### Step 8: Create the final json file

```python
import json
from pathlib import Path

json_filenames = {
    "en": "cleaned_endataset.json",
    # "de": "cleaned_dedataset.json",
    # "es": "cleaned_esdataset.json",
    # "fr": "cleaned_frdataset.json",
    # "it": "cleaned_itdataset.json",
    # "pl": "cleaned_pldataset.json",
    # "pt": "cleaned_ptdataset.json",
}

final_json_filename = "wikinewssum.json"

with open(final_json_filename, "w") as final_json:
    for language, json_filename in json_filenames.items():
        with open(json_filename) as json_file:
            data = json_file.read()
        for entry_str in data.split("\n"):
            if entry_str is None or entry_str == "":
                continue
            entry = json.loads(entry_str)
            new_entry = {
                "language": language,
                "title": entry["title"],
                "news": entry["text"],
                "categories": entry["categories"],
                "sources": []
            }
            for source in entry["sources"]:
                new_entry["sources"].append({
                    "language": source["language"],
                    "title": source["title"],
                    "text": source["maintext"],
                    "url": source["url"],
                    "archive_url": source["archive_url"]
                })
            final_json.write(json.dumps(new_entry))
            final_json.write("\n")



```

### Step 8: Filter samples

```python
from src import Filter
Filter.filter("wikinewssum.json", "filtered_wikinewssum.json")
```

### Step 7: Load it using datasets

```python
from datasets import load_dataset
dataset = load_dataset("json", data_files="filtered_wikinewssum.json")
```
