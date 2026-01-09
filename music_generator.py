import pygame
import numpy as np
import json
import threading


class MusicGenerator:
    def __init__(self, music_file):
        self.sample_rate = 22050
        self.current_track = None
        self.is_playing = False
        self.tracks = {}
        self.note_frequencies = {}

        # Load music definitions
        with open(music_file, 'r') as f:
            data = json.load(f)
            self.tracks = data.get('tracks', {})
            self.note_frequencies = data.get('note_frequencies', {})

        # Pre-generate all tracks
        self.generated_tracks = {}
        for track_name in self.tracks:
            self.generated_tracks[track_name] = self._generate_track(track_name)

    def _generate_waveform(self, freq, duration, waveform_type, volume=0.5):
        """Generate a waveform for a single note"""
        num_samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, num_samples, False)

        if freq == 0:  # REST
            return np.zeros(num_samples)

        if waveform_type == "square":
            wave = np.sign(np.sin(2 * np.pi * freq * t))
        elif waveform_type == "triangle":
            wave = 2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - 1
        elif waveform_type == "sawtooth":
            wave = 2 * (t * freq - np.floor(0.5 + t * freq))
        elif waveform_type == "noise":
            wave = np.random.uniform(-1, 1, num_samples)
        else:  # sine
            wave = np.sin(2 * np.pi * freq * t)

        # Apply envelope (attack-decay-sustain-release)
        envelope = np.ones(num_samples)
        attack = min(int(0.01 * self.sample_rate), num_samples // 4)
        release = min(int(0.02 * self.sample_rate), num_samples // 4)

        if attack > 0:
            envelope[:attack] = np.linspace(0, 1, attack)
        if release > 0:
            envelope[-release:] = np.linspace(1, 0, release)

        return wave * envelope * volume

    def _generate_channel(self, channel_data, tempo):
        """Generate audio for a single channel"""
        waveform_type = channel_data.get('waveform', 'square')
        volume = channel_data.get('volume', 0.3)
        notes = channel_data.get('notes', [])

        # Calculate beat duration from tempo
        beat_duration = 60.0 / tempo

        channel_audio = np.array([])

        for note_data in notes:
            note_name = note_data.get('note', 'REST')
            duration_beats = note_data.get('duration', 0.25)
            duration_seconds = duration_beats * beat_duration

            freq = self.note_frequencies.get(note_name, 0)
            note_wave = self._generate_waveform(freq, duration_seconds, waveform_type, volume)
            channel_audio = np.concatenate([channel_audio, note_wave])

        return channel_audio

    def _generate_track(self, track_name):
        """Generate complete audio for a track by mixing all channels"""
        if track_name not in self.tracks:
            return None

        track_data = self.tracks[track_name]
        tempo = track_data.get('tempo', 120)
        channels = track_data.get('channels', [])

        if not channels:
            return None

        # Generate all channels
        channel_audios = []
        max_length = 0

        for channel in channels:
            audio = self._generate_channel(channel, tempo)
            channel_audios.append(audio)
            max_length = max(max_length, len(audio))

        # Pad channels to same length and mix
        mixed = np.zeros(max_length)
        for audio in channel_audios:
            padded = np.zeros(max_length)
            padded[:len(audio)] = audio
            mixed += padded

        # Normalize to prevent clipping
        max_val = np.max(np.abs(mixed))
        if max_val > 0:
            mixed = mixed / max_val * 0.7

        # Convert to 16-bit stereo
        mixed = np.clip(mixed, -1, 1)
        mixed = (mixed * 32767).astype(np.int16)
        stereo = np.column_stack((mixed, mixed))

        return stereo

    def play(self, track_name, loop=True):
        """Play a music track"""
        if track_name not in self.generated_tracks:
            return

        # Stop current music
        self.stop()

        track_data = self.tracks.get(track_name, {})
        should_loop = track_data.get('loop', loop)

        audio_data = self.generated_tracks[track_name]
        if audio_data is None:
            return

        # Create pygame sound and play
        sound = pygame.sndarray.make_sound(audio_data)

        loops = -1 if should_loop else 0
        self.current_channel = sound.play(loops=loops)
        self.current_track = track_name
        self.is_playing = True

    def stop(self):
        """Stop current music"""
        pygame.mixer.stop()
        self.is_playing = False
        self.current_track = None

    def pause(self):
        """Pause current music"""
        pygame.mixer.pause()
        self.is_playing = False

    def unpause(self):
        """Unpause music"""
        pygame.mixer.unpause()
        self.is_playing = True

    def set_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        # Volume is applied at generation time, this affects the mixer
        pygame.mixer.music.set_volume(volume)

    def get_current_track(self):
        """Get name of currently playing track"""
        return self.current_track

    def is_track_playing(self, track_name):
        """Check if a specific track is playing"""
        return self.current_track == track_name and self.is_playing
