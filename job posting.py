# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 18:29:40 2023

@author: Win 10
"""
import time
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pandas as pd

driver = webdriver.Chrome(ChromeDriverManager().install())
site='https://www.linkedin.com/login'
driver.get(site)  # Open Site in new chrome window
time.sleep(3)

#accept cookies
driver.find_element(By.XPATH, '/html/body/div/main/div[1]/div/section/div/div[2]/button[2]').click()


#signin
driver.find_element(By.XPATH, '//*[@id="username"]').send_keys('xxxx@gmail.com')
driver.find_element(By.XPATH,'//*[@id="password"]').send_keys('xxxx')
driver.find_element(By.XPATH, '//*[@id="organic-div"]/form/div[3]/button').click() #signin button
driver.find_element(By.XPATH, '//*[@id="ember455"]/button').click() #skip adding phone nr
driver.implicitly_wait(30)

#find job function
def job_search(title, location):
    title=title.replace(' ', '%20')
    site = f'https://www.linkedin.com/jobs/search/?geoId=103819153&keywords={title}&location={location}'
    driver.find_element(By.XPATH, '//*[@id="global-nav"]/div/nav/ul/li[3]/a').click()
    driver.get(site)

job_search('analyst', 'Norway')


#limit posting date
driver.find_element(By.XPATH, '//*[@id="ember152"]/button').click()
driver.find_element(By.XPATH, '//*[@id="artdeco-hoverable-artdeco-gen-42"]/div[1]/div/form/fieldset/div[1]/ul/li[4]/label/p/span[1]').click()
driver.find_element(By.XPATH, '//*[@id="ember438"]/span').click() #show results
#job_lists = driver.find_element_by_class_name('jobs-search__results-list’)
#jobs = jobs_lists.find_elements_by_tag_name(‘li’) # return a list
jobs=driver.find_elements(By.CSS_SELECTOR, '.jobs-search-results__list-item')

job_list = [job.text for job in jobs]
links=[]

for job in jobs:
    all_links = job.find_elements_by_tag_name('a')
    for a in all_links:
        if str(a.get_attribute('href')).startswith("https://www.linkedin.com/jobs/view") and a.get_attribute('href') not in links: 
            links.append(a.get_attribute('href'))
        else:
            pass
        
# scroll down for each job element
 driver.execute_script('arguments[0].scrollIntoView();', job)

# go to next page:
 driver.find_element_by_xpath(f"//button[@aria-label='Page {2}']").click()
 time.sleep(3) 


links = []
# Navigate 13 pages
print('Links are being collected now.')
try: 
    for page in range(2,23):
        time.sleep(2)
        jobs_list= driver.find_elements(By.CSS_SELECTOR, '.jobs-search-results__list-item')
    
        for job in jobs_list:
            all_links = job.find_elements_by_tag_name('a')
            for a in all_links:
                if str(a.get_attribute('href')).startswith("https://www.linkedin.com/jobs/view") and a.get_attribute('href') not in links: 
                    links.append(a.get_attribute('href'))
                else:
                    pass
            # scroll down for each job element
            driver.execute_script("arguments[0].scrollIntoView();", job)
        
        print(f'Collecting the links in the page: {page-1}')
        # go to next page:
        driver.find_element_by_xpath(f"//button[@aria-label='Page {page}']").click()
        time.sleep(3)
except:
    pass
print('Found ' + str(len(links)) + ' links for job offers')

job_titles = []
company_names = []
number_employee = []
company_locations = []
work_methods = []
post_dates = []
work_times = [] 
job_desc = []


j = 1
# Visit each link one by one to scrape the information
print('Visiting the links and collecting information just started.')
for i in range(len(links)):
    print(f'Scraping the Job Offer {j}')
    try:
        driver.get(links[i])
        time.sleep(10)
        # Click See more.
        driver.find_element(By.CLASS_NAME, 'artdeco-card__actions').click()
        time.sleep(10)
    except:
        pass
    
    # Find the general information of the job offers
    contents = driver.find_elements(By.CLASS_NAME, 'p5')
    for content in contents:
        try:
            job_titles.append(content.find_element_by_tag_name("h1").text)
            company_names.append(content.find_element_by_class_name("jobs-unified-top-card__company-name").text)
            company_locations.append(content.find_element_by_class_name("jobs-unified-top-card__bullet").text)
            number_employee.append(content.find_elements_by_class_name("jobs-unified-top-card__job-insight")[1].text)
            work_methods.append(content.find_element_by_class_name("jobs-unified-top-card__workplace-type").text)
            post_dates.append(content.find_element_by_class_name("jobs-unified-top-card__posted-date").text)
            work_times.append(content.find_elements_by_class_name("jobs-unified-top-card__job-insight")[0].text)
        except:
            pass
        time.sleep(2)
        
    # Scraping the job description
    job_desc.append(driver.find_element_by_xpath('//*[@id="job-details"]').text)
    time.sleep(2)
    print(f'Scraping the Job Offer {j} Done')
    j+=1

        
# Creating the dataframe 
df = pd.DataFrame(list(zip(job_titles,company_names,
                    company_locations,number_employee, work_methods,
                    post_dates,work_times, job_desc)),
                    columns =['job_title', 'company_name',
                           'company_location', 'number_employee','work_method',
                           'post_date','work_time', 'job description'])

# Storing the data to csv file
df.to_csv('job_posting.csv', index=False)


