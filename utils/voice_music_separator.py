import torch
import torchaudio
import os
from openunmix import predict
import numpy as np
import soundfile as sf


class VoiceMusicSeparator:
    def __init__(self, output_dir='temp_audio'):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

    def process_file(self, audio_path):
        try:
             # Use soundfile to read various audio formats
            audio, sample_rate = sf.read(audio_path)

            # If the audio is not mono, convert it to mono
            if len(audio.shape) > 1:
                audio = np.mean(audio, axis=1)

            # Convert to torch tensor
            audio = torch.FloatTensor(audio).unsqueeze(0)
            
            # Process in chunks to reduce memory usage
            chunk_size = 10 * sample_rate  # 10 seconds chunks
            num_chunks = audio.shape[1] // chunk_size + 1

            vocals = []
            accompaniment = []

            for i in range(num_chunks):
                start = i * chunk_size
                end = min((i + 1) * chunk_size, audio.shape[1])
                chunk = audio[:, start:end]

                # Separate audio
                estimates = predict.separate(chunk, rate=sample_rate, device=self.device)

                vocals.append(estimates['vocals'].squeeze().cpu().numpy())
                
                # Use 'other' if 'accompaniment' is not present
                if 'accompaniment' in estimates:
                    accompaniment.append(estimates['accompaniment'].squeeze().cpu().numpy())
                elif 'other' in estimates:
                    accompaniment.append(estimates['other'].squeeze().cpu().numpy())
                else:
                    raise KeyError("Neither 'accompaniment' nor 'other' key found in estimates")

            vocals = np.concatenate(vocals, axis=1)
            accompaniment = np.concatenate(accompaniment, axis=1)

            # Get base filename without extension
            base_name = os.path.splitext(os.path.basename(audio_path))[0]

            # Define output paths
            voice_output_path = os.path.join(self.output_dir, f"{base_name}_voice.wav")
            music_output_path = os.path.join(self.output_dir, f"{base_name}_music.wav")

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

        except Exception as e:
            print(f"Error processing file: {e}")
            return None, None


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
