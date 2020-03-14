from tkinter import * #@UnusedWildImport
from tkinter import filedialog #@Reimport
import os
import time
from PIL import Image
import pytesseract
import xlrd
import xlwt
import re
import sys
import threading
from threading import Lock
import math

def fun():
    write_log_to_Text("识别中,请稍等...")
    filepath = init_Text.get(1.0, END).strip()#获取输入框中的值 = init_Text.get(1.0, END).strip()#获取输入框中的值
    # 将文件名列表重新排序#
    # 没有xxpng.png干扰的顺序读取
    const = 4 #线程数,可更改
    filelist = os.listdir(filepath)
    filelist.sort(key=lambda x: int(x[:-4]))
    thradsum = int(math.ceil(len(filelist) / const))#计算给每个线程分配的资源数,
    thl = []#线程的集合
    biglist = []#分配资源的集合
    count = 0#计数器
    #创建5个线程,
    for i in range(const):
        biglist.append([])
        if len(filelist) - count >= thradsum:
            for x in range(thradsum):
                biglist[i].append(os.path.join(filepath, filelist[count]))
                count += 1
        else: 
            for x in range(len(filelist) - count):
                biglist[i].append(os.path.join(filepath, filelist[count]))
                count += 1
                
        th1 = threading.Thread(target=init, args=(biglist[i],)) 
        thl.append(th1)
    for t in thl:
        t.setDaemon(True)
        t.start()   
#    dir1 = []
#    dir2 = []
#    dir3 = []
#    dir4 = []
#    dir5 = []
#    for x in range(0, 10):
#        dir1.append(os.path.join(filepath, filelist[x]))
#    th1 = threading.Thread(target=init, args=(dir1,)) 
#    thl.append(th1)
#    
#    for x in range(10, 20):
#        dir2.append(os.path.join(filepath, filelist[x]))
#    th2 = threading.Thread(target=init, args=(dir2,)) 
#    thl.append(th2)
#    
#    for x in range(20, 30):
#        dir3.append(os.path.join(filepath, filelist[x]))
#    th3 = threading.Thread(target=init, args=(dir3,)) 
#    thl.append(th3)
#    
#    for x in range(30, 40):
#        dir4.append(os.path.join(filepath, filelist[x]))
#    th4 = threading.Thread(target=init, args=(dir4,)) 
#    thl.append(th4)
#    
#    for x in range(40, 50):
#        dir5.append(os.path.join(filepath, filelist[x]))
#    th5 = threading.Thread(target=init, args=(dir5,)) 
#    thl.append(th5)
#    print(thl)
#    print(len(thl))

#将文件夹内图片重命名，排除不规范文件名
def re_name(filepath):
    # file_list 文件夹下文件名的列表，以字符串方式排序
    file_list = os.listdir(filepath)
    for filename in file_list:
        oldname = filepath + '/' + filename
        file_num = re.compile('\d+', re.S)
        i = int(file_num.findall(filename)[0])
        newname = filepath + '/' + "%d" % i + ".png"
        # print(newname)
        os.rename(oldname, newname)

#功能函数
#点击选择文件按钮之后调用的第一个函数
def openfile():#打开文件调用函数
    path = filedialog.askopenfilename(title='打开文件', filetypes=[('PNG', '*.png *.PNG'), ('All Files', '*')])
    dols(path)

#将所选路径写入到选择文件的输入框中.并在日志信息框中输出成功

def dols(selectdir):
    if os.path.isfile(selectdir):#判断是不是一个文件，空文件也返回false
        filepath = os.path.split(selectdir)[0]

        # 获取文件名列表
        filelist = os.listdir(filepath)
        # 调用re_name函数，将不规范文件名规范化
        re_name(filepath)
        # 将文件名列表重新排序#
        # 没有xxpng.png干扰的顺序读取
        filelist.sort(key=lambda x: int(x[:-4]), reverse=True)
        init_Text.delete(1.0, END)#防止重复写路径
        init_Text.insert(1.0, filepath)
        if os.path.isdir(filepath): #判断name是不是一个目录，不是目录就返回false
            for s in filelist:
                result_Text.insert(1.0, s + '\n')
            write_log_to_Text("导入目录成功" + "\n" + "点击【全部识别】后开始...")

#保存
#def savefile(self):#打开文件调用函数
#    s = filedialog.askopenfilename(title='打开文件', filetypes=[('All Files', '*')])
#    if os.path.isfile(s):#判断是不是一个文件，空文件也返回false
#        dir = os.path.split(s)[0]
#        self.save_Text.insert(1.0, dir)
#        self.save_button.bind("<Button-1>", pic2str.main(r))
            
