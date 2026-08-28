from textwrap import dedent
from dotenv import load_dotenv
from agno.agent import Agent
from agno.tools.youtube import YouTubeTools
from agno.models.groq import Groq
import re
from youtube_transcript_api import YouTubeTranscriptApi
from rag import VideoRAG
import streamlit as st

load_dotenv()


def get_video_id(url):
    match = re.search(r"(?:v=|youtu\.be/)([^&?/]+)",url)
    if not match:
        raise ValueError("Invalid YouTube URL")

    return match.group(1)

def transcription(url):
    video_id = get_video_id(url)

    api = YouTubeTranscriptApi()
    transcript_list = api.list(video_id)
    transcript = transcript_list.find_transcript(["hi", "en"])

    language = transcript.language_code  # to avoid translation if the video is already in english
    fetched_transcript = transcript.fetch()

    text = ""
    
    for item in fetched_transcript:
        minutes = int(item.start // 60)
        seconds = int(item.start % 60)
        text += f"[{minutes}:{seconds:02d}] {item.text}\n"

    return text,language

def split_transcript(text, max_char=3000):
    current = ""
    chunks = []

    for line in text.splitlines():
        if len(line) + len(current) > max_char:
            chunks.append(current)
            current = ""

        current += line + "\n"

    if current:
        chunks.append(current)

    return chunks


youtube_agent = Agent(
    name="YouTube Agent",
    model=Groq(id="openai/gpt-oss-20b"),
    tools=[YouTubeTools()],
    instructions=dedent("""\
        You convert video transcripts into concise English study text.

        Rules:
        - Use ONLY information from the provided transcript.
        - Preserve timestamps exactly.
        - Never invent timestamps or information.
        - Remove filler, repetition, greetings, and promotional content.
        - Keep important concepts, explanations, examples, and conclusions.
        - Keep the original order.
        - Use simple, natural English.
        - Make the output significantly shorter while preserving important information.
    """),
    markdown=True,
)

def process_transcript(transcript):

    chunks = split_transcript(transcript)
    english_transcript = ""
    print("Got chunks")

    for i,chunk in enumerate(chunks):
        response = youtube_agent.run(
            f"""
            Convert the following YouTube transcript into clear English.

            Rules:
            - Keep ONLY the main points and important information.
            - Remove filler, repetition, greetings, and unnecessary conversation.
            - Preserve important facts, names, companies, technologies, achievements,
            numbers, examples, and conclusions.
            - Keep the original order.
            - Use short, clear sentences.
            - Do not summarize the entire video; keep the important points from this section.
            - keep only important information.
            - Keep timestamps only when they help identify the start of an important topic or section.
            - Do not repeat timestamps for every sentence.
            - Place the timestamp naturally at the end of an important point or beside the section heading.

            Remove:
            - Greetings
            - Filler
            - Repetition
            - Promotional content
            - Unimportant conversation

            Transcript:
            {chunk}
            """
        )

        print(f"Response of {i+1} chunk {response.content}")

        english_transcript += response.content + "\n\n"

    return english_transcript

def process_video(url, rag):

    video_id = get_video_id(url)

    # Create fresh collection for this video
    rag.create_collection(video_id)

    # Get transcript
    transcript, language = transcription(url)

    print("processing video")

    # Translate Hindi -> English if required
    english_transcript = process_transcript(transcript)

    # Split transcript into manageable chunks
    chunks = split_transcript(
        english_transcript,
        max_char=3000
    )

    # Store main points in RAG
    rag.add_chunks(chunks)

    return chunks


def ask_question(query,url):

    video_id = get_video_id(url)

    # Check whether video exists in ChromaDB
    # if not rag.collection_exists(video_id):
    #     return ("No video has been processed yet. "
    #         "Please process a YouTube video first.")

    rag.load_collection(video_id)

    results = rag.search(
        query,
        n_result=3
    )

    documents = results.get("documents",[[]])[0]

    if not documents:
        return "I couldn't find relevant information in the processed video."

    context = "\n\n".join(documents)

    response = youtube_agent.run(
    f"""
    Answer the user's question based primarily on the retrieved video content.

    Retrieved video content:
    {context}

    User question:
    {query}

     Rules:
        - Answer directly and clearly.
        - Use only information contained in the retrieved video content.
        - Combine information from multiple sections when necessary.
        - Do not invent information.
        - Do not use outside knowledge.
        - Do not mention RAG, retrieval, chunks, embeddings, or the transcript.
        - Do not mention timestamps unless the user asks for them.
        - If the retrieved content does not contain enough information to answer,
          say exactly:
          "I couldn't find that information in the video."
    """
)
    return response.content

@st.cache_resource
def get_rag():
    return VideoRAG()

rag = get_rag()




