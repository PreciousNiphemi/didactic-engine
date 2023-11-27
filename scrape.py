import json
import requests.cookies
from linkedin_api import Linkedin
from requests.cookies import cookiejar_from_dict
import pandas as pd
import logging
import time

def extract_string_after_last_slash(url):
    if "/in" in url:
        return url.rsplit('/', 1)[-1]
    else:
        return ""

# Set up logging
logging.basicConfig(filename='script.log', level=logging.INFO)

cookies = cookiejar_from_dict(
{
"liap": "true",
"li_at": "AQEDAS_hWOYBQURIAAABi6wceCEAAAGL9DH-jFYAJA_Bzof15PuhvazZHKyEAC00rc331wjSoVvh04CaxEpwKo36SjBtDLSzSeQW4MJzO54nroVTzdUZEUWhgB5R0_tIJolArbY2V4NLkyb4CqJIOGaI",
"JSESSIONID": '"ajax:0334806952564072133"',
}
)
linkedin = Linkedin("", "", debug=True, cookies=cookies)

# Read the CSV file
df = pd.read_csv('./Connecteam.csv')  # replace 'file.csv' with your CSV file name

def extract_posts(df):
    # Initialize an empty dictionary to store the results
    results = {}

    # Initialize a counter
    counter = 0

    # Iterate over the column
    for url in df['Profile URl']:  # replace 'column_name' with your column name
        if isinstance(url, str):  # check if url is a string
            username = extract_string_after_last_slash(url)
            if username:
                try:
                    start_time = time.time()
                    s = linkedin.get_profile_posts(username, post_count=800)
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    logging.info(f"Extracted posts for {username} in {elapsed_time} seconds")

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

                    # Increment the counter
                    counter += 1

                    # If counter reaches 50, pause for 10-15 minutes and reset counter
                    if counter == 50:
                        time.sleep(600)  # pause for 10 minutes
                        counter = 0  # reset counter

                except Exception as e:
                    logging.error(f"Error occurred while processing {username}: {e}")
            else:
                logging.info(f"Skipped {url} due to invalid format")
        else:
            logging.error(f"Invalid URL: {url}")

    # Return the results
    return results

# Start the script
logging.info('Script started')
start_time = time.time()

# Call the function and store the results
try:
    results = extract_posts(df)
except Exception as e:
    logging.error(f"Script stopped due to error: {e}")
finally:
    # End the script
    end_time = time.time()
    elapsed_time = end_time - start_time
    logging.info(f'Script ended, total time: {elapsed_time} seconds')

    # Write the results into a file as JSON
    with open('data.json', 'w') as f:
        json.dump(results, f)