import datetime

import time
from selenium import webdriver

# 创建一个浏览器对象
driver = webdriver.Chrome()

# 访问指定的URL地址
driver.get('https://movie.douban.com/')
# 显示响应对应的url
print(driver.current_url)
print(driver.title)
time.sleep(2)

inp_query = driver.find_element_by_id('inp-query')
inp_query.click()
inp_query.clear()
inp_query.send_keys('杀死比尔')
driver.find_element_by_xpath('//*[@id="db-nav-movie"]/div[1]/div/div[2]/form/fieldset/div[2]/input').click()



# 截图
driver.save_screenshot(f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.png')
driver.quit()