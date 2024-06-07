import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
import av
import cv2
import base64
import numpy as np
import mediapipe as mp
from keras.models import load_model
import os

model = load_model("model.h5")
label = np.load("labels.npy")
holistic = mp.solutions.holistic
hands = mp.solutions.hands
holis = holistic.Holistic()
drawing = mp.solutions.drawing_utils

# Load and encode the background image
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

bg_image_path = "img/colorfulmusic.png"  # Ensure this path is correct
bg_image_base64 = get_base64_image(bg_image_path)

# Define custom CSS for background image
page_bg_img = f'''
<style>
    .stApp {{
        background-image: url("data:image/png;base64,{bg_image_base64}");
        background-size: cover;
    }}

    .content-container {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.7); /* Adjust the opacity as needed */
        overflow-y: auto;
    }}
</style>
'''

# Inject the CSS into the app
st.markdown(page_bg_img, unsafe_allow_html=True)
st.markdown('<div class="content-container">', unsafe_allow_html=True)



st.header("Mood Melodies")

if "run" not in st.session_state:
    st.session_state["run"] = "true"

try:
    emotion = np.load("emotion.npy")[0]
except:
    emotion = ""

if not emotion:
    st.session_state["run"] = "true"
else:
    st.session_state["run"] = "false"

class EmotionProcessor(VideoProcessorBase):
    def recv(self, frame):
        frm = frame.to_ndarray(format="bgr24")
        frm = cv2.flip(frm, 1)
        res = holis.process(cv2.cvtColor(frm, cv2.COLOR_BGR2RGB))
        lst = []

        if res.face_landmarks:
            for i in res.face_landmarks.landmark:
                lst.append(i.x - res.face_landmarks.landmark[1].x)
                lst.append(i.y - res.face_landmarks.landmark[1].y)

            if res.left_hand_landmarks:
                for i in res.left_hand_landmarks.landmark:
                    lst.append(i.x - res.left_hand_landmarks.landmark[8].x)
                    lst.append(i.y - res.left_hand_landmarks.landmark[8].y)
            else:
                for i in range(42):
                    lst.append(0.0)

            if res.right_hand_landmarks:
                for i in res.right_hand_landmarks.landmark:
                    lst.append(i.x - res.right_hand_landmarks.landmark[8].x)
                    lst.append(i.y - res.right_hand_landmarks.landmark[8].y)
            else:
                for i in range(42):
                    lst.append(0.0)

            lst = np.array(lst).reshape(1, -1)
            pred = label[np.argmax(model.predict(lst))]
            print(pred)
            cv2.putText(frm, pred, (50, 50), cv2.FONT_ITALIC, 1, (255, 0, 0), 2)
            np.save("emotion.npy", np.array([pred]))

        drawing.draw_landmarks(frm, res.face_landmarks, holistic.FACEMESH_TESSELATION,
                               landmark_drawing_spec=drawing.DrawingSpec(color=(0, 0, 255), thickness=-1, circle_radius=1),
                               connection_drawing_spec=drawing.DrawingSpec(thickness=1))
        drawing.draw_landmarks(frm, res.left_hand_landmarks, hands.HAND_CONNECTIONS)
        drawing.draw_landmarks(frm, res.right_hand_landmarks, hands.HAND_CONNECTIONS)

        return av.VideoFrame.from_ndarray(frm, format="bgr24")

if st.session_state["run"] != "false":
    webrtc_streamer(key="key", video_processor_factory=EmotionProcessor)

btn = st.button("Recommend me songs")

if btn:
    if not emotion:
        st.warning("Please let me capture your emotion first")
        st.session_state["run"] = "true"
    else:
        st.success(f"Here are some {emotion} songs for you")
        song_list = os.listdir(f"./song/{emotion}/")
        str_song_path = f"./song/{emotion}/"
        for i in song_list:
            st.write(i.replace(".mp3", "") + ":")
            st.audio(str_song_path + i)
        np.save("emotion.npy", np.array([""]))
        st.session_state["run"] = "false"

        # Adding social media sharing buttons
        base_url = "https://mood-melodies-moody-playlist.streamlit.app/"  
        share_url = f"{base_url}/?mood={emotion}"
        share_text = f"Check out this {emotion} playlist!"

        html = f"""
        <div class="share-buttons">
        <h4>Share your Mood and Mood Based Song Playlist with Your Friends</h4>
            <a href="https://www.facebook.com/sharer.php?u={share_url}" target="_blank">
                <img src="https://upload.wikimedia.org/wikipedia/commons/5/51/Facebook_f_logo_%282019%29.svg" alt="Facebook" width="40" height="40"/>
            </a>&nbsp;&nbsp;
            <a href="https://wa.me/?text={share_text}%20{share_url}" target="_blank">
                <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" alt="WhatsApp" width="40" height="40"/>
            </a>&nbsp;&nbsp;
            <a href="https://www.instagram.com/?url={share_url}" target="_blank">
                <img src="https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png" alt="Instagram" width="40" height="40"/>
            </a>&nbsp;&nbsp;
            <a href="https://www.linkedin.com/shareArticle?mini=true&url={share_url}&title={share_text}&summary={share_text}" target="_blank">
                <img src="https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png" alt="LinkedIn" width="40" height="40"/>
            </a>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)