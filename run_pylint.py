from pylint.lint import Run
import os
import sys


def run_pylint(file_name):
    """Run Pylint directly on the given file."""
    print(f"Running Pylint on {file_name}...")
    try:
        # Run Pylint on the specified file
        Run([file_name])
    except SystemExit as e:
        exit_code = e.code
        if exit_code != 0:
            print(f"Pylint found issues in {file_name}. Exit code: {exit_code}")
        else:
            print(f"Pylint finished successfully for {file_name}.")
        return exit_code


if __name__ == "__main__":
    # Add the project root to PYTHONPATH
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(project_root)

    # Specify the relative path to the file
    file_to_lint = "scrapy_project/spiders/spider.py"

    # Run Pylint
    exit_code = run_pylint(file_to_lint)
    sys.exit(exit_code)
