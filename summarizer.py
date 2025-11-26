import os
import argparse
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
# ----------------------------
# CONFIG
# ----------------------------
DEFAULT_MODEL = "gpt-4.1-mini"  # cheap & great for per-chunk summaries
SUMMARY_PROMPT = """You are a summarization assistant.

Summarize the following content accurately and thoroughly.
Do NOT add information that is not in the text.
Do NOT omit important steps or details.

Return a clean, organized summary:
- No fluff
- No hallucinated steps
- No assumptions
"""


# ----------------------------
# Utility: read text file
# ----------------------------
def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ----------------------------
# Utility: write summary file
# ----------------------------
def save_summary(text, output_dir, index):
    os.makedirs(output_dir, exist_ok=True)
    outfile = os.path.join(output_dir, f"summary_{index:02d}.md")
    with open(outfile, "w", encoding="utf-8") as f:
        f.write(text)
    return outfile


# ----------------------------
# Summarization logic
# ----------------------------
def summarize_text(client, model, text):
    response = client.chat.completions.create(
        model=model, messages=[{"role": "system", "content": SUMMARY_PROMPT}, {"role": "user", "content": text}], temperature=0.2
    )
    return response.choices[0].message.content


# ----------------------------
# MAIN
# ----------------------------
def main():
    parser = argparse.ArgumentParser(description="Summarize chunk files.")
    parser.add_argument("--chunks", default="chunks", help="Folder containing chunk_XX.md")
    parser.add_argument("--out", default="summaries", help="Folder to save summaries")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="OpenAI model to use")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    chunk_files = sorted([f for f in os.listdir(args.chunks) if f.endswith(".md")])

    if not chunk_files:
        print("No chunk files found. Did you run chunker.py first?")
        return

    print(f"Summarizing {len(chunk_files)} chunks with model: {args.model}")

    for idx, filename in enumerate(chunk_files, start=1):
        path = os.path.join(args.chunks, filename)
        text = read_file(path)

        summary = summarize_text(client, args.model, text)
        outfile = save_summary(summary, args.out, idx)

        if args.verbose:
            print(f"Saved {outfile}")

    print(f"\nDone! Created {len(chunk_files)} summaries in '{args.out}'")


if __name__ == "__main__":
    main()
