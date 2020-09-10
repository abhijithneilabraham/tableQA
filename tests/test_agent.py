

from tableqa.agent import Agent
import pytest
import os

currpath=os.path.abspath(os.path.dirname(__file__))

def test_query():
    agent=Agent(os.path.join(currpath,"cleaned_data"))
    qmaps={'how many nuclear medicine activities in 2012':'SELECT COUNT(Activity_Type) FROM activities_data WHERE Activity_Type_Chapter = "Nuclear Medicine" AND Year = "2012" ',
            'find me the diseases having above 3000 cases':'SELECT Disease FROM communicable_diseases_data WHERE Cases  > 3000 ',
            'which are the activities in 2011':'SELECT Activity_Type FROM activities_data WHERE Year = "2011" ',
            'find the maximum number of cases':'SELECT MAX(Cases) FROM communicable_diseases_data',
            'Get me the average age of stomach cancer deaths':'SELECT AVG(Death_Count) FROM cancer_death_data WHERE Cancer_site = "Stomach" '
            }
    for q,sql in qmaps.items():
        res=agent.get_query(q)
        assert res.strip() ==sql.strip()
        
def test_query_schema():
    agent=Agent(os.path.join(currpath,"cleaned_data"),os.path.join(currpath,"schema"))
    qmaps={'how many people died of stomach cancer in 2011':'SELECT SUM(Death_Count) FROM cancer_death WHERE Cancer_site = "Stomach" AND Year = "2011" ',
            'how many deaths of age below 40 had stomach cancer':'SELECT SUM(Death_Count) FROM cancer_death WHERE Cancer_site = "Stomach" AND age  < 40 ',
            'which are the activities in 2011':'SELECT Activity_Type_Chapter FROM activities WHERE Year = "2011" ',
            'find the maximum number of cases':'SELECT MAX(Cases) FROM communicable_diseases ',
            'Get me the average age of stomach cancer deaths':'SELECT AVG(Death_Count) FROM cancer_death WHERE Cancer_site = "Stomach" '
            }
    for q,sql in qmaps.items():
        res=agent.get_query(q)
        assert res.strip() ==sql.strip()
        
        
if __name__ == '__main__':
    pytest.main([__file__])
