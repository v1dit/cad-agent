from abc import ABC, abstractmethod

from app.models.schema import DesignNode


class CADAdapter(ABC):
    name: str

    @abstractmethod
    def generate(self, spec: DesignNode) -> str:
        raise NotImplementedError

    @abstractmethod
    def execute(self, code: str, out_path: str | None = None) -> dict[str, str]:
        raise NotImplementedError
