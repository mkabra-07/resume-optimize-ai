from abc import ABC, abstractmethod
from schemas.resume import ResumeContent

class BaseResumeParser(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> ResumeContent:
        pass
