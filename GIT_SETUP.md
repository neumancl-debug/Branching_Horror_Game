# Upload this prototype with Git

Git tracks the source files. GitHub, GitLab, or your school's Git server stores
the remote copy. These instructions assume GitHub; use your school's URL instead
if required. The project folder already contains an initialized Git repository,
but currently has no commits or remote configured.

## First upload from Windows

1. Install [Git](https://git-scm.com/downloads) if `git --version` does not work.
2. Create an **empty** repository in your Git hosting account. Choose the visibility
   required by your class. Do not initialize it with a README, license, or gitignore;
   those initial files can conflict with the local first commit.
3. Copy the repository's HTTPS clone URL.
4. Open PowerShell and run:

```powershell
cd "C:\Users\dylan\OneDrive\Documents\ChatGPT\CIS350 prototype"
git add .
git status --short
```

Check the staged list. It should include the Python files, documentation,
requirements, `.gitignore`, `.gitattributes`, `pyproject.toml`, `Play.bat`,
`play.sh`, `preview.png`, and `.github/workflows/checks.yml`. It should exclude
`.devtools`, virtual environments, caches, and ZIP/executable files.

Then run these commands, replacing the example repository URL:

```powershell
git commit -m "Add cross-platform Blackthorn game prototype"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

If Git asks for an identity before committing, set your own name and email for
this repository, then retry the commit:

```powershell
git config user.name "Your Name"
git config user.email "YOUR-EMAIL"
```

Use the email you intend to appear on commits (a hosting-provider privacy email
is also suitable). Authenticate through Git's normal browser/credential flow.
Do not put passwords or access tokens in source files or repository URLs.

If `origin` already exists when you do this later, inspect `git remote -v` before
changing it. These first-upload commands assume a new, empty remote; do not force
push over an existing class repository. Clone an existing class repository and
copy these source files into that checkout if your instructor supplied one.

## Verify the upload

Open the repository online and confirm the README and source files are visible.
On GitHub, open **Actions** and inspect the Cross-platform checks workflow. It
tests Windows, macOS, and Linux using Python 3.10 and 3.13. A green run confirms
automated tests and headless rendering for those runners; it does not replace
trying the visible game window on the actual target computers.

## Teammates and instructors

Clone on any supported OS:

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
cd YOUR-REPOSITORY
```

Then follow the operating-system setup in README.md. Each person installs their
own Python dependencies in a local virtual environment. No bundled executables,
ZIP files, or API keys are needed. The GitHub workflow is optional if you use a
different hosting provider; the game itself does not depend on GitHub.

## Later updates

After changing and testing the code:

```bash
git add .
git diff --cached
git commit -m "Describe the change"
git push
```

Review `git diff --cached` before committing to confirm that the intended source
changes are staged. Keep the previously flagged archive quarantined; adding a
gitignore or uploading source does not establish that the archive was safe.
