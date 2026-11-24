# multiaugment

<p align="center">
  A lightweight, multi-modal data augmentation toolkit for machine learning.<br>
  Generate synthetic variations of your <strong>text</strong>, <strong>images</strong>, and <strong>audio</strong> datasets — from the command line.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.6+-blue.svg" alt="Python 3.6+"/>
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT License"/>
  <img src="https://img.shields.io/badge/modalities-text%20•%20image%20•%20audio-orange" alt="Modalities"/>
</p>

---

## What is multiaugment?

Small datasets are one of the biggest bottlenecks in ML. **multiaugment** solves this by automatically generating diverse, augmented copies of your existing data across three modalities:

| Module | Input | Augmentation techniques |
|---|---|---|
| `textaug.py` | `.txt` word list | Letter swaps, deletions, doublings, random substitution, back-translation |
| `imgaug.py` | Folder of JPEGs | Blur, brightness, contrast, noise, rotation, mirror, affine shift |
| `speechaug.py` | Folder of MP3s | White/pink/brown noise, time-stretch, pitch shift |

---

## Requirements

- Python 3.6+
- [FFmpeg](https://ffmpeg.org/download.html) installed and on your PATH *(required for audio augmentation only)*

---

## Installation

Clone the repository and install dependencies into a virtual environment:

```bash
git clone https://github.com/<your-username>/multiaugment.git
cd multiaugment

# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Usage

### 📝 Text Augmentation

Augments a plain-text word list by generating *N* variants of each word using random character-level mutations and back-translation.

```bash
python code/textaug.py <input_file.txt> <output_file.txt> <num_augmentations>
```

**Example:**
```bash
python code/textaug.py tests/texttest/words.txt tests/texttest/augwords.txt 5
```

This will:
1. Read each word from `words.txt`
2. Generate **5 augmented variants** per word
3. Write original + augmented words to `augwords.txt`

**Input (`words.txt`):**
```
apple
banana
neural
```

**Output (`augwords.txt`):**
```
apple
applee
aplpe
aple
ppale
ahple
banana
anbana
...
```

---

### 🖼️ Image Augmentation

Generates *N* augmented copies of every JPEG image in a folder, applying 1–4 stacked random transformations per copy.

```bash
python code/imgaug.py <input_folder> <output_folder> <num_copies>
```

**Example:**
```bash
python code/imgaug.py tests/imgtest/d1 tests/imgtest/d2 5
```

This will:
1. Read all `.jpg` / `.jpeg` images from `d1/`
2. Create **5 augmented copies** of each image
3. Save them to `d2/` as `<original_name>_aug_1.jpg`, `_aug_2.jpg`, ...

**Augmentation techniques applied (randomly stacked):**
- Gaussian blur
- Brightness / contrast adjustment
- Per-pixel RGB noise
- 90° / 270° rotation
- Horizontal mirror
- Affine translation

---

### 🎵 Audio Augmentation

Generates *N* augmented copies of every MP3 file in a folder, each with a randomly applied acoustic perturbation.

```bash
python code/speechaug.py <input_folder> <output_folder> <num_augmentations>
```

**Example:**
```bash
python code/speechaug.py tests/speechtest/input tests/speechtest/output 5
```

This will:
1. Read all `.mp3` files from the input folder
2. Save a clean `_original.mp3` copy
3. Generate **5 augmented variants** per file using noise overlay, time-stretch, or pitch shift

**Augmentation techniques (one applied per copy):**
- White / pink / brown noise overlay
- Time stretch (±10% speed)
- Pitch shift (±2 semitones)

> **Note:** FFmpeg must be installed for audio augmentation to work.
> ```bash
> # Windows (winget)
> winget install FFmpeg
>
> # macOS (Homebrew)
> brew install ffmpeg
>
> # Linux (apt)
> sudo apt install ffmpeg
> ```

---

## Dependencies

| Package | Used by | Purpose |
|---|---|---|
| `Pillow` | `imgaug.py` | Image I/O, filters, transforms |
| `googletrans==4.0.0rc1` | `textaug.py` | Back-translation augmentation |
| `pydub` | `speechaug.py` | Audio I/O and manipulation |
| `numpy` | `speechaug.py` | Noise generation |

---

## License

MIT License — free to use, modify, and distribute.
