"""Upload unisonai-sdk to PyPI."""
import subprocess
import sys
import shutil
import os


def clean():
    """Remove previous build artifacts."""
    for folder in ("build", "dist", "unisonai_sdk.egg-info"):
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"  Removed {folder}/")


def build():
    """Build source and wheel distributions."""
    print("\n[1/3] Building package...")
    subprocess.check_call([sys.executable, "setup.py", "sdist", "bdist_wheel"])
    print("  Build complete.")


def upload(token: str):
    """Upload distributions to PyPI using twine."""
    print("\n[2/3] Uploading to PyPI...")
    subprocess.check_call([
        sys.executable, "-m", "twine", "upload",
        "dist/*",
        "-u", "__token__",
        "-p", token,
    ])
    print("  Upload complete.")


def main():
    token = input("Enter your PyPI API token: ").strip()
    if not token:
        print("Error: token cannot be empty.")
        sys.exit(1)

    # Ensure build tools are installed
    print("[0/3] Checking dependencies...")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "--upgrade", "setuptools", "wheel", "twine"],
        stdout=subprocess.DEVNULL,
    )

    clean()
    build()
    upload(token)

    print("\n[3/3] Cleaning up...")
    clean()
    print("\nDone! Package uploaded to PyPI.")


if __name__ == "__main__":
    main()
