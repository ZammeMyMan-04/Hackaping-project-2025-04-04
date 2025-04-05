import asyncio
import subprocess
from opperai import AsyncOpper
from pydantic import BaseModel
from typing import Annotated, Any, Literal
from instructions import *
import sys
import os
import argparse


# Modell för nyckelord (steg 2-3)
class GitKeywords(BaseModel):
    keywords: list[str]

# Modell för Git-kommandon (steg 4-5)
class GitCommand(BaseModel):
    command: str
    description: str

class GitCommands(BaseModel):
    commands: list[GitCommand]

class QuestionType(BaseModel):
    type: Literal["commands", "explanation"]

# async def get_question_type(opper, user_input):
#     question_type, _ = await opper.call(
#         name="extractQuestionFile",
#         instructions=instructions_validate_answer,
#         input=user_input,
#         output_type=QuestionType
#     )
#     return question_type

def get_input():
    # Skapa en parser för att ta emot kommandoradsargument
    parser = argparse.ArgumentParser(description="GitHelp - Ställ en fråga om Git.")
    
    # Använd 'nargs="+"' för att ta emot alla ord efter githelp som en lista, som sedan kan slås ihop till en sträng
    parser.add_argument('question', nargs='+', type=str, help="Din fråga om Git")

    # Hämta argumentet som skickades från kommandoraden
    args = parser.parse_args()

    # Slå samman alla ord i listan till en enda sträng
    user_input = " ".join(args.question)

    return user_input

def run_commands(commands):
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

    question_type, _ = await opper.call(
        name="extractQuestionFile",
        instructions=instructions_validate_answer,
        input=user_input,
        output_type=QuestionType
    )

    print(f"\n{question_type.type}:\n")

    if question_type.type == "commands":

        # 2️⃣ Opper analyserar input och extraherar nyckelord
        keywords_result, _ = await opper.call(
            name="extractGitKeywords",
            instructions=instructions_find_keywords,
            input=user_input,
            output_type=GitKeywords
        )

        # 3️⃣ (Mellansteg) Bekräfta nyckelorden med användaren
        print("\n🔍 AI hittade följande nyckelord:")
        print(", ".join(keywords_result.keywords))
        confirm = input("Är dessa korrekt? (ja/nej): ").strip().lower()

        if confirm != "ja":
            print("❌ Avbryter. Försök igen med en tydligare beskrivning.")
            return

        # 4️⃣ Konvertera nyckelord till Git-kommandon
        commands_result_0, _ = await opper.call(
            name="generateGitCommands",
            instructions=instructions_generate_gitcommands,
            input=", ".join(keywords_result.keywords),
            output_type=GitCommands
        )

        final_commands_result, _ = await opper.call(
            name="generateGitCommands",
            instructions=instructions_improve_commandorder,
            input=f"Current command order: {commands_result_0.commands}, original input: {user_input}",
            output_type=GitCommands
        )

        # 5️⃣ Bekräfta vilka kommandon som ska köras
        print("\n🚀 Följande Git-kommandon har genererats:")
        for idx, command in enumerate(final_commands_result.commands):
            print(f"\n{idx+1}. 📌 {command.command}")
            #print(f"   📝 {command.description}")

        run_commands(final_commands_result.commands)

    elif question_type.type == "explanation":

        information, _ = await opper.call(
            name="extractGitKeywords",
            instructions=instructions_give_information,
            input=user_input,
            output_type=str
        )

        print(information)

    print("")
    #os.system("deactivate")


if __name__ == "__main__":
    asyncio.run(main())


# opper = Opper(api_key="op-HYCH9WGAIC9Y451XX6Q3")