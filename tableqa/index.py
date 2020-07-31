from data_utils import get_csvs, get_schema_for_csv, get_dataframe,csv_keyword_vocab,del_vocab
from csv2sql import csv2sql,drop_db
from config import db_name
import json


dumpfile = db_name+'.sql'
valuesfile = 'values.json'


def index():
    drop_db()
    del_vocab()
    values = {}
    for csv in get_csvs():
        df = get_dataframe(csv)
        schema = get_schema_for_csv(csv)
        if schema is not None:
            csv2sql(df, schema, dumpfile)
            csv_keyword_vocab(csv,schema)
            for col in schema['columns']:
                if col['type'] == "FuzzyString":
                    colname = col['name']
                    if colname not in values:
                        values[colname] = []
                    vals = values[colname]
                    vals += list(set([x for x in df[colname] if isinstance(x, str)]))
    with open(valuesfile, 'w') as f:
        json.dump(values, f)
    


if __name__ == '__main__':
    index()
