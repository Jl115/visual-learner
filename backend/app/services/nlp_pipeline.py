from typing import List


class NLPPipeline:
    def tokenize(self, text: str) -> List[str]:
        return text.split()

    def extract_keywords(self, text: str) -> List[str]:
        # Placeholder – real implementation uses NLP model
        return text.split()[:10]
