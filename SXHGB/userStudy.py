from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from PIL import Image
import pytesseract
from pytesseract import image_to_string
from selenium.common.exceptions import WebDriverException
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
import re
import random
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException

time.sleep(20)            # 等待chrome 容器先启动   


options = Options()
browser = webdriver.Remote(
            command_executor="http://chrome:4444/wd/hub",
            options=options
)


browser.implicitly_wait(60*3)

browser.maximize_window()

src = './SXHGB/'           # 在DOCKER中路径要加上SXHGB 因为工作路径在上层文件夹

start_time = time.time()


hour_goal: int = 0

user_list = []


class MissionDoneException(Exception):
    pass

with open (src+'user.txt', 'r') as f:
    user_list = f.read().splitlines()


print(user_list)

def find_something(url: str, totalpage_xpath: str, cour_xpath: str):
    """
        查找页面所有课程的url和title
        url: 页面的url
        totalpage_page: 共?页 标签的XPATH
        cour_xpath:     课程标题的XPATH
    """

    browser.get(url)
    time.sleep(2)
    TotalPage = browser.find_element(
        By.XPATH, totalpage_xpath).text
    TotalPage = re.findall(r'\d+', TotalPage)[0]
    # print(TotalPage)
    TotalPage = int(TotalPage)
    page = 1
    url_lists = []
    title_lists = []

    while page < TotalPage+1:
        cour_list = browser.find_elements(
            By.XPATH, cour_xpath)
        urls = [item.get_attribute('href') for item in cour_list]
        titles = [item.text for item in cour_list]
        # print(cour_list)
        # print(page)
        url_lists += urls
        title_lists += titles
        time.sleep(2)
        page += 1
        browser.find_element(By.ID, 'nextpage').click()
    return (url_lists, title_lists)


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

        time.sleep(10)

    except WebDriverException:
        print("webdriver 异常")


def chaxun(name):               # 查询函数
    """
        查询用户年度学习时长，返回时长T
        如果T大于用户年度学习目标时长，则退出程序
    """
    chaxun_url = 'https://www.sxgbxx.gov.cn/uc/home'
    browser.get(chaxun_url)
    shichang = browser.find_element(
        By.XPATH, '/html/body/div[1]/div[1]/div[4]/section[1]/div/div/div[2]/div/p/span[3]').text
    name = name
    print(name+'登录成功')
    print(shichang)
    T = re.findall(r'\d+', shichang)[1]
    T = int(T)

    if T >= int(hour_goal):

        raise MissionDoneException(f"{user}年度学习任务已完成")
        # print('年度学习任务已完成')
        # time.sleep(20)
        # browser.quit()
        # exit()

    else:
        return T


def sign_up():
    """
    专题培训报名 对所有当前正在进行当中的专题培训报名
    """
    print('专题培训报名')

    baoming_url = 'https://www.sxgbxx.gov.cn/front/getplanApplyList'
    totalpage_xpath = '//*[@id="aCoursesList"]/section/section[2]/div[3]/span'
    cour_xpath = '//*[@id="aCoursesList"]/section/section[2]/div[2]/div/ul/li/div/div/h3/a'
    url_lists = find_something(
        url=baoming_url, totalpage_xpath=totalpage_xpath, cour_xpath=cour_xpath)[0]

    for url in url_lists:
        browser.get(url)
        time.sleep(2)
        element_baoming = browser.find_element(
            By.XPATH, '//*[@id="aCoursesList"]/div/div[1]/article[2]/div/div[4]/div/a')

        if element_baoming.text == '报 名':
            element_baoming.click()
            time.sleep(2)
            print('报名成功!!!  sign up sucessful')
        else:
            continue


def find_peixun():
    """获取我的专题培训课程url"""
    print('下载专题培训课程url')

    # https://www.sxgbxx.gov.cn/uc/plan  我的培训
    pei_url = 'https://www.sxgbxx.gov.cn/uc/plan'

    browser.get(pei_url)
    r = browser.page_source
    pei_obj = BeautifulSoup(r, "lxml")
    pei_list = pei_obj.findAll("div", {"class": "e-m-more"})  # 获取我的专题培训内容
    src = './'
    f1 = open(src+'peixun_url.txt', 'w')  # 培训课程的url

    for pid in pei_list:
        pid = str(pid)
        # print(pid)
        pid = re.findall(r'id=(.+?)"', pid)
        print(pid)
        peixun_url = 'https://www.sxgbxx.gov.cn/uc/plan/info?id=' + \
            pid[0]  # 生成培训课题的url
        browser.get(peixun_url)

        # print(browser.page_source)
        time.sleep(10)
        r = browser.page_source
        pei_obj = BeautifulSoup(r, "lxml")
        peixun_list = pei_obj.findAll("a", {"class": "lh-reply-btn"})

        for i in peixun_list:
            # print(i)
            # print(i.get_text())
            # print(i['href'])
            i = 'https://www.sxgbxx.gov.cn' + str(i['href'])
            print(i)
            f1.write(i)
            f1.write('\n')

    f1.close()
    print('专题培训url下载成功')


