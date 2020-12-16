import tensorflow as tf
from create_pretraining_data import *
import json
import re
from glob import glob
import random
import tokenization
import os

tokenizer = tokenization.FullTokenizer(
    vocab_file = 'BERT.wordpiece-vocab.txt', do_lower_case = False
)

os.system('mkdir tfrecord')


def loop(files):
    for file in files:
        output_files = f'tfrecord/bert-{os.path.split(file)[1]}.tfrecord'

        input_files = []
        for input_pattern in [file]:
            input_files.extend(tf.gfile.Glob(input_pattern))

        print('*** Reading from input files ***')
        for input_file in input_files:
            print(input_file)

        max_seq_length = 128
        dupe_factor = 5 if 'common-crawl' in file else 15
        max_predictions_per_seq = 20
        masked_lm_prob = 0.15
        short_seq_prob = 0.1
        rng = random.Random(12345)
        instances = create_training_instances(
            input_files,
            tokenizer,
            max_seq_length,
            dupe_factor,
            short_seq_prob,
            masked_lm_prob,
            max_predictions_per_seq,
            rng,
        )

        print('*** Writing to output files ***')
        for output_file in [output_files]:
            print('  %s', output_file)

        write_instance_to_example_files(
            instances,
            tokenizer,
            max_seq_length,
            max_predictions_per_seq,
            [output_file],
        )


files = glob('data/unlabeled*.csv')

from multiprocessing import Pool
import itertools


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i : i + n]


def multiprocessing(strings, function, cores = 10):
    df_split = chunks(strings, len(strings) // cores)
    pool = Pool(cores)
    pooled = pool.map(function, df_split)
    pool.close()
    pool.join()

cores = 4
if len(files) >= cores:
    multiprocessing(files, loop, cores)
else:
    loop(files)
