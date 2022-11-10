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
from data import lego_theme_container
from data import lego_theme
from data import lego_data_info
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

        xpath = '//*[@id="root"]/div[5]/div/div/div[1]/div[1]/div/button'
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

        xpath = '//button[contains(@class,"Button__Base-sc-1jdmsyi-0 eCVPKR")]'
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

        """This method is will click Theme menu <-- Shop drop down menu.
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

        """This method is will click 'see all themes' <-- Theme menu <-- Shop drop down menu.
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

        """This method is will click 'see all themes' <-- Theme menu <-- Shop drop down menu.
        Args: Xpath 
        Returns: None

        """
        xpath = '//li[@class = "CategoryListingPagestyle__ListItemAlternate-sc-880qxz-7 drzfAx"]'
        theme_list = self.driver.find_elements(By.XPATH,xpath)

        return theme_list

    def _theme_extract_href(self):
        
        theme_href = []
        theme_dict = ({'Lego_theme_link':[],'Theme_name': []})
        for theme_link in self._lego_theme_list()[0::]:
            Theme_name = theme_link.find_element(By.TAG_NAME,'a').get_attribute('data-analytics-title')
            theme_dict['Theme_name'].append(Theme_name)
            Lego_theme_link = theme_link.find_element(By.TAG_NAME,'a').get_attribute('href')
            theme_dict['Lego_theme_link'].append(Lego_theme_link)
            theme_href.append(theme_link.find_element(By.TAG_NAME,'a').get_attribute('href'))
            #Theme_dict['Theme_UUID'].append(uuid.uuid4())
                #print('UUID is',uuid.uuid4())

        return theme_href, theme_dict


    def _extract_themewise_product_link(self)->str:
        for href in self._theme_extract_href()[0][0:1]:
            self.driver.get(href)
            #print(href)
            self._show_all()
            self._lego_product_links()
            lego_details = self._lego_product_info()
        return lego_details

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

        #self. show_all()
        time.sleep(10)
        WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.XPATH, '//*[@data-test = "product-item"]')))
        list_items = self.driver.find_elements(By.XPATH,'//*[@data-test = "product-item"]') 
        lego_links = []
        for legoitems_link in list_items[0::]:
            self.lego_links.append(legoitems_link.find_element(By.TAG_NAME,'a').get_attribute('href'))
        return lego_links

    def _lego_product_info(self)-> dict:
        """Click each lego product link and get the Product name , link, prices.
            Update these info in lego_dict. Create each record unique to avoid copies using UUID"""
        #self.lego_links 
        lego_dict = {
            'Lego_Theme':[],'Product_name':[],'Prices':[],'Rating':[],'Age':[],
            'Availability':[],'Discount':[],'Discounted_Price':[],'link':[],'Pieces':[],'Item_num':[],'VIP_Points':[],
            'UUID':[]}
        lego_link = self._lego_product_links()
        
        for link in lego_link[0::]:
            self.driver.get(link)
            time.sleep(2)
            lego_dict['link'].append(link)
            try:
                time.sleep(2)
                Prices = self.driver.find_element(By.XPATH,'//span[@data-test="product-price"]')
                #Prices = Price.rsplit('/n')
                lego_dict['Prices'].append(Prices.text)
            
            except NoSuchElementException:
                lego_dict['Prices'].append('N/A')

            try:
                time.sleep(2)
                theme_list = self.driver.find_element(By.XPATH,'//a[@class="ProductOverviewstyles__BrandLink-sc-1a1az6h-6 kikPBQ"]')
                lego_theme = theme_list.find_element(By.TAG_NAME,'img').get_attribute('alt')
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
                Discount = self.driver.find_element(By.XPATH,'//div[@data-test="sale-percentage"]')
                #Image_dict['lego_photos'].append(Pictures)
                lego_dict['Discount'].append(Discount.text)
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
                rating_xpath = self.driver.find_element(By.XPATH,'//div[@class="RatingBarstyles__RatingContainer-sc-11ujyfe-2 fgbdIf"]')
                Rating = rating_xpath.get_attribute('title')
                lego_dict['Rating'].append(str(Rating))
                print(Rating)
            except NoSuchElementException:
                lego_dict['Rating'].append('N/A')

            try:
                Availability = self.driver.find_element(By.XPATH,'//p[@data-test="product-overview-availability"]')
                self.Lego_dict['Availability'].append(Availability.text)
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
        lego_product_info_table = pd.DataFrame(self._extract_themewise_product_link())
        return lego_product_info_table

    @staticmethod
    def _create_change_folder_path(self):

        path = '/home/lakshmi/Documents/Data collection pipeline'
        os.mkdir(path)
        os.chdir(path)

        return None
    
    def _data_JSON(self) -> json:
        """Created a JSON file in the root folder clled 'raw_data'-->data.json
        This function used to create a json file in a new folder
        and add the informations found in the previous function.
        """
        lego_json = self._extract_themewise_product_link()
        
        folder = r'raw_data'
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        with open('data.json', 'w') as f:
            f.write(json.dumps(lego_json, indent=4, sort_keys=False))
        
    
    @staticmethod
    def lego_create_images_folder(self) -> None:

        #os.mkdir(os.path.join(os.getcwd(),'Images'))
        os.chdir(os.path.join(os.getcwd(),'Images'))
        folder = r'Images'
        if not os.path.exists(folder):
            os.makedirs(folder)
       

    def _lego_image_downloader(self):
        """Download Firsts image from the lego products and update it as list in image_dict with UUID"""

        
        Image_dict = {'Lego_images' :[],'Image_UUID':[]}

        lego_image_link = self._lego_product_links()

        for link in lego_image_link[0:]:
                self.driver.get(link)
                
                try:
                            
                    time.sleep(1)
                    LT = self.driver.find_element(By.XPATH,'//a[@class="ProductOverviewstyles__BrandLink-sc-1a1az6h-6 kikPBQ"]')
                    Lego_Theme = LT.find_element(By.TAG_NAME,'img').get_attribute('alt')
                    Product_name = self.driver.find_element(By.XPATH,'//h1[@data-test="product-overview-name"]')
                    name = (Product_name.text).replace(' ','_').replace(',','').replace('-','')
                    image = self.driver.find_elements(By.XPATH,'//img[@class = "Imagestyles__Img-m2o9tb-0 jyexzd Thumbnail__StyledImage-e7z052-1 vTyKJ"]') 
                    i = 0
                    for img in image[0::]:
                        get_src = img.get_attribute('src')
                        Image_dict['Lego_images'].append(get_src)
                        #os.mkdir(os.path.join(os.getcwd(),name))
                        #os.chdir(os.path.join(os.getcwd(),name))
                        #name = re.sub('\s+','_',(Product_name.text))
                        with open(f"{Lego_Theme}_{name}_{i}.jpg",'wb') as f:
                                pict = requests.get(get_src)
                                f.write(pict.content)
                                f.close
                        i += 1
                except NoSuchElementException:
                        print('No images found')

                try:
                    Image_dict['Image_UUID'].append(str(uuid.uuid4()))
                    print('UUID is',uuid.uuid4())
                except:
                        pass
        return Image_dict

    def image_data(self):  
        """Create a data table for immages using panda for lego images info"""
        return(print(pd.DataFrame(self._lego_image_downloader()))) 
    
    def _close_scraper(self):
        """
        Closes the windows associated with the scraper. 
        """
        self.driver.quit()
        print("Quiting driver.")

        return None

    def upload_rawdata_to_s3_bucket(self):
        s3_client = boto3.client('s3')
        response = s3_client.upload_file('/home/lakshmi/Documents/Data collection pipeline/raw_data/data.json', 'legobuckets3', 'tests/data.json')


    def _delete_from_local_machine(self):
        """
        Removes the raw data from the local machine. 
        """
        directory = os.path.join(os.getcwd(),'raw_data')
        print("Deleting", directory)
        try:
            shutil.rmtree(directory)
        except FileNotFoundError:
            print("Can't find directory to delete.")

        return None

if __name__ == '__main__' : 
    bot = Scraper()
    
