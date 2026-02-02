import os
import sys
import argparse
from dotenv import load_dotenv, dotenv_values
from openai import OpenAI
from litellm import completion
from litellm.exceptions import AuthenticationError as LiteLLMAuthError
from openai import AuthenticationError as OpenAIAuthError

load_dotenv()
ENV_VARS = dotenv_values()
# ----------------------------
# CONFIG
# ----------------------------
DEFAULT_MODEL = "gpt-4.1"  # cheap & great for per-chunk summaries
SUMMARY_PROMPT = """You are a summarization assistant.

Summarize the following content accurately and thoroughly.
Do NOT add information that is not in the text.
Do NOT omit important steps or details.

Return a clean, organized summary:
- No fluff
- No hallucinated steps
- No assumptions
"""


def get_litellm_api_key():
    # Prefer .env's LITELLM_API_KEY; fall back to env (zshrc).
    return ENV_VARS.get("LITELLM_API_KEY") or os.getenv("LITELLM_API_KEY")


def get_openai_api_key():
    # Prefer .env's OPENAI_API_KEY; fall back to env (zshrc)
    return ENV_VARS.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")


def prompt_fallback():
    answer = input("\n⚠️  LiteLLM failed authentication.\nProceed using OpenAI API instead? [y/N]: ").strip().lower()
    return answer == "y"


def summarize_with_litellm(model, text):
    api_key = get_litellm_api_key()

    response = completion(
        model=model,
        api_key=api_key,
        api_base="https://litellm.spinen.net/v1",
        messages=[
            {"role": "system", "content": SUMMARY_PROMPT},
            {"role": "user", "content": text},
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content


def summarize_with_openai(client, model, text):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SUMMARY_PROMPT},
            {"role": "user", "content": text},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content


def summarize_text(client, model, text):
    # Always try LiteLLM first
    try:
        return summarize_with_litellm(model, text)

    except LiteLLMAuthError as e:
        print(f"\n❌ LiteLLM auth error: {e}")

    except Exception as e:
        print(f"\n❌ LiteLLM error: {e}")

    # Ask before falling back to OpenAI
    if not prompt_fallback():
        print("Aborted by user.")
        sys.exit(1)

    # Fallback to OpenAI using OPENAI_API_KEY
    try:
        return summarize_with_openai(client, model, text)

    except OpenAIAuthError as e:
        print(f"\n❌ OpenAI auth error: {e}")
        sys.exit(1)


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
# MAIN
# ----------------------------
def main():
    parser = argparse.ArgumentParser(description="Summarize chunk files.")
    parser.add_argument("--chunks", default="chunks", help="Folder containing chunk_XX.md")
    parser.add_argument("--out", default="summaries", help="Folder to save summaries")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="OpenAI model to use")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    openai_key = get_openai_api_key()
    if not openai_key:
        print("OPENAI_API_KEY not found. Set it in your .env file or export it in your shell environment.")
        sys.exit(1)

    client = OpenAI(api_key=openai_key)

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
