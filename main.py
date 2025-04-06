import asyncio
import subprocess
from opperai import AsyncOpper
from pydantic import BaseModel
from typing import Annotated, Any, Literal
from instructions import *
import os
import argparse
from services import (
    AsyncOpper,
    GitCommands,
    extract_question_type,
    extract_keywords,
    generate_git_commands,
    give_explanation
)

def get_input():
    # Create a parser to receive command line arguments
    parser = argparse.ArgumentParser(description="GitHelp - Ask a question about Git.") 
    parser.add_argument('question', nargs='+', type=str, help="Your question about Git")
    args = parser.parse_args()
    return " ".join(args.question)

def run_commands(commands: GitCommands):
    print("\n***RUN COMMANDS***")
    for command in commands:
        user_response = input(f"\nDo you want to execute the command: '{command.command}'? [yes(ENTER)/no]: ").strip().lower()
        if user_response in ["", "yes"]:
            if "git commit -m" in command.command:
                commit_message = input("Please enter a commit message: ").strip()
                os.system(f'git commit -m "{commit_message}"')
            else:
                os.system(command.command)
        else:
            print(f"Skipped: {command.command}")
    print("\nDONE\n")

async def main():
    user_question = get_input()

    if not user_question:
        print("Please ask a question.")
        return

    opper = AsyncOpper()

    # Step 1: Identify the type of question
    question_category = await extract_question_type(opper, user_question)
    print(f"\n{question_category.type}:\n")

    if question_category.type == "commands":

        # Step 2: Extract keywords
        extracted_keywords = await extract_keywords(opper, user_question)

        # Step 3: Confirm keywords
        print("\n🔍 The AI identified the following keywords:")
        print(", ".join(extracted_keywords.keywords))
        confirmation = input("Are these correct? (yes/no): ").strip().lower()

        if confirmation not in ["yes", ""]:
            print("❌ Operation canceled. Please try again with a clearer description.")
            return

        # Step 4: Generate Git commands
        git_commands = await generate_git_commands(opper, extracted_keywords.keywords, user_question)

        # Step 5: Print the generated commands and their descriptions
        print("\n🚀 The following Git commands have been generated:")
        for index, command in enumerate(git_commands.commands):
            print(f"\n{index+1}. 📌 {command.command}")
            print(f"   📝 {command.description}")

        # Step 6: Ask for confirmation to execute the commands
        run_commands(git_commands.commands)

    elif question_category.type == "explanation":

        await give_explanation(opper, user_question)

if __name__ == "__main__":
    asyncio.run(main())


# opper = Opper(api_key="op-HYCH9WGAIC9Y451XX6Q3")