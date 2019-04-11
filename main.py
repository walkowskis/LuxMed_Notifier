"""
This is my adaptation of luxmed-monitor-py, originally
created by Kornel Zemla (github.com/lenrok258).
"""


from selenium import webdriver
import json
import time


with open('config.json', encoding='utf-8') as data_file:
    config = json.load(data_file)


def create_driver(headless):
    options = webdriver.ChromeOptions()
    options.add_argument('--window-size=1920,1080')
    if headless:
        options.add_argument('--headless')
    return webdriver.Chrome(options=options, executable_path=r"./chromedriver/chromedriver.exe")


driver = create_driver(config['tool']['headless'])
driver.implicitly_wait(10)


def login():
    driver.get('https://portalpacjenta.luxmed.pl/PatientPortal/Account/LogOn')
    driver.find_element_by_id('Login').send_keys(config['credentials']['luxmedUsername'])
    driver.find_element_by_xpath('//*[@id="TempPassword"]').click()
    driver.find_element_by_xpath(
        '//*[@id="Password"]').send_keys(config['credentials']['luxmedPassword'])
    driver.execute_script('submitLogin()')


def cat_select():
    driver.get('https://portalpacjenta.luxmed.pl/PatientPortal/Reservations/Coordination')
    driver.find_element_by_css_selector('a[datasubcategory*="Przezi"]').click()
    element = driver.find_element_by_xpath(
        "//a[contains(@class, 'activity_button')][contains(text(),'Wizyta')]")
    driver.execute_script("arguments[0].click();", element)


def specialty_select():
    css_path = "div.graphicSelectContainer"
    dropdown = driver.find_elements_by_css_selector(css_path)[3]
    dropdown.click()
    dropdown_search = driver.find_element_by_css_selector("input.search-select")
    dropdown_search.clear()
    dropdown_search.send_keys(config['search']['service'])
    dropdown_item = driver.find_element_by_css_selector("ul#__selectOptions li:not(.hidden)")
    dropdown_item.click()
    close_dropdown()
    time.sleep(2)


def close_dropdown():
    from selenium.webdriver.common.action_chains import ActionChains
    actions = ActionChains(driver)
    body = driver.find_element_by_css_selector("a.logo")
    actions.move_to_element(body).click().perform()


def md_select():
    if len(config['search']['doctor']) > 0:
        css_path = "div.graphicSelectContainer"
        dropdown = driver.find_elements_by_css_selector(css_path)[4]
        dropdown.click()
        dropdown_search = driver.find_element_by_css_selector("input.search-select")
        dropdown_search.clear()
        dropdown_search.send_keys(config['search']['doctors'])
        dropdown_item = driver.find_element_by_css_selector("ul#__selectOptions li:not(.hidden)")
        dropdown_item.click()
        close_dropdown()
        time.sleep(2)
    else:
        pass


def appointment_search():
    submit_button = driver.find_element_by_css_selector("input[type=submit]")
    submit_button.click()


def any_free_slot(time_from, time_to):
    slots = []
    slots_elements = driver.find_elements_by_css_selector('.reserveTable tbody tr')
    for slot in slots_elements:
        try:
            hour = int(slot.text.split(':')[0])
            if time_from <= hour <= time_to:
                slots.append(hour)
        except:
            pass
    print(len(slots))
    return len(slots) != 0


def monitor():
    login()
    cat_select()
    specialty_select()
    md_select()
    while True:
        appointment_search()
        time.sleep(5)
        if any_free_slot(config['search']['timeFrom'], config['search']['timeTo']): appointment_found()
        time.sleep(181)


def appointment_found():
    global driver
    driver = create_driver(False)
    driver.implicitly_wait(10)
    login()
    cat_select()
    specialty_select()
    md_select()
    appointment_search()


def main():
    try:
        monitor()
    except Exception as e:
        print(e)


main()
