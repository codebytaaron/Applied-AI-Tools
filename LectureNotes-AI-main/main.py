import openai

openai.api_key = "YOUR_API_KEY_HERE"

SYSTEM_PROMPT = """
You are a lecture note-taking assistant.
Turn raw lecture input into clear study notes.

Rules:
- Use simple language
- Organize with headings
- Highlight key terms
- Keep it easy to memorize
"""

def generate_notes(lecture_text):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": lecture_text}
        ]
    )
    return response.choices[0].message["content"]

def main():
    print("📝 LectureNotes AI")
    print("Paste your lecture notes below.")
    print("Type END on a new line when finished.\n")

    lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        lines.append(line)

    lecture_text = "\n".join(lines)
    print("\nProcessing lecture...\n")

    notes = generate_notes(lecture_text)
    print("📘 CLEAN NOTES\n")
    print(notes)

if __name__ == "__main__":
    main()
