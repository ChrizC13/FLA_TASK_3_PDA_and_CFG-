from pathlib import Path
import shutil, subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
DIAGRAMS = ROOT / "docs" / "diagrams"

def main():
    dot = shutil.which("dot")
    if dot is None:
        raise SystemExit("Graphviz 'dot' is required to regenerate diagram images. Existing PNG/SVG files are included.")
    files = sorted(DIAGRAMS.glob("*.dot"))
    if not files:
        raise SystemExit("No .dot source files found in docs/diagrams.")
    for source in files:
        for fmt in ("png", "svg"):
            target = source.with_suffix("." + fmt)
            subprocess.run([dot, f"-T{fmt}", str(source), "-o", str(target)], check=True)
            print(f"Generated {target.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
