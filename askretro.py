import sqlite3
import sys
import os
from openai import OpenAI
from rich.console import Console
from rich.table import Table

def get_api_key():
    """
    Retrieves the OpenAI API key from the 'OPENAI_API_KEY' environment variable.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: The 'OPENAI_API_KEY' environment variable is not set.")
        return None
    return api_key

def get_db_schema_from_file(filepath="column_desc.txt"):
    """
    Reads the database schema from a local text file.
    """
    try:
        with open(filepath, 'r') as file:
            schema = file.read()
            return schema
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the schema file: {e}")
        return None

def get_hints_from_file(filepath="hints.txt"):
    """
    Reads hints for the LLM from a local text file.
    """
    try:
        with open(filepath, 'r') as file:
            hints = file.read()
            return hints
    except FileNotFoundError:
        print(f"Warning: The file '{filepath}' was not found. Continuing without hints.")
        return ""
    except Exception as e:
        print(f"An error occurred while reading the hints file: {e}")
        return ""

def generate_sql_with_llm(question):
    """
    Sends a question and database schema to an LLM to generate a SQL query.
    
    Args:
        question (str): The natural language question.

    Returns:
        str: The generated SQL query string.
    """
    api_key = get_api_key()
    if not api_key:
        return None

    db_schema = get_db_schema_from_file()
    if not db_schema:
        return None

    hints = get_hints_from_file()
        
    client = OpenAI(api_key=api_key)
    
    try:
        full_system_prompt = f"You are a SQL expert. Your task is to generate a valid SQLite query for the given question based on the provided database schema. Only provide the SQL query and nothing else.\n\n{db_schema}\n\n{hints}"

        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": full_system_prompt},
                {"role": "user", "content": question}
            ]
        )
        
        generated_query = response.choices[0].message.content.strip()
        print(f"LLM generated query:\n{generated_query}\n")
        
        # Robust cleaning logic
        if generated_query.startswith("```sql"):
            generated_query = generated_query.strip("```sql").strip()
        if generated_query.endswith("```"):
            generated_query = generated_query.strip("```").strip()
        
        query_start = generated_query.lower().find("select")
        if query_start != -1:
            generated_query = generated_query[query_start:]
        
        # Validate the query
        if not generated_query.lower().strip().startswith("select"):
            print("Error: The generated query is not a SELECT statement.")
            return None
            
        return generated_query

    except Exception as e:
        print(f"An error occurred while calling the OpenAI API: {e}")
        return None

def get_corrected_sql_with_llm(question, old_query, error_message):
    """
    Sends the old query and error message to an LLM to get a corrected SQL query.
    """
    api_key = get_api_key()
    if not api_key:
        return None

    db_schema = get_db_schema_from_file()
    if not db_schema:
        return None

    hints = get_hints_from_file()
    client = OpenAI(api_key=api_key)

    try:
        correction_prompt = f"""You are a SQL expert. You generated a query that resulted in an error. Your task is to fix it.
        Original Question: {question}
        Faulty Query:
        {old_query}
        Error Message:
        {error_message}

        Based on the error, provide only the corrected, valid SQLite query.
        """
        full_system_prompt = f"You are a SQL expert. Your task is to generate a valid SQLite query for the given question based on the provided database schema. Only provide the SQL query and nothing else.\n\n{db_schema}\n\n{hints}"

        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": full_system_prompt},
                {"role": "user", "content": correction_prompt}
            ]
        )
        
        generated_query = response.choices[0].message.content.strip()
        print(f"LLM generated corrected query:\n{generated_query}\n")
        
        # Robust cleaning logic
        if generated_query.startswith("```sql"):
            generated_query = generated_query.strip("```sql").strip()
        if generated_query.endswith("```"):
            generated_query = generated_query.strip("```").strip()
        
        query_start = generated_query.lower().find("select")
        if query_start != -1:
            generated_query = generated_query[query_start:]
        
        # Validate the query
        if not generated_query.lower().strip().startswith("select"):
            print("Error: The generated query is not a SELECT statement.")
            return None
            
        return generated_query

    except Exception as e:
        print(f"An error occurred while calling the OpenAI API: {e}")
        return None

def execute_query(sql_query):
    """
    Connects to the database, executes a query, and returns the results.
    On error, it returns the error message.
    """
    conn = None
    try:
        conn = sqlite3.connect('retrosheet.db')
        cursor = conn.cursor()
        
        cursor.execute(sql_query)
            
        results = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        return results, columns
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None, str(e)
    finally:
        if conn:
            conn.close()

def process_question(user_question):
    """
    Takes a user's question, generates SQL, executes it, and prints the results.
    Includes a retry mechanism for failed queries.
    """
    print(f"User question: {user_question}\n")
    sql_query = generate_sql_with_llm(user_question)
    
    if not sql_query:
        return

    results, error = execute_query(sql_query)
    
    if error:
        print("The first query failed. Asking the LLM for a correction...")
        sql_query = get_corrected_sql_with_llm(user_question, sql_query, error)
        if not sql_query:
            return
        results, error = execute_query(sql_query)

    if error:
        print(f"The corrected query also failed. Error: {error}")
        return

    if results:
        table = Table(title="Query Results")
        for column in columns:
            table.add_column(column, justify="right", style="cyan", no_wrap=True)
        
        for row in results:
            table.add_row(*[str(item) for item in row])
        
        console = Console()
        console.print(table)
    else:
        print("No results found for that query.")

def main():
    """
    Main function to run the script in either single-question or interactive mode.
    """
    if len(sys.argv) > 1:
        # Single question mode from command-line arguments
        user_question = ' '.join(sys.argv[1:])
        process_question(user_question)
    else:
        # Interactive mode
        print("Entering interactive mode. Type 'quit' or 'exit' to leave.")
        while True:
            user_question = input("askretro> ")
            if user_question.lower() in ["quit", "exit"]:
                break
            if user_question:
                process_question(user_question)

if __name__ == '__main__':
    main()
