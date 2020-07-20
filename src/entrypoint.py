import os
import subprocess as sp


GITHUB_EVENT_NAME = os.environ['GITHUB_EVENT_NAME']

# Set repository
CURRENT_REPOSITORY = os.environ['GITHUB_REPOSITORY']
# TODO: How about PRs from forks?
TARGET_REPOSITORY = os.environ['INPUT_TARGET_REPOSITORY'] or CURRENT_REPOSITORY
PULL_REQUEST_REPOSITORY = os.environ['INPUT_PULL_REQUEST_REPOSITORY'] or TARGET_REPOSITORY
REPOSITORY = PULL_REQUEST_REPOSITORY if GITHUB_EVENT_NAME == 'pull_request' else TARGET_REPOSITORY

# Set branches
GITHUB_REF = os.environ['GITHUB_REF']
GITHUB_HEAD_REF = os.environ['GITHUB_HEAD_REF']
GITHUB_BASE_REF = os.environ['GITHUB_BASE_REF']
CURRENT_BRANCH = GITHUB_HEAD_REF or GITHUB_REF.rsplit('/', 1)[-1]
TARGET_BRANCH = os.environ['INPUT_TARGET_BRANCH'] or CURRENT_BRANCH
PULL_REQUEST_BRANCH = os.environ['INPUT_PULL_REQUEST_BRANCH'] or GITHUB_BASE_REF
BRANCH = PULL_REQUEST_BRANCH if GITHUB_EVENT_NAME == 'pull_request' else TARGET_BRANCH

GITHUB_ACTOR = os.environ['GITHUB_ACTOR']
GITHUB_REPOSITORY_OWNER = os.environ['GITHUB_REPOSITORY_OWNER']
GITHUB_TOKEN = os.environ['INPUT_GITHUB_TOKEN']

# command related inputs

CHECK_LIBRARY = os.environ['INPUT_CHECK_LIBRARY'] or 'disable'
SKIP_PREPROCESSOR = os.environ['INPUT_SKIP_PREPROCESSOR'] or 'disable'
ENABLE = os.environ['INPUT_ENABLE'] or 'all'
EXCLUDE_CHECK = os.environ['INPUT_EXCLUDE_CHECK'] or 'disable'
INCONCLUSIVE = os.environ['INPUT_INCONCLUSIVE'] or 'enable'
INLINE_SUPPRESSION = os.environ['INPUT_INLINE_SUPPRESSION'] or 'disable'
FORCE_LANGUAGE = os.environ['INPUT_FORCE_LANGUAGE'] or 'disable'
MAX_CTU_DEPTH = os.environ['INPUT_MAX_CTU_DEPTH'] or 'disable'
OUTPUT_FILE = os.environ['INPUT_OUTPUT_FILE'] or 'cppcheck_report.txt'
PLATFORM = os.environ['INPUT_PLATFORM'] or 'disable'

command = ""


def prepare_command():
    global command
    global out_file
    command = command + "cppcheck "
    # check every flags

    if CHECK_LIBRARY == 'enable':
        command = command + " --check-library"

    if SKIP_PREPROCESSOR == 'enable':
        command = command + " --E"

    enable_val = 'all'  # default fallback value

    if ENABLE == 'warning':
        enable_val = 'warning'
    elif ENABLE == 'style':
        enable_val = 'style'
    elif ENABLE == 'performance':
        enable_val = 'performance'
    elif ENABLE == 'portability':
        enable_val = 'portability'
    elif ENABLE == 'information':
        enable_val = 'information'
    elif ENABLE == 'unusedFunction':
        enable_val = "unusedFunction"
    elif ENABLE == 'missingInclude':
        enable_val = 'missingInclude'

    # multiple checks ; comma separated , skipping additional error checking
    if ',' in ENABLE:
        enable_val = ENABLE

    command = command + f" --enable={enable_val}"

    if EXCLUDE_CHECK != 'disable':
        command = command + f" -i {EXCLUDE_CHECK}"
        # assuming user passes a valid path
    if INCONCLUSIVE != 'disable':
        command = command + ' --inconclusive'

    if INLINE_SUPPRESSION == "enable":
        command = command + " --inline-suppr"

    if FORCE_LANGUAGE != 'disable':
        command = command + f" --language={FORCE_LANGUAGE}"
    if MAX_CTU_DEPTH != 'disable':
        command = command + f" --max-ctu-depth={MAX_CTU_DEPTH}"

    if PLATFORM != 'disable':
        command = command + f" --platform={PLATFORM}"

    out_file = OUTPUT_FILE


def run_cppcheck():
    global command
    command = command + f" --output-file={out_file} ."
    sp.call(command, shell=True)


def commit_changes():
    """Commits changes.
    """
    set_email = 'git config --local user.email "flawfinder-action@master"'
    set_user = 'git config --local user.name "flawfinder-action"'

    sp.call(set_email, shell=True)
    sp.call(set_user, shell=True)

    git_checkout = f'git checkout {TARGET_BRANCH}'
    git_add = f'git add {out_file}'
    git_commit = 'git commit -m "cppcheck report added/updated"'
    print('Committing reports.......')

    sp.call(git_checkout, shell=True)
    sp.call(git_add, shell=True)
    sp.call(git_commit, shell=True)


def push_changes():
    """Pushes commit.
    """
    set_url = f'git remote set-url origin https://x-access-token:{GITHUB_TOKEN}@github.com/{TARGET_REPOSITORY}'
    git_push = f'git push origin {TARGET_BRANCH}'
    sp.call(set_url, shell=True)
    sp.call(git_push, shell=True)


def main():

    if (GITHUB_EVENT_NAME == 'pull_request') and (GITHUB_ACTOR != GITHUB_REPOSITORY_OWNER):
        return

    prepare_command()
    run_cppcheck()
    commit_changes()
    push_changes()


if __name__ == '__main__':
    main()
