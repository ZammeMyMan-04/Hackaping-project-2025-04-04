from opperai import AsyncOpper
from pydantic import BaseModel
from typing import Literal
from instructions import *

class GitKeywords(BaseModel):
    keywords: list[str]

class GitCommand(BaseModel):
    command: str
    description: str

class GitCommands(BaseModel):
    commands: list[GitCommand]

class QuestionType(BaseModel):
    type: Literal["commands", "explanation"]

async def extract_question_type(opper: AsyncOpper, user_input: str) -> QuestionType:
    question_type, _ = await opper.call(
        name="extractQuestionFile",
        instructions=instructions_validate_answer,
        input=user_input,
        output_type=QuestionType
    )
    return question_type

async def extract_keywords(opper: AsyncOpper, user_input: str) -> GitKeywords:
    keywords_result, _ = await opper.call(
        name="extractGitKeywords",
        instructions=instructions_find_keywords,
        input=user_input,
        output_type=GitKeywords
    )
    return keywords_result

async def generate_git_commands(opper: AsyncOpper, keywords: list[str], user_input: str) -> GitCommands:
    commands_result_0, _ = await opper.call(
        name="generateGitCommands",
        instructions=instructions_generate_gitcommands,
        input=", ".join(keywords),
        output_type=GitCommands
    )

    final_commands_result, _ = await opper.call(
        name="generateGitCommands",
        instructions=instructions_improve_commandorder,
        input=f"Current command order: {commands_result_0.commands}, original input: {user_input}",
        output_type=GitCommands
    )

    return final_commands_result

async def give_explanation(opper, user_input: str):
    try:
        information, _ = await opper.call(
            name="extractGitKeywords",
            instructions=instructions_give_information,
            input=user_input,
            output_type=str
        )
        print("\n📖 Förklaring:")
        print(information + "\n")
    except Exception as e:
        print(f"❌ Ett fel uppstod vid hämtning av förklaring: {e} \n")