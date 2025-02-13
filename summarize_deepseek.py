import logging
from typing import List
import os

import dotenv
from langchain.chains.summarize import load_summarize_chain
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from tree_sitter import Node
from langchain_core.messages import SystemMessage
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser

from langchain_deepseek import ChatDeepSeek

from prompt_template import SWIFT_FUNCTION_DOC_INSTRUCTION, SWIFT_FUNCTION_DOC_PROMPT
import dotenv

dotenv.load('.env')


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

####################################################################################################################
REFINE_PROMPT_TMPL = (
    "Your job is to produce a final standalone concise documentation comment for a type described by code or comments, \n"
    "following the official Apple and Swift guidelines.\n"
    "The comment include:\n"
    "A concise description of the code's purpose and data flow.\n"
    "Any additional notes or context, if necessary.\n"
    "Every line in your reply should start with ///\n"
    "We have provided an existing documentation up to a certain point: {existing_answer}\n"
    "We have the opportunity to refine the existing documentation with some more context below.\n"
    "------------\n"
    "{text}\n"
    "------------\n"
    "Given the new context, refine the original documentation.\n"
    "If the context isn't useful, return the original documentation.\n"
)
REFINE_PROMPT = PromptTemplate(
    input_variables=["existing_answer", "text"],
    template=REFINE_PROMPT_TMPL,
)
prompt_template = """Write a concise standalone documentation comment for a type described by code or comments, following the official Apple and Swift guidelines:

"{text}"

documentation comment where every line starts with ///:"""
PROMPT = PromptTemplate(template=prompt_template, input_variables=["text"])
####################################################################################################################

chat_model = ChatDeepSeek(model="deepseek-chat", temperature=0, max_tokens=None, max_retries=2)
sum_chain = load_summarize_chain(chat_model, chain_type="refine", question_prompt=PROMPT, refine_prompt=REFINE_PROMPT)

def wrap_triple_slash_comments(text: str, max_line_length=120):
    lines = text.split("\n")
    wrapped_lines = []

    for line in lines:
        line = line.strip()
        if not line.startswith("///"):
            break

        indent = len(line) - len(line.lstrip())
        words = line.split()
        current_line = words[0]
        for word in words[1:]:
            if len(current_line) + len(word) + 1 > max_line_length:
                wrapped_lines.append(current_line)
                current_line = " " * indent + "/// " + word
            else:
                current_line += f" {word}"
        wrapped_lines.append(current_line)

    return "\n".join(wrapped_lines)


def generate_function_documentation(function_implementation: str) -> str:
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=SWIFT_FUNCTION_DOC_INSTRUCTION),
            HumanMessagePromptTemplate.from_template(SWIFT_FUNCTION_DOC_PROMPT),
        ]
    )

    chain = prompt | chat_model | StrOutputParser()
    result = chain.invoke({"function_implementation": function_implementation})
    print(result)
    return ""
    # return wrap_triple_slash_comments(result)


def chain_summarize(text: str) -> str:
    logger.info(f"Summarizing text:\n{text}")
    try:
        docs = RecursiveCharacterTextSplitter().split_documents([Document(page_content=text)])
        result = sum_chain.invoke(docs)
        return wrap_triple_slash_comments(result)
        return ""
    except Exception as e:
        logger.error(f"Failed to summarize text:\n{text}")
        logger.error(e)
        return ""


def generate_function_summary(function: Node) -> str:
    func_body = function.text.decode("utf8")
    if len(func_body.splitlines()) <= 1:
        logger.info(f"Function/property body is too short, skipping:\n{func_body}")
        return ""

    try:
        return wrap_triple_slash_comments(generate_function_documentation(func_body))
    except Exception as e:
        logger.error(f"Failed to generate documentation for function:\n{func_body}")
        logger.error(e)
        return chain_summarize(func_body)


def generate_combined_summary(summaries: List[str]) -> str:
    combined = (
            "/// Documentation of all methods and properties in the current type, should not be included in final documentation:\n///\n"
            + "\n///\n".join(summaries)
    )
    return chain_summarize(combined)


def generate_class_body_summary(class_body: str) -> str:
    return chain_summarize(class_body)


if __name__ == "__main__":
    # Example usage
    swift_function = """
    private let titleLabel: UILabel = {
        let label = UILabel()
        label.text = "热点排行榜".home.localized
        label.font = .aic_semiboldFont(withSize: 15)
        label.textColor = .baseTheme.current.cellTitleColor
        return label
    }()
    """

    # documentation_comment = chain_summarize(swift_function)
    # print(documentation_comment)
    documentation_comment = generate_function_documentation(swift_function)
    print(documentation_comment)
