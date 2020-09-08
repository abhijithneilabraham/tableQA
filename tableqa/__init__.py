def _nltk_downloader():
    try:
        nltk.download('wordnet',quiet=True)
        nltk.download('averaged_perceptron_tagger',quiet=True)
        nltk.download('stopwords',quiet=True)
        nltk.download('punkt',quiet=True)
    except LookupError as e:
        print(e)

_nltk_downloader()


from .nlp import *
from .data_utils import *
from .conditionmaps import *
from .column_types import *
from .clauses import *
from .database import *
from .agent import *