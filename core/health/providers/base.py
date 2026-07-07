from abc import ABC
from abc import abstractmethod


class HealthProvider(ABC):
    @abstractmethod
    def collect(self, records):
        raise NotImplementedError
