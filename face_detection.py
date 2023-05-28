import cv2
import time
import cloudinary.uploader
import cloudinary.utils
from twilio.rest import Client

# Load the face detection classifier
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Open camera
cap = cv2.VideoCapture(0)

# Reign of interest
top_left = (400, 50)
bottom_right = (800, 550)

# Cloudinary configuration
cloudinary.config(
    cloud_name="dymtzczdp",
    api_key='#',  # Replace with your actual API key
    api_secret="wOtWveO_aixYQh89yRo7ZY6XOpw"
)

# Twilio credentials
account_sid = "AC535ba97d039a980d56d7a80fb2d894b5"      # Replace with your twilio id
auth_token = "ce25f78334ed574c4aaef9ee858fccf7"     # Replace with your twilio token
client = Client(account_sid, auth_token)
to_whatsapp_number = 'whatsapp: #'       # Replace with your actual whatsapp_number
from_whatsapp_number = 'whatsapp:+14155238886'      # Replace with your actual API key

# Function to detect faces and send alerts
def detect_faces():
    count = 0
    while True:
        # Read a frame from the camera
        ret, frame = cap.read()

        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the frame
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        # Draw rectangle for area of interest
        cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 3)

        # Draw rectangles around the detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

            # Save the image if it is within the region of interest
            if x > top_left[0] and y > top_left[1] and x + w < bottom_right[0] and y + h < bottom_right[1]:
                filename = f"face/intruder_{count}.jpg"
                cv2.imwrite(filename, frame)

                # Twilio SMS alert
                message = client.messages.create(
                    body="Alert: Intrusion detected at your premises",
                    from_="+19523730493",
                    to="#"      # Replace with your actual whatsapp_number
                )
                print("INTRUDER ALERT")

                # Upload image to Cloudinary
                upload_result = cloudinary.uploader.upload(filename)
                public_id = upload_result['public_id']
                secure_url, options = cloudinary.utils.cloudinary_url(public_id, secure=True)

                # Send image and message via Twilio
                message = client.messages.create(
                    media_url=secure_url,
                    from_=from_whatsapp_number,
                    to=to_whatsapp_number
                )

                count += 1

        # Display the frame
        cv2.imshow('Frame', frame)

        # Exit if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture and close windows
    cap.release()
    cv2.destroyAllWindows()


# Run the face detection function
detect_faces()
