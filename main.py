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
    # Skapa en parser för att ta emot kommandoradsargument
    parser = argparse.ArgumentParser(description="GitHelp - Ställ en fråga om Git.")
    parser.add_argument('question', nargs='+', type=str, help="Din fråga om Git")
    args = parser.parse_args()
    return " ".join(args.question)

def run_commands(commands: GitCommands):
    print("\n***RUN COMMANDS***")
    for command in commands:
        yes_or_no = input(f"\nKör '{command.command}'   [ja(ENTER), nej]: ")
        if yes_or_no in ["", "ja"]:
            if "git commit -m" in command.command:
                message = input("Enter commit message: ")
                os.system(f'git commit -m "{message}"')
            else:
                os.system(command.command)
    print("\nDONE\n")

async def main():
    user_input = get_input()

    if not user_input:
        print("Skriv en fråga.")
        return

    opper = AsyncOpper()

    # 1️⃣ Användaren skriver vad hen vill göra
    #user_input = input("Input: ")

    # question_type, _ = await opper.call(
    #     name="extractQuestionFile",
    #     instructions=instructions_validate_answer,
    #     input=user_input,
    #     output_type=QuestionType
    # )

    # 1: Identify the type of question
    question_type = await extract_question_type(opper, user_input)
    print(f"\n{question_type.type}:\n")

    if question_type.type == "commands":

        # 2️⃣ Opper analyserar input och extraherar nyckelord
        # keywords_result, _ = await opper.call(
        #     name="extractGitKeywords",
        #     instructions=instructions_find_keywords,
        #     input=user_input,
        #     output_type=GitKeywords
        # )

        # 2: Extract keywords
        keywords_result = await extract_keywords(opper, user_input)

        # 3: Confirm keywords
        print("\n🔍 AI hittade följande nyckelord:")
        print(", ".join(keywords_result.keywords))
        confirm = input("Är dessa korrekt? (ja/nej): ").strip().lower()

        if confirm not in ["ja", ""]:
            print("❌ Avbryter. Försök igen med en tydligare beskrivning.")
            return

        # 4️⃣ Konvertera nyckelord till Git-kommandon
        # commands_result_0, _ = await opper.call(
        #     name="generateGitCommands",
        #     instructions=instructions_generate_gitcommands,
        #     input=", ".join(keywords_result.keywords),
        #     output_type=GitCommands
        # )

        # 4: Generate Git commands
        commands = await generate_git_commands(opper, keywords_result.keywords, user_input)



        # final_commands_result, _ = await opper.call(
        #     name="generateGitCommands",
        #     instructions=instructions_improve_commandorder,
        #     input=f"Current command order: {commands.commands}, original input: {user_input}",
        #     output_type=GitCommands
        # )

        # 5️⃣ Bekräfta vilka kommandon som ska köras
        # 5: Print the generated commands and their descriptions
        print("\n🚀 Följande Git-kommandon har genererats:")
        for index, command in enumerate(commands.commands):
            print(f"\n{index+1}. 📌 {command.command}")
            print(f"   📝 {command.description}")

        # 6: Ask for confirmation to run the commands
        run_commands(commands.commands)

    elif question_type.type == "explanation":

        await give_explanation(opper, user_input)

if __name__ == "__main__":
    asyncio.run(main())


# opper = Opper(api_key="op-HYCH9WGAIC9Y451XX6Q3")