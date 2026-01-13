# Plutonium Homebrew Repository

This is a local repository for Plutonium/Foundry VTT homebrew content.

## How to use

1. Point Plutonium to use this `index.json`.
2. To add more content:
    - Create a JSON file in a subfolder (e.g., `spells/my_spells.json`).
    - Add the relative path to the `toImport` array in `index.json`.

## Structure

- \`index.json\`: The main entry point. Lists all files to be imported.
- \`creatures/\`: Folder for bestiary homebrew.
- \`spells/\`: Folder for spell homebrew.
- \`items/\`: Folder for item homebrew.
