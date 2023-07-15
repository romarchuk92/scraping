from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

import re
import json



def wait_element(driver, delay_seconds=1, by=By.TAG_NAME, value=None):
    """
    Иногда элементы на странце не прогружаются сразу
    Функция ждет delay_seconds если элемент еще не прогрузился
    Если за отведенное время элемент не прогружается выбрасывается TimeoutException
    :param driver: driver
    :param delay_seconds: максимальное время ожижания
    :param by: поле поиска
    :param value: значение поиска
    :return: найденный элемент
    """

    return WebDriverWait(driver, delay_seconds).until(
        expected_conditions.presence_of_element_located((by, value))
    )


service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.get("https://spb.hh.ru/search/vacancy?text=python&area=1&area=2")


articles = driver.find_element(By.ID, "a11y-main-content")
# articles = driver.find_element(By.XPATH, "//div[@id='a11y-main-content']")


# Собирается список всех вакансий со страницы поиска вакансий
parsed_data = []
    
for article in articles.find_elements(By.CLASS_NAME, "vacancy-serp-item-body__main-info"):
    
    h3_element = article.find_element(By.TAG_NAME, "h3")
    span_element = h3_element.find_element(By.TAG_NAME, "span")
    a_element = span_element.find_element(By.TAG_NAME, "a")
    a_element_company = article.find_element(By.CLASS_NAME, "vacancy-serp-item__meta-info-company")
    a_element_city = article.find_element(By.CSS_SELECTOR, '[data-qa="vacancy-serp__vacancy-address"]')
    # span_salary_element = article.find_element(By.XPATH, "//span[@class='bloko-header-section-3']").text
    # span_salary_element = article.find_element(By.CSS_SELECTOR, "span.bloko-header-section-3").text

    try:
        span_salary_element = article.find_element(By.CSS_SELECTOR, '[data-qa="vacancy-serp__vacancy-compensation"]')
        salary = span_salary_element.text
        # print(h3_element.text, span_salary_element)
    except : salary = 'ЗП не указана'
      
    title = span_element.text
    link = a_element.get_attribute("href")
    company = a_element_company.text
    city = a_element_city.text

    parsed_data.append(
        {
            "title": title,
            "link": link,
            "salary": salary,
            "company": company,
            "city": city,
        }
    )
    # break

# Проводится проверка на наличие ключевых слов "flask" и "django" в описании к вакансии и добавляется 
# ключ "description" со значением "del", чтобы далее по нему отфильтровать список
for item in parsed_data:
    
    driver.get(item["link"])
    descr = wait_element(driver, by=By.CSS_SELECTOR, value="[data-qa='vacancy-description']").text
    pattern = r'flask|django'

    if re.search(pattern, descr, re.I):
        item["description"] = 'del'          
    else: continue

# Создается новый список в который помещаем отфильтрованные результаты
parsed_data_filter = []

for item in parsed_data:
    try: 
        item["description"] == 'del'

        parsed_data_filter.append(
        {
            "title": item["title"],
            "link": item["link"],
            "salary": item["salary"],
            "company": item["company"],
            "city": item["city"],

        }
    )
    except: continue  

# Записываем отфильтрованный список в json файл
with open('vacancy.json', 'w', encoding='utf8') as outfile:
    json.dump(parsed_data_filter, outfile, ensure_ascii=False, indent="   ")
# print(parsed_data)


