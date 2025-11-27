import sqlite3
import sys
import os
from openai import OpenAI

def get_api_key(filepath="OPEN_API_KEY.txt"):
    """
    Retrieves the OpenAI API key from an environment variable or a local text file.

    It first checks for the 'OPENAI_API_KEY' environment variable. If not found,
    it attempts to read the key from the specified file.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        return api_key
    
    try:
        with open(filepath, 'r') as file:
            api_key = file.read().strip()
            return api_key
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found and the OPENAI_API_KEY environment variable is not set.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the key file: {e}")
        return None

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

def execute_query(sql_query):
    """
    Connects to the database, executes a query, and returns the results.
    """
    conn = None
    try:
        conn = sqlite3.connect('retrosheet.db')
        cursor = conn.cursor()
        
        cursor.execute(sql_query)
            
        results = cursor.fetchall()
        return results
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        user_question = ' '.join(sys.argv[1:])
        print(f"User question: {user_question}\n")

        sql_query = generate_sql_with_llm(user_question)
        
        if sql_query:
            results = execute_query(sql_query)
            
            if results:
                print("Query Results:")
                for row in results:
                    print(row)
            else:
                print("No results found for that query.")
    else:
        print("Please provide a question as a command-line argument.")
        print("Example: python askretro.py \"Who hit the most home runs in 2018?\"")
