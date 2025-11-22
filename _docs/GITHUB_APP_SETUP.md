# Configuring GitHub App for CI/CD Bypass

To allow automated workflows (like Semantic Release) to push directly to protected branches (`main`), we recommend using a GitHub App instead of a Personal Access Token (PAT).

## 1. Create a GitHub App

1.  Go to your GitHub account **Settings** -> **Developer settings** -> **GitHub Apps**.
2.  Click **New GitHub App**.
3.  **GitHub App Name**: e.g., `blender-ai-mcp-bot` (must be globally unique).
4.  **Homepage URL**: Link to your repo.
5.  **Callback URL**: (Ignore/Dummy).
6.  **Webhook**: Uncheck "Active" (we don't need webhooks).
7.  **Permissions** (Repository permissions):
    *   `Contents`: **Read & Write** (to push commits/tags).
    *   `Pull Requests`: **Read & Write** (if you use PRs).
    *   `Metadata`: **Read** (mandatory).
    *   `Workflows`: **Read & Write** (optional, if modifying workflows).
8.  Click **Create GitHub App**.

## 2. Get Credentials

After creation, you will see the App settings page.
1.  **App ID**: Note this number (e.g., `123456`).
2.  **Private Key**: Click "Generate a private key". It will download a `.pem` file.

## 3. Install the App

1.  In the App settings, go to **Install App**.
2.  Click **Install** next to your account/organization.
3.  Select **Only select repositories** and choose `blender-ai-mcp`.
4.  Click **Install**.

## 4. Configure Repository Secrets

Go to your repository (`blender-ai-mcp`) -> **Settings** -> **Secrets and variables** -> **Actions**.
Add two secrets:

1.  `APP_ID`: The App ID from step 2.
2.  `APP_PRIVATE_KEY`: The content of the `.pem` file (copy everything including `-----BEGIN...`).

## 5. Update Branch Protection Rules

1.  Go to Repo **Settings** -> **Branches** -> **Add rule** (or edit `main`).
2.  Enable "Require a pull request before merging".
3.  Look for **"Allow specified actors to bypass required pull requests"**.
4.  Search for your App name (`blender-ai-mcp-bot`) and select it.
5.  Save changes.

## 6. Update Workflow (`release.yml`)

Update the CI/CD workflow to use the App token instead of the default `GITHUB_TOKEN`.

```yaml
steps:
  - name: Generate Token
    uses: actions/create-github-app-token@v1
    id: app-token
    with:
      app-id: ${{ secrets.APP_ID }}
      private-key: ${{ secrets.APP_PRIVATE_KEY }}

  - uses: actions/checkout@v4
    with:
      token: ${{ steps.app-token.outputs.token }} # Use the generated token
      fetch-depth: 0

  - name: Python Semantic Release
    uses: python-semantic-release/python-semantic-release@master
    with:
      github_token: ${{ steps.app-token.outputs.token }} # Pass token to release tool
```
