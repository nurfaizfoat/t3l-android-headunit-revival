# How this repo was published — layman step-by-step

A plain-language recipe for turning a local project folder into a public
GitHub repository with a Linux terminal. Reuse it for any future project.

## What you need first (one-time setup)

1. **A GitHub account** — sign up at https://github.com if you don't have one.
2. **Git installed** — the version-control tool (`/usr/bin/git`, already present).
3. **GitHub CLI (`gh`) installed and logged in** — this is what lets the
   terminal talk to GitHub without you typing passwords:

   ```sh
   gh auth login
   # follow the interactive prompts (browser login is easiest)
   gh auth status   # should print "Logged in to github.com account <you>"
   ```

4. If `gh auth status` says your **Git operations protocol is `ssh`** but you
   have no SSH key set up, switch to HTTPS (the browser-token way, no key
   files needed):

   ```sh
   gh config set git_protocol https
   gh auth setup-git
   ```

## Step by step for a new project

All commands run inside your project folder (`cd /path/to/project` first).

### 1. Decide what must stay private

Write a `.gitignore` file listing anything you never want published:
raw evidence dumps, screenshots, signing keys, build outputs, caches.
For this repo it is already done — see the file for the format. Never
skip this step; once something is pushed publicly, assume it is permanent.

### 2. Scrub personal details from files you WILL publish

- Wi-Fi network names, LAN IP addresses, phone numbers or real names;
- replace them with placeholders like `<unit-ip>` or `<your-ssid>`;
- the credentials themselves live in the ignored private folders.

A quick check before every release:

```sh
grep -rn "192.168\|your-found-password\|your-found-name" *.md *.py
```

### 3. Add a LICENSE unless you want people to read it but never reuse it

In this repo: MIT (`LICENSE` file). Choose at https://choosealicense.com —
for documentation-heavy projects, CC BY 4.0 is an alternative.

### 4. Make the README friendly to strangers

The first 10 lines should say what the project is for people who have never
heard of it, state the warnings up front, and point to the other documents.

### 5. Turn the folder into a git repository and commit

```sh
git init -b main        # starts tracking this folder
git add -A              # stages every non-ignored file
git status --short      # REVIEW THE STAGED LIST — this line matters most
```

If you see a file you would not want on the internet, stop here, fix
the `.gitignore`, and run `git rm --cached <file>` to unstage it.

Then record the first version:

```sh
git commit -m "Initial public release: <one-line summary>"
```

### 6. Create the GitHub repo and push

```sh
gh repo create <repo-name> --public --source=. --push
```

This creates the repository on github.com and uploads your commit in one
command. If it prints an SSH permission error but announces the repo URL,
switch the remote to HTTPS and retry:

```sh
git remote set-url origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

### 7. Review it like a stranger

Open `https://github.com/<your-username>/<repo-name>` in a browser and check:

- the README renders and makes sense to someone who knows nothing;
- no personal data, keys or evidence dumps appear in any file;
- the repo is marked **Public**;
- the license file is displayed in the "About" sidebar area.

### Future updates

After changing files, repeat a scrub check, then:

```sh
git add -A && git commit -m "<what changed>" && git push
```

## Checklist that was applied to this specific repo

- [x] `.gitignore` covers `evidence/`, `changes/`, `.private/`, pycache,
      build outputs, APKs and the regenerable `androguard.db`
- [x] SSID and LAN IPs replaced with `<your-ssid>` / `<unit-ip>` /
      `<laptop-ip>` placeholders in all published markdown
- [x] MIT license added (`LICENSE`)
- [x] README rewritten for a public audience with a device-safety warning
- [x] Staged file list reviewed; secret scan of staged diff came back clean
- [x] Repo pushed and verified at
      https://github.com/nurfaizfoat/t3l-android-headunit-revival
