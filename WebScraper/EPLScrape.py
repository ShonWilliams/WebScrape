import csv
import io
import time

import requests
URL = "https://fbref.com/en/comps/9/2022-2023/2022-2023-Premier-League-Stats"

data = requests.get(URL)

##print(data.text) Displays html text
##We need to go to each indiviual teams url to extract their scores and fixtures
##So first need to find their url from the homepage table. To find that, right click on team and inspect in chrome

from bs4 import BeautifulSoup

soup = BeautifulSoup(data.text, 'lxml')

##Find table in html where all teams urls are stored select allows you to choose from different classes an ids or anything else
standingsTable = soup.select(("table.stats_table"))[0]

##Findall  'a' tags in table findall only finds tag
link = standingsTable.find_all('a')

##get href property of each link
link = [l.get('href') for l in link]

##so basically I am filtering the homepage for just the table then filtering the table for the 'a' tags
##Then I'm going to have to filter the 'a' tags to find only the 'a' tags that I want
## team 'a' tag all have squad in the name, so it will be how I filter the 'a' tags
link = [l for l in link if '/squad']
##links doesn't have full url so have to format string to be what I want
teamLinks = [f'http://fbref.com{l}' for l in link]

teamLinks = teamLinks[0]
data = requests.get(teamLinks)

##pandas has a method that turns data into a dataframe
##basically makes a table of data

import pandas as pd
from io import StringIO
##match looks for specific string inside table
##read_html scans table tags on the page.
##Basically I am scanning the page for tables with Scores and Fixtures string

matches = pd.read_html(teamLinks, match='Scores & Fixtures')

#Start getting Shooting table
soup = BeautifulSoup(data.text, 'lxml')
links = soup.find_all('a')
links = [l.get('href') for l in links]
links = [l for l in links if l and 'all_comps/shooting/' in l]
##There are actualy four uses of the same link so just need one.
links = links[0]

data = requests.get(f'http://fbref.com{links}')
url = StringIO(data.text)

shooting = pd.read_html(url, match='Shooting')[0]

shooting.columns = shooting.columns.droplevel()

##Have to merge two dataframes together

team_data = matches[0].merge(shooting[['Date','Sh','SoT','Dist','FK','PK','PKatt']], on='Date')

#scale for multiple teams and years

years =list (range(2022,2020,-1))

all_matches = []

standingsurl = 'http://fbref.com/en/comps/0/Premier-League-Stats'

for year in years:
    data = requests.get(URL)
    soup = BeautifulSoup(data.text, 'lxml')

    ##Find table in html where all teams urls are stored select allows you to choose from different classes an ids or anything else
    standingsTable = soup.select(("table.stats_table"))[0]

    ##Findall  'a' tags in table findall only finds tag
    link = standingsTable.find_all('a')

    ##get href property of each link
    link = [l.get('href') for l in link]

    ##so basically I am filtering the homepage for just the table then filtering the table for the 'a' tags
    ##Then I'm going to have to filter the 'a' tags to find only the 'a' tags that I want
    ## team 'a' tag all have squad in the name. so it will be how I filter the 'a' tags
    link = [l for l in link if '/squad' in l]
    ##links doesn't have full url so have to format string to be what I want
    teamUrls = [f'http://fbref.com{l}' for l in link]

    previousSeason = soup.select('a.prev')[0].get('href')
    standingsurl = f'htt//fbref.com/{previousSeason}'
    for teamUrl in teamUrls:
        teamName = teamUrl.split("/")[-1].replace('-Stats',"").replace("-"," ")

        data = requests.get(teamUrl)
        matches = pd.read_html(teamUrl, match='Scores & Fixtures')


        soup = BeautifulSoup(data.text, 'lxml')
        links = soup.find_all('a')
        links = [l.get('href') for l in links]
        links = [l for l in links if l and 'all_comps/shooting/' in l]
        ##There are actualy four uses of the same link so just need one.

        data = requests.get(f'http://fbref.com{links[0]}')
        url = StringIO(data.text)

        shooting = pd.read_html(url, match='Shooting')[0]

        shooting.columns = shooting.columns.droplevel()

        ##Have to merge two dataframes together
    try:
        team_data = matches[0].merge(shooting[['Date', 'Sh', 'SoT', 'Dist', 'FK', 'PK', 'PKatt']], on='Date')
    except ValueError:
        continue

    team_data = team_data[team_data['Comp'] == 'Premier League']
    team_data['Season'] = year
    team_data['Team'] = teamName
    all_matches.append(team_data)
    time.sleep(1)

matchDF = pd.concat(all_matches)

matchDF.columns = [c.lower() for c in matchDF.columns]

matchDF.to_csv('matches.csv')