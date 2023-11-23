#!/usr/bin/env python3
import openai
import os
import argparse
import select
import sys

# Create an ArgumentParser object
parser = argparse.ArgumentParser(description='My little proofreader')
parser.add_argument('-q', '--quiet', action='store_true', help='Only output corrected version')
parser.add_argument('-s', '--simplify', action='store_true', help='Simplify paragraph')
parser.add_argument('-n', '--native', action='store_true', help='Write like a native english speaker')
parser.add_argument('-p', '--proofread', action='store_true', help='Proofread paragraph', default=True)
parser.add_argument('-i', '--improve', action='store_true', help='Improve paragraph')
parser.add_argument('-e', '--evaluate', action='store_true', help='Raw evaluate input')

args = parser.parse_args()

if args.simplify or args.native or args.improve:
    args.proofread = False

# Set up OpenAI API credentials
# Read the API key from the file
api_key_file = os.path.expanduser("~/.config/openai.apikey")

with open(api_key_file, "r") as file:
    api_key = file.read().strip()

# Set up OpenAI API credentials
openai.api_key = api_key

# Check if there is input available in stdin
def is_input_available():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

def get_input_text():
    # Read input from stdin
    if is_input_available():
        return sys.stdin.read()
    else:
        if args.evaluate:
            return input("Enter prompt: ")
        else:
            return input("Enter text to proofread: ")


proofread_prompt = "You are a helpful assistant who proofreads text. Just output the corrected text without any errors."
simplify_prompt = "You are a helpful assistant simplifies text. Your job is to reduce the complexity of sentences but you should not make up any content on your own. Break up long sentences if needed. Just output the corrected text without any errors."
native_prompt = "You are a helpful assistant who helps a non-native english speaker to write like a native would. Just output the improved text without any errors."
improve_prompt = "You are a helpful assistant who helps in writing and improves paragraphs that the user writes. But keep it short and concise. Just output the improved text without any errors."
evaluate_prompt = ""


def proofread(input_text):

    prompt = proofread_prompt

    if args.simplify:
        prompt = simplify_prompt
    if args.native:
        prompt = native_prompt
    if args.improve:
        prompt = improve_prompt
    if args.evaluate:
        prompt = evaluate_prompt

    # Generate the completion using OpenAI API
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": input_text}
        ]
    )

    # Extract the generated completion from the API response
    return response.choices[0].message.content

def highlight_corrections(text_with_errors, proofread_version):
    highlighted_text = ""
    error_start = "\033[91m"  # ANSI escape sequence for red color
    error_end = "\033[0m"  # ANSI escape sequence to reset color

    i, j = 0, 0  # Pointers for traversing the strings

    while i < len(text_with_errors) and j < len(proofread_version):
        if text_with_errors[i] == proofread_version[j]:
            highlighted_text += proofread_version[j]
            i += 1
            j += 1
        else:
            highlighted_text += error_start + proofread_version[j]
            j += 1
            highlighted_text += error_end

    # Add any remaining characters from the proofread version
    if j < len(proofread_version):
        highlighted_text += error_start + proofread_version[j:]
        highlighted_text += error_end

    return highlighted_text

def output(text_with_errors, proofread_version):

    if args.quiet:

        #if args.evaluate:
        #    print(text_with_errors + "\n\n")

        print(proofread_version)
    else:

        output_text = proofread_version
        if args.proofread:
            output_text = highlight_corrections(text_with_errors, proofread_version)
        # Print the highlighted text
        print("\nCorrected Version:")
        print(output_text)

# Main Logic
if __name__ == "__main__":
    text_with_errors = get_input_text()
    proofread_version = proofread(text_with_errors)
    output(text_with_errors, proofread_version)
