# run.py
import importlib
import inspect
import time
from typing import Callable, List
from pydantic import BaseModel
from codespeak.helpers.set_attr_for_qualname import set_attr_for_qualname
import pytest
from codespeak.core.executor import execute_from_attributes


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
        return execute_from_attributes(
            logic_modulepath=self.logic_modulepath,
            func_name=self.func_name,
            *args,
            **kwargs,
        )


def qualname_to_name(qualname: str) -> str:
    if "." in qualname:
        return qualname.rsplit(".", 1)[-1]
    else:
        return qualname


class FunctionSwapper:
    def __init__(
        self, func_to_swap_qualname: str, declaration_module: str, logic_modulepath: str
    ):
        self.func_to_swap_qualname = func_to_swap_qualname
        self.declaration_module = declaration_module
        self.logic_modulepath = logic_modulepath

    def pytest_sessionstart(self, session):
        # This method is called before pytest starts running tests
        # Here we can perform the patching
        try:
            module_obj = importlib.import_module(self.declaration_module)
            logic_executor = LogicExecutor(
                logic_modulepath=self.logic_modulepath,
                func_name=qualname_to_name(self.func_to_swap_qualname),
            )
            set_attr_for_qualname(
                module_obj, self.func_to_swap_qualname, logic_executor
            )

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
        swapper = FunctionSwapper(
            func_to_swap_qualname=codespeak_declaration_qualname,
            declaration_module=codespeak_declaration_module,
            logic_modulepath=logic_modulepath,
        )
        pytest.main([test_file, "-k", test_func_qualname], plugins=[swapper, collector])
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
