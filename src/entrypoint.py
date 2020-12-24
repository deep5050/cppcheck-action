"""Drive the parameter collection and execution for cppcheck."""
import operator
import os
import subprocess

GITHUB_EVENT_NAME = os.environ["GITHUB_EVENT_NAME"]

# Set repository
CURRENT_REPOSITORY = os.environ["GITHUB_REPOSITORY"]
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

# Set branches
GITHUB_REF = os.environ["GITHUB_REF"]
GITHUB_HEAD_REF = os.environ["GITHUB_HEAD_REF"]
GITHUB_BASE_REF = os.environ["GITHUB_BASE_REF"]
CURRENT_BRANCH = GITHUB_HEAD_REF or GITHUB_REF.rsplit("/", 1)[-1]
INPUT_TARGET_BRANCH = os.getenv("INPUT_TARGET_BRANCH", CURRENT_BRANCH)
INPUT_PULL_REQUEST_BRANCH = os.getenv("INPUT_PULL_REQUEST_BRANCH", GITHUB_BASE_REF)
BRANCH = (
    INPUT_PULL_REQUEST_BRANCH
    if GITHUB_EVENT_NAME == "pull_request"
    else INPUT_TARGET_BRANCH
)

GITHUB_ACTOR = os.environ["GITHUB_ACTOR"]
GITHUB_REPOSITORY_OWNER = os.environ["GITHUB_REPOSITORY_OWNER"]
INPUT_GITHUB_TOKEN = os.environ["INPUT_GITHUB_TOKEN"]

# domain specific vocabulary for switches:
DISABLED = 'disable'
ENABLED = 'enable'
CHECK_EVERYTHING = 'all'

SCOPE_SEP = ","
KNOWN_SCOPES = (
    CHECK_EVERYTHING,
    "information",
    "missingInclude",
    "performance",
    "portability",
    "style",
    "unusedFunction",
    "warning",
)
# domain specific language between environment and cppcheck parameters:
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
    """Naive split of text as comma separated scope values yielding as-input case strings."""
    if SCOPE_SEP in text:
        for scope in text.split(SCOPE_SEP):
            yield scope.strip()
    else:
        yield text.strip()


def is_valid(scope):
    """Return scope if valid else empty string."""
    return scope if scope in KNOWN_SCOPES else ""


def parse_scopes(text):
    """Return the parsed scopes."""
    scopes = set(t for t in split_csv(text) if is_valid(t))
    if CHECK_EVERYTHING in scopes:
        scopes = [CHECK_EVERYTHING]
    else:
        scopes = sorted(scopes)
    return scopes


def command():
    """Prepare the command vector and set the path to the report file"""
    vector = [
        "cppcheck",
        f"--enable={SCOPE_SEP.join(parse_scopes(DSL[ENABLE_CHECKS]))}",
    ]

    for dim in ACTIONS:
        predicate, ref, template = ACTIONS[dim]
        payload = DSL[dim]
        if predicate(payload, ref):
            vector.append(template if dim in CONSTANT_DIMENSIONS else template.format(payload))

    return vector


def run(vector, where=".", show_version=None, show_help=None):
    """Execute the command in a sub process."""
    show_version = show_version is None
    show_help = show_help is None
    vector.append(f"--output-file={DSL[OUTPUT_FILE]}")
    vector.append(f"{where}")
    print(f"given command {' '.join(vector)}")

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
