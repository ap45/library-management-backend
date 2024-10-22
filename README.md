
# Backend (Django) Project

## 1. Cloning the Repository
To start working on the backend project, first clone the repository:

```bash
git clone https://github.com/ap45/library-management-backend.git
cd library-management-backend
```

## 2. Set Up a Virtual Environment and Install Dependencies
Create and activate a virtual environment, then install the required dependencies listed in `requirements.txt`:

```bash
python -m venv env
source env/bin/activate  # On Windows: .\env\Scripts\activate
pip install -r requirements.txt
```

## 3. Create a Feature Branch
All changes should be made on a new feature branch, **never directly on the `main` branch**. To create a feature branch:

```bash
git checkout -b feature/your-feature-name
```

## 4. Make Your Changes
Work on the Django application and frequently commit your changes:

```bash
git add .
git commit -m "Describe your changes"
```

## 5. Push to Remote Repository
Once you're ready to push the changes:

```bash
git push origin feature/your-feature-name
```

## 6. Submit a Pull Request
After pushing your feature branch, submit a PR:

- Navigate to the repository on GitHub.
- Click **New Pull Request**.
- Choose the **main** branch as the base and **your feature branch** as the compare.
- Describe your changes and **add reviewers**.
- Submit the PR.

## 7. Addressing Review Comments
If changes are requested by a reviewer:

- Make the necessary code updates.
- Commit and push them to the same branch.

```bash
git add .
git commit -m "Address reviewer comments"
git push origin feature/your-feature-name
```

This will invalidate previous approvals, so the PR must be reapproved.

## 8. Merging into `main`
Once the PR has all required approvals and the CI pipeline passes, the code can be merged into the `main` branch.

## Handling Merge Conflicts
If there are merge conflicts, rebase your feature branch onto the latest `main`:

```bash
git fetch origin
git rebase origin/main
# Resolve conflicts
git add <conflicted_file>
git rebase --continue
git push --force-with-lease
```

## What Happens When You Push Code to a Branch

1. **Feature Branch**: 
   When you push code to a feature branch, the CI pipeline runs automatically on GitHub to check if the code builds successfully and passes any tests or checks defined. The Django project is packaged and uploaded as an artifact.

2. **Pull Request Review**:
   After pushing to a feature branch, the code cannot be merged into `main` until a pull request is reviewed and approved by the designated reviewers. Any new commits invalidate the prior approval, and the new commit must be reapproved.

3. **Merging to Main**:
   After all approvals and successful pipeline runs, the feature branch can be merged into `main`. This is done through the pull request and **cannot** be done by pushing directly to `main`.

## Managing Reviews and Approvals

- **Adding Reviewers**: In GitHub, you can select reviewers in the pull request interface under "Reviewers" on the right-hand side. A reviewer will need to approve the PR before it can be merged.
  
- **Requiring Approvals**: Ensure that each PR has the necessary number of approvals (as specified in branch protection rules). If new commits are pushed, approvals are reset, and the most recent commit must be approved again.
