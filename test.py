from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarize import summarize,generate_title
from core.extractor import extract_action_items,extract_key_decisions,extract_questions
source = "https://youtu.be/ZmDBbnmKpqQ"
chunks = process_input(source)

transcript = transcribe_all(chunks)

print(transcript[:500]+ "..." if len(transcript) > 500 else transcript)

title = generate_title(transcript)
summary = summarize(transcript)

print(f"Title : {title}")
print(f"Summary of following {title}: \n {summary}")


action = extract_action_items(transcript)
print(f"Action taken: {action}")
key_decisions = extract_key_decisions(transcript)
print(f"key decsion made : {key_decisions}")
questions = extract_questions(transcript)
print(f"Questions raised : {questions}")

