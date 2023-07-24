import random
from mido import MidiFile, Message, MidiTrack

num = 2


def define_chord(midi_note, chords):
    """
    Returns the chord corresponding to the given MIDI note.

    Args:
        midi_note (int): The MIDI note value.
        chords (dict): A dictionary mapping note numbers to chord names.

    Returns:
        str: The chord corresponding to the MIDI note.
    """
    note = midi_note % 12
    return chords.get(note)


def define_note(chord, chords):
    """
    Returns the MIDI note corresponding to the given chord.

    Args:
        chord (str): The chord name.
        chords (dict): A dictionary mapping note numbers to chord names.

    Returns:
        int: The MIDI note corresponding to the chord.
    """
    for cur_note, cur_chord in chords.items():
        if cur_chord == chord:
            return cur_note


CHORDS = {0: 'C', 1: 'C#', 2: 'D', 3: 'D#', 4: 'E', 5: 'F', 6: 'F#', 7: 'G', 8: 'G#', 9: 'A', 10: 'A#', 11: 'B'}
POSSIBLE_CHORDS = []
for i in range(24, 96):
    POSSIBLE_CHORDS.append((i, define_chord(i, CHORDS), [i, i + 4, i + 7]))
    POSSIBLE_CHORDS.append((i, define_chord(i, CHORDS) + 'm', [i, i + 3, i + 7]))


def get_melody_per_chord(melody):
    """
    Divides the melody into arrays that are played on top of each chord.
    Chord duration is the length of each bar, divided by 2.

    Args:
        melody (MidiFile): The melody, to which accompaniment is generated.

    Returns:
        list: list of arrays of midi note values
    """
    n_notes = {}
    track = melody.tracks[0]
    cct = melody.ticks_per_beat * num
    chord_change_time = cct
    a = 0
    n_notes[a] = []
    for msg in track:
        if msg.type == 'note_off':
            if chord_change_time == 0:
                chord_change_time = cct
                a += 1
                n_notes[a] = []
            if msg.time <= chord_change_time:
                chord_change_time -= msg.time
                n_notes[a].append(msg.note)
            else:
                note_time = msg.time
                while note_time >= chord_change_time:
                    note_time -= chord_change_time
                    chord_change_time = cct
                    n_notes[a].append(msg.note)
                    a += 1
                    n_notes[a] = []
                if note_time != 0:
                    chord_change_time -= note_time
                    n_notes[a].append(msg.note)
    print(n_notes)
    return n_notes


def chords_position(chromosome):
    """
    Calculates the value for fitness function. Adjacent notes in progression
    should not place from each other further than an octave and should not be
    adjacent on the piano.

    Args:
        chromosome (list): The chromosome representing a chord progression.

    Returns:
        float: value
    """
    value = 0
    overall = 0
    for i in range(len(chromosome) - 1):
        if 1 < abs(chromosome[i][0] - chromosome[i + 1][0]) < 12:
            value += 20
        overall += 1
    return value / overall


def chords_belong_to_good_ones(chromosome, good_chords):
    """
    Calculates the value for fitness function.
    It is preferable that chord belongs to the good_chords list.

    Args:
        chromosome (list): The chromosome representing a chord progression.
        good_chords (list): The list of chords considered good.

    Returns:
        float: value
    """
    value = 0
    overall = 0
    for gene in chromosome:
        if gene in good_chords:
            value += 20
        overall += 1
    return value / overall


def chords_belong_to_interval(chromosome, melody):
    """
    Calculates the value for fitness function.
    It is preferable that chord belongs to the interval on the piano.
    Note - lowest of the notes, that are played overtop the cord.
    Interval - from (note - 2.5 octaves) to (note - 0.5 octave).

    Args:
        chromosome (list): The chromosome representing a chord progression.
        melody (list): melody, divided by chords.

    Returns:
        float: value
    """
    value = 0
    overall = 0

    for i in range(len(chromosome)):
        note = min(melody[i])
        if note - 30 <= chromosome[i][0] <= note - 6:
            value += 20
        overall += 1
    return value / overall


def chords_dont_clash_with_melody(chromosome, melody):
    """
    Calculates the value for fitness function.
    It is preferable that the notes, played overtop each chord,
    are present in the chord.

    Args:
        chromosome (list): The chromosome representing a chord progression.
        melody (list): melody, divided by chords.

    Returns:
        float: value
    """
    value = 0
    overall = len(chromosome)
    for i in range(len(chromosome)):
        value_per_chord = 0
        notes = melody[i]
        for j in range(len(notes)):
            a = int(notes[j]) % 12
            b = [int(x) % 12 for x in chromosome[i][2]]
            if a in b:
                value_per_chord += 20
        value += value_per_chord / len(notes)
    return value / overall


