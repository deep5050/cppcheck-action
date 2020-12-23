"""Drive the parameter collection and execution for cppcheck."""
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
INPUT_TARGET_BRANCH = os.environ["INPUT_TARGET_BRANCH"] or CURRENT_BRANCH
INPUT_PULL_REQUEST_BRANCH = os.environ["INPUT_PULL_REQUEST_BRANCH"] or GITHUB_BASE_REF
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

PARAMETERS = {
    "INPUT_CHECK_LIBRARY": os.getenv("INPUT_CHECK_LIBRARY", "disable"),
    "INPUT_SKIP_PREPROCESSOR": os.getenv("INPUT_SKIP_PREPROCESSOR", "disable"),
    "INPUT_ENABLE": os.getenv("INPUT_ENABLE", "all"),
    "INPUT_EXCLUDE_CHECK": os.getenv("INPUT_EXCLUDE_CHECK", "disable"),
    "INPUT_INCONCLUSIVE": os.getenv("INPUT_INCONCLUSIVE", "enable"),
    "INPUT_INLINE_SUPPRESSION": os.getenv("INPUT_INLINE_SUPPRESSION", "disable"),
    "INPUT_FORCE_LANGUAGE": os.getenv("INPUT_FORCE_LANGUAGE", "disable"),
    "INPUT_MAX_CTU_DEPTH": os.getenv("INPUT_MAX_CTU_DEPTH", "disable"),
    "INPUT_OUTPUT_FILE": os.getenv("INPUT_OUTPUT_FILE", "cppcheck_report.txt"),
    "INPUT_PLATFORM": os.getenv("INPUT_PLATFORM", "disable"),
}
# INPUT_GITHUB_USER = os.getenv("INPUT_GITHUB_USERNAME",  "cppcheck-action")
# INPUT_GITHUB_EMAIL = os.getenv("INPUT_GITHUB_EMAIL", "cppcheck-action@master")
# INPUT_COMMIT_MSG = os.getenv("INPUT_COMMIT_MSG", "cppcheck report added or updated")


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


def prepare(command=None):
    """Prepare the command vector and set the path to the report file"""
    command = [] if command is None else command
    command.append("cppcheck")

    if PARAMETERS["INPUT_CHECK_LIBRARY"] == "enable":
        command.append("--check-library")

    if PARAMETERS["SKIP_PREPROCESSOR"] == "enable":
        command.append("-E")

    scopes = set(t for t in split_csv(PARAMETERS["INPUT_ENABLE"]) if is_valid(t))
    if "all" in scopes:
        scopes = ["all"]
    else:
        scopes = sorted(scopes)

    command.append(f"--enable={SCOPE_SEP.join(scopes)}")

    if PARAMETERS["INPUT_EXCLUDE_CHECK"] != "disable":
        command.append(f"-i {PARAMETERS['INPUT_EXCLUDE_CHECK']}")

    if PARAMETERS["INPUT_INCONCLUSIVE"] != "disable":
        command.append("--inconclusive")

    if PARAMETERS["INPUT_INLINE_SUPPRESSION"] == "enable":
        command.append("--inline-suppr")

    if PARAMETERS["INPUT_FORCE_LANGUAGE"] != "disable":
        command.append(f"--language={PARAMETERS['INPUT_FORCE_LANGUAGE']}")

    if PARAMETERS["INPUT_MAX_CTU_DEPTH"] != "disable":
        command.append(f"--max-ctu-depth={PARAMETERS['INPUT_MAX_CTU_DEPTH']}")

    if PARAMETERS["INPUT_PLATFORM"] != "disable":
        command.append(f"--platform={PARAMETERS['INPUT_PLATFORM']}")


def run(command, where=".", show_version=None, show_help=None):
    """Execute the command in a sub process."""
    show_version = show_version if show_version is None else True
    show_help = show_help if show_help is None else True
    command.append(f"--output-file={PARAMETERS['INPUT_OUTPUT_FILE']} {where}")
    print(f"given command {' '.join(command)}")

    if show_version:
        print("checking version")
        subprocess.call("cppcheck --version", shell=True)

    if show_help:
        subprocess.call("cppcheck --help", shell=True)

    subprocess.call(command, shell=True)


# def commit_changes():
#     """Commits changes."""
#     set_email = f"git config --local  user.email {GITHUB_EMAIL}"
#     set_user = f"git config --local  user.name {GITHUB_USER}"

#     subprocess.call(set_email, shell=True)
#     subprocess.call(set_user, shell=True)

#     git_checkout = f"git checkout {INPUT_TARGET_BRANCH}"
#     git_add = f"git add {out_file}"
#     git_commit = f'git commit -m  "{COMMIT_MSG}"'

#     print("Committing reports.......")

#     subprocess.call(git_checkout, shell=True)
#     subprocess.call(git_add, shell=True)
#     subprocess.call(git_commit, shell=True)


# def push_changes():
#     """Pushes commit."""
#     set_url = (
#         f"git remote set-url origin https://x-access-token:{GITHUB_TOKEN}"
#         f"@github.com/{INPUT_TARGET_REPOSITORY}")
#     git_push = f"git push origin {INPUT_TARGET_BRANCH}"
#     subprocess.call(set_url, shell=True)
#     subprocess.call(git_push, shell=True)


def main():
    """Drive the parameter extraction and execution of cppcheck."""
    if all((GITHUB_EVENT_NAME == "pull_request", GITHUB_ACTOR != GITHUB_REPOSITORY_OWNER)):
        return

    command = []
    prepare(command)
    run(command)
    # commit_changes()
    # push_changes()


if __name__ == "__main__":
    main()
