import whisper
import os 
# lazy from sarvamai import SarvamAI

WHISPER_MODEL = os.getenv("WHISPER_MODEL","small")
# SARVAM_STT_MODEL = os.getenv("SARVAM_STT_MODEL", "saaras:v4")

# client = SarvamAI(
#     api_subscription_key=os.getenv("SARVAM_API_KEY")
# )

_model = None


def load_model():
    global _model 
    if _model is None:
        print(f"loading model")
        _model = whisper.load_model(WHISPER_MODEL)
        print("whisper model loaded successfully")

    return _model

# def load_model():
#     print("Sarvam AI client ready")
#     return client

def transcribe_chunks(chunk_path:str,translate:bool=False)->str:
    model = load_model()
    task = "translate" if translate else "transcribe"
    result = model.transcribe(chunk_path,task=task)

    return result['text']

def transcribe_all(chunks:list,translate:bool =False):
    full_transcript = ""
    for i,chunk in enumerate(chunks):
        print(f"Transcribing chunk {i+1}")
        text = transcribe_chunks(chunk,translate=translate)
        full_transcript += text + " "
    print("Transcribtion Completed")

    return full_transcript
    

# def transcribe_chunks(chunk_path: str, translate: bool = False) -> str:
#     model = load_model()

#     task = "translate" if translate else "transcribe"

#     with open(chunk_path, "rb") as audio_file:
#         result = model.speech_to_text.transcribe(
#             file=audio_file,
#             model=SARVAM_STT_MODEL,
#             mode=task
#         )

#     return result.transcript

# def transcribe_all(chunks:list,translate:bool =False):
#     full_transcript = ""
#     for i,chunk in enumerate(chunks):
#         print(f"Transcribing chunk {i+1}")
#         text = transcribe_chunks(chunk,translate=translate)
#         full_transcript += text + " "
#     print("Transcribtion Completed")

#     return full_transcript.strip()




