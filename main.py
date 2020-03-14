import os
from PIL import Image,ImageFilter,ImageEnhance
import time
import cv2
import numpy
import glob
import os
import datetime

#新建目标文件夹
def mkdir(path):
    path = path.strip()
    path = path.rstrip("\\")

    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)
        return True
    else:
        return False

#主 图片预处理
def imgTransfer(im):
    im = im.filter(ImageFilter.MedianFilter(1))
    im = ImageEnhance.Contrast(im).enhance(1.5)
    im = im.convert('L')  # 灰度图转换
    im = denoising(im)  # 图片去噪
    imgc = binarizing(im, 200)  # 图片二值化
    return imgc

#去噪
def denoising(im):
    pixdata = im.load()
    w, h = im.size
    for j in range(1, h - 1):
        for i in range(1, w - 1):
            count = 0
            if pixdata[i, j - 1] > 245:
                count = count + 1
            if pixdata[i, j + 1] > 245:
                count = count + 1
            if pixdata[i + 1, j] > 245:
                count = count + 1
            if pixdata[i - 1, j] > 245:
                count = count + 1
            if count > 2:
                pixdata[i, j] = 255
    return im

#图片增强，二值化函数
def binarizing(im, threshold):
    pixdata = im.load()
    w, h = im.size
    for j in range(h):
        for i in range(w):
            if pixdata[i, j] < threshold:
                pixdata[i, j] = 255
            else:
                pixdata[i, j] = 0
    return im

#反色。把黑底变白底255，把不是白底的（字）变为黑色0
def inverse_color(image):
    for row in range(src.shape[0]):
        for col in range(src.shape[1]):
            for channel in range(src.shape[2]):
                if mask[row, col, channel] == 0:
                    val = 0
                else:
                    reverse_val = 255 - src[row, col, channel]
                    val = 255 - reverse_val * 256 / mask[row, col, channel]
                    if val < 0:
                        val = 0
                image[row, col, channel] = val
    height,width,_ = image.shape
    img2 = image.copy()
    for i in range(height):
        for j in range(width):
            img2[i,j] = (255-image[i,j])
            if img2[i, j].sum(axis=None, dtype=None, out=None)!=765:
                img2[i,j] = 0
    return img2

#删除中间缓存图片
def delete_file(src):
    if os.path.isfile(src):
        try:
            os.remove(src)
        except:
            pass
    elif os.path.isdir(src):
        for item in os.listdir(src):
            itemsrc=os.path.join(src,item)
            delete_file(itemsrc)
        try:
            os.rmdir(src)
        except:
            pass

if __name__ == '__main__':
    srcpath = "E:/tianmao"
    maskpath = "E:/mask"
    finpath = "E:/fin"

    mkpath = maskpath
    mkdir(mkpath)
    mkpath = finpath
    mkdir(mkpath)

    for filepath in os.listdir(srcpath):
        filename1 = os.path.splitext(filepath)[1]
        filename1 = filename1.lower()
        if filename1 == '.jpg' or filename1 == '.png' or filename1 == '.jpeg' or filename1 == '.bmp':

            src = cv2.imread(filepath)
            start = time.clock()
            print("正在生成" + (filepath) + "水印图...")
            im = Image.open(filepath)
            imgc = imgTransfer(im)  # 图片预处理,二值化,图片增强
            imgc.save(os.path.join(maskpath, os.path.basename(filepath)))
            print("当前水印图生成完毕")
            mask = cv2.imread(os.path.join(maskpath, os.path.basename(filepath)))
            print("已获取原图: " + (filepath))
            print("已获取其水印图: " + (os.path.join(maskpath, os.path.basename(filepath))))
            print ("正在生成，请稍后...")
            saver = numpy.zeros(src.shape, numpy.uint8)
            result = inverse_color(saver)
            cv2.imwrite((finpath) + "/" + (filepath), result)
            end = time.clock()
            print ("耗时" + str(round(end - start)) + "秒")
            print("当前测试图片生成完毕！" + "\n")

    dirname = maskpath
    delete_file(dirname)
    print("结束！")