import ebooklib
from ebooklib import epub
import os
import sys
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError


# Define environment variables
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-3.5-turbo-1106"

def reformat_text_with_openai_api(text):
    openai.api_key = os.getenv('OPENAI_API_KEY')

    system_prompt = "Your task is to reformat the following text by adding logical paragraph breaks. Paragraphs may not contain more than 3 sentences."

    user_prompt = text  # This is the text read from the file

    try:
        client = OpenAI(api_key=API_KEY)
        completion = client.chat.completions.create(
            model=MODEL,
            temperature=0,
            max_tokens=200,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        response = completion.choices[0].message.content.strip()
        return response
    except Exception as e:
        print(f"Error in OpenAI API call: {e}")
        return None


def convert_text_to_epub(original_file, reformatted_text):
    base_name = os.path.splitext(os.path.basename(original_file))[0]
    epub_file_name = os.path.splitext(original_file)[0] + '.epub'

    # Create an epub book
    book = epub.EpubBook()

    # Set metadata
    book.set_identifier('id_' + base_name)
    book.set_title(base_name.replace('_', ' ').replace('-', ' '))
    book.set_language('en')

    # Create a chapter
    c1 = epub.EpubHtml(title='Chapter 1', file_name='chap_01.xhtml', lang='en')
    c1.content = '<h1>Chapter 1</h1><p>' + reformatted_text + '</p>'

    book.add_item(c1)
    book.toc = (epub.Link('chap_01.xhtml', 'Chapter 1', 'chap1'),)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    style = 'BODY {color: white;}'
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)
    book.spine = ['nav', c1]

    epub.write_epub(epub_file_name, book, {})
    print(f"ePub file created: {epub_file_name}")

def process_file(file_path, prompt):
    with open(file_path, 'r') as file:
        content = file.read()

    reformatted_text = reformat_text_with_openai_api(content, prompt)
    if reformatted_text:
        convert_text_to_epub(file_path, reformatted_text)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py [text_file] [prompt]")
    else:
        process_file(sys.argv[1], sys.argv[2])
