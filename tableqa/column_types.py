import numpy as np
import nltk
import datetime




def _overlap(x, y, exclude=[]):
    exclude = [t.lower() for t in exclude]
    xt = nltk.word_tokenize(x.lower())
    yt = nltk.word_tokenize(y.lower())
    ret = 0
    for t in xt:
        if t in yt and t not in exclude:
            ret += 1
    return ret


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

class ColumnType(object):
    sql_type = "VARCHAR(1000)"
    def __init__(self):
        if self.__class__ == ColumnType:
            raise Exception("Abstract class.")
    def adapt(self, x):
        return x


class String(ColumnType):
    pass


class Number(ColumnType):
    def __init__(self, min_value=None, max_value=None):
        if self.__class__ == Number:
            raise Exception("Abstract class.")
        self.min_value = None
        self.max_value = None

    def adapt(self, x, context=None, allowed_kws=[]):
        allowed_kws = [kw.lower() for kw in allowed_kws]
        allowed = [
            "than",
            "above",
            "below",
            "from",
            "to",
            "between",
            "greater",
            "bigger",
            "larger",
            "more",
            "less",
            "between",
            "and"
        ] + allowed_kws
        def isnum(x):
            try:
                float(x)
                if self.min_value is not None and float(x) < self.min_value:
                    return False
                if self.max_value is not None and float(x) > self.max_value:
                    return False
                return True
            except:
                return False
        xt = nltk.word_tokenize(x.lower())
        nums = len([t for t in xt if isnum(t)])
        if not nums:
            return None
        xt = [t for t in xt if isnum(t) or t in allowed]
        if context is not None:
            ct = nltk.word_tokenize(context.lower())
            idx = _find(ct, xt) # TODO multiple instances
            idx2 = idx + len(xt) - 1
            while idx > 0 and (isnum(ct[idx - 1]) or ct[idx - 1] in allowed):
                idx -= 1
            while idx2 < len(ct) - 1 and (isnum(ct[idx2 + 1]) or ct[idx2 + 1] in allowed):
                idx2 += 1
            return ' '.join([w for w in nltk.word_tokenize(context)[idx: idx2 + 1] if w.lower() not in allowed_kws])
        return x

class Integer(Number):
    sql_type = "INT"


class Age(Integer):
    def __init__(self):
        super(Age, self).__init__(1, 100)


class Decimal(Number):
    sql_type = "DECIMAL(10, 2)"


class FuzzyString(String):
    def __init__(self, values, exclude=[]):
        self.values = values
        self.exclude = exclude.copy()

    def adapt(self, x):
        scores = [_overlap(x, v, self.exclude) for v in self.values]
        idx = np.argmax(scores)
        mx = scores[idx]
        if mx == 0:
            return None
        return self.values[idx]


class Year(Integer):
    def adapt(self, x, context=None, *args, **kwargs):
        # TODO
        x = x.lower()
        curr = datetime.datetime.now().year
        if x == "last year" or x == "previous year":
            return curr - 1
        elif x == "next year":
            return curr + 1
        elif x == "current year" or x == "this year":
            return curr
        else:
            allowed = [
                "than",
                "above",
                "below",
                "from",
                "to",
                "between",
                "greater",
                "bigger",
                "larger",
                "more",
                "less",
                "between",
                "and"]
            xt = nltk.word_tokenize(x.lower())
            xt = [t for t in xt if t not in ['the' 'year']]
            flag = False
            for t in xt:
                if t.isdigit():
                    flag = True
                    if float(t) >= 3000 or float(t) <= 1900:
                        return None
                elif t not in allowed:
                    return None
            if not flag:
                return
            if context is not None:
                ct = nltk.word_tokenize(context.lower())
                idx = _find(ct, xt) # TODO multiple instances
                idx2 = idx + len(xt) - 1
                while idx > 0 and (ct[idx - 1].isdigit() or ct[idx - 1] in allowed):
                    idx -= 1
                while idx2 < len(ct) - 1 and (ct[idx2 + 1].isdigit() or ct[idx2 + 1] in allowed):
                    idx2 += 1
                return ' '.join(nltk.word_tokenize(context)[idx: idx2 + 1])
            return x

class Categorical(String):

    def __init__(self, mapping):
        self.mapping = mapping

    def adapt(self, x):
        scores = []
        for k, vs in self.mapping.items():
            scores.append((k, max([_overlap(x, v) for v in vs])))
        mx = max(scores, key=lambda x: x[1])
        if mx[1] == 0:
            return None
        return mx[0]



def get(name):
    return globals()[name]
