# Retrosheet Query

This project allows you to query a Retrosheet baseball database using natural language. You ask a question in plain English, and the script uses an AI model to convert your question into a SQL query, which is then run against the database.

## Getting Started

### 1. Create the SQLite Database

This project requires a SQLite database named `retrosheet.db`. You will need to create this database and import the data from the `.csv` files in this repository. The `column_desc.txt` file describes the tables and their columns.

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

This project requires the `openai` Python library.

```bash
pip install openai
```

## How to Use

To ask a question, run the `askretro.py` script with your question as a command-line argument.

```bash
python askretro.py "Your question here"
```

**Example:**

```bash
python askretro.py "Who hit the most home runs in 2018?"
```

The script will print the generated SQL query and then the results of the query.

## Other Scripts

This repository contains other scripts (`retrosearch.py`, `individual.py`, etc.) that are not the primary focus of this project. They provide additional ways to interact with the Retrosheet data but may not be as up-to-date as `askretro.py`.