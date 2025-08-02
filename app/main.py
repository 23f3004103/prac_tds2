from fastapi import FastAPI
from pydantic import BaseModel
import re
import requests
from io import StringIO
from .llm import ask_llm, extract_code, debug_llm
from .executor import safe_execute
from .scraper import fetch_text_from_url


app = FastAPI()


class Task(BaseModel):
    question: str


@app.post("/api/")
async def analyze(task: Task):
    # If question contains a URL, fetch page content and incorporate it in prompt
    match = re.search(r'https?://\S+', task.question)
    if match:
        url = match.group(0)
        page_text = fetch_text_from_url(url)
        if page_text.startswith("Failed to retrieve"):
            return {"error": page_text}
        updated_question = f"""
Given the following webpage content:

\"\"\"{page_text}\"\"\"

{task.question.strip()}
"""
    else:
        updated_question = task.question.strip()

    # Construct initial LLM prompt for generating analysis code
    prompt = f"""
You are a skilled data scientist and software engineer.

You are provided with the following content, which may contain text, tables, or mixed data:

Your task:

1. Identify and extract any structured data (tables, lists) from the content.
2. Clean and preprocess the data, including:
   - Removing footnotes, reference markers, and extra whitespace.
   - Recognizing and extracting dates or years, converting to standardized formats.
   - Parsing numeric/currency fields, safely converting strings (with commas, symbols, ranges) to numbers.
3. Infer data schema and types using headers or heuristics.
4. Perform the analysis or answer the questions provided below using Python.
5. Produce visualizations if asked, encoding any images as base64 data URIs under 100 KB.
6. Handle missing or ambiguous data gracefully, returning clear error messages if the task cannot be completed.
7. Return your final answer by assigning it to a Python variable named `result`.

Important best practices to follow:
- When parsing tables with pandas, wrap HTML strings with `io.StringIO` to avoid warnings.
- Check if dataframe columns have multiple levels before dropping levels.
- Verify expected columns exist before filtering or selecting.
- Clean numeric columns by removing any nondigit characters using raw-regex.
- Parse year fields extracting 4-digit numbers carefully.
- Use valid Python variable names (no special characters or starting digits).
- Wrap key processing steps in try-except blocks.
- Validate dataframe is not empty before sorting or indexing.
- Return only executable Python code. No explanations or markdown.

User question:

\"\"\"{updated_question}\"\"\"

Your response:

Assign the final result to a variable named `result`.
"""

    # Ask LLM for initial code
    raw_code = await ask_llm(prompt)
    code = extract_code(raw_code)

    print(code)

    # Debugging/refinement prompt with explicit instructions enforcing best practices
    debug_prompt = f"""
You are a debugging assistant for data scientists and software engineers.

Correct and improve the following Python code according to best practices:

- Wrap HTML strings passed to pandas.read_html with io.StringIO.
- Safely drop dataframe MultiIndex columns if applicable.
- Check for existence of expected columns before filtering.
- Clean number fields with raw string regex removing nondigit chars.
- Parse and coerce year fields safely extracting 4-digit years.
- Use valid Python variable names only.
- Add try-except blocks around major steps to catch errors and assign meaningful messages to `result`.
- Ensure dataframe is not empty before indexing/sorting.
- Simplify code for readability.
- Remove deprecated or warning-prone code.

Return only the corrected executable Python code below, no explanations or markdown.:

{code}
"""

    # Ask LLM to debug and improve code
    updated_raw_code = await debug_llm(debug_prompt)
    corrected_code = extract_code(updated_raw_code)

    # Execute corrected code safely
    result = safe_execute(corrected_code)

    # Debug prints (optional — remove or comment out in production)
    print("RAW LLM CODE:\n", updated_raw_code)
    print("Execution result:\n", result)

    return result
