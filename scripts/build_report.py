"""Compile the IEEEtran report from version-controlled LaTeX source."""
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def main():
    engine = shutil.which('pdflatex')
    if engine is None:
        raise SystemExit('Install TeX Live or MiKTeX with pdfLaTeX, listings and tabularx.')
    source = ROOT / 'docs' / 'ieee'
    destination = ROOT / 'reports' / 'project-report.pdf'
    with tempfile.TemporaryDirectory(prefix='ieee-report-') as directory:
        for _ in range(2):
            result = subprocess.run(
                [engine, '-interaction=nonstopmode', '-halt-on-error',
                 f'-output-directory={directory}', 'project-report.tex'],
                cwd=source, capture_output=True, text=True,
            )
            if result.returncode:
                raise SystemExit(result.stdout[-6000:])
        log = (Path(directory) / 'project-report.log').read_text(errors='replace')
        if 'There were undefined references' in log:
            raise SystemExit('Unresolved report references.')
        shutil.copyfile(Path(directory) / 'project-report.pdf', destination)
        print(destination)

if __name__ == '__main__':
    main()
