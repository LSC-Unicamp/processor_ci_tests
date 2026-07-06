"""Compatibility imports for the former root-level core package."""


def __getattr__(name: str):
    if name == 'ProcessorCITest':
        from riscv_test_runner.core.runner import ProcessorCITest

        return ProcessorCITest
    raise AttributeError(name)


__all__ = ['ProcessorCITest']
