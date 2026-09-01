# Backward/Forward Sweep Power Flow

Educational Python implementation of the backward/forward sweep algorithm for radial distribution-system power-flow analysis.

## Contents

| File | Purpose |
|---|---|
| `backward_forward_sweep.py` | Main script implementing the iterative backward/forward sweep. |
| `33Bus.txt`, `33Line.txt` | Default 33-bus test-system input used by the script. |
| `3Bus.txt`, `3Line.txt` | Smaller historical test inputs. |

The script currently reads the 33-bus input files from its working directory and prints voltages, currents, losses, and iteration information to the console.

## Requirements

- Python 3.8 or later
- `numpy`, `pandas`, and `matplotlib`

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python backward_forward_sweep.py
```

## Notes

- The current script is a standalone teaching/research script rather than an importable package.
- The original filename has been normalized to `backward_forward_sweep.py`. The script remains at the repository root so its relative data paths continue to work.
- New cache, virtual-environment, and generated-output files are excluded by `.gitignore`.

## License and citation

A reuse license and formal citation guidance will be added after the intended reuse terms are chosen.
