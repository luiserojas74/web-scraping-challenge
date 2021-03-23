from splinter import Browser
from bs4 import BeautifulSoup 
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time


def scrape():
    # Set up Splinter
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)

    # URLs
    NASA_Mars_News_URL = 'https://mars.nasa.gov/news/'
    JPL_Mars_Space_Images_URL = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    Mars_Facts_URL = 'https://space-facts.com/mars/'
    Mars_Hemispheres_URL = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

    # NASA Mars News
    url = NASA_Mars_News_URL
    browser.visit(url)
    time.sleep(1)
    # HTML object
    html = browser.html
    # Parse HTML with Beautiful Soup
    soup = BeautifulSoup(html, 'html.parser')
    # Retrieve all elements that contain article information
    articles = soup.find_all('div', class_='list_text')
    titles_list = []
    p_list = []
    # Iterate through each article
    for article in articles:
        # Use Beautiful Soup's find() method to navigate and retrieve attributes
        title = article.find('div', class_='content_title')
        news_title = title.text
        titles_list.append(news_title)
        paragraph = article.find('div', class_='article_teaser_body')
        news_p = paragraph.text
        p_list.append(news_p)

    # JPL Mars Space Images - Featured Image
    url = JPL_Mars_Space_Images_URL
    browser.visit(url)
    time.sleep(1)
    # HTML object
    html = browser.html
    # Parse HTML with Beautiful Soup
    soup = BeautifulSoup(html, 'html.parser')
    # Click on the FULL IMAGE BUTTON
    browser.links.find_by_partial_text('FULL IMAGE').click()
    # Retrieve featured image
    soup_child = BeautifulSoup(browser.html, 'html.parser')
    featured_image = soup_child.find('img', class_='fancybox-image')['src']
    base = "https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/"
    featured_image_url = base +  featured_image

    # Mars Facts
    url = Mars_Facts_URL
    table = pd.read_html(url)
    df = table[0]
    df.columns = ['Description', '']
    df.set_index('Description', inplace=True)
    html_table = df.to_html()

    # Mars Hemispheres
    url = Mars_Hemispheres_URL
    browser.visit(url)
    time.sleep(1)
    # HTML object
    html = browser.html
    # Parse HTML with Beautiful Soup
    soup = BeautifulSoup(html, 'html.parser')
    # Retrieve all elements that contain hemispheres
    hemisphere_list = soup.find_all('div', class_='item')
    hemisphere_image_urls = []
    # Iterate through each hemisphere
    for hemisphere in hemisphere_list:
        # Use Beautiful Soup's find() method to navigate and retrieve attributes
        title = hemisphere.find('h3').text
        anchor = hemisphere.find('a')
        href = anchor['href']
        link_found = browser.links.find_by_partial_text(title)
        link_found.click()
        # Child page
        soup_child = BeautifulSoup(browser.html, 'html.parser')
        download = soup_child.find('div', class_='downloads')
        ul = download.find('ul')
        li_list = ul.find_all('li')
        for li in li_list:
            if "Original" in li.text:
                hemisphere_image_dict = {"title": title, "img_url": li.a['href']}
                hemisphere_image_urls.append(hemisphere_image_dict)
        browser.back()

    # Store data in a dictionary
    mars_dict = {"title": titles_list[0], 
        "paragraph": p_list[0],
        "featured_image_url": featured_image_url,
        "html_table": html_table,
        "hemisphere_image_urls": hemisphere_image_urls }

    # Close the browser after scraping
    browser.quit()

    # Return results
    return mars_dict
