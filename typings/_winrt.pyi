import typing

@typing.type_check_only
class IAsyncOperation(_winrt._winrt_base):
    """
    base class for wrapped WinRT object instances.
    """

    @staticmethod
    def completed():
        """ """
        ...
    @staticmethod
    def error_code():
        """ """
        ...
    @staticmethod
    def id():
        """ """
        ...
    def __await__(self):
        """
        Return an iterator to be used in await expression.
        """
        ...
    def cancel(self, *args, **kwargs):
        """ """
        ...
    def close(self, *args, **kwargs):
        """ """
        ...
    def get_results(self, *args, **kwargs):
        """ """
        ...
    ...
