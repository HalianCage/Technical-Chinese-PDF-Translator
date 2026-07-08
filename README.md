
# Chinese CAD Translation Tool

A local tool for extracting, translating, and reflowing Chinese text from CAD-exported PDFs. It combines OCR (PP-OCRv5 via ONNX), translation services, and PDF rendering to produce translated PDFs while preserving layout.

## Key Features

- High-accuracy text extraction using PP-OCRv5 ONNX models
- Integrated translation pipeline to translate extracted Chinese text
- Reflowed output PDFs with translated text, preserving original layout
- CLI and GUI entry points for flexible usage

## Repository Layout

- `run_app.py` — main application entrypoint
- `backend/` — backend API and core job management
  - `backend/main.py` — background server / task runner
  - `backend/api/translations.py` — translation API endpoints
- `ppocrv5_onnx/` — OCR model code, configs, and ONNX models
- `services/` — higher-level services such as `pdf_translator.py`
- `utils/` — helper utilities for text extraction, PDF output, etc.
- `frontend/gui.py` — lightweight GUI frontend
- `requirements.txt` — Python dependencies

For details, explore the code in each folder.

## Requirements

- Python 3.10+
- A working `pip` and virtual environment tool (venv/virtualenv)


## Installation

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows: .venv\Scripts\activate
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. Ensure the OCR models exist under `ppocrv5_onnx/models/` (the repo includes `PP-OCRv5_mobile_det` and `PP-OCRv5_mobile_rec` directories).

4. Create a new directory named "trained_helsinki" in the root. Download the transformer-based fine tuned translation model from the below link and store it in that directory: https://drive.google.com/drive/folders/1_yP-LEZWHUcNDyPAghA2J7akIBTeEbut?usp=sharing. You could also use any other translation model you want!

## Quick Start

- Run the start-up script (recommended):

```bash
python run_app.py
```

- Run the GUI front-end directly:

```bash
python frontend/gui.py
```

- Run backend server (development):

```bash
python backend/main.py
```

The app will accept PDF inputs, perform OCR + translation, and write translated PDFs to an output folder (see `utils/output_pdf_handler.py`).


## Architecture Overview

- OCR: `ppocrv5_onnx/` contains the OCR engine and model harness (`engine.py`, `ocr_engine.py`). It runs detection + recognition and outputs bounding boxes and text.
- Backend: `backend/` coordinates jobs and exposes API endpoints consumed by the GUI or CLI.
- Services: `services/` implements higher-level translation and PDF reflow logic.
- Utils: `utils/` includes helpers for PDF output, text extraction, and translation glue code.

This separation keeps model inference isolated from job orchestration and UI concerns.

## Configuration

- Runtime variables are collected in `runtime_variables.py`. Edit this file to adjust paths, API keys, or runtime settings.
- OCR config: `ppocrv5_onnx/config.yaml` and model `inference.yml` files control model input sizes and postprocessing.

## Troubleshooting

- If OCR quality is poor: verify correct model files are placed under `ppocrv5_onnx/models/` and check `ppocrv5_onnx/config.yaml` for preprocessing settings.
- If dependencies fail to install: upgrade `pip` and install common build tools (e.g., `wheel`, platform C-build tools) before installing packages.
- For large PDFs: increase memory or process pages in smaller batches.
- Make sure you have downloaded the translation model and at the correct location.ws

## Development Notes

- To rebuild a standalone executable, see the `run_app.spec` which is configured for `pyinstaller` in the `build/` output folder. Adjust the spec then run:

```bash
pyinstaller run_app.spec
```

## Contributing

Feel free to open issues or pull requests. Suggested contribution steps:

1. Fork the repo
2. Create a feature branch
3. Add tests for new functionality
4. Open a pull request describing the change

