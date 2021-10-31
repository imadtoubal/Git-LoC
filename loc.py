import sys

import numpy as np
import pandas as pd
import requests
from tqdm import tqdm

LOC_URL = 'https://api.codetabs.com/v1/loc?github=[username]/[reponame]'
GITHUB_URL = 'https://api.github.com/users/[username]/repos'

COUNT_BLANKS = False
COUNT_COMMENTS = False
COUNT_FORKS = False

def get_loc(username, reponame):
    loc_url = LOC_URL.replace('[username]', username)
    loc_url = loc_url.replace('[reponame]', reponame)
    response = requests.get(loc_url)
    if response.status_code == 200:
        return response.json()
    else:
        print('Error: {}'.format(response.status_code))
        # sys.exit(1)

def get_repos(username):
    github_url = GITHUB_URL.replace('[username]', username)
    response = requests.get(github_url)
    if response.status_code == 200:
        return response.json()
    else:
        print('Error: {}'.format(response.status_code))
        # sys.exit(1)

if __name__ == '__main__':
    assert len(sys.argv) != 3, 'Usage: python3 loc.py [username]'
    username = sys.argv[1]
    
    repos = get_repos(username)
    repos = [repo['name'] for repo in repos if (COUNT_FORKS or repo['fork'] == False)]
    
    result_dict = {}
    for repo_name in tqdm(repos, desc="Querying repos"):
        response = get_loc(username, repo_name)
        current_repo_count = {}
        for r in response:
            current_repo_count[r['language']] = r['lines']
            if not COUNT_BLANKS:
                current_repo_count[r['language']] -= r['blanks']
            if not COUNT_COMMENTS:
                current_repo_count[r['language']] -= r['comments']
                
        result_dict[repo_name] = current_repo_count
        
    # Aggregate the lines of code for each language
    aggregated_count = {}
    for repo_name, repo_count in tqdm(result_dict.items(), desc="Aggregating"):
        for lang, count in repo_count.items():
            if lang not in aggregated_count:
                aggregated_count[lang] = count
            else:
                aggregated_count[lang] += count
    df = pd.DataFrame(result_dict).T.fillna(0)
    df['Repository'] = df.index
    df.index = np.arange(len(df))
    # Add the aggregated count as new row
    df = df.append(df.sum(axis=0), ignore_index=True)
    df.iloc[-1,-1] = 'Total'
    df.to_csv(f'results-{username}.csv')
    

            
                
        
        



