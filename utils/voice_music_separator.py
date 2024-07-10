import torch
import torchaudio
import os
from openunmix import predict
import numpy as np

class VoiceMusicSeparator:
    def __init__(self, output_dir='temp_audio'):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

    def process_file(self, audio_path):
        # Load audio file
        audio, sample_rate = torchaudio.load(audio_path)

        # Separate audio
        estimates = predict.separate(audio, rate=sample_rate, device=self.device)

        print(f"Estimate keys: {estimates.keys()}")
        print(f"Original audio shape: {audio.shape}")
        print(f"Vocals shape: {estimates['vocals'].shape}")

        # Get base filename without extension
        base_name = os.path.splitext(os.path.basename(audio_path))[0]

        # Define output paths
        voice_output_path = os.path.join(self.output_dir, f"{base_name}_voice.wav")
        music_output_path = os.path.join(self.output_dir, f"{base_name}_music.wav")

        # Prepare the audio for saving
        vocals = estimates['vocals'].squeeze().cpu().numpy()
        original_audio = audio.squeeze().cpu().numpy()

        # Ensure the lengths match
        min_length = min(vocals.shape[1], original_audio.shape[1])
        vocals = vocals[:, :min_length]
        original_audio = original_audio[:, :min_length]

        # Calculate the accompaniment
        accompaniment = original_audio - vocals

        # Ensure the audio is in the correct range
        vocals = np.clip(vocals, -1, 1)
        accompaniment = np.clip(accompaniment, -1, 1)

        # Convert to 16-bit PCM
        vocals = (vocals * 32767).astype(np.int16)
        accompaniment = (accompaniment * 32767).astype(np.int16)

        # Save separated audio
        torchaudio.save(voice_output_path, torch.from_numpy(vocals), sample_rate)
        torchaudio.save(music_output_path, torch.from_numpy(accompaniment), sample_rate)

        return voice_output_path, music_output_path

    def process_multiple_files(self, audio_files):
        results = []
        for audio_file in audio_files:
            voice_path, music_path = self.process_file(audio_file)
            results.append({
                'original': audio_file,
                'voice': voice_path,
                'music': music_path
            })
        return results


if __name__ == "__main__":
    # Usage example
    separator = VoiceMusicSeparator()

    # Single file
    # single_result = separator.process_file('temp_audio/glowing-horizons-electronic-music-201993.mp3')
    # single_result = separator.process_file('temp_audio/audio_example.mp3')
    single_result = separator.process_file('sample_songs/eterna-cancao-wav-12569.mp3')
    
    print(f"Single file result: {single_result}")

    # Multiple files
    # audio_files = [
    #     'path/to/your/audio_file1.wav',
    #     'path/to/your/audio_file2.wav',
    #     'path/to/your/audio_file3.wav'
    # ]
    # multiple_results = separator.process_multiple_files(audio_files)
    # for result in multiple_results:
    #     print(f"Original: {result['original']}")
    #     print(f"Voice output: {result['voice']}")
    #     print(f"Music output: {result['music']}")
    #     print("---")