def fitness_function(chromosome, good_chords, melody_by_chords):
    """
    Calculates the fitness value of a chromosome based on the given criteria.

    Args:
        chromosome (list): The chromosome representing a chord progression.
        good_chords (list): The list of chords considered good.
        melody_by_chords (list): melody, divided by chords.

    Returns:
        float: The fitness value of the chromosome.
    """
    w1 = 1
    w2 = 1
    w3 = 1
    w4 = 1.5
    res_1 = w1 * chords_position(chromosome)
    res_2 = w2 * chords_belong_to_good_ones(chromosome, good_chords)
    res_3 = w3 * chords_belong_to_interval(chromosome, melody_by_chords)
    res_4 = w4 * chords_dont_clash_with_melody(chromosome, melody_by_chords)
    res = res_1 + res_2 + res_3 + res_4
    return res


def crossover(chromosome1, chromosome2):
    """
    Performs crossover between two chromosomes.

    Args:
        chromosome1 (list): The first chromosome.
        chromosome2 (list): The second chromosome.

    Returns:
        list: The child chromosome produced by crossover.
    """
    point = random.randint(1, len(chromosome1) - 1)
    child = chromosome1[:point] + chromosome2[point:]
    return child


def get_temp(midi):
    """
    Gets the tempo of the melody.

    Args:
        midi (MidiFile): The melody.

    Returns:
        int: The temp of the song (in microseconds per beat).
    """
    temp = 500000
    for track in midi.tracks:
        for msg in track:
            if msg.type == 'set_tempo':
                temp = msg.tempo
                break
    return temp


def get_n_chords(midi):
    """
    Gets the number of beats.

    Args:
        midi (MidiFile): The melody.

    Returns:
        int: The length of the song in microseconds, divided by tempo.
    """
    return int(midi.length * 10 ** 6 // get_temp(midi))


class GeneticAlgo:
    """
    Class representing the Genetic Algorithm for accompaniment generation.
    """

    def __init__(self, midi_file):
        """
        Initializes the GeneticAlgo object.

        Args:
            midi_file (str): The MIDI file name.
        """
        self.population_size = 150
        self.num_generations = 300
        self.elite_size = 25
        self.mutation_rate = 0.001

        self.midi_origin = MidiFile(midi_file)
        # self.chromosome_size = get_n_chords(self.midi_origin) // num
        self.melody_by_chords = get_melody_per_chord(self.midi_origin)
        self.chromosome_size = len(self.melody_by_chords)

    def generate_chromosome(self):
        """
        Generates a random chromosome.

        Returns:
            list: A randomly generated chromosome.
        """
        chromosome = []
        for _ in range(self.chromosome_size):
            gene = random.choice(POSSIBLE_CHORDS)
            chromosome.append(gene)
        return chromosome

    def generate_population(self):
        """
        Generates a population of chromosomes.

        Returns:
            list: A list of randomly generated chromosomes.
        """
        population = []
        for _ in range(self.population_size):
            population.append(self.generate_chromosome())
        return population

    def mutate(self, child):
        """
        Applies mutation to a chromosome.

        Args:
            child (list): The chromosome to be mutated.

        Returns:
            list: The mutated chromosome.
        """
        for i in range(len(child)):
            if random.random() < self.mutation_rate:
                child[i] = random.choice(POSSIBLE_CHORDS)
        return child

    def create_next_generation(self, population, good_chords):
        """
        Creates the next generation of chromosomes based on the current population.

        Args:
            population (list): The current population of chromosomes.
            good_chords (list): The list of chords considered good.

        Returns:
            list: The next generation of chromosomes.
        """
        next_generation = []
        elite = sorted(population, key=lambda x: fitness_function(x, good_chords, self.melody_by_chords), reverse=True)[
                :self.elite_size]
        next_generation.extend(elite)

        while len(next_generation) < len(population):
            chromosome1, chromosome2 = random.choices(population, k=2)
            child = crossover(chromosome1, chromosome2)
            child = self.mutate(child)
            next_generation.append(child)

        return next_generation

    def genetic_algorithm(self, good_chords):
        """
        Runs the genetic algorithm to generate the best chord progression (accompaniment) to the melody.

        Args:
            good_chords (list): The list of chords considered good.

        Returns:
            list: The best chord progression generated by the genetic algorithm.
        """
        population = self.generate_population()

        for generation in range(self.num_generations):
            best_chromosome = max(population, key=lambda x: fitness_function(x, good_chords, self.melody_by_chords))
            print(
                f"Generation: {generation + 1}, Best Fitness: {fitness_function(best_chromosome, good_chords, self.melody_by_chords)}")
            population = self.create_next_generation(population, good_chords)

        best_chromosome = max(population, key=lambda x: fitness_function(x, good_chords, self.melody_by_chords))
        print(f"Best Individual: {best_chromosome}")
        print(f"Best Fitness: {fitness_function(best_chromosome, good_chords, self.melody_by_chords)}")
        return best_chromosome
