import argparse
import os
import pandas as pd


# arguments: sourmash_gather_file, alternate_gather_file
def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('sourmash_gather_file')
    p.add_argument('alternate_gather_file')
    return p.parse_args()

def main():
    args = parse_args()

    try:
        df_sourmash_gather = pd.read_csv(args.sourmash_gather_file).set_index('md5')
    except:
        df_sourmash_gather = pd.read_csv(args.sourmash_gather_file).set_index('match_md5')

    df_alternate_gather = pd.read_csv(args.alternate_gather_file).set_index('md5')

    sourmash_gather_md5s_list = df_sourmash_gather.index.tolist()
    alternate_gather_md5s_list = df_alternate_gather.index.tolist()

    for i in range(len(sourmash_gather_md5s_list)):
        if sourmash_gather_md5s_list[i] != alternate_gather_md5s_list[i]:
            print(f"First md5s different at index {i}")
            print(f"sourmash gather md5: {sourmash_gather_md5s_list[i]}")
            print(f"alternate gather md5: {alternate_gather_md5s_list[i]}")
            print('--------')

            # show next five md5s
            print('next five md5s')
            for j in range(i+1, i+6):
                print(f"sourmash gather md5: {sourmash_gather_md5s_list[j]}")
                print(f"alternate gather md5: {alternate_gather_md5s_list[j]}")
                print('--------')

            break

    sourmash_gather_md5s = set(df_sourmash_gather.index)
    alternate_gather_md5s = set(df_alternate_gather.index)
    commond_md5s = sourmash_gather_md5s & alternate_gather_md5s



    # show some stats
    print(f"Number of md5s in sourmash gather: {len(sourmash_gather_md5s)}")
    print(f"Number of md5s in alternate gather: {len(alternate_gather_md5s)}")
    print(f"Number of md5s in sourmash gather but not in alternate gather: {len(sourmash_gather_md5s - alternate_gather_md5s)}")
    print(f"Number of md5s in alternate gather but not in sourmash gather: {len(alternate_gather_md5s - sourmash_gather_md5s)}")
    print(f"Number of md5s in both sourmash gather and alternate gather: {len(sourmash_gather_md5s & alternate_gather_md5s)}")

    # for every md5 in common, test that the relevant columns are the same
    for md5 in commond_md5s:
        sourmash_gather_row = df_sourmash_gather.loc[md5]
        alternate_gather_row = df_alternate_gather.loc[md5]

        # test sourmash_gather_row's intersect_bp is the same as alternate_gather_row's num_overlap_orig
        try:
            assert sourmash_gather_row['intersect_bp'] == alternate_gather_row['num_overlap_orig']*1000
            assert abs(sourmash_gather_row['f_orig_query'] - alternate_gather_row['f_orig_query']) < 0.0001
            #assert abs(sourmash_gather_row['f_match'] - alternate_gather_row['f_match']) < 0.0001
            assert abs(sourmash_gather_row['f_unique_to_query'] - alternate_gather_row['f_unique_query']) < 0.0001
            assert abs(sourmash_gather_row['f_unique_weighted'] - alternate_gather_row['f_weighted_query']) < 0.0001
        except AssertionError:
            print(f"md5 {md5} has different values in sourmash gather and alternate gather")
            print(f"sourmash gather row: {sourmash_gather_row}")
            print(f"alternate gather row: {alternate_gather_row}")
            print('--------')
            continue
    
    # for the md5s in sourmash gather but not in alternate gather, compute the sum of f_unique_weighted
    total_f_unique_weighted = 0
    for md5 in sourmash_gather_md5s - alternate_gather_md5s:
        sourmash_gather_row = df_sourmash_gather.loc[md5]
        total_f_unique_weighted += sourmash_gather_row['f_unique_weighted']

    print(f"Total f_unique_weighted for md5s in sourmash gather but not in alternate gather: {total_f_unique_weighted}")

    # for the md5s in alternate gather but not in sourmash gather, compute the sum of f_weighted_query
    total_f_weighted_query = 0
    for md5 in alternate_gather_md5s - sourmash_gather_md5s:
        alternate_gather_row = df_alternate_gather.loc[md5]
        total_f_weighted_query += alternate_gather_row['f_weighted_query']

    print(f"Total f_weighted_query for md5s in alternate gather but not in sourmash gather: {total_f_weighted_query}")

    # for the md5s in both sourmash gather and alternate gather, compute the sum of f_unique_weighted
    total_f_unique_weighted = 0
    for md5 in commond_md5s:
        sourmash_gather_row = df_sourmash_gather.loc[md5]
        total_f_unique_weighted += sourmash_gather_row['f_unique_weighted']

    print(f"Total f_unique_weighted for md5s in both sourmash gather and alternate gather: {total_f_unique_weighted}")

if __name__ == '__main__':
    main()