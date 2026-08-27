import streamlit as st
from youtube_analyzer import get_video_id, process_video,get_rag,ask_question

rag = get_rag()

st.set_page_config(
    page_title="YouTube AI Assistant",
    page_icon="🎬",
    layout="wide"
)
# CSS

st.markdown("""
<style>


.stApp {
    background-color: #000000;
    color: white;
}

[data-testid="stAppViewContainer"] {
    background-color: #000000;
}

[data-testid="stHeader"] {
    background-color: #000000;
}

.question-label {
    color: white;
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 8px;
}

/* Main title */
.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: 700;
    margin-bottom: 5px;
    color: #FFFFFF;
}

.subtitle {
    text-align: center;
    color: #A0A0A0;
    font-size: 18px;
    margin-bottom: 35px;
}

/* Question label */
div[data-testid="stTextInput"] label {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

/* Question input */
div[data-testid="stTextInput"] input {
    background-color: #111111 !important;
    color: #FFFFFF !important;
    border: 1px solid #333333 !important;
    border-radius: 10px !important;
}

div[data-testid="stTextInput"] input:focus {
    border: 1px solid #6C63FF !important;
    box-shadow: 0 0 0 1px #6C63FF !important;
}

div[data-testid="stTextInput"] input::placeholder {
    color: #777777 !important;
}

/* Center button */

.button-container {
    display: flex;
    justify-content: center;
}

.stButton > button {
    background-color: #6C63FF !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}

.stButton > button:hover {
    background-color: #574FE0 !important;
}

.answer-box {
    background-color: #111111;
    border: 1px solid #292929;
    border-radius: 12px;
    padding: 20px;
    color: #FFFFFF;
}

/* Thumbnail container */

.thumbnail-wrapper {
    position: relative;
    width: 400px;
    padding: 4px;
    border-radius: 18px;
    overflow: hidden;
    margin: 30px auto 20px auto;
}


/* Moving snake light */

.thumbnail-wrapper::before {
    content: "";
    position: absolute;
    width: 180%;
    height: 180%;
    top: -40%;
    left: -40%;

    background: conic-gradient(
        transparent 0deg,
        transparent 300deg,
        rgba(255, 255, 255, 0.25) 320deg,
        #ffffff 340deg,
        #ffffff 360deg
    );

    animation: rotateLight 8s linear infinite;
}

/* Thumbnail itself */

.thumbnail {
    position: relative;
    width: 100%;
    display: block;
    border-radius: 14px;
    z-index: 1;
}

/* Keep light animation moving */

@keyframes rotateLight {

    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(360deg);
    }

}

/* Scanning box */

.scan-box {
    width: 400px;
    margin: 0 auto;
    padding: 18px;
    border-radius: 14px;
    background: #111111;
    border: 1px solid #292929;
    text-align: center;
    font-size: 17px;
    color: #FFFFFF;
}

.wait-text {
    color: #888888;
    font-size: 14px;
    margin-top: 5px;
}

</style>
""", unsafe_allow_html=True)


# Header

st.markdown(
    '<div class="main-title">🎬 YouTube AI Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Analyze a YouTube video, generate a summary, and ask questions.'
    '</div>',
    unsafe_allow_html=True
)


# Session state

if "video_url" not in st.session_state:
    st.session_state.video_url = None

if "processing" not in st.session_state:
    st.session_state.processing = False

if "main_points" not in st.session_state:
    st.session_state.main_points = None

if "transcript" not in st.session_state:
    st.session_state.transcript = None

if "language" not in st.session_state:
    st.session_state.language = None

if "explanation" not in st.session_state:
    st.session_state.explanation = None

if "video_processed" not in st.session_state:
    st.session_state.video_processed = False

if "question" not in st.session_state:
    st.session_state.question = ""

if "answer" not in st.session_state:
    st.session_state.answer = None

# Dialog

@st.dialog("🎬 Add YouTube Video")
def video_dialog():

    st.write(
        "Enter the URL of the YouTube video you want to analyze."
    )

    url = st.text_input(
        "YouTube URL",
        placeholder="https://www.youtube.com/watch?v=..."
    )

    st.info(
        "⏳ Video analysis may take some time depending on "
        "the length of the video."
    )

    if st.button(
        "🚀 Start Analysis",
        type="primary",
        use_container_width=True
    ):

        if not url:
            st.warning("Please enter a YouTube URL.")
            return

        try:
            get_video_id(url)

        except ValueError:
            st.error("Please enter a valid YouTube URL.")
            return

        st.session_state.video_url = url
        st.session_state.main_points = None
        st.session_state.explanation = None
        st.session_state.transcript = None
        st.session_state.language = None
        st.session_state.video_processed = False
        st.session_state.processing = True

        st.rerun()

# Video processing

if not  st.session_state.video_url:
    st.markdown(
        '<div class="main-title">Upload a video to get started</div>',
        unsafe_allow_html=True
    )
    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:

        if st.button(
            "🎥 Upload a Video",
            type="primary",
            use_container_width=True
        ):
            video_dialog()

if st.session_state.video_url:

    url = st.session_state.video_url

    try:

        video_id = get_video_id(url)

        thumbnail_url = (
            f"https://img.youtube.com/vi/"
            f"{video_id}/maxresdefault.jpg"
        )

        st.markdown(
            f"""
            <div class="thumbnail-wrapper">
                <img src="{thumbnail_url}" class="thumbnail">
            </div>
            """,
            unsafe_allow_html=True
        )


        if st.session_state.processing:

            st.markdown(
            """
            <div class="scan-box">
                <div style="font-size: 28px;">🔍</div>
                <div style="font-size: 18px; font-weight: 600;">
                    AI is scanning the video...
                </div>
                <div class="wait-text">
                    Extracting important points from the video
                    and preparing your explanation.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

            with st.spinner("Processing video..."):

                explanation_points = process_video(
                    url,
                    rag
                )

            # Store the generated main points
            st.session_state.main_points = "\n\n".join(explanation_points)

            st.session_state.processing = False
            st.session_state.video_processed = True

            st.rerun()

        # EXPLAIN VIDEO BUTTON

        if (
            st.session_state.video_processed
            and not st.session_state.explanation
        ):

            st.markdown(
                "<br>",
                unsafe_allow_html=True
            )

            col1, col2, col3 = st.columns([1, 1, 1])

            with col2:

                if st.button(
                    "🧠 Explain Video",
                    type="primary",
                    use_container_width=True
                ):

                    with st.spinner(
                        "AI is generating the explanation..."
                    ):

                        explanation = st.session_state.main_points

                    st.session_state.explanation = explanation

                    st.rerun()

        # DISPLAY EXPLANATION

        if st.session_state.explanation:

            st.markdown("<br>", unsafe_allow_html=True)

            st.subheader("📖 Full Explanation")

            st.markdown(
                st.session_state.explanation
            )

    except Exception as e:

        st.error(
            f"Something went wrong: {str(e)}"
        )

        st.session_state.processing = False

    # QUESTION ANSWERING

if st.session_state.video_processed:

    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("💬 Ask a Question")

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        query = st.text_input(
            "Ask a question about this video",
            placeholder="e.g. What technologies were used?",
            label_visibility="visible"
        )

    if st.button(
        "Ask",
        type="primary",
    ):

        if not query.strip():

            st.warning("Please enter a question.")

        else:

            with st.spinner("Finding the answer..."):

                answer = ask_question(
                    query,
                    st.session_state.video_url
                )

            st.session_state.answer = answer

            st.rerun()


    # DISPLAY ANSWER

if st.session_state.answer:

    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("🤖 Answer")

    st.markdown(
        st.session_state.answer
)