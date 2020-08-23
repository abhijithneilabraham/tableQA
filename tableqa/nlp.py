import nltk
from nltk.corpus import stopwords
from data_utils import data_utils
import os
from transformers import TFBertForQuestionAnswering, BertTokenizer
from transformers import TFAutoModelForSequenceClassification, AutoTokenizer
import tensorflow as tf
from rake_nltk import Rake
import column_types
import json
from clauses import Clause
from conditionmaps import conditions
from nltk.stem import WordNetLemmatizer 

qa_model = TFBertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
qa_tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
rerank_model = TFAutoModelForSequenceClassification.from_pretrained('bert-large-cased-whole-word-masking')
rerank_tokenizer = AutoTokenizer.from_pretrained('bert-large-cased-whole-word-masking')
lemmatizer = WordNetLemmatizer()
lem=lemmatizer.lemmatize
stop_words = set(stopwords.words('english'))


def extract_keywords_from_doc(doc, phrases=True, return_scores=False):
    if phrases:
        r = Rake()
        if isinstance(doc, (list, tuple)):
            r.extract_keywords_from_sentences(doc)
        else:
            r.extract_keywords_from_text(doc)
        if return_scores:
            return [(b, a) for a, b in r.get_ranked_phrases_with_scores()]
        else:
            return r.get_ranked_phrases()
    else:
        if not isinstance(doc, (list, tuple)):
            doc = [doc]
        ret = []
        for x in doc:
            for t in nltk.word_tokenize(x):
                if t.lower() not in stop_words:
                    ret.append(t)
        return ret


def extract_keywords_from_query(query, phrases=True):
    if not phrases:
        tokens = nltk.pos_tag(nltk.word_tokenize(query))
        return [t[0] for t in tokens if  t[0].lower() not in stop_words and t[1] != '.']
    kws = extract_keywords_from_doc(query, phrases=True)
    tags = dict(nltk.pos_tag(nltk.word_tokenize(query)))
    filtered_kws = []
    for kw in kws:
        kw_tokens = nltk.word_tokenize(kw)
        for t in kw_tokens:
            if t in tags and tags[t][0] in ('N', 'C', 'R', 'S'):
                filtered_kws.append(kw)
                break
    return filtered_kws


def qa(docs, query, return_score=False, return_all=False, return_source=False, sort=False):
    if isinstance(docs, (list, tuple)):
        answers_and_scores = [qa(doc, query, return_score=True) for doc in docs]
        if sort:
            sort_ids = list(range(len(docs)))
            sort_ids.sort(key=lambda i: -answers_and_scores[i][1])
            answers_and_scores = [answers_and_scores[i] for i in sort_ids]
        if return_source and sort:
            docs = [docs[i] for i in sort_ids]
        if not return_score:
            answers = [a[0] for a in answers_and_scores]
        else:
            answers = answers_and_scores
        if return_source:
            if return_score:
                answers = [answers[i] + (docs[i],) for i in range(len(docs))]
            else:
                answers = [(answers[i], docs[i]) for i in range(len(docs))]
        return answers if return_all else answers[0]

    doc = docs
    input_ids = qa_tokenizer.encode(query, doc)

    if len(input_ids) > 512:
        sentences = nltk.sent_tokenize(doc)
        if len(sentences) == 1:
            if return_score:
                return '', -1000
            else:
                return ''
        else:
            return qa(sentences, query, return_score=return_score)
    sep_index = input_ids.index(qa_tokenizer.sep_token_id)
    num_seg_a = sep_index + 1
    num_seg_b = len(input_ids) - num_seg_a
    segment_ids = [0]*num_seg_a + [1]*num_seg_b
    start_scores, end_scores = qa_model(tf.constant([input_ids]),
                                 token_type_ids=tf.constant([segment_ids]))
    
    tokens = qa_tokenizer.convert_ids_to_tokens(input_ids)
    num_input_tokens = sep_index + 1
    answer_start = tf.argmax(start_scores[0][num_input_tokens:]) + num_input_tokens
    answer_end = tf.argmax(end_scores[0][num_input_tokens:]) + num_input_tokens

    answer = ' '.join(tokens[int(answer_start.numpy()): int(answer_end.numpy() + 1)])
    answer = answer.replace(' #', '').replace('#', '').replace('[CLS]', '').replace('[SEP]', '')
    if not return_score:
        return answer
    input_kws = set(extract_keywords_from_query(query.lower(), phrases=False))
    answer = answer.replace(' #', '').replace('#', '').replace('[CLS]', '').replace('[SEP]', '')
    answer_kws = set(extract_keywords_from_query(answer.lower(), phrases=False))
    num_input_kws = len(input_kws)
    input_kws.update(answer_kws)
    if len(input_kws) == num_input_kws:
        score = 0
    else:
        score = float((start_scores[0][answer_start] + end_scores[0][answer_end]))
    return answer, score



