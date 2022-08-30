"""Drive the parameter collection and execution for cppcheck."""
import operator
import os
import subprocess
import sys

ENCODING = "utf-8"
SCA_EXECUTOR = "cppcheck"
DISPLAY_SCA_VERSION = True
DISPLAY_SCA_HELP = True
SOURCE_ROOT = "."

# The following environment reads will fail execution if variables not set:
GITHUB_EVENT_NAME = os.environ["GITHUB_EVENT_NAME"]
# Set repository
CURRENT_REPOSITORY = os.environ["GITHUB_REPOSITORY"]
# Set branches
GITHUB_REF = os.environ["GITHUB_REF"]
GITHUB_HEAD_REF = os.environ["GITHUB_HEAD_REF"]
GITHUB_BASE_REF = os.environ["GITHUB_BASE_REF"]
# Owners and tokens
GITHUB_ACTOR = os.environ["GITHUB_ACTOR"]
GITHUB_REPOSITORY_OWNER = os.environ["GITHUB_REPOSITORY_OWNER"]
INPUT_GITHUB_TOKEN = os.environ["INPUT_GITHUB_TOKEN"]

# Derive from environment with defaults:
# TODO: How about PRs from forks?
INPUT_TARGET_REPOSITORY = os.getenv("INPUT_TARGET_REPOSITORY", CURRENT_REPOSITORY)
INPUT_PULL_REQUEST_REPOSITORY = os.getenv(
    "INPUT_PULL_REQUEST_REPOSITORY", INPUT_TARGET_REPOSITORY
)
REPOSITORY = (
    INPUT_PULL_REQUEST_REPOSITORY
    if GITHUB_EVENT_NAME == "pull_request"
    else INPUT_TARGET_REPOSITORY
)

CURRENT_BRANCH = GITHUB_HEAD_REF or GITHUB_REF.rsplit("/", 1)[-1]
INPUT_TARGET_BRANCH = os.getenv("INPUT_TARGET_BRANCH", CURRENT_BRANCH)
INPUT_PULL_REQUEST_BRANCH = os.getenv("INPUT_PULL_REQUEST_BRANCH", GITHUB_BASE_REF)
BRANCH = (
    INPUT_PULL_REQUEST_BRANCH
    if GITHUB_EVENT_NAME == "pull_request"
    else INPUT_TARGET_BRANCH
)


# Define cppcheck specific vocabulary for switches:
DISABLED = "disable"
ENABLED = "enable"
CHECK_EVERYTHING = "all"

CHECKS_SEP = ","
KNOWN_CHECKS = (
    CHECK_EVERYTHING,
    "information",
    "missingInclude",
    "performance",
    "portability",
    "style",
    "unusedFunction",
    "warning",
)
OTHERS_SEP = " -"

# Domain specific mapping between environment and cppcheck parameters:
CHECK_LIBRARY = "INPUT_CHECK_LIBRARY"
SKIP_PREPROCESSOR = "INPUT_SKIP_PREPROCESSOR"
ENABLE_CHECKS = "INPUT_ENABLE"
EXCLUDE_CHECK = "INPUT_EXCLUDE_CHECK"
ENABLE_INCONCLUSIVE = "INPUT_INCONCLUSIVE"
FORCE = "INPUT_FORCE"
INLINE_SUPPRESSION = "INPUT_INLINE_SUPPRESSION"
ENFORCE_LANGUAGE = "INPUT_FORCE_LANGUAGE"
MAX_CTU_DEPTH = "INPUT_MAX_CTU_DEPTH"
OUTPUT_FILE = "INPUT_OUTPUT_FILE"
PLATFORM_TYPE = "INPUT_PLATFORM"
STD = "INPUT_STD"
OTHER_OPTIONS = "INPUT_OTHER_OPTIONS"


# Main interface map for cppcheck instrumentation and outputs:
DSL = {
    CHECK_LIBRARY: os.getenv(CHECK_LIBRARY, DISABLED),
    SKIP_PREPROCESSOR: os.getenv(SKIP_PREPROCESSOR, DISABLED),
    ENABLE_CHECKS: os.getenv(ENABLE_CHECKS, CHECK_EVERYTHING),
    EXCLUDE_CHECK: os.getenv(EXCLUDE_CHECK, DISABLED),
    ENABLE_INCONCLUSIVE: os.getenv(ENABLE_INCONCLUSIVE, ENABLED),
    FORCE: os.getenv(FORCE, DISABLED),
    INLINE_SUPPRESSION: os.getenv(INLINE_SUPPRESSION, DISABLED),
    ENFORCE_LANGUAGE: os.getenv(ENFORCE_LANGUAGE, DISABLED),
    MAX_CTU_DEPTH: os.getenv(MAX_CTU_DEPTH, DISABLED),
    OUTPUT_FILE: os.getenv(OUTPUT_FILE, None),
    PLATFORM_TYPE: os.getenv(PLATFORM_TYPE, DISABLED),
    STD: os.getenv(STD, DISABLED),
    OTHER_OPTIONS: os.getenv(OTHER_OPTIONS, DISABLED),
}


def split_other_options(text):
    """Naive split of other options as space-dash separated entries yielding single options."""
    if OTHERS_SEP in text:
        is_first = True
        for entry in text.split(OTHERS_SEP):
            yield entry.strip() if is_first else f'-{entry.strip()}'  # other entries lose dash
            is_first = False
    else:
        yield text.strip()



