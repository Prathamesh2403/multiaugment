import sys
import os
import random
import numpy as np

# Add FFmpeg to PATH before importing pydub so it finds the binaries
os.environ["PATH"] += r";C:\Users\ACER\Downloads\ffmpeg-7.1.1-essentials_build\ffmpeg-7.1.1-essentials_build\bin"

from pydub import AudioSegment
from pydub.generators import WhiteNoise

def _make_noise_segment(noise_type, duration_ms, frame_rate=44100, channels=1):
    """Generate white, pink, or brown noise as an AudioSegment using numpy."""
    n_samples = int(frame_rate * duration_ms / 1000)

    if noise_type == 'white':
        samples = np.random.uniform(-1, 1, n_samples)

    elif noise_type == 'pink':
        # Voss-McCartney pink noise algorithm
        num_rows = 16
        array = np.empty((n_samples, num_rows))
        array[:] = np.random.uniform(-1, 1, (n_samples, num_rows))
        # Only update each row at its own binary rate
        for col in range(num_rows):
            step = 2 ** col
            array[::step, col] = np.random.uniform(-1, 1, len(array[::step, col]))
        samples = array.sum(axis=1)
        samples /= num_rows  # normalise

    elif noise_type == 'brown':
        # Brown (Brownian / red) noise = cumulative sum of white noise
        white = np.random.uniform(-1, 1, n_samples)
        samples = np.cumsum(white)
        samples /= np.max(np.abs(samples))  # normalise to [-1, 1]

    else:
        raise ValueError("Invalid noise type")

    # Convert float [-1,1] → int16 and wrap in AudioSegment
    samples_int16 = (samples * 32767).astype(np.int16)
    raw_data = samples_int16.tobytes()
    return AudioSegment(
        data=raw_data,
        sample_width=2,       # 16-bit = 2 bytes
        frame_rate=frame_rate,
        channels=channels
    )

def add_noise(audio, noise_type, noise_level):
    duration_ms = len(audio)
    noise = _make_noise_segment(noise_type, duration_ms,
                                frame_rate=audio.frame_rate,
                                channels=audio.channels)
    # Adjust noise volume relative to the audio level
    noise = noise - (noise.dBFS - audio.dBFS - noise_level)
    return audio.overlay(noise)

def time_stretch(audio, rate):
    return audio._spawn(audio.raw_data, overrides={
        "frame_rate": int(audio.frame_rate * rate)
    }).set_frame_rate(audio.frame_rate)

def pitch_shift(audio, semitones):
    new_sample_rate = int(audio.frame_rate * (2 ** (semitones / 12)))
    return audio._spawn(audio.raw_data, overrides={
        "frame_rate": new_sample_rate
    }).set_frame_rate(audio.frame_rate)

def augment_audio(audio):
    augmentations = [
        lambda a: add_noise(a, random.choice(['white', 'pink', 'brown']), random.uniform(-20, -10)),
        lambda a: time_stretch(a, random.uniform(0.9, 1.1)),
        lambda a: pitch_shift(a, random.uniform(-2, 2))
    ]
    return random.choice(augmentations)(audio)

def main(input_folder, output_folder, num_augmentations):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for filename in os.listdir(input_folder):
        if filename.lower().endswith('.mp3'):
            input_path = os.path.join(input_folder, filename)
            audio = AudioSegment.from_mp3(input_path)
            
            output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_original.mp3")
            audio.export(output_path, format="mp3")
            
            for i in range(num_augmentations):
                augmented_audio = augment_audio(audio)
                output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_aug_{i+1}.mp3")
                augmented_audio.export(output_path, format="mp3")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python audio_augment.py <input folder> <output folder> <number of augmented samples per audio>")
        sys.exit(1)

    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
    num_augmentations = int(sys.argv[3])

    main(input_folder, output_folder, num_augmentations)