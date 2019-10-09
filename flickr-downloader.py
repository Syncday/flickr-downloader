import multiprocessing
from functools import partial
from os import path, makedirs

from requests.adapters import HTTPAdapter
from selenium import webdriver
from time import sleep, time
from lxml import etree
import requests
import img_download
#   全局变量
from selenium.webdriver.support.wait import WebDriverWait

pixel = ""
max_page = 1
driver = webdriver
pic_list = list()


def get_real_link(link,max_retries=3):
    retries = 0
    while retries<max_retries:
        try:
            html = etree.HTML(requests.get(link, timeout=5).text)
            real_link = html.xpath("//div[@id='all-sizes-header']/dl[2]/dd/a/@href")[0]
            return real_link
        except Exception as e:
            retries = retries+1
    return None


#   获取图片信息
def get_pic_info(url):
    global driver
    pages = 9999999
    page = 1
    global max_page
    while (page <= max_page and page <= pages) or len(pic_list) == 0:
        try:
            print("\r\033[1;34m正在获取第", page, "页图片链接...\033[0m", end="")
            #   设置超时时间
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
                sleep(1)
                if check_height<driver.execute_script("return document.body.scrollHeight;"):
                    continue
                sleep(2)
            titles = driver.find_elements_by_xpath("//div[@class='photo-list-photo-interaction']//a[@class='title']")
            links = driver.find_elements_by_xpath("//div[@class='photo-list-photo-interaction']//a[@class='overlay']")
            if len(links) != 0:
                print("\r\033[1;34m第", page, "页图片链接获取完成\033[0m", end="")
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
    driver.close()
    return pic_list


if __name__ == '__main__':
    print("\033[1;34m"
          "================================\n"
          "         Flick Downloader\n"
          "================================\033[0m")
    url = "https://www.flickr.com/photos/" + input("请输入名字：")  # 主页网址
    max_page = input("请输入获取页数(默认全部)：")  # 最大页数
    pixel = input("请选择分辨率（o>k>h>l）：")
    while 1:
        save_path=input("\r请输入保存路径(默认当前目录)：")
        if save_path == "":
            save_path = "."
        if path.exists(save_path):
            break
        print("\r\033[1;31m路径不存在\033[0m")
    dic_name = url.split("/")[-1]
    if max_page=="":
        max_page = 999999
    else:
        max_page = int(max_page)
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

    #   获取真实链接
    new_list = []
    i = 0
    count = len(pic_list)
    for pic in pic_list:
        title = pic[0]
        i = i+1
        print("\r\033[1;34m正在获取下载链接 "+str(i)+"/"+str(count)+": \033[0m" + pic[1],end="")
        real_link = get_real_link(pic[1])
        if real_link is not None:
            new_list.append([title,real_link])
        else:
            print("\r\033[1;31m获取下载链接出错: \033[0m" + pic[1])
    print("\r\033[1;34m已获取下载链接数 "+str(len(new_list))+"\033[0m", end="")
    sleep(10)
    pic_list.clear()
    #   下载
    index = 0
    downlod_count = 0
    error_count = 0
    count = len(new_list)
    for pic in new_list:
        index = index+1
        msg = img_download.download(pic[1],pic[0],save_path)
        for info in msg:
            for i in info:
                status_info = i.split(":", 1)
                if status_info[0] == "Error":
                    error_count = error_count+1
                    print("\r\033[1;31m" + status_info[0] + ": \033[0m" + status_info[1])
                elif status_info[0] == "Note":
                    print("\r\033[1;33m" + status_info[0] + ": \033[0m" + status_info[1])
                elif status_info[0] == "Skip":
                    print("\r\033[1;34m" + status_info[0] + " "+str(index)+"/"+str(count)+": \033[0m" + status_info[1], end="")
                else:
                    downlod_count =downlod_count+1
                    print("\r\033[1;34m" + status_info[0] + " " + str(index) + "/" + str(count) + ": \033[0m" +status_info[1], end="")


    print("\r\033[1;34m完成(下载:"+str(downlod_count)+",出错:"+str(error_count)+")\033[0m")