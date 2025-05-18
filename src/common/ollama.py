from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate


def get_model_response(model_name: str, template: str, verbose: bool = False) -> str:
    model: OllamaLLM = OllamaLLM(model=model_name)
    prompt: ChatPromptTemplate = ChatPromptTemplate.from_template(template)
    chain = prompt | model
    result = chain.invoke({})

    # Log result
    if verbose:
        print("=== Generated Meal Plan ===\n")
        print(result)

    return result