def find_course():
    """
    下载所有课程的url
    """
    # 课程列表
    print('下载课程url')
    cou_url = "https://www.sxgbxx.gov.cn/front/showCourseList"
    browser.get(cou_url)
    # cou_html = urlopen(cou_url)
    # src = './'
    time.sleep(10)

    f1 = open(src+'cou_url.txt', 'w')
    # f2 = open(src+'cou_name.txt', 'w')

    page = 0
    TotalPage = browser.find_element(
        By.XPATH, '//*[@id="aCoursesList"]/section/section[2]/div[1]/section[1]/span/tt[2]').text
    TotalPage = int(TotalPage)

    while page < TotalPage:
        cou_obj = BeautifulSoup(browser.page_source, "lxml")
        cou_list = cou_obj.findAll("a", {"class": "j-course-title"})

        print(page+1)
        for cou in cou_list:

            print(cou.get_text())
            print(cou['href'])

            f1.write(cou['href'])
            f1.write('\n')

            # f2.write(cou.get_text())

            # f2.write('\n')
        browser.find_element(By.ID, 'nextpage').click()
        time.sleep(2)
        page += 1
    f1.close()
    # f2.close()

    print('课程url下载成功')


def find_undo_course():
    """
    下载所有未完成课程的url  can not work with headless!!!
    """
    undo_url = 'https://www.sxgbxx.gov.cn/uc/course_tzc?status=1'
    totalpage_xpath = '/html/body/div[1]/div[1]/div[4]/section[2]/div/div/article/div[3]/div/span'
    cour_xpath = '/html/body/div[1]/div[1]/div[4]/section[2]/div/div/article/div[2]/div/div/ul/li/div/div[2]/div/a'
    url_list = find_something(
        url=undo_url, totalpage_xpath=totalpage_xpath, cour_xpath=cour_xpath)[0]
    # print(url_list)
    with open('undo.txt', 'w+') as f:
        for url in url_list:
            f.write(url+'\n')


def time_counter():
    """
    按分计时
    """
    end_time = time.time()
    study_time = (end_time - start_time) / 60
    print('已学习%s分' % study_time)


def day_counter():
    """
    按天计时
    """
    end_time = time.time()
    study_time = (end_time - start_time) / 60   # 以分为单位
    study_time = int(study_time)                # 取整
    dtime = int(study_time / 60 / 24)           # 天
    other = study_time % (24*60)
    htime = other // 60                         # 时
    mtime = other % 60                          # 分

    print('已学习%s天%s时%s分' % (dtime, htime, mtime))


