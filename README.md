This is a bunch of streamlit applications using the API. The "API_Test" file is a simple test: it's a small application for searching for French companies.

The second application, the subject of this project, is a dashboard using the GitHub API to track the progress of PRs (merged and closed). To make the code work, you need a GitHub token (classic, not detailed) and place it in a .env file like this: GITHUB_TOKEN=ghp_tokenid. You then need to place this .env file in your repository or local folder.

Using the GitHub API dashboard:
Enter the URL of your repository or account (automatic detection), then access the statistics, with filtering and display options.
