# P2-Positioning
The focus of this project is to design, implement, test, and document a method for determining the distance between a transmitting and a receiving WIFI

To install dependencies simpy run:
```bash
pip install -r requirements.txt
```
---

# Git workflow

When working on the project, each feature is designated a branch, which is merged with the master branch, before pushing to production.

As each feature is designated its own branch, you can create a new branch using

```bash
git branch <branch_name>
```

> An alternative workflow is to create your changes on the **master** branch and the push them onto its own branch after. This is done with the [Git switch](https://git-scm.com/docs/git-switch) command.
>
> ```bash
> git switch -c <branch_name>
> ```
>
> This creates a new branch for your feature, and moves all your changes to it.

Next, you can add your changes to the index with [Git add](https://git-scm.com/docs/git-add), and [Git commit](https://git-scm.com/docs/git-commit)

```bash
git add -p
git commit -m "<description>"
```

Next, we 'll push our changes onto the branch with [Git push](https://git-scm.com/docs/git-push).

```bash
git push
```

If its the first time pushing from the branch it might be necessary to set the upstream branch.

```bash
git push --set-upstream origin <branch_name>
```

Once you've executed `git push`, and the push has went through, you should be prompted with a link to create a new merge request. This is how you should request to get your feature added the the **master** branch. Simply create a new merge request, give it a name, and a brief description, and await approval.

> **Git Status:**
> If you, at any point, wishes to know the current status of your index, you can use the [Git status](https://git-scm.com/docs/git-status) command. This is a nice way to get an overview, of how files have been changed, and what changes have been added to the index.
>
> ```bash
> git status
> ```
