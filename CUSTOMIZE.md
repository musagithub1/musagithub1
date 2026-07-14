# Customize this profile

The repository is ready for the `musagithub1/musagithub1` profile repository on the current `master` branch.

## Update your information

1. Edit `profile.json`.
2. Replace `assets/avatar.png` with a square portrait if needed.
3. Regenerate both theme files:

```bash
python -m pip install -r requirements.txt
python scripts/generate_profile.py
```

The generator writes `dark.svg` and `light.svg` in the repository root.

## Publish on GitHub

Upload all files and folders from this package to the root of `musagithub1/musagithub1`. Keep these files in the root:

- `README.md`
- `dark.svg`
- `light.svg`
- `profile.json`

Keep `assets/` and `scripts/` as included so the design remains easy to update later.

## Branch note

The image URLs inside `README.md` use the current `master` branch. If the repository is later renamed to `main`, change both occurrences of `/master/` to `/main/`.
