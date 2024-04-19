import requests
from bs4 import BeautifulSoup
import csv

def scrape_page(soup, quotes):
    #finds all the div elements named quote on the page
    quotes_elements = soup.find_all('div', class_='quote')

    #iterate over those div elements to extract desired data
    #Looking for quote text, quotes author, and tags for the quote

    for quotes_elements in quotes_elements:
        #extract text
        text = quotes_elements.find('span', class_='text').text

        #extract author
        author = quotes_elements.find('small', class_='author').text

        #extract tags. There is a div called tag and within that are tag classes with <a> element for href
        tag_elements = quotes_elements.find('div', class_='tags').find_all('a', class_='tag')

        #store tags in an array
        tags = []
        for tag_element in tag_elements:
            tags.append(tag_element.text)


        #put text , author, and tags array into the quotes array as a dictionary

        quotes.append(
            {
                'text':text,
                'author': author,
                'tags':', '.join(tags)
            }

        )

#target url
base_url = input('What site would you like to scrape: \n')
print(base_url)
#base_url = 'https://quotes.toscrape.com'

#defining user agent header
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}

#retrieving target url
page = requests.get(base_url, headers=headers)

#parsing target page with BeautifulSoup
soup = BeautifulSoup(page.text, 'html.parser')

#intializing the quotes array variable

quotes = []

#scrape homepage
scrape_page(soup, quotes)

#Get next element
next_li_element = soup.find('li', class_='next')
print(next_li_element)
#if there is a next page to scrape
while next_li_element is not None:
    next_page = next_li_element.find('a', href=True)['href']

    #get new page
    page = requests.get(base_url + next_page, headers=headers)

    #parse new page
    soup = BeautifulSoup(page.text, 'html.parser')

    #scrape new page
    scrape_page(soup,quotes)

    #looking for the "Next ->" HTML element in the new page
    next_li_element = soup.find('li', class_='next')

#reading quotes.csv file and creating one if not created
csv_file = open('quotes.csv', 'w', encoding='utf-8', newline='')

#intialize writer
writer = csv.writer(csv_file)

#write the column headers
writer.writerow(['Quote', 'Author', 'Tags'])

#writing each row of the CSV
for quote in quotes:
    writer.writerow(quote.values())

#terminating process
csv_file.close()



