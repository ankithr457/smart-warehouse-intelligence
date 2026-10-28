# IEEE Conference Report Source

The report uses the IEEEtran conference class with US Letter paper, two columns, a title and author block, an abstract, index terms, numbered sections, numbered tables and figures, and bracketed references. Page numbers are retained for project review.

## Build the PDF

Install TeX Live or MiKTeX with pdfLaTeX, listings and tabularx, then run from the repository root:

```bash
python scripts/build_report.py
```

The build compiles `project-report.tex` twice to resolve references and replaces `reports/project-report.pdf`. Figure paths refer to the committed images in `reports/figures/`.

After regenerating the analysis, install `requirements-report.txt` and run `python scripts/build_figures.py` to refresh the result charts. Refresh browser captures with `node scripts/capture_dashboards.cjs` after installing Playwright and Chromium. Update the narrative and result tables in the LaTeX source to match the new exports before compiling.

## Source and Scope

`IEEEtran.cls` is the unmodified IEEEtran 1.8b class distributed through CTAN. Its original license and attribution remain in the file. Template source: https://ctan.org/pkg/ieeetran

This is an independent technical project report. It has not been submitted to, accepted by or published by IEEE. A conference submission would require the target venue's specific page limit and submission settings.
