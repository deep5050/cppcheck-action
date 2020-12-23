"""Drive the parameter collection and execution for cppcheck."""
import operator
import os
import subprocess

GITHUB_EVENT_NAME = os.environ["GITHUB_EVENT_NAME"]

# Set repository
CURRENT_REPOSITORY = os.environ["GITHUB_REPOSITORY"]
# TODO: How about PRs from forks?
INPUT_TARGET_REPOSITORY = os.environ["INPUT_TARGET_REPOSITORY"] or CURRENT_REPOSITORY
INPUT_PULL_REQUEST_REPOSITORY = (
        os.environ["INPUT_PULL_REQUEST_REPOSITORY"] or INPUT_TARGET_REPOSITORY
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

# command related inputs
SCOPE_SEP = ","
KNOWN_SCOPES = (
    "all",
    "informaton",
    "missingInclude",
    "performance",
    "portability",
    "style",
    "unusedFunction",
    "warning",
)
# domain specific language between environment and cppcheck parameters:
INPUT_CHECK_LIBRARY = "INPUT_CHECK_LIBRARY"
INPUT_SKIP_PREPROCESSOR = "INPUT_SKIP_PREPROCESSOR"
INPUT_ENABLE = "INPUT_ENABLE"
INPUT_EXCLUDE_CHECK = "INPUT_EXCLUDE_CHECK"
INPUT_INCONCLUSIVE = "INPUT_INCONCLUSIVE"
INPUT_INLINE_SUPPRESSION = "INPUT_INLINE_SUPPRESSION"
INPUT_FORCE_LANGUAGE = "INPUT_FORCE_LANGUAGE"
INPUT_MAX_CTU_DEPTH = "INPUT_MAX_CTU_DEPTH"
INPUT_OUTPUT_FILE = "INPUT_OUTPUT_FILE"
INPUT_PLATFORM = "INPUT_PLATFORM"

# domain specific vocabulary for switches:
DISABLED = 'disabled'
ENABLED = 'enabled'

DSL = {
    INPUT_CHECK_LIBRARY: os.getenv(INPUT_CHECK_LIBRARY, "disable"),
    INPUT_SKIP_PREPROCESSOR: os.getenv(INPUT_SKIP_PREPROCESSOR, "disable"),
    INPUT_ENABLE: os.getenv(INPUT_ENABLE, "all"),
    INPUT_EXCLUDE_CHECK: os.getenv(INPUT_EXCLUDE_CHECK, "disable"),
    INPUT_INCONCLUSIVE: os.getenv(INPUT_INCONCLUSIVE, "enable"),
    INPUT_INLINE_SUPPRESSION: os.getenv(INPUT_INLINE_SUPPRESSION, "disable"),
    INPUT_FORCE_LANGUAGE: os.getenv(INPUT_FORCE_LANGUAGE, "disable"),
    INPUT_MAX_CTU_DEPTH: os.getenv(INPUT_MAX_CTU_DEPTH, "disable"),
    INPUT_OUTPUT_FILE: os.getenv(INPUT_OUTPUT_FILE, "cppcheck_report.txt"),
    INPUT_PLATFORM: os.getenv(INPUT_PLATFORM, "disable"),
}


def split_csv(text):
    """Naive split of text as comma separated scope values yielding lower case strings."""
    if SCOPE_SEP in text:
        for scope in text:
            yield scope.strip().lower()
    else:
        yield scope.strip().lower()


def is_valid(scope):
    """Return scope if valid else empty string."""
    return scope if scope in KNOWN_SCOPES else ""


def parse_scopes():
    """Return the parsed scopes."""
    scopes = set(t for t in split_csv(DSL[INPUT_ENABLE]) if is_valid(t))
    if "all" in scopes:
        scopes = ["all"]
    else:
        scopes = sorted(scopes)
    return scopes


def command():
    """Prepare the command vector and set the path to the report file"""
    vector = [
        "cppcheck",
        f"--enable={SCOPE_SEP.join(parse_scopes())}",
    ]

    actions = {
        INPUT_CHECK_LIBRARY: (operator.eq, ENABLED, "--check-library"),
        INPUT_SKIP_PREPROCESSOR: (operator.eq, ENABLED, "-E"),
        INPUT_INLINE_SUPPRESSION: (operator.eq, ENABLED, "--inline-suppr"),
        INPUT_INCONCLUSIVE: (operator.eq, DISABLED, "--inconclusive"),

        INPUT_EXCLUDE_CHECK: (operator.eq, DISABLED, "-i {{}}"),
        INPUT_FORCE_LANGUAGE: (operator.eq, DISABLED, "--language={{}}}"),
        INPUT_MAX_CTU_DEPTH: (operator.eq, DISABLED, "--max-ctu-depth={{}}}"),
        INPUT_PLATFORM: (operator.ne, DISABLED, "--platform={{}}"),
    }

    constant_dimensions = (
        INPUT_CHECK_LIBRARY,
        INPUT_SKIP_PREPROCESSOR,
        INPUT_INLINE_SUPPRESSION,
        INPUT_INCONCLUSIVE)

    unary_dimensions = (
        INPUT_EXCLUDE_CHECK,
        INPUT_FORCE_LANGUAGE,
        INPUT_MAX_CTU_DEPTH,
        INPUT_PLATFORM)

    for dim in constant_dimensions:
        predicate, ref, contribution = actions[dim]
        if predicate(DSL[dim], ref):
            vector.append(contribution)

    for dim in unary_dimensions:
        predicate, ref, contribution = actions[dim]
        payload = DSL[dim]
        if predicate(payload, ref):
            vector.append(contribution.format(payload))

    return vector


def run(vector, where=".", show_version=None, show_help=None):
    """Execute the command in a sub process."""
    show_version = show_version if show_version is None else True
    show_help = show_help if show_help is None else True
    vector.append(f"--output-file={DSL[INPUT_OUTPUT_FILE]}")
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
    main()
