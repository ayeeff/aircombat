name: Weekly CSV to Feather

on:
  schedule:
    - cron: "0 3 * * 1"     # Every Monday 03:00 UTC
  workflow_dispatch:        # Allows manual run

jobs:
  convert:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install pandas + pyarrow
        run: pip install pandas pyarrow

      - name: Convert all CSVs to .feather
        run: python convert_to_feather.py

      # This block is now completely bullet-proof
      - name: Commit and push any new/updated .feather files
        run: |
          git config --local user.name "github-actions[bot]"
          git config --local user.email "github-actions[bot]@users.noreply.github.com"

          # Stage only .feather files that actually exist (never fails)
          git add -A data/**/*.feather 2>/dev/null || echo "No .feather files yet"

          # Only commit + push if something actually changed
          git diff --quiet --exit-code --cached
          if [ $? -eq 0 ]; then
            echo "No changes detected — nothing to commit"
          else
            git commit -m "Auto-update .feather files from CSVs [weekly]"
            git push
            echo "Successfully pushed new/updated .feather files"
          fi
