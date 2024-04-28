#from pushbullet import Pushbullet
import RPi.GPIO as GPIO
import smtplib
import time
import requests
import vonage
channel=14
buzzer=4
ledred=20
ledgreen=21
SPICLK=11
SPIMISO=9
SPIMOSI=10
SPICS=8
mq2_dpin = 26
mq2_apin = 0
GMAIL_USER_TO=["cjkteam25@gmail.com","kyrillosadel503@gmail.com","ebraamadeeb8@gmail.com"]
GMAIL_USER_FROM="carlosadel503@gmail.com"
PASS="vgrkiiyfmfbdzdif"
SUBJECT='ALERT!'
TEXT= 'Fire in The company, Fire is increasing please evacuate'
TEXT2='Smoke Detected, Please evacuate'
num=0

client = vonage.Client(key="e49723a1", secret="LBwx5QQ6GVAYm019")
sms = vonage.Sms(client)
#pb= Pushbullet("o.yI2MhPKc2rrfwfJUakaFZbnsp7toy5DG")
#print (pb.devices)

#dev =pb.get_device ('Oppo F7')


def send_mail(channel):
	server=smtplib.SMTP('smtp.gmail.com:587')
	server.starttls()
	server.login(GMAIL_USER_FROM,PASS)
	header='From: ' + GMAIL_USER_FROM
	header= header + '\n' + 'Subject: ' +SUBJECT + '\n'
	print (header)
	msg = header + '\n' + TEXT + '\n\n'
	server.sendmail(GMAIL_USER_FROM,GMAIL_USER_TO,msg)
	server.quit()
	print("text sent")
	time.sleep(6)
    
def send_mail2(mq2_apin):
	server = smtplib.SMTP('smtp.gmail.com:587')
	server.starttls()
	server.login(GMAIL_USER_FROM,PASS)
	header= 'To: ' + GMAIL_USER_TO +'\n' + 'From: ' + GMAIL_USER_FROM
	header= header + '\n' + 'Subject: ' +SUBJECT + '\n'
	print (header)
	msg= header + '\n' + TEXT2 + '\n\n'
	server.sendmail(GMAIL_USER_FROM,GMAIL_USER_TO,msg)
	server.quit()
	print("text sent")
	time.sleep(6)
    
def init():
    GPIO.setwarnings(False)
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SPIMOSI, GPIO.OUT)
    GPIO.setup(SPIMISO, GPIO.IN)
    GPIO.setup(SPICLK, GPIO.OUT)
    GPIO.setup(SPICS, GPIO.OUT)
    GPIO.setup(mq2_dpin,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
    #GPIO.setup(mq2_dpin,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(channel,GPIO.IN)
    GPIO.setup(buzzer,GPIO.OUT)
    GPIO.setup(ledred,GPIO.OUT)
    GPIO.setup(ledgreen,GPIO.OUT)

    #GPIO.add_event_callback(channel,callback)
    def callback(channel):
        print("flame detected")
    GPIO.add_event_detect(channel,GPIO.BOTH, bouncetime=300) 
    GPIO.add_event_callback(channel,callback)  
    GPIO.output(buzzer,GPIO.LOW) 
    GPIO.output(ledgreen,GPIO.HIGH)
    GPIO.output(ledred,GPIO.LOW)
     
#def callback(channel):
 #   print("flame detected")
 
# let us know when the pin goes HIgH or LOW
#assign function GPio BIN,
#Run function on change
#infinite loop
#read SPI data from MCP3008 chip,8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
    #print("ADC Num!!",adcnum)
    if ((adcnum > 7) or (adcnum < 0)):
        return -1
    GPIO.output(cspin, True)	

    GPIO.output(clockpin, False)  # start clock low
    GPIO.output(cspin, False)     # bring CS low

    commandout = adcnum
    commandout |= 0x18  # start bit + single-ended bit
    commandout <<= 3    # we only need to send 5 bits here
    for i in range(5):
        if (commandout & 0x80):
                GPIO.output(mosipin, True)
        else:
                GPIO.output(mosipin, False)
        commandout <<= 1
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)

    adcout = 0
    # read in one empty bit, one null bit and 10 ADC bits
    for i in range(12):
            GPIO.output(clockpin, True)
            GPIO.output(clockpin, False)
            adcout <<= 1
            if (GPIO.input(misopin)):
                    adcout |= 0x1

    GPIO.output(cspin, True)
    
    adcout >>= 1       # first bit is 'null' so drop it
    return adcout
    
def main():
    init()
    
    time.sleep(4)
    while True:
            COlevel=readadc(mq2_apin, SPICLK, SPIMOSI, SPIMISO, SPICS)
            
            SmokeTrigger = ((COlevel/1024.)*3.3)
            
            if GPIO.input(channel) == GPIO.HIGH:
                print ("fire in the company")
                GPIO.output(ledgreen,GPIO.LOW)
                GPIO.output(buzzer, 1)
                GPIO.output(ledred, GPIO.HIGH)
                time.sleep(3)
                GPIO.output(buzzer, 0)
                GPIO.output(ledred, GPIO.LOW)
                time.sleep(1)
                responseData = sms.send_message(
                    {
                        "from": "Manager",
                        "to": "201274159805",
                        "text": "Fire  in The company, Please Evacuate",
                    }
                )

                if responseData["messages"][0]["status"] == "0":
                    print("Message sent successfully.")
                else:
                    print(f"Message failed with error: {responseData['messages'][0]['error-text']}")
              
                try :
                    send_mail(channel)
                except:   
                    continue
 #               push =dev.push_note ("fire", "pleaaaaase evacuate")
               
            elif (SmokeTrigger>1.60):
                print("Gas leakage")
                print("Current Gas AD vaule = " +str("%.2f"%((COlevel/1024.)*3.3))+" V")
                
                GPIO.output(ledgreen,GPIO.LOW)
                GPIO.output(buzzer, 1)
                GPIO.output(ledred, GPIO.HIGH)
                time.sleep(3)
                GPIO.output(buzzer, 0)
                GPIO.output(ledred, GPIO.LOW)
                time.sleep(1)
                #push =dev.push_note ("Gas leakage", "pleake evacuate")
                #print ("Sent") 
                
                responseData = sms.send_message(
                    {
                        "from": "Manager",
                        "to": "201274159805",
                        "text": "Alert! Smoke Detected",
                    }
                )

                if responseData["messages"][0]["status"] == "0":
                    print("Message sent successfully.")
                else:
                    print(f"Message failed with error: {responseData['messages'][0]['error-text']}")
                try: 
                    send_mail2(mq2_apin)
                    
                except:
                    continue 
                    
            else:
                print ("you are safe")
                
                time.sleep(1)
                GPIO.output(buzzer, 0)
                GPIO.output(ledred,GPIO.LOW)
                GPIO.output(ledgreen,GPIO.HIGH)
if __name__=='__main__':
    try:
        main()
        pass
    except KeyboardInterrupt:
        GPIO.cleanup()
        pass    


