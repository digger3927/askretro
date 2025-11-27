# Retrosheet Query: Ask Natural Language Questions About Baseball History

Have you ever wanted to ask complex questions about baseball history without needing to be a database expert? This project is your personal baseball research assistant. It leverages the power of AI to let you query the comprehensive Retrosheet database using plain English.

Simply ask a question like "Who hit the most home runs in 2018?" or "Which pitcher had the most strikeouts in the 2014 playoffs?", and the script will convert your question into a SQL query, run it against the database, and present the results in a clean, easy-to-read table.

## Features

*   **Natural Language Queries:** Ask questions in plain English. No SQL knowledge required.
*   **AI-Powered:** Uses an AI model to translate your questions into valid SQLite queries.
*   **Self-Correcting SQL:** If the initial query fails, the script automatically asks the AI to correct its own mistake, making the system more robust.
*   **Interactive Mode:** Start a session to ask multiple questions without re-running the script.
*   **Formatted Output:** Results are displayed in a clean, readable table right in your terminal.

## Getting Started

### 1. Create the SQLite Database

This project requires a SQLite database named `retrosheet.db`. You will need to create this database and import the data from the Retrosheet `.csv` files. The `column_desc.txt` file in this repository describes the necessary tables and their columns.

**TODO:** A script to automate the database creation process should be created.

### 2. Set up your OpenAI API Key

The natural language query feature uses the OpenAI API. You need to provide an API key in one of the following ways:

*   **Environment Variable (Recommended):**
    Set the `OPENAI_API_KEY` environment variable to your OpenAI API key.
    ```bash
    export OPENAI_API_KEY="your-api-key-here"
    ```

*   **File:**
    Create a file named `OPEN_API_KEY.txt` in the root of the project and paste your OpenAI API key into it.

### 3. Install Dependencies

This project requires the `openai` and `rich` Python libraries.

```bash
pip install openai rich
```

## How to Use

You can use this tool in two ways:

### 1. Interactive Mode

For an ongoing research session, run the script without any arguments to enter interactive mode.

```bash
python askretro.py
```

You will be greeted with an `askretro>` prompt. Type your questions and hit Enter. To end the session, type `quit` or `exit`.

### 2. Single Question Mode

For a single, one-off question, you can pass the question directly as a command-line argument.

```bash
python askretro.py "Your question here"
```

**Example:**

```bash
python askretro.py "Who had the most wins as a pitcher in the 1995 regular season?"
```