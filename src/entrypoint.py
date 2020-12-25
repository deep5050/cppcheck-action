"""Drive the parameter collection and execution for cppcheck."""
import operator
import os
import subprocess

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
INPUT_PULL_REQUEST_REPOSITORY = (
        os.getenv("INPUT_PULL_REQUEST_REPOSITORY", INPUT_TARGET_REPOSITORY)
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
DISABLED = 'disable'
ENABLED = 'enable'
CHECK_EVERYTHING = 'all'

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
# Domain specific mapping between environment and cppcheck parameters:
CHECK_LIBRARY = "INPUT_CHECK_LIBRARY"
SKIP_PREPROCESSOR = "INPUT_SKIP_PREPROCESSOR"
ENABLE_CHECKS = "INPUT_ENABLE"
EXCLUDE_CHECK = "INPUT_EXCLUDE_CHECK"
ENABLE_INCONCLUSIVE = "INPUT_INCONCLUSIVE"
INLINE_SUPPRESSION = "INPUT_INLINE_SUPPRESSION"
ENFORCE_LANGUAGE = "INPUT_FORCE_LANGUAGE"
MAX_CTU_DEPTH = "INPUT_MAX_CTU_DEPTH"
OUTPUT_FILE = "INPUT_OUTPUT_FILE"
PLATFORM_TYPE = "INPUT_PLATFORM"

# Main interface map for cppcheck instrumentation and outputs:
DSL = {
    CHECK_LIBRARY: os.getenv(CHECK_LIBRARY, DISABLED),
    SKIP_PREPROCESSOR: os.getenv(SKIP_PREPROCESSOR, DISABLED),
    ENABLE_CHECKS: os.getenv(ENABLE_CHECKS, CHECK_EVERYTHING),
    EXCLUDE_CHECK: os.getenv(EXCLUDE_CHECK, DISABLED),
    ENABLE_INCONCLUSIVE: os.getenv(ENABLE_INCONCLUSIVE, ENABLED),
    INLINE_SUPPRESSION: os.getenv(INLINE_SUPPRESSION, DISABLED),
    ENFORCE_LANGUAGE: os.getenv(ENFORCE_LANGUAGE, DISABLED),
    MAX_CTU_DEPTH: os.getenv(MAX_CTU_DEPTH, DISABLED),
    OUTPUT_FILE: os.getenv(OUTPUT_FILE, "cppcheck_report.txt"),
    PLATFORM_TYPE: os.getenv(PLATFORM_TYPE, DISABLED),
}

# Prepare actions to be taken using the above environment interface map:
CONSTANT_ACTIONS = 4
ACTIONS = {  # group by arity of actions to simplify processing below
    # constant actions:
    CHECK_LIBRARY: (operator.eq, ENABLED, "--check-library"),
    SKIP_PREPROCESSOR: (operator.eq, ENABLED, "-E"),
    INLINE_SUPPRESSION: (operator.eq, ENABLED, "--inline-suppr"),
    ENABLE_INCONCLUSIVE: (operator.ne, DISABLED, "--inconclusive"),
    # unary actions:
    EXCLUDE_CHECK: (operator.ne, DISABLED, "-i {{}}"),
    ENFORCE_LANGUAGE: (operator.ne, DISABLED, "--language={}"),
    MAX_CTU_DEPTH: (operator.ne, DISABLED, "--max-ctu-depth={}"),
    PLATFORM_TYPE: (operator.ne, DISABLED, "--platform={}"),
}
CONSTANT_DIMENSIONS = tuple(ACTIONS.keys())[:CONSTANT_ACTIONS]


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
    """Prepare the command vector and set the path to the report file"""
    dsl = DSL if dsl is None else dsl
    actions = ACTIONS if actions is None else actions

    vector = [
        "cppcheck",
        f"--enable={checks_sep.join(parse_checks(dsl))}",
    ]

    for dim in actions:
        predicate, ref, template = actions[dim]
        payload = dsl[dim]
        if predicate(payload, ref):
            vector.append(template if dim in constant_dimensions else template.format(payload))

    return vector


def run(vector, where=".", show_version=None, show_help=None):
    """Execute the command in a sub process."""
    show_version = show_version is None
    show_help = show_help is None
    vector.append(f"--output-file={DSL[OUTPUT_FILE]}")
    vector.append(f"{where}")
    print("--------------------------------------")
    print(f"given command: {' '.join(vector)}")

    if show_version:
        print("checking version")
        subprocess.call("cppcheck --version", shell=True)

    if show_help:
        subprocess.call("cppcheck --help", shell=True)

    subprocess.call(vector, shell=True)


def main():
    """Drive the parameter extraction and execution of cppcheck."""
    if all((GITHUB_EVENT_NAME == "pull_request", GITHUB_ACTOR != GITHUB_REPOSITORY_OWNER)):
        return

    run(command())


if __name__ == "__main__":
    main()  # pragma: no cover
