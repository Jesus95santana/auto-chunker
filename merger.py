import os
import argparse
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
# ----------------------------
# CONFIG
# ----------------------------
DEFAULT_MODEL = "gpt-5.1"  # use a strong model for the final synthesis

MERGE_PROMPT = """You are an expert synthesizer.

You will receive multiple summaries of different sections of one large document.

Your job:
- Merge them into ONE unified, coherent document
- Maintain original meaning with NO hallucinations
- Keep structure clean and professional
- No assumptions
- No extra steps not found in the summaries
- No commentary
- Only pure synthesized content

Output a well-structured markdown document.
"""


# ----------------------------
# Utility: read file
# ----------------------------
def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ----------------------------
# MAIN
# ----------------------------
def main():
    parser = argparse.ArgumentParser(description="Merge chunk summaries into a final SOP.")
    parser.add_argument("--summaries", default="summaries", help="Folder containing summary_XX.md")
    parser.add_argument("--out", default="FINAL_SOP.md", help="Output final markdown file")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model for final synthesis")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    summary_files = sorted([f for f in os.listdir(args.summaries) if f.endswith(".md")])

    if not summary_files:
        print("No summary files found. Did you run summarizer.py?")
        return

    # Combine summaries
    combined_input = ""
    for filename in summary_files:
        path = os.path.join(args.summaries, filename)
        text = read_file(path)
        combined_input += f"\n\n### {filename}\n{text}\n"

    if args.verbose:
        print("Sending merged summaries to model...")

    response = client.chat.completions.create(
        model=args.model, messages=[{"role": "system", "content": MERGE_PROMPT}, {"role": "user", "content": combined_input}], temperature=0.2
    )

    final_text = response.choices[0].message.content

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(final_text)

    print(f"\nCreated final merged summary: {args.out}")


if __name__ == "__main__":
    main()
