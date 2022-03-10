#Import selenium
#get_ipython().system('pip install selenium')
#Import Splinter
#Import BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager

def scrape_all():
    # Set the executable path and initialize the chrome browser in splinter
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)

    news_title, news_paragraph = mars_news(browser)

    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": hemispheres(browser),
        "last_modified": dt.datetime.now()
    }

    browser.quit()
    return data

def mars_news(browser):        
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Convert the browser html to a soap object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')
        slide_elem.find("div", class_='content_title')
        # Use the parent element to find the first a tag and save it as 'news_title'
        news_title = slide_elem.find("div", class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_="article_teaser_body").get_text()
    except AttributeError:
        return None, None    
    
    return news_title, news_p

#### JPL Space Images Featured Images

# Visit URL
def featured_image(browser):
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    html = browser.html
    browser = soup(html, 'html.parser')
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()
    
    # Find the more infor button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.link.find_by_partial_text('more info')
    more_info_elem.click()

    ## Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")

    except AttributeError:
        return None

    # Use the base url to create an absolate url
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

    return img_url

#### Mars Facts
def mars_facts():
    # Add try/except for error handling
    try:
        df = pd.read_html('http://space-facts.com/mars/')[0]
    except BaseException:    
        return None

    # Assign column and set index of df
    df.columns=['Description', 'Mars']
    df.set_index('Description', inplace=True)
    
    # Convert dataframe into HTML add bootstrap
    return df.to_html(classes="table table-striped")

if __name__ == "_main_":
    print(scrape_all())    

# Challenge
def hemispheres(browser):
    url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(url)

# Create a list to hold the images and titles
    hemisphere_image_urls = []

# First get the list of all hemispheres
    links = browser.find_by_css('a.product-item h3')

    # Next loop thorugh those links click the link find the sample anchor return herf
    for index in range (len(links)):
    
        # Find the elements on each loop to avoid a state element exception
        browser.find_by_css('a.product-item h3')[index].click()
        hemisphere_data = scrape_hemisphere(browser.html)
        hemisphere_image_urls.append(hemisphere_data) 
        # Finally navigate backwards
        browser.back()

    return hemisphere_image_urls

def scrape_hemisphere(html_text):
    # parse html text
    hemi_soup = soup(html_text, "html.parser")

    try:
        title_element = hemi_soup.find("h2", class_="title").get_text()
        sample_element = hemi_soup.find("a", text="Sample").get("href")
    except ArithmeticError:
        title_element = None
        sample_element = None
    hemispheres_dictionary = {
        "title": title_element,
        "img_url": sample_element
    }
    return hemispheres_dictionary
           
if __name__ == "__main__":
    print (scrape_all())
