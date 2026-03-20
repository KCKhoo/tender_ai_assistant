import asyncio
import os
import pickle
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from llama_cloud import AsyncLlamaCloud

load_dotenv()


class PDFLlamaParser:
    def __init__(
        self,
        llama_parse_tier: str,
        llama_parse_version: str,
        custom_prompt: str | None = None,
        concurrency: int = 10,
    ):
        """
        Initialize the PDFLlamaParser.

        :param llama_parse_tier: Parsing tier for LlamaParse
        :param llama_parse_version: Version of parsing model
        :param custom_prompt: Custom prompt to guide parsing behavior.
        :param concurrency: Maximum number of concurrent parsing tasks.
        """

        self.client = AsyncLlamaCloud(api_key=os.getenv("LLAMA_CLOUD_API_KEY"))
        self.llama_parse_tier = llama_parse_tier
        self.llama_parse_version = llama_parse_version
        self.custom_prompt = custom_prompt
        self.semaphore = asyncio.Semaphore(concurrency)

    async def parse_single_pdf(self, file_path: Path) -> Any:
        """
        Call LlamaParse API to parse PDF

        :param file_path: Absolute path to the PDF file
        """

        async with self.semaphore:
            print(f"Parsing: {file_path.name}")

            file_obj = await self.client.files.create(
                file=str(file_path),
                purpose="parse",
            )

            parse_params = {
                "tier": self.llama_parse_tier,
                "version": self.llama_parse_version,
                "file_id": file_obj.id,
                "expand": ["markdown"],
                "crop_box": {  # To remove header and footer
                    "top": 0.075,
                    "bottom": 0.075,
                },
                "output_options": {
                    "markdown": {
                        "tables": {
                            "merge_continued_tables": True,
                            "compact_markdown_tables": True,
                            "output_tables_as_markdown": True,
                        }
                    },
                    "extract_printed_page_number": False,
                },
            }

            if self.custom_prompt:
                parse_params["agentic_options"] = {"custom_prompt": self.custom_prompt}

            result = await self.client.parsing.parse(**parse_params)

            return result

    def save_parsed_result(self, result: Any, output_path: str) -> None:
        """
        Save the parsed result as a pickle file

        :param result: Data to be saved as a pickle file
        :output_path: File path where the pickle file will be saved
        """

        with open(output_path, "wb") as f:
            pickle.dump(result, f)

    async def parse_and_save(self, file_path: Path, output_dir: Path) -> None:
        """
        Parse a single PDF file and save the result as a pickle file.

        :param file_path: Absolute path to the PDF file
        :output_path: Directory where the pickle file will be saved
        """

        result = await self.parse_single_pdf(file_path)
        output_path = os.path.join(output_dir, f"{file_path.stem}.pkl")
        self.save_parsed_result(result, output_path)

    async def parse_all_pdfs(
        self, raw_doc_dir: str, parsed_doc_dir: str, skip_dirs: str | None = None
    ) -> None:
        """
        Recursively parse all PDF files in a given directory

        :param raw_doc_dir: Directory containing source PDF files to be parsed
        :param parsed_doc_dir: Directory where parsed files will be saved.
        :param skip_dirs: Optional directory to exclude from parsing
        """

        raw_doc_dir = Path(raw_doc_dir)
        parsed_doc_dir = Path(parsed_doc_dir)
        if skip_dirs is None:
            skip_dirs = []

        pdf_files = list(raw_doc_dir.rglob("*.pdf"))

        tasks = []
        for pdf_file in pdf_files:
            if any(skip in pdf_file.parts for skip in skip_dirs):
                print(f"Skipping: {pdf_file.name}")
                continue

            relative_path = pdf_file.relative_to(raw_doc_dir).parent
            target_parsed_doc_dir = parsed_doc_dir / relative_path
            target_parsed_doc_dir.mkdir(exist_ok=True, parents=True)
            tasks.append(self.parse_and_save(pdf_file, target_parsed_doc_dir))

        if tasks:
            print(f"Processing {len(tasks)} files...")
            await asyncio.gather(*tasks)
        else:
            print("No valid PDF files found.")
