import multiprocessing
from functools import partial
from os import path, makedirs

from requests.adapters import HTTPAdapter
from selenium import webdriver
from time import sleep, time
from lxml import etree
import requests

#   全局变量
from selenium.webdriver.support.wait import WebDriverWait

pixel = ""
max_page = 1
driver = webdriver
pic_list = list()


def get_download(pic, dic_name, pic_list):
    try:
        #   获取下载链接
        html = etree.HTML(requests.get(pic[1]).text)
        real_link = html.xpath("//div[@id='all-sizes-header']/dl[2]/dd/a/@href")[0]
        #   创建文件夹
        dir = "./pic/" + dic_name
        file_name = pic[0] + ".jpg"
        if not path.exists(dir):
            makedirs(dir)
        #   关闭持久链接,重连次数为3
        session = requests.session()
        session.keep_alive = False
        session.mount('http://', HTTPAdapter(max_retries=3))
        session.mount('https://', HTTPAdapter(max_retries=3))
        #   下载图片
        data = requests.get(real_link, headers={"referer": pic[1]})
        if data.status_code != 200:
            data = requests.get(pic[1].replace("jpg", "png"), headers={"referer": pic[1]})
            file_name = pic[0] + ".png"
        #   存在文件。如果文件大小相同则跳过
        if path.exists(dir + "/" + file_name):
            file_size = path.getsize(dir + "/" + file_name)
            content_size = len(data.content)
            if file_size == content_size:
                print("\r\033[1;34m跳过：", file_name, "\033[0m", end="")
                return
            file_name = pic[0] + "_" + str(time()).split(".")[0] + ".jpg"
            print("\r\033[1;33m注意：\033[0m", pic[0], "有重名文件，新文件为", file_name)
        with open(dir + "/" + file_name, 'wb') as f:
            f.write(data.content)
            f.close()
        print("\r\033[1;34m当前 %s/%s：" % (pic_list.index(pic), len(pic_list)), file_name, "下载完成\033[0m", end="")
    except Exception as e:
        print("\r\033[1;31m出错：\033[0m", e)
        print("\033[1;31m出错链接：\033[0m\n", pic[1])


#   获取图片信息
def get_pic_info(url):
    global driver
    pages = 1
    page = 1
    global max_page
    while page <= max_page and page <= pages or len(pic_list) == 0:
        try:
            print("\r\033[1;34m正在获取第", page, "页图片链接...\033[0m", end="")
            #   设置超时时间
            WebDriverWait(driver, 10)
            driver.get(url + "/page" + str(page))
            if page == 1:
                pages = driver.find_elements_by_xpath("//div[@class='view pagination-view"
                                                      " requiredToShowOnServer photostream']/a")
                pages = len(pages) - 1
            #   滚动条位置。不变，则认为加载完成
            scroll_height = list()
            while True:
                driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
                check_height = driver.execute_script("return document.body.scrollHeight;")
                if check_height in scroll_height:
                    break
                else:
                    scroll_height.append(check_height)
                sleep(10)
            titles = driver.find_elements_by_xpath("//div[@class='photo-list-photo-interaction']//a[@class='title']")
            links = driver.find_elements_by_xpath("//div[@class='photo-list-photo-interaction']//a[@class='overlay']")
            #   添加图片信息，标题，引导链接
            for i in range(len(titles)):
                pic_list.append([titles[i].get_attribute("innerText")
                                .replace("?", "").replace("*", "").replace("/", "")
                                .replace("\\", "").replace(">", "").replace("<", "")
                                .replace("|", "").replace(":", "")
                                    , links[i].get_attribute("href") + "sizes/" + pixel])
            if len(titles) > 0:
                page = page + 1
        except Exception as e:
            print("\r", e)
    print("\r", end="")
    driver.close()
    return pic_list


if __name__ == '__main__':
    print("\033[1;34m"
          "================================\n"
          "         Flick Downloader\n"
          "================================\033[0m")
    url = "https://www.flickr.com/photos/" + input("请输入名字：")  # 主页网址
    max_page = int(input("输入获取页数（留空默认全部）："))  # 最大页数
    max_thread = int(input("输入下载线程（Default=1，Max=5）："))  # 最大线程数
    pixel = input("请选择分辨率（o>k>h>l）：")
    dic_name = url.split("/")[-1]
    #   配置driver
    chrome_opt = webdriver.ChromeOptions()
    #   不显示图片，减少渲染时间
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_opt.add_experimental_option("prefs", prefs)
    #   隐藏窗口
    chrome_opt.add_argument("headless")
    driver = webdriver.Chrome(r"D:\App\IDE\Python3\driver\chromedriver", options=chrome_opt)
    #  获取图片链接
    pic_list = get_pic_info(url)
    # 多线程下载
    pool = multiprocessing.Pool(max_thread if max_thread < 5 else 5)
    pool.map(partial(get_download, dic_name=dic_name,pic_list=pic_list), pic_list)
    print("\n\033[1;34m完成\033[0m")
