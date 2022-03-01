import timeit

from rapidfuzz.fuzz import partial_token_set_ratio
from rapidfuzz.process import cdist
import pandas as pd
import numpy as np
import boto3

from fuzzup.fuzz import (
    fuzzy_cluster, 
    compute_prominence,
    match_whitelist
)

def load_danish_companies(file="companies-name-municipality.json"):
    s3 = boto3.resource('s3')
    companies = pd.read_json(s3.Bucket("nerbonanza").Object(file).get()['Body'])
    return companies

#### SIMULATE DATA
PERSONS = ['Donald Trump', 'Donald Trump', 
           'J. biden', 'joe biden', 'Biden', 
           'Bide', 'mark esper', 'Christopher c . miller', 
           'jim mattis', 'Nancy Pelosi', 'trumps',
           'Trump', 'Donald', 'miller']

# ALIGN WITH HUGGINGFACE 'TRANSFORMERS' NER PIPELINE OUTPUT FORMAT
n = len(PERSONS)
PERSONS_NER = pd.DataFrame(data = PERSONS, columns=['word'])
PERSONS_NER["entity_group"] = "PER"
PERSONS_NER["score"] = np.random.sample(n)
PERSONS_NER["start"] = np.random.randint(100, size=n)
PERSONS_NER["end"] = np.random.randint(100, size=n)
PERSONS_NER = PERSONS_NER.to_dict(orient="records")

#### FUZZUP WORKFLOW
clusters, _ = fuzzy_cluster(PERSONS_NER, 
                            scorer=partial_token_set_ratio, 
                            workers=2,
                            cutoff=70,
                            merge_output=True)
pd.DataFrame.from_dict(clusters)

clusters = compute_prominence(clusters, 
                              merge_output=True)
pd.DataFrame.from_dict(clusters)

whitelist = ["Donald Trump", "Joe Biden"]
   
companies = load_danish_companies()
company_names = companies.name.tolist()

# match with whitelists
match_whitelist(words=clusters, 
                whitelist=company_names,
                merge_output=True,
                aggregate_cluster=True,
                to_dataframe=True,
                score_cutoff=80,
                scorer=partial_token_set_ratio)












    


    











