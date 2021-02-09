import abc


class PersistenceTextIO(abc.ABC):
    """
    Interface that is able to read text from a source, and save it back.
    """
    @abc.abstractmethod
    def read_text(self):
        pass

    @abc.abstractmethod
    def save_text(self, text: str):
        pass
