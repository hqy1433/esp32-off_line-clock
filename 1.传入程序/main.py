from machine import Pin, SPI
import machine,network,time,_thread 
import vga2_8x16 as small_font
import vga2_16x32 as big_font
import usocket as socket  # 引用socket模块
import st7789,st7789py
import DS3231micro #时钟库
import dht  #传感器驱动库

def refresh_time():
    with open('index.html', 'rb') as f:  
        html_content = f.read()
        
    ap = network.WLAN(network.AP_IF)
    ap.config(essid='ESP-32')
    ap.active(True)  # 开启无线热点
    
    tft.text(big_font, "Use WEB Browser", 0, 0)
    tft.text(big_font, "To Access This", 0, 32)
    tft.text(big_font, ap.ifconfig()[0], 32, 64, st7789py.color565(0,0,255))
    tft.text(big_font, "To Update Time", 0, 96)
    tft.text(big_font, "SSID:ESP-32", 0, 128)

    
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # (重要)设置端口释放后立即就可以被再次使用
    s.bind(socket.getaddrinfo("0.0.0.0", 80)[0][-1])  # 绑定地址
    s.listen(1)  # 开启监听（最大连接数1）
    
    time_dic={}
    while True:  # mian()函数中进行死循环，在这里保持监听浏览器请求与对应处理
        client_sock, client_addr = s.accept()  # 接收来自客户端的请求与客户端地址
        client_sock.write(html_content)# 向客户端发送网页内容
        request = client_sock.recv(1024)
        client_sock.close()
        if p19.value():
            tft.fill(0)
            tft.text(big_font, "Failed get", 0, 0)
            tft.text(big_font, "REBOOT in 5 S", 0, 32)
            time.sleep(5)
            machine.reset()  #重启ESP32
        if request.decode().partition('\r\n\r\n')[-1]:
            date=request.decode().partition('\r\n\r\n')[-1]
            print(date)
            #ap.active(False)
            date=date.split('&')
            for pair in date:
                key,value = pair.split('=')
                time_dic[key] = int(value)
            return time_dic
        
Ds3231 = DS3231micro.DS3231(22,21)
st7789.ST7789(SPI(2, 60000000), dc=Pin(2), cs=Pin(5), rst=Pin(15))
tft = st7789py.ST7789(SPI(2, 60000000), 240, 240, reset=Pin(15), dc=Pin(2), cs=Pin(5), rotation=0)
tft.fill(0)
d = dht.DHT22(Pin(4))
p19=Pin(19,Pin.IN)
weekend={"01":"Mon.","02":"Tues.","03":"Wed.","04":"Thurs.","05":"Fri.","06":"Sat.","07":"Sun."}


if p19.value():
    time_list=refresh_time()
    Ds3231.setDateTime(time_list['year'],time_list['month'],time_list['day'],time_list['weekday'],time_list['hour'],time_list['minute'],time_list['second'])
    tft.fill(0)
    tft.text(big_font, "Successful get", 0, 0)
    tft.text(big_font, "REBOOT in 5 S", 0, 32)
    time.sleep(5)
    machine.reset()  #重启ESP32
    
tft.text(big_font, "_______________", 0, 88)

while True:
    time_list=Ds3231.getDateTime()
    for i in range(len(time_list)):
        if len(str(time_list[i]))<2:
            time_list[i]="0"+str(time_list[i])
        else:
            time_list[i]=str(time_list[i])

    tft.text(big_font, "20"+time_list[0]+"."+time_list[1]+"."+time_list[2], 24, 44)
    tft.text(small_font, weekend[time_list[3]], 192, 60)
    tft.text(big_font, time_list[4]+":"+time_list[5]+":"+time_list[6], 56, 76)
    
    d.measure()
    tft.text(big_font, "T:"+str(d.temperature())+" "+"H:"+str(d.humidity())+"%", 8, 120)
       
