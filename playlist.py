import streamlit as st
import base64
import os

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


st.header("Your Emotion Based Playlist")

# Extract mood from URL query parameters
query_params = st.experimental_get_query_params()
mood = query_params.get("mood", [None])[0]

if mood:
    st.header(f"Feeling {mood} !")
    st.success(f"Here are some {mood} songs for you")
    song_list = os.listdir(f"./song/{mood}/")
    str_song_path = f"./song/{mood}/"
    for i in song_list:
        st.write(i.replace(".mp3", "") + ":")
        st.audio(str_song_path + i)
else:
    st.warning("Mood not specified in the URL. Please go back and select a mood.")