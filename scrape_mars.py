

from splinter import Browser
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd

# Use Chrome to scrape the following urls
def init_browser():
    executable_path = {"executable_path": "chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    """
    We will scrape latest NASA Mars News, JPL Mars Space Images, lateset Mars weather, Mars Facts, Mar's hemispheres images from differents url
    and return all results in a dictionary
    
    """
    # Store all the data we scraped in a dictionary
    Mars_info = {}

    # -----------------------------
    # 1. The latest NASA Mars News
    #------------------------------
    # URL of page to be scraped
    url= "https://mars.nasa.gov/news/"

    # Retrieve page with the requests module
    browser = init_browser()
    browser.visit(url)
    soup = bs(browser.html, 'html.parser')
    # Collect the latest News Title and Paragraph Text as a dictionary, set title as key, paragraph as value.
    News_result = soup.find("li",class_="slide")

    # Identify title of news
    news_title = News_result.find('div',{'class':'content_title'}).text
    # Identify paragraghy
    new_para = News_result.find('div',{'class':'article_teaser_body'}).text
    # Store title and para in the dictionary
    Mars_info["news_title"] = news_title
    Mars_info['news_para'] = new_para
    
   
    
    # ------------------------   
    # 2.JPL Mars Space Images
    # ------------------------
    # Use chrome to scrape
    browser = init_browser()
   
    # URL of page to be scraped
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)
    # HTML object
    html = browser.html
    # Parse HTML with Beautiful Soup
    soup = bs(html, 'html.parser')
    # Retrieve full size image url
    article = soup.find("li",class_="slide")
    featured_image_url=article.find("img",class_='thumb')['src']
    # Get full url
    featured_image_url = url[:24] + featured_image_url
    # Store the latest feature image url in the dictionary
    Mars_info['featured_image_url'] = featured_image_url


    # ------------------------
    # 3. lateset Mars weather
    # -----------------------
    #URL of page to be scraped
    url = "https://twitter.com/marswxreport?lang=en"
    response = requests.get(url)
    soup = bs(response.text, 'html.parser')
    # Scrape weather from tweets about "Mars Weather"
    weather_list = soup.find_all("p",class_="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text")
    # Make sure the data we get is valid and complete which should include with "high" "low" "gusting"
    for weather in weather_list:
        try:
            mars_weather = weather.text
            mars_weather_1 = [i.lower() for i in mars_weather.split(" ")]
            # We hope the weather data is valid and complited which should include word"high","low","gusting"
            if ("low" in mars_weather_1) and ("high" in mars_weather_1) and ("gusting" in mars_weather_1):
                if mars_weather_1[-1].split(".")[0]=="hpapic" :
                    mars_weather = mars_weather[:-26]
                Mars_info['mars_weather'] = mars_weather
                break
        except:
            pass
   

    # -----------------
    # 4. Mars Facts
    # -----------------
    # URL of page to be scraped
    url = "https://space-facts.com/mars/"
    # Use Panda's 'read_html' to parse the url
    tables = pd.read_html(url)
    Mars_fact_df = tables[0]
    # change columns name
    Mars_fact_df.columns = ['Description','value']
    # Delete ":" in values of the first column
    Mars_fact_df['Description']= Mars_fact_df['Description'].apply(lambda x: x.rstrip(":")) 
    print(Mars_fact_df)   

    # Convert dataframe as html table and delete extra "\n"
    html_table = Mars_fact_df.to_html()
    html_table = html_table.replace("\n","")
    # Delete the frist table head
    html_table = html_table.replace("<th></th>","")
    # Change text align from right to center
    html_table = html_table.replace("right","center")

    # Delete index
    for i in range(len(Mars_fact_df)):
        str = f"<th>{i}</th>"
        html_table = html_table.replace(str,"")
    

    # Store html table in the dictionary
    Mars_info['Mars_Facts'] = html_table
       
    #----------------------------
    # 5. Mar's hemispheres images
    #----------------------------
    # Store hemispheres name and url 
    hemis_name_list=[]
    url_list = []
    image_url_list = []
    
    # URL of page to be scraped
    url= "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    response= requests.get(url)
    soup = bs(response.text, "html.parser")

    # Get Mars hemisphere name
    itemLink_1 = soup.find_all("div",class_ = "description")
    for item in itemLink_1:
        Hemis_name = item.find("h3").text
        Hemis_name = "_".join(Hemis_name.split(" "))
        hemis_name_list.append(Hemis_name)

    # Get Mars hemisphere image url
    itemLink_2 = soup.find_all("a",class_ = "itemLink product-item")
    for item in itemLink_2:
        url=item['href']
        expand_url = 'https://astrogeology.usgs.gov' + url
        url_list.append(expand_url)
    
    # Scrape the hemisphere urls
    image_url_list=[]
    for url in url_list:
        response = requests.get(url)
        soup = bs(response.text,"html.parser")
        image_url = soup.find("img",class_="wide-image")['src']
        image_url = 'https://astrogeology.usgs.gov' + image_url
        image_url_list.append(image_url)

    # Store hemisphere name and image url as dictionary form
    for i in range(len(hemis_name_list)):
        Mars_info[hemis_name_list[i]] = image_url_list[i]

    # Close the browser after scraping
    browser.quit()

    return Mars_info
    

