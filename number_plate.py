import cv2
import time
import requests
import subprocess

harcascade = "model/haarcascade_russian_plate_number.xml"
api_url = 'https://api.api-ninjas.com/v1/imagetotext'
api_key = '#'  # Replace with your actual API key

cap = cv2.VideoCapture(0)
cap.set(3, 640)  # width
cap.set(4, 480)  # height

min_area = 500
count = 0

capture_interval = 1  # Time interval between captures (in seconds)
api_request_interval = 3  # Time interval between API requests (in seconds)
start_time = time.time()
last_api_request_time = 0

# taget array
number_plates = ['1234','21BHO001AA','567','3333','21 BH 0001 A4','1 BH 0001 AA', 'HR26DK8337']
while True:
    success, img = cap.read()

    plate_cascade = cv2.CascadeClassifier(harcascade)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    plates = plate_cascade.detectMultiScale(img_gray, 1.1, 4)

    for (x, y, w, h) in plates:
        area = w * h

        if area > min_area:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(img, "Number Plate", (x, y - 5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 255), 2)

            img_roi = img[y:y + h, x:x + w]
            cv2.imshow("ROI", img_roi)

            current_time = time.time()
            elapsed_time = current_time - start_time

            if elapsed_time >= capture_interval and current_time - last_api_request_time >= api_request_interval:
                cv2.imwrite("plates/scaned_img_" + str(count) + ".jpeg", img_roi)

                # Sending image to the Image to Text API
                files = {'image': open("plates/scaned_img_" + str(count) + ".jpeg", 'rb')}
                headers = {'X-Api-Key': api_key}
                r = requests.post(api_url, headers=headers, files=files)
                response = r.json()
                
                if isinstance(response, list) and len(response) > 0:
                    text_fields = [plate['text'] for plate in response]
                    if text_fields != ';' :
                        joined_text = ' '.join(text_fields)
                    print("Text Field:", joined_text)  # Print the joined text fields
                    if joined_text in number_plates:
                       print("Match found vehicle is stolen")
                       subprocess.call(["python3", "face_detection.py"])
                    else:
                      print("No record found")
                count += 1
                start_time = current_time
                last_api_request_time = current_time

    cv2.imshow("Result", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()