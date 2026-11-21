# NeuAug — How It Works

NeuAug is a **data augmentation toolkit** for machine learning. It solves the common problem of small datasets by generating synthetic variations of existing data across three modalities: **text (words)**, **images**, and **speech (audio)**. Each modality has its own standalone Python script in the `code/` directory.

---

## Project Structure

```
neuaug/
├── logo.png                        # Project logo
├── README.md                       # Quick-start usage guide
├── HOW_IT_WORKS.md                 # This file — detailed explanation
├── code/
│   ├── textaug.py                  # Word/text augmentation script
│   ├── imgaug.py                   # Image augmentation script
│   └── speechaug.py                # Audio/speech augmentation script
└── tests/
    ├── texttest/
    │   ├── words.txt               # Sample input words
    │   └── augwords.txt            # Example augmented output
    └── imgtest/
        ├── d1/                     # Sample input images + augwords.txt
        └── d2/                     # Example augmented image outputs
```

---

## 1. `code/textaug.py` — Word / Text Augmentation

### Purpose
Takes a plain-text file of words (one per line) and generates *N* augmented variants of each word, simulating real-world typos, spelling variations, and back-translation paraphrases. This is useful for training NLP models to be robust against spelling errors.

### How to run
```bash
python textaug.py <input_file.txt> <output_file.txt> <num_augmentations>
# Example:
python textaug.py tests/texttest/words.txt tests/texttest/augwords.txt 5
```

### Augmentation techniques (7 strategies, one picked randomly per augmentation)

| Function | What it does | Example (`apple`) |
|---|---|---|
| `shift_one_letter(word)` | Swaps two **adjacent** letters at a random position | `apple` → `aplpe` |
| `shift_two_letters(word)` | Rotates a window of **three** adjacent letters (shifts by 2) | `apple` → `palpe` |
| `exchange_two_letters(word)` | Swaps **any two** randomly chosen letters (non-adjacent OK) | `apple` → `elppa` |
| `exchange_one_letter(word)` | Replaces one letter with a **random a–z character** | `apple` → `ahple` |
| `double_letter(word)` | **Duplicates** one random letter | `apple` → `applee` |
| `remove_letter(word)` | **Deletes** one random letter | `apple` → `aple` |
| `translate_and_back(word)` | **Back-translation**: translates the word to a random language (French/German/Spanish/Italian/Portuguese) then back to English via `googletrans` | `artificial` → `artificial` (or a paraphrase) |

### Execution flow
```
main()
 ├── Read all words from input file into a list
 └── For each word:
      ├── Keep the original word (always included in output)
      └── Call augment_word() N times → appends N variants
          └── augment_word() randomly selects one of the 7 functions above
Write all words (originals + augmented) to output file
```

### Output format
The output file contains the original word followed immediately by its N augmented variants, then the next word, and so on:
```
apple
applee
ppale
aplpe
...
banana
anbana
...
```

### Dependencies
- `googletrans` — Google Translate API wrapper (for back-translation)
- `random`, `string` — standard library

---

## 2. `code/imgaug.py` — Image Augmentation

### Purpose
Takes a folder of JPG/JPEG images and produces *N* augmented copies of each, applying random combinations of visual transformations. This is used to artificially expand image datasets for computer vision models.

### How to run
```bash
python imgaug.py <input_folder> <output_folder> <num_copies>
# Example:
python imgaug.py tests/imgtest/d1 tests/imgtest/d2 5
```

### Augmentation techniques (7 strategies, 1–4 applied randomly per image)

| Transformation | What it does |
|---|---|
| **Gaussian Blur** | Blurs the image with a random radius between 0.5 and 1.5 |
| **Brightness adjust** | Scales brightness randomly between ×0.8 (darker) and ×1.2 (brighter) |
| **Contrast adjust** | Scales contrast randomly between ×0.8 and ×1.2 |
| **Add noise** | Adds per-pixel RGB noise of ±20 to simulate sensor grain |
| **Rotate 90 / 270°** | Rotates the image 90° clockwise or counter-clockwise randomly |
| **Mirror (flip)** | Horizontally flips the image left-to-right |
| **Shift** | Applies an affine translation of 20–30px horizontally and ±10px vertically |

> **Key design choice:** Unlike `textaug.py` (which picks *one* technique), `imgaug.py` stacks between **1 and 4 random augmentations** on each copy, producing richer and more diverse output.

### Execution flow
```
main()
 ├── Create output folder if it doesn't exist
 └── For each .jpg / .jpeg file in input folder:
      ├── Open image with PIL
      └── For i in range(num_copies):
           ├── Make a fresh copy of the original image
           ├── Call augment_image() → applies 1–4 random transforms
           └── Save as "<original_name>_aug_<i+1>.jpg"
```

