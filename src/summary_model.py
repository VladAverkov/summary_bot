from dataclasses import dataclass
from typing import List, Optional, Union

from transformers import AutoTokenizer, T5ForConditionalGeneration
import torch


@dataclass
class SummaryModel:
    model_name: str = 't5-small'
    max_input_length: int = 500  # Maximum input length in characters for each block
    device: Union[torch.device, str] = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    tokenizer: Optional[AutoTokenizer] = None
    model: Optional[T5ForConditionalGeneration] = None

    def __post_init__(self):
        if self.tokenizer is None or self.model is None:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = T5ForConditionalGeneration.from_pretrained(self.model_name).to(self.device)

    def _split_text_into_blocks(self, text: str) -> List[str]:
        """
        Splits the text into blocks, each no longer than max_input_length characters.
        """
        blocks = [text[i:i + self.max_input_length] for i in range(0, len(text), self.max_input_length)]
        return blocks

    def _generate_summary(self, text_block: str, max_length: int = 150) -> str:
        """
        Generates a summary for a given text block.
        """
        input_ids = self.tokenizer.encode(text_block, add_special_tokens=True, truncation=True, max_length=self.max_input_length)
        input_ids = torch.tensor([input_ids]).to(self.device)

        with torch.inference_mode():
            output_ids = self.model.generate(
                input_ids=input_ids,
                max_length=max_length,
                num_beams=4,
                no_repeat_ngram_size=4,
                early_stopping=True
            )[0]
        return self.tokenizer.decode(output_ids, skip_special_tokens=True)

    def summarize(self, text: str, max_length: int = 150) -> str:
        """
        Summarizes the text by generating its concise version.
        """
        blocks = self._split_text_into_blocks(text)

        summaries = []
        for block in blocks:
            summary = self._generate_summary(block, max_length)
            summaries.append(summary)

        final_summary = " ".join(summaries)
        return final_summary
