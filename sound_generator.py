import pygame
import numpy as np


class SoundGenerator:
    def __init__(self, sound_defs):
        self.sample_rate = 22050
        self.sounds = {}
        self.generate_all_sounds(sound_defs)

    def generate_waveform(self, freq, duration, waveform_type, volume=0.5):
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)

        if waveform_type == "square":
            wave = np.sign(np.sin(2 * np.pi * freq * t))
        elif waveform_type == "sawtooth":
            wave = 2 * (t * freq - np.floor(0.5 + t * freq))
        elif waveform_type == "triangle":
            wave = 2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - 1
        elif waveform_type == "noise":
            wave = np.random.uniform(-1, 1, len(t))
        else:  # sine
            wave = np.sin(2 * np.pi * freq * t)

        return wave * volume

    def generate_sweep(self, start_freq, end_freq, duration, waveform_type, volume):
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        freq = np.linspace(start_freq, end_freq, len(t))
        phase = 2 * np.pi * np.cumsum(freq) / self.sample_rate

        if waveform_type == "square":
            wave = np.sign(np.sin(phase))
        elif waveform_type == "sawtooth":
            wave = 2 * (phase / (2 * np.pi) - np.floor(0.5 + phase / (2 * np.pi)))
        else:
            wave = np.sin(phase)

        # Apply decay envelope
        envelope = np.linspace(1, 0, len(t))
        return wave * envelope * volume

    def generate_explosion(self, start_freq, end_freq, duration, volume):
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        freq = np.linspace(start_freq, end_freq, len(t))

        # Mix noise with frequency sweep
        noise = np.random.uniform(-1, 1, len(t))
        tone = np.sin(2 * np.pi * np.cumsum(freq) / self.sample_rate)
        wave = 0.7 * noise + 0.3 * tone

        # Apply decay envelope
        envelope = np.exp(-3 * t / duration)
        return wave * envelope * volume

    def generate_descending(self, notes, note_duration, waveform_type, volume):
        wave = np.array([])
        for note in notes:
            note_wave = self.generate_waveform(note, note_duration, waveform_type, volume)
            # Add decay to each note
            envelope = np.linspace(1, 0.3, len(note_wave))
            wave = np.concatenate([wave, note_wave * envelope])
        return wave

    def generate_noise_decay(self, freq, duration, waveform_type, volume):
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)

        if waveform_type == "square":
            wave = np.sign(np.sin(2 * np.pi * freq * t))
        else:
            wave = np.sin(2 * np.pi * freq * t)

        # Add noise component
        noise = np.random.uniform(-0.3, 0.3, len(t))
        wave = wave + noise

        # Apply sharp decay
        envelope = np.exp(-10 * t / duration)
        return wave * envelope * volume

    def wave_to_sound(self, wave):
        # Normalize and convert to 16-bit integers
        wave = np.clip(wave, -1, 1)
        wave = (wave * 32767).astype(np.int16)

        # Create stereo by duplicating mono channel
        stereo_wave = np.column_stack((wave, wave))

        sound = pygame.sndarray.make_sound(stereo_wave)
        return sound

    def generate_all_sounds(self, sound_defs):
        for name, params in sound_defs.items():
            sound_type = params.get("type", "sweep")
            volume = params.get("volume", 0.5)
            waveform = params.get("waveform", "square")

            if sound_type == "sweep":
                wave = self.generate_sweep(
                    params["start_freq"],
                    params["end_freq"],
                    params["duration"],
                    waveform,
                    volume
                )
            elif sound_type == "explosion":
                wave = self.generate_explosion(
                    params["start_freq"],
                    params["end_freq"],
                    params["duration"],
                    volume
                )
            elif sound_type == "descending":
                wave = self.generate_descending(
                    params["notes"],
                    params["note_duration"],
                    waveform,
                    volume
                )
            elif sound_type == "noise_decay":
                wave = self.generate_noise_decay(
                    params["freq"],
                    params["duration"],
                    waveform,
                    volume
                )
            else:
                wave = self.generate_waveform(
                    params.get("freq", 440),
                    params.get("duration", 0.1),
                    waveform,
                    volume
                )

            self.sounds[name] = self.wave_to_sound(wave)

    def play(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
