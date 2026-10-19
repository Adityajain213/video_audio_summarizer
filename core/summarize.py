
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
    )

def split_transcript(transcript: str) -> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=200
    )
    return splitter.split_text(transcript)

def summarize(transcript: str) -> str:
    llm = get_llm()

    map_prompt = ChatPromptTemplate.from_messages([
        ("system", "Summarize this portion of a meeting transcript concisely."),
        ("human", "{text}")
    ])

    map_chain = map_prompt | llm | StrOutputParser()

    chunks = split_transcript(transcript)

    chunk_summarize = [
        map_chain.invoke({"text": chunk})
        for chunk in chunks
    ]

    combined = "\n\n".join(chunk_summarize)

    combined_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an expert meeting summarizer. Combine the partial "
            "summaries into one final professional summary in bullet points."
        ),
        ("human", "{text}")
    ])

    combined_chain = combined_prompt | llm | StrOutputParser()

    return combined_chain.invoke({"text": combined})


def generate_title(transcript: str) -> str:
    llm = get_llm()

    title_chain = (
        ChatPromptTemplate.from_messages([
            (
                "system",
                "Based on the meeting transcript, generate a suitable short "
                "meeting title. Use at most 8 words. Return the title only."
            ),
            ("human", "{text}")
        ])
        | llm
        | StrOutputParser()
    )

    return title_chain.invoke({"text": transcript[:2000]})
