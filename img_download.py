# -*- coding: utf-8 -*-
# @Time    : 2019/10/7
# @Author  : syncday

"""
@ links     : Direct download link for images
function    : get image info without download, compare with local file and determine whether to download
:return     list(message)
"""

from os import path
import requests


def download(link: str, img_name: str, save_path=".", headers: dict = "") -> list:
    message = list()
    try:
        #   Get only the headers, no content
        img_info = requests.head(link, headers=headers).headers
        try:
            img_size = img_info["Content-Length"]
        except Exception as e:
            img_size = "0"
        img_format = img_info["Content-Type"].split("/")[-1].replace("jpeg", "jpg")

        #   Check if is in image format
        if img_info["Content-Type"].split("/")[0] != "image":
            return ["Error: Link:" + link + ", Info: '" + img_name + "' is not a image"]

        #   Determine the save path and confirm if the file already exists
        img_name = img_name.replace("?", "").replace("*", "").replace("/", "").replace("\\", "").replace(">", "") \
            .replace("<", "").replace("|", "").replace(":", "").replace("\"", "")
        if img_name == "":
            img_name = img_size
        save_path = save_path + "/"
        save_path = save_path.replace("//", "/")
        file_path = save_path + img_name + "." + img_format
        if path.exists(file_path):
            if str(path.getsize(file_path)) == img_size:
                message.append(["Skip: '" + img_name + "' already exists, skip download"])
                return message
            else:
                img_name = img_name + "_" + img_size
                file_path = save_path + img_name + "." + img_format
                if path.exists(file_path):
                    message.append(["Skip: '" + img_name + "' already exists, skip download"])
                    return message
                message.append(["Note: '" + img_name.split("_", 1)[0] + "' is renamed, new name is '" + img_name])
        #   get image
        data = requests.get(link, headers=headers)

        #   save image
        with open(file_path, 'wb') as f:
            f.write(data.content)
            f.close()
        message.append(["Saved: '" + img_name + "' is saved"])
        return message
    except Exception as e:
        message.append(["Error: Link:" + link + ", Info:" + str(e)])
        return message
