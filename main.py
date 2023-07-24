from accompaniment_generator import *
from genetic_algo import *
from chorus_generator import *
from melody_generator import *


value = 1
while value != 0:
    melody = Melody('rivers_flow_in_you.mid')
    value = melody.generate()


midi_file = 'verse_melody.mid'
GA = GeneticAlgo(midi_file)
accomp = Accompaniment(midi_file, GA.chromosome_size)
midi = accomp.generate_accomp()


midi = generate_chorus('rivers_flow_in_you.mid', midi)

