import json
import re

import requests

from src.module.constants import GEMINI_API_KEY, GEMINI_MODEL


class ResponseGenerator:
    """Generate LLM responses using retrieved context"""

    def __init__(self, prompt_template, llm_model=GEMINI_MODEL):
        """
        Initialize the response generator.

        :param prompt_template: Prompt template
        :param llm_model: Gemini model name to use for generation.
        """

        self.prompt_template = prompt_template
        self.llm_model = llm_model

    @staticmethod
    def aggregate_context(context_nodes):
        """Aggregate retrieved context nodes into a formatted string."""
        context_list = []
        for i, c in enumerate(context_nodes[::-1], start=1):
            context = f"""
[Start of Excerpt {i}]
Document Name: {c.metadata["file_name"]}
Header Path: {c.metadata["header_path"]}
Page Number(s): {c.metadata["page_span"]}
Excerpts: {c.text}
[End of Excerpt {i}]
            """
            context_list.append(context)

        return "\n\n".join(context_list)

    def build_prompt(self, question, agg_context):
        """Construct the final prompt by replacing placeholders in the prompt template with the given question
        and aggregated context"""

        prompt = self.prompt_template

        if question:
            prompt = prompt.replace("<<question>>", question)

        if agg_context:
            prompt = prompt.replace("<<excerpts>>", agg_context)

        return prompt

    def generate_response(self, question, context, citation=True):
        """Generate a response from the LLM given a question and context."""

        agg_context = self.aggregate_context(context)
        prompt = self.build_prompt(question, agg_context)
        response = self.call_gemini(prompt)

        if citation:
            return self._process_citation(response)
        else:
            return response

    def _process_citation(self, text):
        """Format inline citations in the response."""

        refs = {}
        ordered = []

        def repl(match):
            citation = " ".join(match.group(1).split())
            if citation not in refs:
                refs[citation] = len(refs) + 1
                ordered.append(citation)
            return f"[{refs[citation]}]"

        text = re.sub(r"\[Citation:\s*(.*?)\]", repl, text)

        if not ordered:
            return text

        references = "\n\n".join(
            f"[{i}] {citation}" for i, citation in enumerate(ordered, 1)
        )
        return f"{text}\n\n##### References\n{references}"

    def call_gemini(self, prompt):
        """Call the Gemini API to generate a response from a prompt."""

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.llm_model}:generateContent"
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": GEMINI_API_KEY,
            }
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
            }

            resp = requests.post(
                url,
                headers=headers,
                data=json.dumps(payload),
                # timeout=self.timeout,
            )

            if resp.status_code != 200:
                raise Exception(f"Gemini HTTP Error {resp.status_code}: {resp.text}")

            data = resp.json()["candidates"][0]["content"]["parts"][0]["text"]

        except Exception as e:
            raise Exception(f"Error in calling Gemini API: {e}") from e

        return data