#日志动态打印
def write_log_to_Text(logmsg):
    #获取当前时间
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    logmsg_in = str(current_time) + " " + str(logmsg) + "\n"      #换行
    log_Text.insert(END, logmsg_in)
    init_window.update()
    
#以下函数是识别图片的
def NumAndName(str):
    result = []
    str_1 = r'注册号:'
    str_2 = r'名称:'
    #正则表达式
    # Num = re.compile(str_1 + '(\w{18})', re.S)
    # Name = re.compile(str_2 + '(.*?有限公司)', re.S)
    Num = re.compile(str_1 + '(\w{18})', re.S)
    Name = re.compile('\w{18}' + '(.*?有限公司)', re.S)
    #贪婪匹配提取并容错判断
    if len(Num.findall(str)) == 0:
        result = None
    else:
        num = Num.findall(str)[0]
        if len(Name.findall(str)) == 0:
            result = None
        else:
            name = Name.findall(str)[0]
            result.append(num)
            result.append(name)
            result[1] = result[1].replace('企业名称:', '')
    return result

def py2ex(file, Num_Name, filename):
    num = Num_Name[0]
    name = Num_Name[1]
    file_num = re.compile('\d+', re.S)
    i_str = file_num.findall(filename)[0]
    i = int(i_str) + 1
    data_sheet.write(i, 0, name)
    data_sheet.write(i, 1, num)
    return file

#点击全部处理之后,第一个调用此函数
def init(filepath):
    global file, data_sheet
    # tesseract-ocr功能地址 可能可以删
    tesseract_cmd = 'E:/python/Install_tesseract-ocr/Tesseract-OCR/tesseract.exe'

    # 创建表，sheet.write(行, 列, "内容")
    file = xlwt.Workbook(encoding='utf-8')
    # 创建sheet
    data_sheet = file.add_sheet('企业信息')
    data_sheet.write(0, 0, "企业名称")
    data_sheet.write(0, 1, "企业注册号")
    lock = Lock()
    #开始识别
    for filename in filepath:
        # 调用tesseract-ocr识别图片
        pic2str = pytesseract.image_to_string(Image.open(filename), lang='chi_sim', config='digits')

        #获取文字信息并提取特征
        Information = ''.join(pic2str.split())
        result = NumAndName(Information)
        filename = os.path.basename(filename)#E:/fin/1.png 返回 1.png
        if result == None:
            write_log_to_Text("    " + "【" + filename + "】" + "    " + '识别失败')
            print(filename + '识别失败')
        else:
            write_log_to_Text("    " + "【" + filename + "】" + "    " + '识别成功')
            print(filename + ':' + str(result))
            #输出到excel
            py2ex(file, result, filename)
        lock.acquire()#互斥锁,只允许同时一个进行
        file.save("企业信息.xls")
        lock.release()
#GUI界面函数
def main():
    global init_window
    init_window = Tk()#实例化出一个父窗口
    init_window.title("图片识别工具_v1.0")  #窗口名
    #1068x681为窗口大小，+130 +10 定义窗口弹出时的默认展示位置
    init_window.geometry('1000x481+130+150')
    #标签
    result_label = Label(init_window, text="选择待处理路径:")
    result_label.grid(row=0, column=0)
    result_label = Label(init_window, text="日志信息")
    result_label.grid(row=1, column=4)
    result_label = Label(init_window, text="选择待保存路径:")
    result_label.grid(row=4, column=0)
    #文本框
    global init_Text, result_Text, log_Text, save_Text
    
    init_Text = Text(init_window, width=28, height=1)  #选择打开路径
    init_Text.grid(row=0, column=1)
        
    result_Text = Text(init_window, width=41, height=29)  # 选定路径内容展示
    result_Text.grid(row=1, column=0, columnspan=2, rowspan=2)
        
    log_Text = Text(init_window, width=88, height=27)  #处理日志展示
    log_Text.grid(row=2, column=4)

    save_Text = Text(init_window, width=28, height=1)  #选择保存路径,rowspan=1
    save_Text.grid(row=4, column=1)
       
    #按钮
    global open_button, all_button, save_button
    open_button = Button(init_window, text="选择文件", bg="lightblue", command=openfile)  # 调用内部方法  加()为直接调用
    open_button.grid(row=0, column=3)
#    one_button = Button(init_window, text="单个处理")  # 调用内部方法  加()为直接调用
#    one_button.grid(row=2, column=4)
    all_button = Button(init_window, text="全部识别", bg="lightblue", command=fun)  # 调用内部方法  加()为直接调用
    all_button.grid(row=2, column=3)
    save_button = Button(init_window, text="保存文件", bg="lightblue")  # 调用内部方法  加()为直接调用
    save_button.grid(row=4, column=3)
    #显示全部
    init_window.mainloop()

if __name__ == '__main__':
    main()
