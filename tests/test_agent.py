

from tableqa.agent import Agent
import pytest
import os
import pandas as pd
import json



currpath=os.path.abspath(os.path.dirname(__file__))

df=pd.read_csv(os.path.join(os.path.join(currpath,"cleaned_data"),'Cancer Death - Data.csv'))

with open(os.path.join(os.path.join(currpath,"schema"),'Cancer Death - Data.json')) as f:
    schema=json.load(f)


def test_query():
    agent=Agent(os.path.join(currpath,"cleaned_data"))
    qmaps={'how many nuclear medicine activities in 2012':"SELECT COUNT(activity_type) FROM activities_data WHERE activity_type_chapter = 'Nuclear Medicine' AND year = '2012' ",
            'find me the diseases having above 3000 cases':'SELECT disease FROM communicable_diseases_data WHERE cases  > 3000 ',
            'which are the activities in 2011':"SELECT activity_type,activity_type_chapter FROM activities_data WHERE year = '2011' ",
            'find the maximum number of cases':"SELECT MAX(cases) FROM communicable_diseases_data",
            'Get me the average of stomach cancer deaths':"SELECT AVG(death_count) FROM cancer_death_data WHERE cancer_site = 'Stomach' ",
            'how many activities between 2011 and 2014':"SELECT COUNT(activity_type) FROM activities_data WHERE year  BETWEEN 2011 AND 2014"
            }
    for q,sql in qmaps.items():
        res=agent.get_query(q)
        if res.strip() != sql.strip():
            print("question",q)
            print("predicted",res)
            print("actual",sql)
            raise AssertionError
        
def test_query_schema():
    agent=Agent(os.path.join(currpath,"cleaned_data"),os.path.join(currpath,"schema"))
    qmaps={'how many people died of stomach cancer in 2011':"SELECT SUM(death_count) FROM cancer_death WHERE cancer_site = 'Stomach' AND year = '2011' ",
            'how many deaths of age below 40 had stomach cancer':"SELECT SUM(death_count) FROM cancer_death WHERE cancer_site = 'Stomach' AND age  < 40 ",
            'which are the activities in 2011':"SELECT activity_type_chapter,activity_type FROM activities WHERE year = '2011' ",
            'find the maximum number of cases':"SELECT MAX(cases) FROM communicable_diseases ",
            'Get me the average of stomach cancer deaths':"SELECT AVG(death_count) FROM cancer_death WHERE cancer_site = 'Stomach' ",
            'how many people between age 30 and 40 died of stomach cancer':"SELECT SUM(death_count) FROM cancer_death WHERE cancer_site = 'Stomach' AND age  BETWEEN 30 AND 40 "
            }
    for q,sql in qmaps.items():
        res=agent.get_query(q)
        if res.strip() != sql.strip():
            print("question",q)
            print("predicted",res)
            print("actual",sql)
            raise AssertionError


def test_query_df():
    agent=Agent(df)
    q='Get me the average age of stomach cancer in male'
    sql="SELECT AVG(age) FROM dataframe WHERE gender = 'Male' AND cancer_site = 'Stomach' "  
    res=agent.get_query(q)
    if res.strip() != sql.strip():
        print("question",q)
        print("predicted",res)
        print("actual",sql)
        raise AssertionError

def test_query_df_schema():
    agent=Agent(df,schema)
    q='how many people died of stomach cancer in 2011'
    sql="SELECT SUM(death_count) FROM cancer_death WHERE cancer_site = 'Stomach' AND year = '2011' "       
    res=agent.get_query(q)
    if res.strip() != sql.strip():
        print("question",q)
        print("predicted",res)
        print("actual",sql)
        raise AssertionError
    
        
if __name__ == '__main__':
    pytest.main([__file__])
