import numpy as np

class Stats:
    
    def __init__(self, dataset):
        self.dataset = dataset
        self.len_text = []
        self.nb_sources = []
        self.len_sources = []
        self.lang_sources = []
        for sample in dataset:
            self.len_text.append(len(" \n ".join(sample["text"]).split()))
            self.nb_sources.append(len(sample["sources"]))
            lang = []
            lenghts = []
            for source in sample["sources"]:
                lang.append(source["language"])
                lenghts.append(len(source["maintext"].split()))
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
            lenght = 100 * round(lenght/100)
            if lenght in distri.keys():
                distri[lenght] += 1
            else:
                distri[lenght] = 1
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