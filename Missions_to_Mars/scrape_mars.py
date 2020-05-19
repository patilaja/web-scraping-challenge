#Import dependecies
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import time

#Set global variables to store the data from the funtions
#Deafult parser - it can be orriden at fucntion level
parser= 'html.parser'
#Default browser wait time to allow page load. 
wait_time = 5
#Save news tilte and news paragraph
news_title=""
news_p=""
#Featured Image URL
featured_image_url=""
#Mars weather
mars_weather=""
#Mars Fact
mars_fact_table=""
#Mars high res image and title dictionary 
hemisphereimageurls = {} 

#@NOTE: please replace the path with your actual path to the chromedriver
#Set Chrome browser path
executable_path = {'executable_path': '/Users/anuaj/bin/chromedriver'}
browser = Browser('chrome', **executable_path, headless=True)

#Function to get Beatifulsoup oject for the given url and parser
def getSoupObject(url,parser,sleep_time):

    #Visit url
    browser.visit(url)

    #Add wait time to load browser
    time.sleep(sleep_time)

    #Set beautifulsoup object
    html = browser.html
    soup = BeautifulSoup(html,parser)

    #Return Beatifulsoup oject
    return soup

#Function to scrape data from various websites
def scrape():

    #NASA Mars News
    mars_news =getMarsNews()
    #Parse mNews
    try:
        if len(mars_news.split("**"))>1:
            news_title = mars_news.split("**")[0]
            news_p = mars_news.split("**")[1]
    except:
        news_title = ""
        news_p = ""

    #JPL Mars Space Images - Featured Image
    featured_image_url = getMarsSpaceImage()

    #Mars Weather
    mars_weather = getMarsWeather()

    #Mars Facts
    mars_fact_table = getMarsFacts().replace("\n","")

    #Get Mars Title and high res image
    hemisphereimageurls = getMarsTitleImage()

    #Close the browser
    browser.quit()

    #Build Dictionary of objects
    mars_doc= {  "news_title": news_title, "news_p": news_p,
                 "featuredimageurl": featured_image_url,
                 "mars_weather": mars_weather,
                 "mars_facts" : mars_fact_table,
                 "hemisphereimageurls": hemisphereimageurls }
    
    #Return scrapping results             
    return mars_doc

#Function to collect the latest News Title and Paragraph Text from https://mars.nasa.gov/. 
def getMarsNews():
       
    #Mars news URL
    mars_news_url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    
    #Call function to get Beautifulsoup object
    mars_news_soup =  getSoupObject(mars_news_url,parser,wait_time)

    #Review webpage and get html tag and class for searcg
    mars_news = mars_news_soup.find_all('div', class_='list_text')

    #Loop through news
    for news in mars_news:
        try:
            #Save news tilte and news paragraph
            ntitle= news.find('div', class_='content_title').text
            newsp=news.find('div', class_='article_teaser_body').text
            #Return results (Adding "**" as seperator)
            return ntitle+"**"+newsp
        except:
            #If error continue to next news - this is simply to make sure we have news title and news paragraph 
            return "Error has occured-getMarsNews"

#Function to get Featured Mars Image  
def getMarsSpaceImage():
    #JPL base url
    jpl_base_url ='https://www.jpl.nasa.gov'

    #JPL seach url 
    jpl_url = 'https://www.jpl.nasa.gov/spaceimages/details.php?id=PIA02570'
    
    #Call function to get Beautifulsoup object
    jpl_soup =  getSoupObject(jpl_url,parser,wait_time)

    #Find the figure tage with ledge class with soup oject 
    jpl_image_urls = jpl_soup.find_all('figure', class_='lede')

    #Get to specific URL
    for jpg_image_url in jpl_image_urls:
        return jpl_base_url+jpg_image_url.find("a")["href"]
    


#Function to get Mars Weather from twitter account 
def getMarsWeather():
    #Mars weather tweeter handle
    mars_weather_tweet_handle="https://twitter.com/marswxreport?lang=en"

    #Call function to get Beautifulsoup object
    mars_weather_tweet_soup =  getSoupObject(mars_weather_tweet_handle,parser,20)

    #Parse tweet page using span tag and class
    mars_weather_tweets= mars_weather_tweet_soup.find_all("span",class_="css-901oao css-16my406 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0")

    #Loop through tweets - we just need latest
    for mars_weather_tweet in mars_weather_tweets:
        #Get the Insight text - this is where weather info starts
        try:
            if (mars_weather_tweet.text.split()[0]=="InSight"):
                #Return result
                return mars_weather_tweet.text
        except:
            return "Error has occured - getMarsWeather"
    
      
#Function to get Mars Facts from  https://space-facts.com/mars/ 
def getMarsFacts():
     #Mars fact URL
    mars_fact_url="https://space-facts.com/mars/"

    #Use Pandas to get html table 
    mars_fact_dfs = pd.read_html(mars_fact_url)

    #Get first table and display
    mars_fact_df=mars_fact_dfs[0]

    #Rename df columns
    mars_fact_df= mars_fact_df.rename(columns={0:"Description",1:"Value"})

    #Covert to html string
    return mars_fact_df.to_html(index=False)   
    

#Function to get title and high resolution images for each of Mar's hemispheres
def getMarsTitleImage():
    #Mars base url
    mars_hemispheres_base_url="https://astrogeology.usgs.gov"

    #Mars Hemispheres URL
    mars_hemispheres_url="https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"

    #Call function to get Beautifulsoup object
    mars_hemispheres_soup = getSoupObject(mars_hemispheres_url,parser,20)

    #Search through html document to get to list of items
    mars_hemispheres= mars_hemispheres_soup.find_all("div",class_="item")

    #Let's build title list and page name list that will give us high res image
    titles=[]
    hemisphere_urls=[]

    #Loop through beautifulsoup results
    for mars_hemisphere in mars_hemispheres:
        #Search for h3 tag to get title
        mars_title =mars_hemisphere.find("h3").text
        #Append title to list
        titles.append(mars_title)
        #Get page reference
        pagelink=mars_hemispheres_base_url +mars_hemisphere.a['href']
        #Sppend page link to list
        hemisphere_urls.append(pagelink)
    
    #Get List of high res image
    hemisphere_full_img=[]

    #Let's loop through each URL
    for hemisphere_url in hemisphere_urls:

        #Call function to get Beautifulsoup object
        hemisphere_full_soup = getSoupObject(hemisphere_url,parser,15)
                
        #Parse div tages of download class
        mars_hemisphere_full_images= hemisphere_full_soup.find_all("div",class_="downloads")
        
        #Loop through list
        for mars_hemisphere_full_image in mars_hemisphere_full_images:
            #Get the a tag and href value
            image_url = mars_hemisphere_full_image.a['href']
            #Append url in to list 
            hemisphere_full_img.append(image_url)

    #Create df
    hemisphereimageurls_df=pd.DataFrame({"title":titles,"img_url":hemisphere_full_img})

    #Convert df to dictionary and return results
    return hemisphereimageurls_df.to_dict(orient='records')

