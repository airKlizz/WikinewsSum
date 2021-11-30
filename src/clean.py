import json
import re

from cleantext import clean
from tqdm import tqdm


class Clean:

    to_remove_pattern = r"\[\[File:[^\]]+\]\]"
    to_remove_pattern_bis = r"{{[^w][^}]+}}"
    intern_link_pattern = r"{{w\|[^|}]+\|(?P<name>[^}]+)}}"
    intern_link_pattern_bis = r"{{w\|(?P<name>[^}]+)}}"
    intern_link_pattern_ter = r"{{\w+\|(?P<name>[^}]+)}}"
    promote_pattern = r"\[\[(?P<name>[^\]\|]+)\]\]"
    promote_pattern_bis = r"\[\[[^\]\|]+\|(?P<name>[^\]]+)\]\]"
    source_link_pattern = r"\[http[\S]* (?P<name>[^\]]+)\]"
    html_comment_pattern = r"(<!--.*?-->)"
    html_pattern = r"<[^>]*>>?"
    css_pattern = r"{\|[^}]*\|}"
    begin_pattern = r"^.{,20}}}"
    brackets_pattern = r"{{(?P<name>\w+)}}"
    brackets_pattern_bis = r"{{[^}]*}}"
    # begin_pattern = r"^\S+\|\S+\|\S+\|"
    img_pattern = r"\|?(thumb|thumbnail|right|upright|left|upleft|esquerda|miniaturadaimagem|[0-9]+px)\|((thumb|thumbnail|right|upright|left|upleft|esquerda|[0-9]+px)(=[0-9\.]{0,5})?)?\)?((thumb|thumbnail|right|upright|left|upleft|esquerda|[0-9]+px)(=[0-9\.]{0,5})?)?\|?"
    img_pattern_bis = r"\|(thumb|thumbnail|right|upright|left|upleft|esquerda|miniaturadaimagem|[0-9]+px)\|?"

    @classmethod
    def clean_text(cls, text):
        text = re.sub(cls.to_remove_pattern, "", text)
        text = re.sub(cls.to_remove_pattern_bis, "", text)
        text = re.sub(cls.intern_link_pattern, r"\1", text)
        text = re.sub(cls.intern_link_pattern_bis, r"\1", text)
        text = re.sub(cls.intern_link_pattern_ter, r"\1", text)
        text = re.sub(cls.promote_pattern, r"\1", text)
        text = re.sub(cls.promote_pattern_bis, r"\1", text)
        text = re.sub(cls.source_link_pattern, r"\1", text)
        text = re.sub(cls.html_comment_pattern, "", text)
        text = re.sub(cls.html_pattern, "", text)
        text = re.sub(cls.css_pattern, "", text)
        text = re.sub(cls.begin_pattern, "", text)
        text = re.sub(cls.brackets_pattern, r"\1", text)
        text = re.sub(cls.brackets_pattern_bis, "", text)
        text = re.sub(cls.img_pattern, "", text)
        text = re.sub(cls.img_pattern_bis, "", text)

        return text
        # from https://github.com/jfilter/clean-text#usage
        return clean(
            text,
            fix_unicode=True,  # fix various unicode errors
            to_ascii=False,  # transliterate to closest ASCII representation
            lower=False,  # lowercase text
            no_line_breaks=False,  # fully strip line breaks as opposed to only normalizing them
            no_urls=True,  # replace all URLs with a special token
            no_emails=True,  # replace all email addresses with a special token
            no_phone_numbers=True,  # replace all phone numbers with a special token
            no_numbers=False,  # replace all numbers with a special token
            no_digits=False,  # replace all digits with a special token
            no_currency_symbols=False,  # replace all currency symbols with a special token
            no_punct=False,  # remove punctuations
            replace_with_punct="",  # instead of removing punctuations you may replace them
            replace_with_url="<URL>",
            replace_with_email="<EMAIL>",
            replace_with_phone_number="<PHONE>",
            replace_with_number="<NUMBER>",
            replace_with_digit="0",
            replace_with_currency_symbol="<CUR>",
            lang="en",  # set to 'de' for German special handling
        )

    @classmethod
    def clean_texts_in_dataset(cls, dataset):
        cleaned_dataset = []
        for entry in tqdm(dataset):
            sources = []
            for source in entry["sources"]:
                cleaned_source = source.copy()
                cleaned_source["text"] = cls.clean_text(source["text"])
                sources.append(cleaned_source)
            cleaned_entry = entry.copy()
            cleaned_entry["sources"] = sources
            cleaned_entry["title"] = cls.clean_text(entry["title"])
            cleaned_entry["news"] = list(map(cls.clean_text, entry["news"]))
            cleaned_dataset.append(cleaned_entry)
        return cleaned_dataset

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
    def non_interesting_title(
        cls,
        dataset,
        black_words=[
            "Météo en France",
            "Bulletin météo",
            "Campeonato",
            "Pandemia COVID-19 w Polsce",
        ],
    ):
        new_dataset = []
        for entry in tqdm(dataset):
            ok = True
            for black_word in black_words:
                if black_word.lower() in entry["title"].lower():
                    ok = False
            if ok:
                new_dataset.append(entry)
        return new_dataset

    @classmethod
    def clean(
        cls,
        input_filename,
        output_filename,
        sources_min_len=100,
        sources_max_len=10000,
        min_nb_sources=1,
        max_nb_sources=10,
        news_min_len=100,
        news_max_len=5000,
        ratio=1.5,
    ):
        with open(input_filename) as input_f:
            dataset = [
                json.loads(entry_str)
                for entry_str in tqdm(input_f.read().split("\n"))
                if entry_str is not None and entry_str != ""
            ]

        print("Original dataset size: ", len(dataset))
        new_dataset = cls.clean_texts_in_dataset(dataset)
        new_dataset = cls.short_or_long_sources(new_dataset, sources_min_len, sources_max_len)
        print("After having filtered short or long sources: ", len(new_dataset))
        new_dataset = cls.too_many_sources(new_dataset, min_nb_sources, max_nb_sources)
        print("After having filtered samples with too many sources: ", len(new_dataset))
        new_dataset = cls.short_or_long_news(new_dataset, news_min_len, news_max_len)
        print("After having filtered short or long news: ", len(new_dataset))
        new_dataset = cls.too_short_ratio_sources_news(new_dataset, ratio)
        print(
            "After having filtered samples with a too short ratio sources/news: ",
            len(new_dataset),
        )
        new_dataset = cls.non_interesting_title(new_dataset)
        print(
            "After having filtered samples with black words: ",
            len(new_dataset),
        )

        with open(output_filename, "w") as output_f:
            for entry in tqdm(new_dataset):
                output_f.write(json.dumps(entry))
                output_f.write("\n")
