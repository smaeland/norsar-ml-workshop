import csv
import h5py
import numpy as np

def prep_signal_plus_noise(output_name, num_train_events=1000, num_test_events=100, vertical_only=False):

    # Collect the contents of the flippin csv files
    signal_traces = []
    errors = 0
    with open('chunk2.csv') as fin:

        header = fin.readline()

        for line in fin:
            
            if line.startswith(' '):        # TODO fix these overflow lines
                print('Skipping line:', line)
                continue

            row = line.strip().split(',')
            try:
                name, p_start, s_start, mag = row[-1], float(row[6]), float(row[10]), float(row[23])
            except ValueError:
                errors += 1
                continue

            signal_traces.append([name, p_start, s_start, mag])

    print(f'Signal file: {errors} errors')

    noise_traces = []
    with open('chunk1.csv') as fin:

        header = fin.readline()

        for line in fin:
            row = line.strip().split(',')
            name = row[-1]
            noise_traces.append([name, -1, -1, -1])


    # Read h5 files and randomly pick events
    fin_signal = h5py.File('chunk2.hdf5', 'r')
    data_signal = fin_signal.get('data')
    fin_noise = h5py.File('chunk1.hdf5', 'r')
    data_noise = fin_noise.get('data')

    num_events_total = num_train_events + num_test_events
    if (num_events_total) > 0.7 * (len(signal_traces) + len(noise_traces)):
        print()
        print('Unlikely to be enough events in files')
        print(f'(Asked for {num_events_total}, have {len(signal_traces) + len(noise_traces)})')
        print()

    data_out = []
    type_out = []
    p_start_out = []
    s_start_out = []
    mag_out = []
    errors = 0

    rng = np.random.default_rng(seed=42)

    while len(data_out) < num_events_total:

        type = rng.integers(0, 1, endpoint=True)

        if type == 0:
            name, p_start, s_start, mag = noise_traces.pop(0)
            data = data_noise.get(name)
            
            if data is None:
                errors += 1
            else:
                data = data[:]
                if vertical_only:
                    data = np.expand_dims(data[:, 2], axis=1)
                data_out.append(data)
                type_out.append(type)
                p_start_out.append(p_start)
                s_start_out.append(s_start)
                mag_out.append(mag)

        elif type == 1:
            name, p_start, s_start, mag = signal_traces.pop(0)
            data = data_signal.get(name)

            if data is None:
                errors += 1
            else:
                data = data[:]
                if vertical_only:
                    data = np.expand_dims(data[:, 2], axis=1)
                data_out.append(data)
                type_out.append(type)
                p_start_out.append(p_start)
                s_start_out.append(s_start)
                mag_out.append(mag)

        
        #print('name:', name, 'type:', type, 'p_start:', p_start, 's_start:', s_start, 'mag:', mag)

    print('Key errors:', errors)

    # Write train file
    train_file = output_name + '_TRAIN.h5'
    ftrain = h5py.File(train_file, 'w')
    ftrain.create_dataset('waveforms', data=np.stack(data_out[:num_train_events]), dtype=np.float32)
    ftrain.create_dataset('type', data=np.array(type_out[:num_train_events]), dtype=np.int8)
    ftrain.create_dataset('p_start', data=np.array(p_start_out[:num_train_events]), dtype=np.int16)
    ftrain.create_dataset('s_start', data=np.array(s_start_out[:num_train_events]), dtype=np.int16)
    ftrain.create_dataset('mag', data=np.array(mag_out[:num_train_events]), dtype=np.float16)
    ftrain.close()
    
    # Write test file 
    test_file = output_name + '_TEST.h5'
    ftest = h5py.File(test_file, 'w')
    ftest.create_dataset('waveforms', data=np.stack(data_out[num_train_events:]), dtype=np.float32)
    ftest.create_dataset('type', data=np.array(type_out[num_train_events:]), dtype=np.int8)
    ftest.create_dataset('p_start', data=np.array(p_start_out[num_train_events:]), dtype=np.int16)
    ftest.create_dataset('s_start', data=np.array(s_start_out[num_train_events:]), dtype=np.int16)
    ftest.create_dataset('mag', data=np.array(mag_out[num_train_events:]), dtype=np.float16)
    ftest.close()

    print(f'Output written to {train_file}, {test_file}')
    

def prep_signal(output_name, num_train_events=1000, num_test_events=100, vertical_only=False):

    signal_traces = []
    errors = 0
    with open('chunk2.csv') as fin:

        header = fin.readline()

        for line in fin:
            row = line.strip().split(',')
            try:
                name, p_start, s_start, mag = row[-1], float(row[6]), float(row[10]), float(row[23])
            except ValueError:
                errors += 1
                continue

            signal_traces.append([name, p_start, s_start, mag])

    print(f'Signal file: {errors} errors')


    # Read h5 files and randomly pick events
    fin_signal = h5py.File('chunk2.hdf5', 'r')
    data_signal = fin_signal.get('data')

    num_events_total = num_train_events + num_test_events
    if (num_events_total) > 0.7 * len(signal_traces):
        print()
        print('Unlikely to be enough events in files')
        print(f'(Asked for {num_events_total}, have {len(signal_traces)})')
        print()

    data_out = []
    type_out = []
    p_start_out = []
    s_start_out = []
    mag_out = []
    errors = 0


    while len(data_out) < num_events_total:

        name, p_start, s_start, mag = signal_traces.pop(0)
        data = data_signal.get(name)

        if data is None:
            errors += 1
        else:
            data = data[:]
            if vertical_only:
                data = np.expand_dims(data[:, 2], axis=1)
            data_out.append(data)
            p_start_out.append(p_start)
            s_start_out.append(s_start)
            mag_out.append(mag)

        
        #print('name:', name, 'type:', type, 'p_start:', p_start, 's_start:', s_start, 'mag:', mag)

    print('Key errors:', errors)

    # Write train file
    train_file = output_name + '_TRAIN.h5'
    ftrain = h5py.File(train_file, 'w')
    ftrain.create_dataset('waveforms', data=np.stack(data_out[:num_train_events]), dtype=np.float32)
    ftrain.create_dataset('p_start', data=np.array(p_start_out[:num_train_events]), dtype=np.int16)
    ftrain.create_dataset('s_start', data=np.array(s_start_out[:num_train_events]), dtype=np.int16)
    ftrain.create_dataset('mag', data=np.array(mag_out[:num_train_events]), dtype=np.float16)
    ftrain.close()
    
    # Write test file 
    test_file = output_name + '_TEST.h5'
    ftest = h5py.File(test_file, 'w')
    ftest.create_dataset('waveforms', data=np.stack(data_out[num_train_events:]), dtype=np.float32)
    ftest.create_dataset('p_start', data=np.array(p_start_out[num_train_events:]), dtype=np.int16)
    ftest.create_dataset('s_start', data=np.array(s_start_out[num_train_events:]), dtype=np.int16)
    ftest.create_dataset('mag', data=np.array(mag_out[num_train_events:]), dtype=np.float16)
    ftest.close()

    print(f'Output written to {train_file}, {test_file}')
    

if __name__ == '__main__':
    
    prep_signal_plus_noise('sample_events_Zonly', num_train_events=10, num_test_events=10, vertical_only=True)

    prep_signal_plus_noise('events_classification_Zonly', 100000, 10000, vertical_only=True)

    prep_signal('events_phases_Zonly', 100000, 10000, vertical_only=True)

#    pick_events('events_ENZ.h5', 100000, 10000, vertical_only=False)