# Prepare actions to be taken using the above environment interface map:
CONSTANT_ACTIONS = 4
ACTIONS = {  # group by arity of actions to simplify processing below
    # constant actions:
    CHECK_LIBRARY: (operator.eq, ENABLED, "--check-library", None),
    SKIP_PREPROCESSOR: (operator.eq, ENABLED, "-E", None),
    INLINE_SUPPRESSION: (operator.eq, ENABLED, "--inline-suppr", None),
    ENABLE_INCONCLUSIVE: (operator.ne, DISABLED, "--inconclusive", None),
    FORCE: (operator.ne, DISABLED, "--force", None),
    # unary actions:
    EXCLUDE_CHECK: (operator.ne, DISABLED, "-i{}", None),  # Newer versions of cppcheck (>1.9) do not accept a space here
    ENFORCE_LANGUAGE: (operator.ne, DISABLED, "--language={}", None),
    MAX_CTU_DEPTH: (operator.ne, DISABLED, "--max-ctu-depth={}", None),
    PLATFORM_TYPE: (operator.ne, DISABLED, "--platform={}", None),
    STD: (operator.ne, DISABLED, "--std={}", None),
    OTHER_OPTIONS: (operator.ne, DISABLED, "{}", split_other_options),
}
CONSTANT_DIMENSIONS = tuple(ACTIONS.keys())[:CONSTANT_ACTIONS]

CPPCHECK_NO_PATHS_OPENED_INDICATOR = (
    "cppcheck: error: could not find or open any of the paths given."
)


def split_csv(text):
    """Naive split of text as comma separated check aspects yielding as-input case strings."""
    if CHECKS_SEP in text:
        for check in text.split(CHECKS_SEP):
            yield check.strip()
    else:
        yield text.strip()


def is_valid(check):
    """Return scope if valid else empty string."""
    return check if check in KNOWN_CHECKS else ""


def parse_checks(dsl):
    """Return the parsed checks."""
    checks = set(t for t in split_csv(dsl[ENABLE_CHECKS]) if is_valid(t))
    if CHECK_EVERYTHING in checks:
        checks = [CHECK_EVERYTHING]
    else:
        checks = sorted(checks)
    return checks


def command(dsl=None, actions=None, checks_sep=CHECKS_SEP, constant_dimensions=CONSTANT_DIMENSIONS):
    """Prepare the command vector and set the path to the report file, if set"""
    dsl = DSL if dsl is None else dsl
    actions = ACTIONS if actions is None else actions

    vector = [
        SCA_EXECUTOR,
        f"--enable={checks_sep.join(parse_checks(dsl))}",
    ]

    for dim in actions:
        predicate, ref, template, processing = actions[dim]
        payload = dsl[dim]
        if predicate(payload, ref):
            if not processing:
                vector.append(template if dim in constant_dimensions else template.format(payload))
            else:  # implicit dim not in constant_dimension
                for chunk in processing(payload):
                    vector.append(template.format(chunk))


    return vector


def display_sca_executor_version():
    """Capture current behavior and document tool version."""
    return subprocess.run((SCA_EXECUTOR, "--version"), capture_output=True, check=False)


def display_sca_executor_help():
    """Capture current behavior and document tool version."""
    return subprocess.run((SCA_EXECUTOR, "--help"), capture_output=True, check=False)


def run(vector, where=SOURCE_ROOT, show_version=False, show_help=False):
    """Execute the command in a sub process."""
    if show_version:
        print("retrieving cppcheck version")
        completed = display_sca_executor_version()
        print(" ", completed.stdout.decode(ENCODING, errors="ignore").strip())

    if show_help:
        print("retrieving cppcheck help")
        completed = display_sca_executor_help()
        for line in completed.stdout.decode(ENCODING, errors="ignore").split("\n"):
            print(" ", line)

    if DSL[OUTPUT_FILE] is not None:
      vector.append(f"--output-file={DSL[OUTPUT_FILE]}")

    vector.append(f"{where}")
    print("executing static code analysis")
    print(f"  effective command: {' '.join(vector)}")
    print("output from analysis")
    try:
        completed = subprocess.run(vector, capture_output=True, check=True)
    except FileNotFoundError as err:
        print("command not found?", err)
        return 1
    except subprocess.CalledProcessError as err:
        print("source root not found?", err)
        print("details:")
        print(err.stdout.decode(ENCODING, errors="ignore"))
        return 1

    if not completed.returncode:  # currently cppcheck is happy to find no source file
        print("errors from execution")

    lines = completed.stdout.decode(ENCODING, errors="ignore").split("\n")

    for line in lines:
        print(" ", line)

    if lines[0].strip() == CPPCHECK_NO_PATHS_OPENED_INDICATOR:
        print("no source files found during execution?")

    if completed.stderr:
        print("captured output on standard error:")
        for line in completed.stderr.decode(ENCODING, errors="ignore").split("\n"):
            print(" ", line)
    return None


def main():
    """Drive the parameter extraction and execution of cppcheck."""
    if GITHUB_ACTOR != GITHUB_REPOSITORY_OWNER:
        return 2

    return run(command(), SOURCE_ROOT, DISPLAY_SCA_VERSION, DISPLAY_SCA_HELP)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
