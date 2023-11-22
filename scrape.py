import json
import requests.cookies
from linkedin_api import Linkedin
from requests.cookies import cookiejar_from_dict
import pandas as pd

def extract_string_after_last_slash(url):
    return url.rsplit('/', 1)[-1]

cookies = cookiejar_from_dict(
{
"liap": "true",
"li_at": "AQEDAS_hWOYBQURIAAABi6wceCEAAAGL9DH-jFYAJA_Bzof15PuhvazZHKyEAC00rc331wjSoVvh04CaxEpwKo36SjBtDLSzSeQW4MJzO54nroVTzdUZEUWhgB5R0_tIJolArbY2V4NLkyb4CqJIOGaI",
"JSESSIONID": '"ajax:0334806952564072133"',
}
)
linkedin = Linkedin("", "", debug=True, cookies=cookies)

# Read the CSV file
df = pd.read_csv('./test.csv')  # replace 'file.csv' with your CSV file name

def extract_posts(df):
    # Initialize an empty dictionary to store the results
    results = {}

    # Iterate over the column
    for url in df['Profile URl']:  # replace 'column_name' with your column name
        if isinstance(url, str):  # check if url is a string
            username = extract_string_after_last_slash(url)
            s = linkedin.get_profile_posts(username, post_count=800)

            # Extract the text and url into a separate array
            posts = []
            for post in s:
                if 'commentary' in post:
                    text = post['commentary']['text']['text']
                    url = next((action['url'] for action in post['updateMetadata']['updateActions']['actions'] if 'url' in action), None)
                    if url:
                        posts.append({'postDetails': text, 'postLink': url})
                elif 'resharedUpdate' in post and 'commentary' in post['resharedUpdate']:
                    text = post['resharedUpdate']['commentary']['text']['text']
                    url = next((action['url'] for action in post['updateMetadata']['updateActions']['actions'] if 'url' in action), None)
                    if url:
                        posts.append({'postDetails': text, 'postLink': url})

            # Add the posts to the results dictionary
            results[username] = posts
        else:
            print(f"Invalid URL: {url}")

    # Return the results
    return results

# Call the function and store the results
results = extract_posts(df)

# Write the results into a file as JSON
with open('data.json', 'w') as f:
    json.dump(results, f)