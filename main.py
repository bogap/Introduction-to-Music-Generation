from accompaniment_generator import *
from genetic_algo import *

midi_file = 'verse_melody.mid'

GA = GeneticAlgo(midi_file)
accomp = Accompaniment(midi_file, GA.chromosome_size)

accomp.generate_accomp()

