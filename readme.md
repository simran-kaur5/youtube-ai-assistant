# YouTube AI Assistant

YouTube AI Assistant is a Streamlit-based application that lets you analyze a YouTube video, generate a concise explanation, and ask questions about the video.

I built this project to experiment with combining **LLMs, RAG, embeddings, and YouTube transcripts** into one application.

## What it does

* Takes a YouTube video URL
* Extracts the video transcript
* Cleans and converts the transcript into concise English
* Splits the content into smaller chunks
* Generates embeddings using Sentence Transformers
* Stores the chunks in ChromaDB
* Retrieves relevant content when a question is asked
* Uses an LLM to answer questions based on the video content
* Generates a short explanation containing the main points

## Tech Stack

* **Python**
* **Streamlit** – Web interface
* **Agno** – AI agent framework
* **Groq** – LLM inference
* **YouTube Transcript API** – Transcript extraction
* **Sentence Transformers** – Text embeddings
* **ChromaDB** – Vector database
* **Scikit-learn** – Similarity-related utilities

## How the RAG part works

The basic flow is:

```text
YouTube URL
     ↓
Extract Transcript
     ↓
Clean / Process Transcript
     ↓
Split into Chunks
     ↓
Generate Embeddings
     ↓
Store in ChromaDB
     ↓
User asks a Question
     ↓
Retrieve Relevant Chunks
     ↓
LLM generates the Answer
```

The question-answering system uses the retrieved video content as context instead of sending the entire video transcript to the model every time.

## Project Structure

```text
youtube-ai-assistant/
│
├── app.py
├── youtube_analyzer.py
├── rag.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Running Locally

Clone the repository:

```bash
git clone https://github.com/simran-kaur5/youtube-ai-assistant.git
cd youtube-ai-assistant
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project directory:

```env
GROQ_API_KEY=your_api_key_here
```

Then run the Streamlit application:

```bash
streamlit run app.py
```

## Notes

The application currently uses a local ChromaDB directory for storing the processed video chunks.

For the deployed version, the vector database is mainly intended for the current application session. A persistent hosted vector database would be a better choice for a production application.

## Future Improvements

Some things I plan to improve:

* Reduce the number of LLM calls during transcript processing
* Improve the UI and loading experience
* Add support for more transcript languages
* Add better error handling for unavailable transcripts
* Use persistent cloud vector storage
* Improve retrieval quality for longer videos
* Add conversation history for follow-up questions

## Author

**Simran Kaur**

GitHub: https://github.com/simran-kaur5
