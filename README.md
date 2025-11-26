# Python Auto-Chunker

This project provides a robust, cross-platform Python pipeline designed for reliably processing and summarizing very large documents (10,000–100,000+ words). It implements the **chunk → summarize → merge** pattern, leveraging OpenAI APIs to produce clean, accurate, and often SOP-style outputs.

## 🚀 Features

- **Handles Massive Documents**: Processes files that exceed standard LLM context window limits.
- **Structured Outputs**: Generates outputs in formats like SOPs or structured markdown.
- **High Accuracy & Completeness**: Minimizes hallucinations and ensures no missing sections.
- **Cost-Efficient**: Optimized for API usage, especially with models like `gpt-4.1-mini`.
- **Automation-Friendly**: Designed for CLI use, shell aliases, and integration with automation tools.
- **Cross-Platform**: Works on Linux, macOS, and Windows.
- **Modular Design**: Composed of distinct scripts for chunking, summarizing, and merging.

## 💡 How It Works

The pipeline follows a three-step process:

1.  **Chunking (`chunker.py`)**: Large input files (`.md`, `.txt`) are split into smaller, manageable chunks. This process is aware of sentence boundaries and preserves markdown formatting to avoid cutting content mid-way.
2.  **Summarization (`summarizer.py`)**: Each chunk is then sent to an OpenAI model (defaulting to `gpt-4.1-mini`) for summarization. A specific prompt ensures accuracy and completeness for each segment.
3.  **Merging (`merger.py`)**: Finally, all individual chunk summaries are concatenated and processed by a more powerful model (defaulting to `gpt-5.1`) to produce a single, coherent, and structured final summary or SOP.

## 🛠️ Installation & Setup

1.  **Clone the repository**:

    ```bash
    git clone <repository_url>
    cd python-auto-chunker
    ```

    _(Replace `<repository_url>` with the actual URL if this were a public repo)_

2.  **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

    _(Note: `requirements.txt` would typically list `openai` and `python-dotenv`)_

3.  **Configure OpenAI API Key**:
    Create a `.env` file in the root directory of the project with your OpenAI API key:
    ```dotenv
    OPENAI_API_KEY=your_actual_api_key_here
    ```

## ▶️ Usage

The pipeline can be run using the `pipeline.py` script.

### Command Line Interface (CLI)

```bash
python pipeline.py <input_file.md> [options]
```

**Common Options:**

- `--chunk_words <number>`: Specify the target word count for each chunk (e.g., `--chunk_words 1800`).
- `--chunk_chars <number>`: Specify the target character count for each chunk.
- `--summarizer_model <model_name>`: Override the default summarizer model (e.g., `--summarizer_model gpt-3.5-turbo`).
- `--merger_model <model_name>`: Override the default merger model (e.g., `--merger_model gpt-4o`).
- `--verbose`: Enable verbose logging.

**Example:**

```bash
python pipeline.py my_long_document.md --chunk_words 2000 --verbose
```

This will process `my_long_document.md`, chunking it into pieces of approximately 2000 words, summarizing each chunk, and then merging the summaries into a final output file (e.g., `my_long_document_sop.md`) in the current directory.

### Making it a Global CLI Tool

For convenience, you can create a shell alias or function in your `.zshrc` or `.bashrc` file:

**Shell Function (Recommended):**

```bash
sop-gpt() {
  python3 /path/to/your/python-auto-chunker/pipeline.py "$@"
}
```

_(Replace `/path/to/your/python-auto-chunker/` with the actual path to the project directory)_

After adding this to your shell configuration, reload your shell or run `source ~/.zshrc` (or `source ~/.bashrc`). You can then run the pipeline from anywhere:

```bash
sop-gpt your_document.md --chunk_words 1500
```

## 💰 Cost Considerations

The cost of using this pipeline is primarily driven by OpenAI API token usage.

- **`gpt-4.1-mini`** is recommended for chunk summarization due to its low cost and good performance.
- **`gpt-5.1`** (or a similar powerful model) is recommended for the final merging step to ensure high-quality synthesis.

Costs are typically low, often in the range of **~$0.10–$1.50** for documents up to 50,000 words, depending on model choice and processing depth.

## ⚖️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
