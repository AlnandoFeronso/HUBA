<p align="center"><strong>HUBA</strong> &middot; <em>FPGA-based probabilistic computer</em></p>

---

# Example documentation structure

This is an example to adapt. Start with one folder and split only when it gets crowded.

```
docs/
├── README.md          # index for the whole docs folder
├── overview/          # project goals, glossary, background
│   └── introduction.md
├── architecture/      # p-bit design and system decisions
│   └── design.md
├── hardware/          # FPGA/HDL modules, constraints, boards
│   └── fpga-specs.md
├── software/          # Python and C++ code, host tools, APIs
│   └── api-reference.md
├── simulation/        # models and simulation results
│   └── model-results.md
├── testing/           # test plans and results
│   └── test-report.md
├── guides/            # setup and how-to
│   └── getting-started.md
├── reports/           # experiments, measurements, status
│   └── experiment-1.md
└── assets/            # images shared by documents
    └── diagram.png
```

| Folder | What belongs here |
|--------|-------------------|
| overview | goals, glossary, project background |
| architecture | p-bit design and system decisions |
| hardware | FPGA/HDL modules, constraints, boards |
| software | Python and C++ code, host tools, APIs |
| simulation | models and simulation results |
| testing | test plans and results |
| guides | setup and how-to |
| reports | experiments, measurements, status |
| assets | images shared by documents |

## Where does my document go?

- Put a new feature description in architecture/
- Put a board configuration guide in hardware/
- Put an experiment summary in reports/

---

<p align="center"><sub><strong>HUBA</strong> &middot; Licensed under the Apache License 2.0 &middot; see the <code>LICENSE</code> file in the repository root</sub></p>