def xuexi(url):
    """
    提供单个学习页面的url，自动开始学习
    """
    browser.get(url)
    # print(browser.page_source)

    browser.find_element(By.XPATH,
                         '//*[@id="aCoursesList"]/div/div[2]/div/div[1]/div/div[2]/div[2]/div/ul/li').click()  # 切换到培训内容详情页
    # print(browser.page_source)
    cou_obj = BeautifulSoup(browser.page_source, 'lxml')
    time.sleep(3)
    li_list = cou_obj.findAll('li')  # 找到所有培训课程
    # print('--------------------------------------')
    # print(li_list)

    for li in li_list:

        day_counter()
        
        try:

            li_html = str(li)
            # print('--------------------------------------')
            # print(li_html)
            if 'kpoint_list' not in li_html:
                continue
            id = re.findall(r'kp_\d+', li_html)
            id = ''.join(id)
            # print(id)

            if '视频播放' in li_html:
                if '100%' in li_html:
                    continue
                title = li.get_text()  # 找到课程标题
                print(title)
                shichang = re.findall(r'\d+分\d+秒', li_html)
                shichang = re.findall(r'\d+', str(shichang))
                shichang = int(shichang[0]) * 60 + int(shichang[1])
                percent = re.findall(r'\d+\%', li_html)
                percent = re.findall(r'\d+', str(percent))
                percent = int(percent[0])
                # print('看视频')
                # print("本视频长%s秒" % shichang)
                # print("已学习%d%%" % percent)
                t = shichang * (100 - percent) * 0.01

                try:
                    browser.find_element(By.ID, id).click()
                except ElementClickInterceptedException:

                    print('计时器维护中')
                    browser.quit()
                    exit()
                   
                time.sleep(3)
                action = ActionChains(browser)
                # title = browser.find_element_by_xpath('//*[@id="N-course-box"]/article/div/div[2]/section/h3/span')  # 鼠标移动到标题
                # action.move_to_element(title).click().perform()
                time.sleep(20)
                action.send_keys(Keys.SPACE).perform()  # 单击空格
                time.sleep(t + 40)
                print(li.get_text() + "学习完毕")
                print('\n')
                print('\n')
                browser.refresh()

            elif '音频播放' in li_html:
                if '100%' in li_html:
                    continue
                title = li.get_text()  # 找到课程标题
                print(title)
                shichang = re.findall(r'\d+分\d+秒', li_html)
                shichang = re.findall(r'\d+', str(shichang))
                shichang = int(shichang[0]) * 60 + int(shichang[1])
                percent = re.findall(r'\d+\%', li_html)
                percent = re.findall(r'\d+', str(percent))
                percent = int(percent[0])
                # print('听音频')
                # print("本音频长%s秒" % shichang)
                # print("已学习%d%%" % percent)
                t = shichang * (100 - percent) * 0.01

                try:
                    browser.find_element(By.ID, id).click()

                except ElementClickInterceptedException:

                    print('计时器维护中')
                    browser.quit()
                    exit()
                

                time.sleep(t + 20)
                print(li.get_text() + "学习完毕")
                print('\n')
                print('\n')
                browser.refresh()

            elif '随堂小测验' in li_html:
                continue

            else:
                if '100%' in li_html:
                    continue
                print('读文字')

                try:
                    browser.find_element(By.ID, id).click()
                    
                except ElementClickInterceptedException:

                    print('计时器维护中')
                    browser.quit()
                    exit()
                
                time.sleep(5)
                print(li.get_text() + "学习完毕")
                print('\n')
                print('\n')
                browser.refresh()
        except TimeoutException:
            print('加载时间异常')
            continue
        except NoSuchElementException:
            print('元素异常')
            continue
        except WebDriverException:
            print('webdriver异常')
            continue
        
def shunxu_xuexi(url_file: str):
    """
    按顺序进行课程学习
    """
    with open(src + url_file, 'r') as f:
        cou_url_list = f.read().splitlines()

        # sum = len(cou_url_list)
    for cou_url in cou_url_list:

        print('--------------------------------------------------------------------------')
        print(cou_url)
        try:
            chaxun(name)
            xuexi(cou_url)
        except TimeoutException:
            print('加载时间异常')
            continue
        except NoSuchElementException:
            print('元素异常')
            continue
        except WebDriverException:
            print('webdriver异常')
            continue

def random_xuexi(url_file: str):
    """
    随机选课进行学习
    """

    with open(src + url_file, 'r') as f:
        cou_url_list = f.read().splitlines()
        sum = len(cou_url_list)

    for x in range(1, sum):  # 每次随机学习
        # 课程学习页面
        cou_url = (cou_url_list[random.randint(1, sum - 1)])
        print('--------------------------------------------------------------------------')
        print(cou_url)
        try:
            chaxun(name)
            xuexi(cou_url)
        except TimeoutException:
            print('加载时间异常')
            continue
        except NoSuchElementException:
            print('元素异常')
            continue
        except WebDriverException:
            print('webdriver异常')
            continue

def study(ume, pwd, name):
    """
     用户的学习操作步骤
    """

    login(ume, pwd, name)       # 登录

    chaxun(name)               # 查询时长

    # sign_up()              # 专题培训报名

    # find_peixun()          # 获取专题培训url

    # find_course()          # 获取课程url

    # find_undo_course()     # 获取未完成课程的url Can't work in headless chrome

    # shunxu_xuexi('undo.txt')      # 按顺序学习未完成的课程

    # 完成课程学习功能
    print(name+"课程学习开始")
    shunxu_xuexi('cou_url.txt')
    # random_xuexi('cou_url.txt')
    print(name+"课程学习结束")

    # 完成专题培训学习功能
    print(name+"专题培训开始")

    shunxu_xuexi('peixun_url.txt')               # 顺序学习
    # random_xuexi('peixun_url.txt')           # 随机学习
    # print(name+"专题培训结束")
    time.sleep(10)
    print('**************************************************************************************************************************')


if __name__ == "__main__":
    
    
    

    for user in user_list:
        ume, pwd, name = user, user, user
        
        try:
            print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
            print(f'********{name} START TO STUDY********')
            study(ume=ume, pwd=pwd, name=name)
            
        except MissionDoneException as e:
            print(e)
            continue
        except:
            print('Unknow Error')
            continue
        
    
   