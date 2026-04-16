# envdiff

A CLI tool to compare `.env` files across environments and flag missing or mismatched keys.

---

## Installation

```bash
pip install envdiff
```

Or install from source:

```bash
git clone https://github.com/youruser/envdiff.git
cd envdiff && pip install .
```

---

## Usage

Compare two `.env` files:

```bash
envdiff .env.development .env.production
```

**Example output:**

```
Missing in .env.production:
  - DATABASE_URL
  - DEBUG

Mismatched keys:
  - APP_PORT: 3000 (development) vs 8080 (production)

✔ All other keys match.
```

Compare multiple files at once:

```bash
envdiff .env.development .env.staging .env.production
```

Use the `--strict` flag to exit with a non-zero code if any differences are found (useful in CI pipelines):

```bash
envdiff .env .env.production --strict
```

---

## Options

| Flag | Description |
|------|-------------|
| `--strict` | Exit with code 1 if differences are found |
| `--ignore KEY` | Ignore a specific key during comparison |
| `--quiet` | Suppress output, only use exit codes |

---

## License

This project is licensed under the [MIT License](LICENSE).