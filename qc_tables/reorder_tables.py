#!/usr/bin/env python3

import sys
sys.path.insert(0,'../')

from qc_level2 import get_qc_table

# quick hacky script that uses the read function get_qc_table()
# to create a dataframe and then write it again!

def main(): # the main data crunching program


    tables = ['qc_table_asfs30.csv','qc_table_asfs40.csv', 'qc_table_asfs50.csv','qc_table_tower.csv']

    for table in tables: 
        with open(table) as table_file:
            table_header = [table_file.readline() for iline in range(0,6)]
        t = get_qc_table(table).sort_values('qc_val')
        #t['qc_val'].astype('int32', copy=False) # not necessary

        t.to_csv(f'{table}.new', date_format='%Y%m%d %H%M%S', index=False, header=None) # add our own header
        with open(f'{table}.new', 'r+') as table_file:
            content = table_file.read()
            table_file.seek(0)
            table_file.write(''.join(table_header) + content)

# this runs the function main as the main program... this is a hack that allows functions
# to come after the main code so it presents in a more logical, C-like, way
if __name__ == '__main__':
    main()

