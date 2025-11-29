# WebsiteGPT

Crawl websites and build an AI-powered knowledge base for intelligent Q&A.

## Features

- Crawl websites and extract content
- Create searchable vector database
- Chat with your knowledge base using AI
- Store data in Pinecone cloud database

## Installation

1. Clone the repository:
```bash
git clone https://github.com/MishalQamar/websiteGPT.git
cd websiteGPT
```

2. Install dependencies:
```bash
uv sync
```

3. Create a `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
```

## Setup

1. Get OpenAI API key from [platform.openai.com](https://platform.openai.com)
2. Create Pinecone account at [pinecone.io](https://www.pinecone.io)
3. Create an index named `websitegpt` in Pinecone dashboard
4. Add both API keys to `.env` file

## Usage

Start the app:
```bash
streamlit run setting.py
```

1. Enter your OpenAI API key in the sidebar
2. Enter website URL and prefix filter
3. Choose crawl depth (0-5)
4. Click "Start Crawling"
5. Go to Chat page to ask questions