stop_words = stopwords.words('english')
stop_words.append('whose')





def _norm(x):
    x = x.strip()
    while '  ' in x:
        x = x.replace('  ', ' ')
    return x.lower()


def _underscore(x):
    return _norm(x).replace(' ', '_')




valuesfile = "values.json"

with open(valuesfile, 'r') as f:
    values = json.load(f)

def _find(lst, sublst):
    for i in range(len(lst)):
        flag = False
        for j in range(len(sublst)):
            if sublst[j] != lst[i + j]:
                flag = True
                break
        if not flag:
            return i
    return -1

def _window_overlap(s1, e1, s2, e2):
    return s2 <= e1 if s1 <s2 else s1 <= e2
class Nlp:
    def __init__(self,data_dir,schema_dir):
        self.data_dir=data_dir
        self.schema_dir=schema_dir
        self.data_process=data_utils(data_dir, schema_dir)
        
    def slot_fill(self,csv, q):
        # example: slot_fill(get_csvs()[2], "how many emarati men of age 22 died from stomach cancer in 2012")
        schema = self.data_process.get_schema_for_csv(csv)
        def _is_numeric(typ):
            # TODO
            return issubclass(column_types.get(typ), column_types.Number)
        slots = []
        mappings = {}
        for col in schema['columns']:
            colname = col['name']
            if 'keywords' in col.keys():
                keyword=col['keywords'][0]
                q=q.replace(colname,keyword)
            else:
                keyword=colname
            if colname == 'index':
                continue
            coltype = col['type']
            if coltype == "Categorical":
                mappings[colname] = col["mapping"]
    
            if _is_numeric(coltype):
                colquery="number of {}".format(keyword)
            else:
                colquery="which {}".format(keyword)
            
            val, score = qa(q, colquery, return_score=True)
            vt =  nltk.word_tokenize(val)
            start_idx = _find(nltk.word_tokenize(q), vt)
            end_idx = start_idx + len(vt) - 1
            print("filling slots:",colname, val, score)
            slots.append((colname, coltype, val, score, start_idx, end_idx))
        slots.sort(key=lambda x: -x[3])
        windows = []
        slots_filtered = []
        for s in slots:
            if s[-2] < 0:
                continue
            win = s[-2:]
            flag = False
            for win2 in windows:
                if _window_overlap(*(win + win2)):
                    flag = True
                    break
            if flag:
                continue
            windows.append(win)
            slots_filtered.append(s[:-2])
        slots = slots_filtered
    
        ret = []
        for s in slots:
            if s[1] == "FuzzyString":
                vals = values[s[0]]
                fs = column_types.FuzzyString(vals, exclude=s[0].split('_'))
                val = fs.adapt(s[2])
            elif s[1] == "Categorical":
                cat = column_types.Categorical(mappings[s[0]])
                val = cat.adapt(s[2])
            elif _is_numeric(s[1]):
    
                val = column_types.get(s[1])().adapt(s[2], context=q, allowed_kws=[s[0]])
            else:
                val = column_types.get(s[1])().adapt(s[2])
            if val is not None:
                ret.append((s[0], s[1], val, s[3]))
    
        return ret
    
    
    def validate_slots(self,cols, query, return_indices=False):
        assert cols
        if isinstance(cols, str):
            cols = [cols]
        max_seq_len = 64
        filter_cols = True
        inputs = [rerank_tokenizer.encode_plus(query, choice, add_special_tokens=True)
                    for choice in cols]
        max_len = min(max(len(t['input_ids']) for t in inputs), max_seq_len)
        input_ids = [t['input_ids'][:max_len] +
                        [0] * (max_len - len(t['input_ids'][:max_len])) for t in inputs]
        attention_mask = [[1] * len(t['input_ids'][:max_len]) +
                            [0] * (max_len - len(t['input_ids'][:max_len])) for t in inputs]
        token_type_ids = [t['token_type_ids'][:max_len] +
                        [0] * (max_len - len(t['token_type_ids'][:max_len])) for t in inputs]
        input_ids = tf.constant(input_ids)
        attention_mask = tf.constant(attention_mask)
        token_type_ids = tf.constant(token_type_ids)
        logits = rerank_model(input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids)[0]
        scores = []
        for logit in logits:
            neg_logit = logit[0]
            score = logit[1]
            if score > neg_logit or not filter_cols:
                scores.append(score - neg_logit)
        return scores
    
    def cond_map(self,s):
        data=conditions
        
        conds=[lem(i,pos='a') for i in s.split() if not i.isdigit()]
        
        for cond in conds:
            for k,v in data.items():
                  if cond in v:
                      num=s.split()[-1]
                      s=f'{k} {num}'
        return s
    
       
    
    def kword_extractor(self,q):
        ret=[]
        for t in nltk.word_tokenize(q):
            if t.lower() not in stop_words:
                kwd=lem(t.lower())
                ret.append(kwd)
        return ret               
    
    def unknown_slot_extractor(self,schema,sf_columns,ex_kwd):
        maxcount=0
        unknown_slot=None
        flag=False
        
        for col in schema["columns"]:
            if col["name"] not in sf_columns:
                col_kwds=[]    
                if '_' in col["name"]:
                    col_kwds.extend(col["name"].split("_"))
                else:
                    col_kwds.append(col["name"])
                if 'keywords' in col.keys():
                    col_kwds.extend(col["keywords"])
                    
                col_kwds=[lem(i.lower()) for i in col_kwds]
            
                count=len(set(col_kwds) & set(ex_kwd))
                
                if count>maxcount:
                    maxcount=count
                    unknown_slot=col["name"]
                   
                    flag=True  if col["type"] in ["Year","Integer","Decimal","Age"] else False
                    
        return unknown_slot,flag
    


            
    def csv_select(self,q):
        maxcount=0
        kwds=self.kword_extractor(q)
         
        with open('vocab.json') as f:
            vocab = json.load(f)
        for csv, v in vocab.items():
            kwds2 = [lem(i) for i in v]
            count = len([k for k in kwds2 if k in kwds])
            schema=self.data_process.get_schema_for_csv(os.path.join(self.data_dir,csv))
            name=schema["name"]
            priority=name.lower().split('_')
            check_kwd=self.data_process.kwd_checker(csv, vocab)
            if len(set(priority) & set(kwds))>0 and not any(i in priority for i in check_kwd):
                return os.path.join(self.data_dir,csv)
            if count>maxcount:
                maxcount=count
                selected_csv=csv
    
        
        if not maxcount:
            return None
        return os.path.join(self.data_dir,selected_csv)
    def get_sql_query(self,csv,q):
        sf=self.slot_fill(csv, q)
        sub_clause=''' WHERE {} = "{}" '''
        schema=self.data_process.get_schema_for_csv(csv)
        
        sf_columns=[i[0] for i in sf]
    
        ex_kwd=self.kword_extractor(q)
        unknown_slot,flag=self.unknown_slot_extractor(schema,sf_columns,ex_kwd)
        clause=Clause()
        question=""
    
        if flag: 
            for col in schema["columns"]:
                if "priority" in col.keys() and flag:
                    question=clause.adapt(q,inttype=True,priority=True)
                    
                else:   
                    question=clause.adapt(q,inttype=True)
    
        else:
            question=clause.adapt(q)
        if unknown_slot is None:
            unknown_slot='*'
        question=question.format(unknown_slot,schema["name"].lower())
        
        valmap = {}
        def get_key(val):
            return f"val_{len(valmap)}"
        print(sf)
        for i,s in enumerate(sf):
            col,val=s[0],s[2]
            typ = column_types.get(s[1])
            if i>0:
                sub_clause='''AND {} = "{}" '''
            if issubclass(typ, column_types.Number):
                val=self.cond_map(val)
                
            if issubclass(typ, column_types.String):
                k = get_key(val)
                valmap[k] = val
            else:
                k = val
            
    
            if any(i in conditions.keys() for i in k):
                
                subq=sub_clause.format(col, k)
                subq=subq.replace('=','')
                subq=subq.replace('"','')
            else:
                subq=sub_clause.format(col, k)
            
            
            question+=subq            
    
        
        return question, valmap
    
    
    
   

    
    
