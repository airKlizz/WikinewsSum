import json
from tqdm import tqdm

class Clean:
    
    @classmethod
    def short_or_long_sources(cls, dataset, sources_min_len=100, sources_max_len=10000):
        new_dataset = []
        for entry in tqdm(dataset):
            sources = []
            for source in entry["sources"]:
                if len(source["text"]) <= sources_max_len and len(source["text"]) > sources_min_len:
                    sources.append(source)
            entry["sources"] = sources
            new_dataset.append(entry)
        return new_dataset
    
    @classmethod
    def too_many_sources(cls, dataset, min_nb_sources=1, max_nb_sources=10):
        new_dataset = []
        for entry in tqdm(dataset):
            if len(entry["sources"]) <= max_nb_sources and len(entry["sources"]) >= min_nb_sources:
                new_dataset.append(entry)
        return new_dataset
    
    @classmethod
    def short_or_long_news(cls, dataset, news_min_len=100, news_max_len=5000):
        new_dataset = []
        for entry in tqdm(dataset):
            news = "\n\n".join([txt.replace("\n", "") for txt in entry["news"]])
            if len(news) <= news_max_len and len(news) > news_min_len:
                entry["news"] = news
                new_dataset.append(entry)
        return new_dataset
    
    @classmethod
    def too_short_ratio_sources_news(cls, dataset, ratio=1.5):
        new_dataset = []
        for entry in tqdm(dataset):
            if len(entry["news"]) * ratio <= len(" ".join([source["text"] for source in entry["sources"]])):
                new_dataset.append(entry)
        return new_dataset        
        
    @classmethod
    def clean(cls, input_filename, output_filename, sources_min_len=100, sources_max_len=10000, min_nb_sources=1, max_nb_sources=10, news_min_len=100, news_max_len=5000, ratio=1.5):
        with open(input_filename) as input_f:
            dataset = [json.loads(entry_str) for entry_str in tqdm(input_f.read().split("\n")) if entry_str is not None and entry_str != ""]  
        
        print(len(dataset))
        new_dataset = cls.short_or_long_sources(dataset, sources_min_len, sources_max_len)
        print(len(new_dataset))
        new_dataset = cls.too_many_sources(new_dataset, min_nb_sources, max_nb_sources)
        print(len(new_dataset))
        new_dataset = cls.short_or_long_news(new_dataset, news_min_len, news_max_len)
        print(len(new_dataset))
        new_dataset = cls.too_short_ratio_sources_news(new_dataset, ratio)
        print(len(new_dataset))
        
        with open(output_filename, "w") as output_f:
            for entry in tqdm(new_dataset):
                output_f.write(json.dumps(entry))
                output_f.write("\n")