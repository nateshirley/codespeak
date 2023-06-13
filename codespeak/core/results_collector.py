# run.py
import importlib
from unittest.mock import patch
import inspect
import time
from typing import Any, Callable, List
from pydantic import BaseModel
from codespeak.helpers.set_attr_for_qualname import set_attr_for_qualname
from codespeak.core.executor import (
    execute_from_typed_attributes,
)
import pytest


class ResultsCollector:
    def __init__(self):
        self.reports = []
        self.collected = 0
        self.exitcode = 0
        self.passed = 0
        self.failed = 0
        self.xfailed = 0
        self.skipped = 0
        self.total_duration = 0

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        report = outcome.get_result()
        if report.when == "call":
            self.reports.append(report)

    def pytest_collection_modifyitems(self, items):
        self.collected = len(items)

    def pytest_terminal_summary(self, terminalreporter, exitstatus):
        self.exitcode = exitstatus
        self.passed = len(terminalreporter.stats.get("passed", []))
        self.failed = len(terminalreporter.stats.get("failed", []))
        self.xfailed = len(terminalreporter.stats.get("xfailed", []))
        self.skipped = len(terminalreporter.stats.get("skipped", []))
        self.total_duration = time.time() - terminalreporter._sessionstarttime


class CrashReport(BaseModel):
    path: str
    lineno: int
    message: str


class LogicExecutor:
    def __init__(self, logic_modulepath: str, func_name: str):
        self.logic_modulepath = logic_modulepath
        self.func_name = func_name

    def __call__(self, *args, **kwargs):
        _args: List[Any] = list(args) or []
        _kwargs = kwargs or {}

        # even if i hardcode a return value here, it still regenerates the damn code
        # return 4
        # it's only using the logic executor in the nested testing
        # do u think
        print("calling logic EXECUTOR")
        # so this is only getting called once but the function is called twice
        # so it

        return execute_from_typed_attributes(
            logic_modulepath=self.logic_modulepath,
            func_name=self.func_name,
            args=_args,
            kwargs=_kwargs,
        )


def qualname_to_name(qualname: str) -> str:
    if "." in qualname:
        return qualname.rsplit(".", 1)[-1]
    else:
        return qualname


def do_nothing(*args, **kwargs):
    print("doing nothing")
    return 5


# could i just get rid of the swapper by setting the pass conditions?
# the swapper sucks
class FunctionSwapper:
    def __init__(
        self, declaration_qualname: str, declaration_module: str, logic_modulepath: str
    ):
        print(
            "swapping declaration at module: ",
            declaration_module,
            " qualname:",
            declaration_qualname,
            "with logic at modulepath:",
            logic_modulepath,
        )
        self.declaration_qualname = declaration_qualname
        self.declaration_module = declaration_module
        self.logic_modulepath = logic_modulepath

    def pytest_sessionstart(self, session):
        # This method is called before pytest starts running tests
        # Here we can perform the patching
        print("SESSION STARTED")
        try:
            module_obj = importlib.import_module(self.declaration_module)
            logic_executor = LogicExecutor(
                logic_modulepath=self.logic_modulepath,
                func_name=qualname_to_name(self.declaration_qualname),
            )
            _dir = dir(module_obj)
            print("dir attr:", _dir)
            setattr(module_obj, self.declaration_qualname, do_nothing)

            # set_attr_for_qualname(module_obj, self.declaration_qualname, do_nothing)
            print("swapped codespeak func for logic")

        except Exception as e:
            raise Exception("couldn't swap codespeak func for logic in tests, e:", e)


class TestRunner(BaseModel):
    reports: List[pytest.TestReport]
    crash_reports: List[CrashReport]
    collected: int
    exitcode: int
    passed: int
    failed: int
    xfailed: int
    skipped: int
    total_duration: float

    class Config:
        arbitrary_types_allowed = True

    @staticmethod
    def run_test_func(
        test_file: str,
        test_func_qualname: str,
        codespeak_declaration_module: str,
        codespeak_declaration_qualname: str,
        logic_modulepath: str,
    ):
        collector = ResultsCollector()
        # swapper = FunctionSwapper(
        #     declaration_qualname=codespeak_declaration_qualname,
        #     declaration_module=codespeak_declaration_module,
        #     logic_modulepath=logic_modulepath,
        # )
        # print(
        #     "running test file bleh:",
        #     test_file,
        #     " with declaration module:",
        #     codespeak_declaration_module,
        # )
        print(
            "swapping declaration at module: ",
            codespeak_declaration_module,
            " qualname:",
            codespeak_declaration_qualname,
            "with logic at modulepath:",
            logic_modulepath,
        )
        # this is still not using the code that was just generated
        # We'll mock the function in the declaration module with our logic executor.
        logic_executor = LogicExecutor(
            logic_modulepath=logic_modulepath,
            func_name=qualname_to_name(codespeak_declaration_qualname),
        )
        with patch(
            f"{codespeak_declaration_module}.{codespeak_declaration_qualname}",
            new=logic_executor,
        ):
            print("testing with PYTEST.MAIn")
            # okay so this by itself is getting called twic.e
            # that kind of nulls anythin
            pytest.main(
                ["-s", test_file, "-k", test_func_qualname],
                plugins=[],  # [collector],  # swapper,
            )
        # pytest.main(
        #     ["-s", test_file, "-k", test_func_qualname],
        #     plugins=[swapper, collector],  # swapper,
        # )
        crash_reports = []
        for report in collector.reports:
            try:
                cr = vars(report.longrepr.reprcrash)
                crash_reports.append(CrashReport.parse_obj(cr))
                if len(crash_reports) > 1:
                    raise Exception(
                        "unexpected double crash report for single function"
                    )
            except AttributeError:
                pass
        return TestRunner(
            reports=collector.reports,
            crash_reports=crash_reports,
            collected=collector.collected,
            exitcode=collector.exitcode,
            passed=collector.passed,
            failed=collector.failed,
            xfailed=collector.xfailed,
            skipped=collector.skipped,
            total_duration=collector.total_duration,
        )


"""
original print statements (not using)

for crash in test_result.crash_reports:
    print("crash:", crash)
print("exit code:", test_result.exitcode)
print(
    "passed:",
    test_result.passed,
    "failed:",
    test_result.failed,
    "xfailed:",
    test_result.xfailed,
    "skipped:",
    test_result.skipped,
)
print("total duration:", test_result.total_duration)
"""

# this is how you would get the error messages up the stack trace. not using for now. already have the final error message.
"""
for report in test_result.reports:
    print("id:", report.nodeid, "outcome:", report.outcome)
    # print(vars(report))
    try:
        entries = report.longrepr.reprtraceback.reprentries
        for entry in entries:
            # print("entry:", vars(entry).keys())
            # line = entry.line
            # print("line:", line)
            # print("entry:", vars(entry))
            # print(entry.reprfileloc)
            print(hasattr(entry, "reprfileloc"))
            re = getattr(entry, "reprfileloc")
            print("re:", vars(re))
    except Exception as e:
        pass
    # print(report.longrepr.reprtraceback.reprentries)
# print("report vals:", test_result.reports[0].dict())
"""
