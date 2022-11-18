from crypt import methods
import time
import pandas as pd
from pandas import DataFrame
import os
import requests
from bs4 import BeautifulSoup
import uuid
from uuid import UUID
import json
import shutil
import boto3
from dataclasses import dataclass
#from data import lego_theme_container
#from data import lego_theme
#from data import lego_data_info
from logging import exception
from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException #used to debug the program
from webdriver_manager.chrome import ChromeDriverManager
from pydantic import validate_arguments


class Scraper():
    """This class is to scarpe the Lego Website"""

    def __init__(self, url:str = 'https://www.lego.com/en-gb')-> None:

        """ Initailising the Lego Website address"""
        self.driver = Chrome(ChromeDriverManager().install())
        self.driver.get(url)
        self.driver.maximize_window()
        return None

    def lego_continue(self)-> None:
        """ This function is created to click the cookie button in the Webpage.
        Args: xpath
        Returns: None
         """

        #'//*[@id="root"]/div[5]/div/div/div[1]/div[1]/div/button'
        xpath = '//*[@id="__next"]/div/div[4]/div/div/div[1]/div[1]/div/button'
        try:
            time.sleep(2)
            WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH, xpath)))
            self.driver.find_element(By.XPATH, xpath).click()
        except TimeoutException:
            print('no elements found')

        return None

    def necessary_cookies(self)-> None:

        """This method is meant to click the 'just necessary cookies' 
        Args: xpath
        Returns: None
        """

        xpath = '//button[@class ="Button__Base-sc-ae3gos-0 dhqLRS"]'
        try:
            #time.sleep(2)
            WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH, xpath)))
            self.driver.find_element(By.XPATH,xpath).click()
        except TimeoutException:
            print('no elements found')

        return None

    def shop(self)-> None:

        """This method is will click 'Shop' menu from lego website.
        Args: Xpath as "data-test = see-all-link"
        Returns: None
        """
        xpath ='//*[@id="blt51f52bea34c3fb01_menubutton"]'
        try:
            time.sleep(2)
            WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH, xpath)))
            self.driver.find_element(By.XPATH,xpath).click()
        except TimeoutException:
                print('no elements found')
    
        return None

    def _shop_by_theme(self) -> None:

        """This method is will click shop --> set by theme menu drop down menu.
        Args: Xpath
        Returns: None
        """
        xpath = '//*[@id="blt6e23fc5280e75abb_submenubutton"]/div'
        try:
           time.sleep(2)
           WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH, xpath)))
           self.driver.find_element(By.XPATH,xpath).click()
        except TimeoutException:
           print('no elements found')

        return None

    def _click_see_all_theme(self) -> None:

        """This method  will click 'see all themes' <-- Theme menu <-- Shop drop down menu.
        Args: Xpath as "data-test = see-all-link"
        Returns: None

        """
        xpath = '//*[@data-test="see-all-link"]'
        try:
           time.sleep(2)
           WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH, xpath)))
           self.driver.find_element(By.XPATH,xpath).click()
        except TimeoutException:
           print('no elements found')

        return None

    def _lego_theme_list(self) -> list:

        """This method will extract the theme list where it will be used to extract its href and its name in 
        _theme_extract_href method.
        Args: Xpath 
        Returns: None

        """
        time.sleep(2)
        xpath = '//li[@class = "CategoryListingPagestyle__ListItemAlternate-sc-880qxz-7 kCapDO"]'
        theme_list = self.driver.find_elements(By.XPATH,xpath)

        return theme_list

    def _theme_extract_href(self):
        """From above method -lego_theme_list , we are going to get each theme link(href) and its name 

        
        Args: Xpath
        Returns:
            dictionary, list
        """
        time.sleep(2)
        self.theme_href = []
        #theme_dict = ({'Lego_theme_link':[],'Theme_name': []})
        for theme_link in self._lego_theme_list()[0::]:
            
            self.theme_href.append(theme_link.find_element(By.TAG_NAME,'a').get_attribute('href'))
            
        return self.theme_href
    
    def _extract_themewise_product_link(self)->str:
        for href in self.theme_href[0:1]:
            self.driver.get(href)
            #print(href)
            self._show_all()
            self._lego_product_links()
            self.lego_details = self._lego_product_info()
        return self.lego_details

    def _show_all(self) -> None:
        """This method clicks the 'show all' button in the page in order to display all the search result of the multile page"""
        xpath = '//a[@data-test="pagination-show-all"]'
        #'//*[@id="blt441564c4a0c70d99"]/section/div/div/div[3]/a'
        #'//*[@id="blt5881a9b7772d3176"]/section/div/div/div[3]/a'
        try:
            time.sleep(2)
            WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH, xpath)))
            self.driver.find_element(By.XPATH,xpath).click()
        except TimeoutException:
            print("only one page lego product is available. No Show all button' is displayed")

        return None

    def _lego_product_links(self) -> list:
        """List_item = finds the list of products or container.
           Each list in the container get the href of each products of items in the container  """

        time.sleep(10)
        WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.XPATH,'//*[@data-test = "product-item"]')))
        list_items = self.driver.find_elements(By.XPATH,'//*[@data-test = "product-item"]') 
        lego_links = []
        for legoitems_link in list_items[0::]:
            lego_links.append(legoitems_link.find_element(By.TAG_NAME,'a').get_attribute('href'))
        return lego_links

    def _lego_product_info(self)-> dict:
        """Click each lego product link and get the Product name , link, prices.
            Update these info in lego_dict. Create each record unique to avoid copies using UUID"""
        #self.lego_links
        time.sleep(2) 
        lego_dict = {
            'Lego_Theme':[],'Product_name':[],'Prices':[],'Recommendation':[],'Age':[],
            'Availability':[],'Discount':[],'Discounted_Price':[],'link':[],'Pieces':[],'Item_num':[],'VIP_Points':[],
            'UUID':[]}
        lego_products = self._lego_product_links()
        
        for link in lego_products[0::]:
            self.driver.get(link)
            time.sleep(2)
            lego_dict['link'].append(link)
            try:
                time.sleep(2)
                P = self.driver.find_element(By.XPATH,'//span[@data-test="product-price"]').text
                Prices = P.rsplit('Price\n')
                p = (Prices[1])
                lego_dict['Prices'].append(p)
                print (p)
            except NoSuchElementException:
                lego_dict['Prices'].append('N/A')

            try:
                time.sleep(2)
                theme_list = self.driver.find_element(By.XPATH,'//a[@class="ProductOverviewstyles__BrandLink-sc-1a1az6h-6 josPGv"]')
                lego_theme = theme_list.find_element(By.TAG_NAME,'img').get_attribute('alt')
                #lego_theme = self.driver.find_elements(By.XPATH,'//span[@class="ProductOverviewstyles__Microdata-sc-1a1az6h-3 fCXkEZ"]')[1].text
                lego_dict['Lego_Theme'].append(lego_theme)
            except NoSuchElementException:
                lego_dict['Lego_Theme'].append('N/A')

            try:
                time.sleep(2)
                Product_name = self.driver.find_element(By.XPATH,'//h1[@data-test="product-overview-name"]')
                lego_dict['Product_name'].append(Product_name.text)
            
            except NoSuchElementException:
                lego_dict['Product_name'].append('N/A')
            #bot.driver.find_element(By.XPATH,'//span[@data-test="product-price"]')
            try:
                Discount = self.driver.find_element(By.XPATH,'//div[@data-test="sale-percentage"]').text
                D = Discount.rsplit('Price\n')
                dp = (D[1])
                lego_dict['Prices'].append(p)
                print (p)
                lego_dict['Discount'].append(dp)
                print(Discount.text)
            except NoSuchElementException:
                lego_dict['Discount'].append('No Discount')   
            try:
                Age = self.driver.find_element(By.XPATH,'//div[@data-test="ages-value"]')
                    #Age = Age_xpath.get_attribute('span')
                lego_dict['Age'].append(Age.text)
                print(Age.text)
            
            except NoSuchElementException:
                lego_dict['Age'].append('N/A')

            try:
                Pieces = self.driver.find_element(By.XPATH,'//div[@data-test="pieces-value"]')
                lego_dict['Pieces'].append(Pieces.text)
                print(Pieces.text)
            except NoSuchElementException:
                lego_dict['Pieces'].append('Num of Pieces not available for this product ')
            try:
                Discounted_Price = self.driver.find_element(By.XPATH,'//span[@data-test="product-price-sale"]')
                lego_dict['Discounted_Price'].append(Discounted_Price.text)
                print(Discounted_Price.text)
            except NoSuchElementException:
                lego_dict['Discounted_Price'].append('N/A')
            try:
                time.sleep(2)
                
                r = self.driver.find_element(By.XPATH,'//button[@data-test="pdp-reviews-accordion-title"]').click()
                time.sleep(2)
                Recommendation = self.driver.find_element(By.XPATH,'//span[@class="Text__BaseText-sc-13i1y3k-0 ibdTpK"]')
                lego_dict['Recommendation'].append(Recommendation.text)
                print(Recommendation)
            except NoSuchElementException:
                lego_dict['Recommendation'].append('N/A')

            try:
                Availability = self.driver.find_element(By.XPATH,'//p[@data-test="product-overview-availability"]')
                lego_dict['Availability'].append(Availability.text)
                print(Availability.text)
            except NoSuchElementException:
                lego_dict['Availability'].append('N/A')
            try:
                Item_num = self.driver.find_element(By.XPATH,'//div[@data-test="item-value"]')
                lego_dict['Item_num'].append(Item_num.text)
                print(Item_num.text)
            except NoSuchElementException:
                lego_dict['Item_num'].append('N/A')
            try:
                VIP_Points = self.driver.find_element(By.XPATH,'//div[@data-test="vip-points-value"]')
                lego_dict['VIP_Points'].append(VIP_Points.text)
                print(VIP_Points.text)
            except NoSuchElementException:
                lego_dict['VIP_Points'].append('N/A')
                     
            try:
                lego_dict['UUID'].append(str(uuid.uuid4()))
                print('UUID is',uuid.uuid4())
            
            except:
                pass

        return lego_dict
    
    def _Data_list(self):
        """Create a data table using panda for product info"""
        lego_product_info_table = pd.DataFrame(self.lego_details)
        return lego_product_info_table

    @staticmethod
    def _create_change_folder_path():

        path = '/home/lakshmi/Documents/Data collection pipeline'
        os.mkdir(path)
        os.chdir(path)

        return None
    
    def _data_JSON(self) -> json:
        """Created a JSON file in the root folder clled 'raw_data'-->data.json
        This function used to create a json file in a new folder
        and add the informations found in the previous function.
        """
        lego_json = self.lego_details
        
        folder = r'raw_data'
        if not os.path.exists(folder):
            os.mkdir(folder)
        
            with open('/home/lakshmi/Documents/Data collection pipeline/raw_data/data.json', 'w') as folder:
                folder.write(json.dumps(lego_json, indent=4, sort_keys=False))
        
    
    @staticmethod
    def lego_create_images_folder(self) -> None:

        #os.mkdir(os.path.join(os.getcwd(),'Images'))
        os.chdir(os.path.join(os.getcwd(),'Images'))
        folder = r'Images'
        if not os.path.exists(folder):
            os.makedirs(folder)
            
    def _extract_lego_images(self)-> str:
        for href in self.theme_href[0:1]:
            self.driver.get(href)
            #print(href)
            self._show_all()
            self._lego_product_links()
            self.Image_download = self._lego_image_downloader()
        return self.Image_download


    def _lego_image_downloader(self):
        """Download Firsts image from the lego products and update it as list in image_dict with UUID"""

        
        Image_dict = {'Lego_images' :[],'Image_UUID':[]}
        
        lego_image_link = self._lego_product_links()

        for link in lego_image_link[0:]:
                self.driver.get(link)
                
                try:
                            
                    time.sleep(1)
                    LT = self.driver.find_element(By.XPATH,'//a[@class="ProductOverviewstyles__BrandLink-sc-1a1az6h-6 josPGv"]')
                    Lego_Theme = LT.find_element(By.TAG_NAME,'img').get_attribute('alt')
                    Product_name = self.driver.find_element(By.XPATH,'//h1[@data-test="product-overview-name"]')
                    name = (Product_name.text).replace(' ','_').replace(',','').replace('-','')
                    image = self.driver.find_elements(By.XPATH,'//img[@class = "Imagestyles__Img-sc-1qqdbhr-0 cajeby"]')
                    #//img[@class = "Imagestyles__Img-m2o9tb-0 jyexzd Thumbnail__StyledImage-e7z052-1 vTyKJ"]') 
                    i = 1
                    for img in image[0::]:
                        get_src = img.get_attribute('src')
                        Image_dict['Lego_images'].append(get_src)
                        with open(f'/home/lakshmi/Documents/Data collection pipeline/raw_data/Images/"{Lego_Theme}_{name}_{i}.jpg"','wb') as f:
                            pict = requests.get(get_src)
                            f.write(pict.content)
                            f.close
                            Image_dict['Image_UUID'].append(str(uuid.uuid4()))
                            print('UUID is',uuid.uuid4())
                
                        i += 1
                except NoSuchElementException:
                        print('No images found')

                
        return Image_dict

    def image_data(self):  
        """Create a data table for immages using panda for lego images info"""
        return(print(pd.DataFrame(self.Image_download))) 
    
    def _close_scraper(self):
        """
        Closes the windows associated with the scraper. 
        """
        self.driver.quit()
        print("Quiting driver.")

        return None

    def upload_rawdata_to_s3_bucket(self):
        s3_client = boto3.client('s3')
        response = s3_client.upload_file('/home/lakshmi/Documents/Data collection pipeline/raw_data/data.json', 'legobuckets3', 'data.json')

   
if __name__ == '__main__' : 

    bot = Scraper()
    bot.lego_continue()
    bot.necessary_cookies()
    bot.shop()
    bot._shop_by_theme()
    bot._click_see_all_theme()
    bot._lego_theme_list()
    bot._theme_extract_href()
    bot._extract_themewise_product_link()
    bot._Data_list()
    bot._data_JSON()
    bot.lego_create_images_folder()
    bot._extract_lego_images()
    bot.image_data()
    bot.upload_rawdata_to_s3_bucket()

    

