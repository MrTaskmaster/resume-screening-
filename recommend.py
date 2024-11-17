import pandas as pd
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')

from app import category_name

df = pd.read_csv('./new_recommend.csv')

df.rename(columns = {'Skills (Keywords for Resume)':'skills'}, inplace = True)

def recommend():
    category = category_name
    results = df.loc[df["Domain"] == category]
    one = results['skills']

    llist = one.tolist()

    corpus = " "
    for i in range(0, len(llist)):
        corpus = corpus + str(llist)

    tokenizer = nltk.tokenize.RegexpTokenizer('\w+')
    # Tokenizing the text
    tokens = tokenizer.tokenize(corpus)

    words = []
    # Looping through the tokens and make them lower case
    for word in tokens:
        words.append(word.lower())

    newrecom = []

    for i in words:
        if i != 'law':
            m = i
            newrecom.append(m)
            # print(newarr)
            # print(i)
        else:
            continue

    newrecommend = []

    for j in range(0, 10):
        newrecommend.append(newrecom[j])

    recom = newrecommend
    return recom

