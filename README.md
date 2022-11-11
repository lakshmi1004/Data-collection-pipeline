# Data-collection-pipeline  - LEGO
An implementation of an industry grade data collection pipeline that runs scalably in the cloud.
It uses Python code to automatically control your browser, extract information from a website, and store it on the cloud in a data warehouses and data lake.The system conforms to industry best practices such as being containerised in Docker and running automated tests.

Mile Stone #1: Set up the environment and install dependencies

Created repository in Github - Data-collection-pipeline
Created folder in local Data collection pipeline
Created new virtual environment.Started by creating the environment, activate it, and then install pip by running the following command in your terminal "conda install pip". Then, to install the rest of the libraries, run "pip install <library>"
conda create -n selenium python=3.8
conda activate selenium
pip install ipykernel
pip list > requirements.txt
pip install pandas
pip install selenium
Installing the chrome web driver go to pypi website.
Beautiful soup:
pip install BeautifulSoup4
import requests
from bs4 import BeautifulSoup

Mile stone #2: Choose Website to Scrap:

Choosen Lego Uk website

Mile Stone #3: Prototype finding the individual page for each entry

Task1:Created a Scraper class

I will use Python,Requests, and BeautifulSoup to scrap some pages from Lego.
Created methods

