import json
import re
import sys
from functools import cache
from pathlib import Path
from typing import Dict, Iterable, List, Union

CURR_DIR = Path(__file__).parent.absolute()
CLI_TEMPLATE_DIR = (
    CURR_DIR.parent.parent / "libs/cli/langchain_cli/integration_template/docs"
)

INFO_BY_DIR: Dict[str, Dict[str, Union[int, str]]] = {
    "chat": {
        "issue_number": 22296,
    },
    "document_loaders": {
        "issue_number": 22866,
    },
    "stores": {},
    "llms": {
        "issue_number": 24803,
    },
    "text_embedding": {"issue_number": 14856},
    "toolkits": {"issue_number": "TODO"},
    "tools": {"issue_number": "TODO"},
    "vectorstores": {"issue_number": 24800},
    "retrievers": {"issue_number": "TODO"},
}


@cache
def _get_headers(doc_dir: str) -> Iterable[str]:
    """Gets all markdown headers ## and below from the integration template.

    Ignores headers that contain "TODO"."""
    ipynb_name = f"{doc_dir}.ipynb"
    if not (CLI_TEMPLATE_DIR / ipynb_name).exists():
        raise FileNotFoundError(f"Could not find {ipynb_name} in {CLI_TEMPLATE_DIR}")
    with open(CLI_TEMPLATE_DIR / ipynb_name, "r") as f:
        nb = json.load(f)

    headers: List[str] = []
    for cell in nb["cells"]:
        if cell["cell_type"] == "markdown":
            for line in cell["source"]:
                if not line.startswith("##") or "TODO" in line:
                    continue
                header = line.strip()
                headers.append(header)
    return headers


def check_header_order(path: Path) -> None:
    doc_dir = path.parent.name
    if doc_dir not in INFO_BY_DIR:
        # Skip if not a directory we care about
        return
    headers = _get_headers(doc_dir)
    issue_number = INFO_BY_DIR[doc_dir].get("issue_number", "nonexistent")

    print(f"Checking {doc_dir} page {path}")

    with open(path, "r") as f:
        doc = f.read()
    regex = r".*".join(headers)
    if not re.search(regex, doc, re.DOTALL):
        issueline = (
            (
                " Please see https://github.com/langchain-ai/langchain/issues/"
                f"{issue_number} for instructions on how to correctly format a "
                f"{doc_dir} integration page."
            )
            if isinstance(issue_number, int)
            else ""
        )
        raise ValueError(
            f"Document {path} does not match the expected header order.{issueline}"
        )


def main(*new_doc_paths: Union[str, Path]) -> None:
    for path in new_doc_paths:
        path = Path(path).resolve().absolute()
        if CURR_DIR.parent / "docs" / "integrations" in path.parents:
            check_header_order(path)
        else:
            continue


if __name__ == "__main__":
    main(*sys.argv[1:])
