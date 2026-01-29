#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from rich.console import Console

console = Console()

def run(system, user):
    load_dotenv()
    if os.getenv("MOCK_MODE","true").lower()=="true":
        return "MOCK OUTPUT\n\n" + user[:600]
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    r = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL"),
        messages=[
            {"role":"system","content":system},
            {"role":"user","content":user}
        ],
        temperature=0.2
    )
    return r.choices[0].message.content

def main():
    raw = open("examples/input.txt").read()
    from prompt import SYSTEM_PROMPT
    out = run(SYSTEM_PROMPT, raw)
    open("out.md","w").write(out)
    console.print("done")

if __name__ == "__main__":
    main()
