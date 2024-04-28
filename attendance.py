from flask import Flask, request, jsonify

import RPi.GPIO as GPIO

import sqlite3

import cv2

import numpy as np

import face_recognition

import os

import csv

import smtplib

from datetime import datetime

# from PIL import ImageGrab

import time

import dlib

import mysql.connector



app = Flask(__name__)



dataset_path = 'ImagesAttendance'

ledred=20

ledgreen=16

db_host = "172.20.10.6"

db_user = "pi"

db_name = "employee_management"

GMAIL_USER_TO=["nabilnesma97@gmail.com","kyrillosadel503@gmail.com","ebraamadeeb8@gmail.com","tasneemsherif45@gmail.com"]

GMAIL_USER_FROM="carlosadel503@gmail.com"

PASS="vgrkiiyfmfbdzdif"

SUBJECT='ALERT!'

TEXT= 'Unknown Human is Detected!!'

def init():

    GPIO.setwarnings(False)

    GPIO.cleanup()

    GPIO.setmode(GPIO.BCM)

    GPIO.setup(ledred,GPIO.OUT)

    GPIO.setup(ledgreen,GPIO.OUT)

    GPIO.output(ledgreen,GPIO.LOW)

    GPIO.output(ledred,GPIO.LOW)

def send_mail():

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

	time.sleep(3)

def initialize_database():

    conn = mysql.connector.connect(host=db_host,

        user=db_user,

        database=db_name)

    c = conn.cursor()

    conn.commit()

    conn.close()





def load_face_recognition_model():

    # Load the trained face recognition model from disk

    return dlib.face_recognition_model_v1(face_recognition_model)



def load_dataset():

    # Load the dataset of known faces and their corresponding IDs

    dataset = {}

    conn = mysql.connector.connect(host=db_host,

                                   user=db_user,

                                   database=db_name)

    c = conn.cursor()

    c.execute("SELECT employee_id FROM employees_attendence")

    rows = c.fetchall()

    for row in rows:

        dataset[row[0]] = row[0]

    conn.close()

    return dataset





path = 'ImagesAttendance'

ID = 0

images = []

classNames = []

myList = os.listdir(path)

print(myList)



for cl in myList:

  curImg = cv2.imread(f'{path}/{cl}')

  ID = ID + 1

  images.append(curImg)

  classNames.append(os.path.splitext(cl)[0])

print(classNames , ID)

print(classNames)









def findEncodings(images):

  encodeList = []

  for img in images:

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    encode = face_recognition.face_encodings(img)[0]

    encodeList.append(encode)

  return encodeList



def mark_attendance(ID):

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = mysql.connector.connect(host=db_host,

                                   user=db_user,

                                   database=db_name)

    c = conn.cursor()

    if ID not in mark_attendance.marked_attendance:  # Check if ID has already been marked

            c.execute("INSERT INTO employees_attendence (employee_id, created_at, attendance) VALUES (%s, %s, 'ATTENDEE')", (ID, created_at))

            mark_attendance.marked_attendance.append(ID)  # Add ID to the marked_attendance list

    

    conn.commit()

    conn.close()

mark_attendance.marked_attendance = [] 



@app.route('/api/attendance', methods=['GET'])

def get_attendance():

    conn = mysql.connector.connect(host=db_host,

                                   user=db_user,

                                   database=db_name)

    c = conn.cursor()

    c.execute("SELECT * FROM employees_attendence")





    rows = c.fetchall()

    conn.close()



    employees_attendence = []

    for row in rows:

        record = {'id': row[0], 'employee_id': row[1], 'created_at': row[2], 'attendance': row[3]}

        employees_attendence.append(record)



    return jsonify(employees_attendence)





if __name__ == '__main__':

    initialize_database()

    dataset = load_dataset()



    encodeListKnown = findEncodings(images)

    print('Encoding Complete')



    cap = cv2.VideoCapture(0)



    while True:

        init()

        success, img = cap.read()

        # img = captureScreen()

        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)

        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)



        facesCurFrame = face_recognition.face_locations(imgS)

        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)



        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):

            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)

            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

            # print(faceDis)

            matchIndex = np.argmin(faceDis)



            if faceDis[matchIndex] < 0.50:

                name = classNames[matchIndex].upper()

                mark_attendance(name)

                GPIO.output(ledgreen,GPIO.HIGH)

                time.sleep(2)



            else:

                name = 'Unknown'

                GPIO.output(ledred,GPIO.HIGH)

                time.sleep(2)

                try:

                    send_mail()

                except:

                    continue    

            print(name)

            y1, x2, y2, x1 = faceLoc

            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)

            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)



        cv2.imshow('Webcam', img)

        cv2.waitKey(1)

