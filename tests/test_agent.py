

from tableqa.agent import Agent
import pytest
import os

currpath=os.path.abspath(os.path.dirname(__file__))

def test_query():
    agent=Agent(os.path.join(currpath,"cleaned_data"))
    qmaps={'how many nuclear medicine activities in 2012':'SELECT COUNT(activity_type) FROM activities_data WHERE activity_type_chapter = "Nuclear Medicine" AND year = "2012" ',
            'find me the diseases having above 3000 cases':'SELECT disease FROM communicable_diseases_data WHERE cases  > 3000 ',
            'which are the activities in 2011':'SELECT activity_type FROM activities_data WHERE year = "2011" ',
            'find the maximum number of cases':'SELECT MAX(cases) FROM communicable_diseases_data',
            'Get me the average age of stomach cancer deaths':'SELECT AVG(death_count) FROM cancer_death_data WHERE cancer_site = "Stomach" '
            }
    for q,sql in qmaps.items():
        res=agent.get_query(q)
        assert res.strip() ==sql.strip()
        
def test_query_schema():
    agent=Agent(os.path.join(currpath,"cleaned_data"),os.path.join(currpath,"schema"))
    qmaps={'how many people died of stomach cancer in 2011':'SELECT SUM(death_count) FROM cancer_death WHERE cancer_site = "Stomach" AND year = "2011" ',
            'how many deaths of age below 40 had stomach cancer':'SELECT SUM(death_count) FROM cancer_death WHERE cancer_site = "Stomach" AND age  < 40 ',
            'which are the activities in 2011':'SELECT activity_type_chapter FROM activities WHERE year = "2011" ',
            'find the maximum number of cases':'SELECT MAX(cases) FROM communicable_diseases ',
            'Get me the average age of stomach cancer deaths':'SELECT AVG(death_count) FROM cancer_death WHERE cancer_site = "Stomach" '
            }
    for q,sql in qmaps.items():
        res=agent.get_query(q)
        assert res.strip() ==sql.strip()
        
        
if __name__ == '__main__':
    pytest.main([__file__])
