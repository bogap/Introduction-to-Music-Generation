from mido import Message, MidiFile, MidiTrack, MetaMessage
from random import choice
import numpy as np


def check_note_pitch(note):
    """
    For a melody I chose 3-5 piano octaves.
    In midi notes it is in (47, 84) interval.
    So, method returns a midi note in this interval.

    :return: appropriate midi note
    """
    while note >= 84:
        note -= 12
    while note <= 47:
        note += 12
    return note

# num = 2
#
# def get_melody_per_chord(melody):
#     n_notes = {}
#     track = melody.tracks[0]
#     cct = melody.ticks_per_beat * num
#     chord_change_time = cct
#     a = 0
#     n_notes[a] = []
#     for msg in track:
#         if msg.type == 'note_off':
#             if chord_change_time == 0:
#                 chord_change_time = cct
#                 a += 1
#                 n_notes[a] = []
#             if msg.time <= chord_change_time:
#                 chord_change_time -= msg.time
#                 n_notes[a].append(msg.note)
#             else:
#                 note_time = msg.time
#                 while note_time >= chord_change_time:
#                     note_time -= chord_change_time
#                     chord_change_time = cct
#                     n_notes[a].append(msg.note)
#                     a += 1
#                     n_notes[a] = []
#                 if note_time != 0:
#                     chord_change_time -= note_time
#                     n_notes[a].append(msg.note)
#     print(n_notes)
#     return n_notes


class Melody:

    def __init__(self, midi_file_path):
        self.melody_duration = 0
        self.orig_midi = MidiFile(midi_file_path, clip=True)

        self.melody_midi = MidiFile()
        self.track = MidiTrack()
        self.melody_midi.tracks.append(self.track)

        self.orig_notes = []
        self.markov_chain = {}
        self.melody_notes = []
        self.num_notes = 16

        # Add time signature and tempo variables
        self.time_signature = (4, 4)  # Default 4/4 time signature
        # self.tempo_value = self.num_notes * 14

        # Add note durations and their probabilities
        self.note_durations = {
            120: 0.1,
            240: 0.4,
            480: 0.4,
            960: 0.1,
        }

    def define_orig_notes(self):
        """
        Method fills list of notes with midi values of Megalovania melody.

        :return: None
        """
        for note in self.orig_midi.tracks[1]:
            if note.type == 'note_on':
                self.orig_notes.append(note.note)

    def create_markov_chain(self):
        """
        Method creates a first-order Markov chain based on the midi notes
        from Megalovania melody.

        :return: dictionary Markov chain
        """
        for i in range(len(self.orig_notes) - 1):
            current_note = self.orig_notes[i]
            next_note = self.orig_notes[i + 1]
            if self.markov_chain.get(current_note, 0) == 0:
                self.markov_chain[current_note] = [next_note]
            else:
                self.markov_chain[current_note].append(next_note)

        # # Prevent consecutive identical notes
        # for key, value in self.markov_chain.items():
        #     if key in value:
        #         value.remove(key)

        return self.markov_chain

    def generate_melody_notes(self):
        """
        Method generates sequence of midi notes for melody based on
        statistical data from created Markov chain.

        :return: list of midi notes of generated melody
        """

        current_note = choice(list(self.markov_chain.keys()))
        for _ in range(self.num_notes):
            self.melody_notes.append(current_note)
            next_notes = self.markov_chain.get(current_note)
            last_note = current_note
            if next_notes:
                current_note = check_note_pitch(choice(next_notes))
                while abs(current_note - last_note) < 2 or abs(current_note - last_note) > 24:
                    current_note = check_note_pitch(choice(next_notes))
            else:
                current_note = check_note_pitch(choice(list(self.markov_chain.keys())))
                while abs(current_note - last_note) < 2 or abs(current_note - last_note) > 24:
                    current_note = check_note_pitch(choice(list(self.markov_chain.keys())))

        return self.melody_notes

    def create_midi(self):
        """
        Method creates a midi file from list of midi notes.

        :return: None
        """
        # Set time signature and tempo messages in the MIDI file
        self.track.append(
            MetaMessage('time_signature', numerator=self.time_signature[0], denominator=self.time_signature[1], time=0))
        # self.track.append(MetaMessage('set_tempo', tempo=self.tempo_value, time=0))
        melody_duration = 0

        for note in self.melody_notes:
            note_duration = np.random.choice(list(self.note_durations.keys()), p=list(self.note_durations.values()))

            # Calculate the duration in ticks based on the tempo and note duration
            ticks_per_beat = self.melody_midi.ticks_per_beat
            duration_ticks = int(note_duration)  # 4 is the default duration for quarter notes

            self.track.append(Message('note_on', note=note, velocity=127, time=0))
            self.track.append(Message('note_off', note=note, velocity=127, time=duration_ticks))
            melody_duration += duration_ticks

        self.melody_midi.save("verse_melody.mid")
        # print(melody_duration)
        val = melody_duration % 960
        # print(val)
        melody_duration -= melody_duration % 960
        return val

    def melody_time(self):
        """
        Method returns duration of a generated melody.

        :return: melody duration
        """
        time = 0
        for note in self.melody_midi.tracks[0]:
            if note.type == 'note_on' or note.type == 'note_off':
                time += note.time
        return time

    def generate(self):
        self.define_orig_notes()
        self.create_markov_chain()
        self.generate_melody_notes()
        value = self.create_midi()
        return value


value = 1
while value != 0:
    melody = Melody('rivers_flow_in_you.mid')
    value = melody.generate()