### Helper functions
- `add_noise(image)` — iterates every pixel and adds random RGB noise, clamping to [0, 255]
- `mirror_image(image)` — thin wrapper around `PIL.Image.FLIP_LEFT_RIGHT`
- `shift_image(image, shift_x, shift_y)` — applies an AFFINE transform for translation

### Output naming
```
img 1.jpg  →  img 1_aug_1.jpg, img 1_aug_2.jpg, ..., img 1_aug_N.jpg
img 2.JPG  →  img 2_aug_1.jpg, img 2_aug_2.jpg, ..., img 2_aug_N.jpg
```

### Dependencies
- `Pillow (PIL)` — image I/O, filters, enhancements, transforms
- `random`, `os`, `sys` — standard library

---

## 3. `code/speechaug.py` — Speech / Audio Augmentation

### Purpose
Takes a folder of MP3 audio files and creates *N* augmented copies of each, applying random acoustic perturbations. Useful for training robust speech recognition or audio classification models.

### How to run
```bash
python speechaug.py <input_folder> <output_folder> <num_augmentations>
# Example:
python speechaug.py input_audio augmented_audio 5
```

### Augmentation techniques (3 strategies, one picked randomly per copy)

| Function | What it does | Parameters |
|---|---|---|
| `add_noise(audio, type, level)` | Overlays **white, pink, or brown noise** at a random dB level | noise level: −20 to −10 dBFS relative to signal |
| `time_stretch(audio, rate)` | **Speeds up or slows down** the audio by resampling the frame rate | rate: ×0.9 to ×1.1 (then resets to original sample rate) |
| `pitch_shift(audio, semitones)` | **Shifts the pitch** up or down by altering the sample rate | ±2 semitones |

> **Note on time_stretch & pitch_shift:** Both use pydub's `_spawn` trick — they temporarily change the declared `frame_rate` of the raw audio data (which changes playback speed/pitch), then re-encode at the original frame rate. This is a lightweight approach that avoids a full STFT-based resample.

### Noise types explained
- **White noise** — equal energy at all frequencies (harsh hiss)
- **Pink noise** — energy falls off at higher frequencies (softer, more natural)
- **Brown noise** — energy falls off even more steeply (deep rumble)

### Execution flow
```
main()
 ├── Create output folder if it doesn't exist
 └── For each .mp3 file in input folder:
      ├── Load audio with pydub
      ├── Save a clean copy as "<name>_original.mp3"
      └── For i in range(num_augmentations):
           ├── Call augment_audio() → applies one random augmentation
           └── Save as "<name>_aug_<i+1>.mp3"
```

> Unlike `imgaug.py`, `speechaug.py` also saves a copy of the **original audio** in the output folder (renamed `_original.mp3`), keeping everything in one place.

### Dependencies
- `pydub` — audio I/O and manipulation
- `pydub.generators` — `WhiteNoise`, `PinkNoise`, `BrownNoise` generators
- `numpy` — imported but not directly used (pydub depends on it internally)
- `random`, `os`, `sys` — standard library

---

## 4. Test Data (`tests/`)

### `tests/texttest/`
| File | Purpose |
|---|---|
| `words.txt` | 10 sample English words used as textaug input (apple, banana, fruits, waterfall, human, species, artificial, intelligence, neural, networks) |
| `augwords.txt` | Pre-generated output: each word followed by 5 augmented variants (60 lines total), showing the kinds of letter-swap/removal/duplication errors the tool produces |

### `tests/imgtest/`
| Path | Purpose |
|---|---|
| `d1/img 1.jpg`, `d1/img 2.JPG` | Sample input images fed to imgaug.py |
| `d1/augwords.txt` | Empty placeholder file (not used by imgaug.py) |
| `d2/img 1_aug_1.jpg` … `img 2_aug_5.jpg` | 10 pre-generated augmented images (5 per original), showing the visual diversity the tool produces |

---

## Design Philosophy

1. **Simplicity** — Each script is self-contained (~65–91 lines) with no shared library code, making them easy to drop into any project.
2. **Randomness** — All augmentations are random, so running the same script twice produces different outputs, maximising dataset diversity.
3. **Non-destructive** — Originals are never modified; all output goes to a separate file/folder.
4. **CLI-first** — All scripts are invoked from the command line with three arguments: input, output, count.

---

## Comparison Table

| Feature | `textaug.py` | `imgaug.py` | `speechaug.py` |
|---|---|---|---|
| Input format | `.txt` (one word per line) | Folder of `.jpg`/`.jpeg` | Folder of `.mp3` |
| Output format | `.txt` | Folder of `.jpg` | Folder of `.mp3` |
| # of techniques | 7 | 7 | 3 |
| Techniques applied per copy | 1 (random) | 1–4 (stacked) | 1 (random) |
| Saves original in output | ✅ (always first) | ❌ | ✅ (`_original.mp3`) |
| External API needed | ✅ (Google Translate) | ❌ | ❌ |
| Key dependency | `googletrans` | `Pillow` | `pydub` |
