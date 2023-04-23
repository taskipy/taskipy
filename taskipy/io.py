import abc

class AbstractIO(abc.ABC):
    @abc.abstractmethod
    def write_line(self, line: str) -> None:
        pass


class AppIO(AbstractIO):
    def write_line(self, line: str) -> None:
        print(line)

