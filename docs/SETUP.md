# Setup and reproduction

## Run on Windows

1. Install Python 3.10 or newer and Git. Open PowerShell in your project directory.
2. Clone and create an isolated environment:

   ```powershell
   git clone https://github.com/mitsosasim/computer_architecture.git
   cd computer_architecture
   py -3 -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

3. Rebuild tables from the supplied data, then regenerate plots:

   ```powershell
   .\.venv\Scripts\python.exe tools/analyze.py
   .\.venv\Scripts\python.exe tools/plot_results.py
   .\.venv\Scripts\python.exe -m unittest discover -s tests -v
   ```

4. Open `build/plots` in File Explorer. Open `build/branches.csv`, `build/cpu.csv`, and `build/memory.csv` in Calc or Excel. `build/results.json` contains configuration means and parsed sweep parameters.
5. For the original analysis, open the PDF reports in each assignment folder. The `.ods` workbooks and `.odt` reports remain editable in LibreOffice. No macros or office installation are needed for the Python workflow.

Commands were verified on Linux with Python 3.12. Windows commands use the same Python scripts and standard-library paths, but were not executed on Windows. The analysis has no dependency on the original colon-containing Linux directory names because those names are stored inside compressed JSON records.

## Linux / macOS

From the repository root:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python tools/analyze.py
python tools/plot_results.py
python -m unittest discover -s tests -v
```

The analysis reads source data without modifying it. Its generated files are under `build/` and may be regenerated. `--output PATH` selects a separate analysis directory. For a custom directory, pass `--input PATH/results.json --output PATH/plots` to `tools/plot_results.py`.

## Evidence and metric definitions

- Branch data is the supplied `all_stats.txt`. The parser produces 20 predictor/benchmark records. The reported ratio is `system.cpu.commit.branchMispredicts / system.cpu.branchPred.lookups`. It is not automatically the fraction of conditional branches predicted incorrectly, nor an accuracy percentage.
- CPU data comes from the five numeric benchmark columns in `sim2_stats.ods`. All 25 usable rows have their mean checked against the workbook's cached average. The report describes sequential tuning: later resource groups retain earlier choices. Do not interpret those plots as isolated one-variable experiments with every other resource held at the initial default. The report's multiplicative MiP is a coursework cost proxy, not measured power, area, or money.
- Cache data consists of five gzip-compressed JSONL files, one per benchmark. Every record retains the complete original `stats.txt` text and its original configuration label. There are 74 records per file. The supplementary `example-config.json` is one original simulator configuration, not a portable launch script.
- Task 1 covers 3 line sizes × 4 L1 associativities. Task 2 covers 3 L2 sizes × 3 L2 associativities × 3 replacement policies × 2 inclusion settings. Task 3 covers 2 prefetchers × 4 degrees. Each configuration must have exactly one record from each of five benchmarks.
- `l1d_miss_rate` reads `system.cpu.dcache.overallMissRate::total`; `l2_miss_rate` independently reads `system.l2cache.overallMissRate::total`. The original task-2 extractor reads the L1D counter despite discussing a global miss rate. Current column names follow the actual counters and do not relabel L1D values as L2 or global rates.
- `dram_bytes_per_second` is `system.mem_ctrl.dram.bwTotal::total`. Plots divide by 10^9 to show decimal GB/s. One passage in the original report calls this bytes per cycle. That passage is preserved as historical text, while current plots use the counter's byte/second unit.
- Multiple gem5 statistic dumps are handled by selecting the final dump without mixing stale fields from earlier dumps. Averages are unweighted arithmetic means of per-benchmark IPC, not pooled instruction/cycle ratios or geometric-mean speedups.

All plots reanalyze historical simulation output. Benchmark identities, source programs, and the complete executable course environment are missing. The comparisons are not measurements of the host machine running these Python scripts.

## Predictor source boundaries

`GAgPredictor.cc/.hh` and `PAgPredictor.cc/.hh` target the course gem5 `BPredUnit` interface. They are not standalone C++ programs. Generated `params/GAgPred.hh`, `params/PAgPred.hh`, their Python SimObject declarations, build registration, exact simulator revision, and benchmark commands are absent. A current gem5 installation alone does not establish compatibility. No verified full-simulator build command can be recovered from these files.

GAg indexes a shared pattern table from global outcome history. PAg selects local history by branch address, then indexes a shared counter table. Both skip wrong-path updates and leave several history hooks empty. In particular, PAg allocates tables using entry counts but builds masks as `(1 << ltableHeight) - 1` and `(1 << gtableHeight) - 1`. For the report's 256/32-entry settings those shifts exceed the normal unsigned width, and the resulting indexing is unsafe. Table-size and counter-width validation also needs review. No algorithmic repair or new predictor-performance claim is included here. Archived results do not prove that the supplied source, unchanged, generated them.

For fresh simulations, recover the original course gem5 checkout, SimObject declarations, SConscript entries, benchmark programs and arguments, and run scripts. Resolve the indexing/history concerns before integrating and testing the predictors. Existing reports and measurements should remain historical evidence even if a future implementation changes.

## Original scripts and report build

The memory assignment's `scripts` folder preserves the student's extraction and bar-chart scripts. Their original absolute input paths and fixed output filenames make them historical references. Use `tools/analyze.py` as the portable entry point. `bar_graph.py` contains manually entered averages, whereas the current plots derive them from raw statistics.

The concise report uses pdfLaTeX. Compile `docs/report/main.tex` from its own directory with two passes of `pdflatex -interaction=nonstopmode -halt-on-error main.tex`. The Overleaf ZIP contains `main.tex` at its root and all required figures. Original course reports are separate and unchanged.
