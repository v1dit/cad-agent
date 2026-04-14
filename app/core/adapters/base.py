from abc import ABC, abstractmethod

from app.models.schema import DesignNode


class CADAdapter(ABC):
    @abstractmethod
    def generate(self, spec: DesignNode) -> str:
        raise NotImplementedError
