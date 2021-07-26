import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def matching(df):
    df = df.fillna(0)
    df_copy = df.copy()

    df_interests = df.iloc[:,:9]
    df_names = df.iloc[:, 9:]

    # tf-idf logic
    individual_sum_df = df_names.sum()
    total_sum = sum(individual_sum_df)

    for index in df_names.index:
        for name in df_names.columns:
            if index != name.replace(' (S)',''):
                df_copy.loc[index, name] *= total_sum/individual_sum_df[name]

    # Matching participant-participant
    # Initialise variables and perform cosine similarity
    cosine_similarity_participants = cosine_similarity(df_copy)
    cosine_similarity_list = list(cosine_similarity_participants)
    cosine_similarity_list_copy = cosine_similarity_list.copy()

    for i in range(len(cosine_similarity_list)):
        cosine_similarity_list[i][i] = -1
        
    participants_list = df.index.values.tolist()
    unmatched_participants = df.index.values.tolist() # initialise all participants as unmatched
    matched_participants = []
    pairwise_list = []

    global cosine_similarity_dict
    cosine_similarity_dict = {}
    for i in range(len(cosine_similarity_participants)):
        cosine_similarity_dict[unmatched_participants[i]] = list(cosine_similarity_list[i])
        
    cosine_similarity_dict_copy = {}
    for i in range(len(cosine_similarity_participants)):
        cosine_similarity_dict_copy[unmatched_participants[i]] = list(cosine_similarity_list_copy[i])

    # remove participants to keep track of who is left
    def remove_pair(index1, index2): 
        if index1 < index2:
            for key, value in cosine_similarity_dict.items():
                value.pop(index1)
                value.pop(index2 - 1)
        else:
            for key, value in cosine_similarity_dict.items():
                value.pop(index2)
                value.pop(index1 - 1)

    # averaging logic
    def averaging_lists(list1, list2):
        # average of lists
        combined_lists = np.array([np.where(np.asarray(list1) == -1, 0, np.asarray(list1)), np.where(np.asarray(list2) == -1, 0, np.asarray(list2))])
        return list(np.average(combined_lists, axis=0))

    # Matching logic
    while len(unmatched_participants) > 2:
        
        # get highest participant
        max_participant = max(cosine_similarity_dict, key=cosine_similarity_dict.get) # participant with highest similarity score
        max_participant_list = cosine_similarity_dict[max_participant] # highest participant similarity list
        
        # get best match
        match_index = max_participant_list.index(max(max_participant_list)) # index of best match in max_participant_list
        match_partcipant = unmatched_participants[match_index] # kerberos of best match
        
        # append pair
        matched_participants.append([max_participant, match_partcipant])
        
        # add to new df
        pairwise_list.append(averaging_lists(cosine_similarity_dict_copy[max_participant], cosine_similarity_dict_copy[match_partcipant]))
        
        # remove pair
        del cosine_similarity_dict[max_participant]
        del cosine_similarity_dict[match_partcipant]
        
        remove_pair(unmatched_participants.index(max_participant), unmatched_participants.index(match_partcipant))
        
        unmatched_participants.remove(max_participant)
        unmatched_participants.remove(match_partcipant)

    # append final 2
    matched_participants.append(unmatched_participants)
    pairwise_list.append(averaging_lists(cosine_similarity_dict_copy[max_participant], cosine_similarity_dict_copy[match_partcipant]))

    # Matching pair-pair
    # Initialise variables and perform cosine similarity
    pairwise_df = pd.DataFrame(pairwise_list)
    pairwise_cosine_similarity = cosine_similarity(pairwise_df)

    pairwise_cosine_similarity_list = list(pairwise_cosine_similarity)
                                        
    pairs_list = matched_participants.copy()
    unmatched_pairs = matched_participants.copy()
                                        
    global pairwise_cosine_similarity_dict
    pairwise_cosine_similarity_dict = {}
    for i in range(len(pairs_list)):
        pairwise_cosine_similarity_dict[','.join(unmatched_pairs[i])] = list(pairwise_cosine_similarity_list[i])

    # remove pairs to keep track of who is left
    def remove_pairs(index1, index2): 
        if index1 < index2:
            for key, value in pairwise_cosine_similarity_dict.items():
                value.pop(index1)
                value.pop(index2 - 1)
        else:
            for key, value in pairwise_cosine_similarity_dict.items():
                value.pop(index2)
                value.pop(index1 - 1)

    # Matching logic
    groupings = {}
    group_number = 1
    while len(unmatched_pairs) > 2:
        
        # get lowest pair
        min_pair = min(pairwise_cosine_similarity_dict, key=pairwise_cosine_similarity_dict.get) # pair with lowest similarity score
        min_pair_list = pairwise_cosine_similarity_dict[min_pair] # lowest pair similarity list

        # get worst match
        match_pair_index = min_pair_list.index(min(min_pair_list)) # index of worst match in min_pair_list
        match_pair = unmatched_pairs[match_pair_index] # kerberos of worst matched pair
        
        # add pairs
        groupings[group_number] = {}
        groupings[group_number]['members'] = min_pair.split(",") + match_pair

        # remove pairs
        del pairwise_cosine_similarity_dict[min_pair]
        del pairwise_cosine_similarity_dict[','.join(match_pair)]
        
        remove_pairs(unmatched_pairs.index(min_pair.split(",")), unmatched_pairs.index(match_pair))
        
        unmatched_pairs.remove(min_pair.split(","))
        unmatched_pairs.remove(match_pair)
        
        group_number += 1

    # add final 2
    groupings[group_number] = {}
    groupings[group_number]['members'] = list(np.concatenate(unmatched_pairs).flat)

    # get top 3 interests
    for key, value in groupings.items():
        combined_array = []
        for member in value['members']:
            combined_array.append(df_interests.loc[member].tolist())
        value['interests_values'] = np.average(combined_array, axis=0).tolist()
        value['top_interests'] = sorted( [(x,df_interests.columns[i].replace(" (N)", "")) for (i,x) in enumerate(value['interests_values'])], reverse=True )[:3]

    return groupings