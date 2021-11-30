import json

import numpy as np
from tqdm import tqdm


class Stats:
    def __init__(self, input_filename):
        with open(input_filename) as input_f:
            dataset = [
                json.loads(entry_str)
                for entry_str in tqdm(input_f.read().split("\n"))
                if entry_str is not None and entry_str != ""
            ]
        self.dataset = dataset
        self.languages = []
        self.len_text = []
        self.nb_sources = []
        self.len_sources = []
        self.lang_sources = []
        for sample in dataset:
            self.languages.append(sample["language"])
            self.len_text.append(len(" \n ".join(sample["news"]).split()))
            self.nb_sources.append(len(sample["sources"]))
            lang = []
            lenghts = []
            for source in sample["sources"]:
                lang.append(source["language"])
                lenghts.append(len(source["text"].split()))
            self.len_sources.append(lenghts)
            self.lang_sources.append(lang)

    def number_of_samples(self):
        return len(self.dataset)

    def number_of_sources(self):
        return self.describe_list(self.nb_sources)

    def number_of_sources_distribution(self):
        distri = {}
        for nb in self.nb_sources:
            if nb in distri.keys():
                distri[nb] += 1
            else:
                distri[nb] = 1
        return distri

    def len_of_samples(self):
        return self.describe_list(self.len_text)

    def len_of_samples_distribution(self):
        distri = {}
        for lenght in self.len_text:
            lenght = 100 * round(lenght / 100)
            if lenght in distri.keys():
                distri[lenght] += 1
            else:
                distri[lenght] = 1
        return distri

    def languages_distribution(self):
        distri = {}
        for lg in self.languages:
            if lg in distri.keys():
                distri[lg] += 1
            else:
                distri[lg] = 1
        return distri

    @staticmethod
    def describe_list(l):
        l = np.array(l)
        return {
            "mean": np.mean(l),
            "min": np.min(l),
            "5%": np.percentile(l, 5),
            "25%": np.percentile(l, 25),
            "50%": np.percentile(l, 50),
            "75%": np.percentile(l, 75),
            "95%": np.percentile(l, 95),
            "max": np.max(l),
        }
