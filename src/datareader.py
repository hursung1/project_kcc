
from preprocess.gen_embeddings_for_slu import slot_list
import time
import random
# import logging


# logger = logging.getLogger()

y1_set = ["O", "B", "I"]
y2_set = ['O', 'B-playlist', 'I-playlist', 'B-music_item', 'I-music_item', 'B-geographic_poi', 'I-geographic_poi', 'B-facility', 'I-facility', 'B-movie_name', 'I-movie_name', 'B-location_name', 'I-location_name', 'B-restaurant_name', 'I-restaurant_name', 'B-track', 'I-track', 'B-restaurant_type', 'I-restaurant_type', 'B-object_part_of_series_type', 'I-object_part_of_series_type', 'B-country', 'I-country', 'B-service', 'I-service', 'B-poi', 'I-poi', 'B-party_size_description', 'I-party_size_description', 'B-served_dish', 'I-served_dish', 'B-genre',  'I-genre', 'B-current_location', 'I-current_location', 'B-object_select', 'I-object_select', 'B-album', 'I-album', 'B-object_name', 'I-object_name', 'B-state', 'I-state', 'B-sort', 'I-sort', 'B-object_location_type', 'I-object_location_type', 'B-movie_type', 'I-movie_type', 'B-spatial_relation', 'I-spatial_relation', 'B-artist', 'I-artist', 'B-cuisine', 'I-cuisine', 'B-entity_name', 'I-entity_name', 'B-object_type', 'I-object_type', 'B-playlist_owner', 'I-playlist_owner', 'B-timeRange', 'I-timeRange', 'B-city', 'I-city', 'B-rating_value', 'B-best_rating', 'B-rating_unit', 'B-year', 'B-party_size_number', 'B-condition_description', 'B-condition_temperature']
domain_set = ["AddToPlaylist", "BookRestaurant", "GetWeather", "PlayMusic", "RateBook", "SearchCreativeWork", "SearchScreeningEvent"]

SLOT_PAD = 0
PAD_INDEX = 0
UNK_INDEX = 1

def read_file(filepath, domain=None):
    seed = time.time()
    domain_list, label_list, utter_list, y_list = [], [], [], []
    '''
    domain_list: lists of domain
    label_list: lists of label
    utter_list: lists of labels concatenated with tokens of query
    y1_list: lists of BIO labels w/o labels
    '''
    max_length = 0
    with open(filepath, "r") as f:
        for i, line in enumerate(f):
            line = line.strip()  # query \t BIO-labels
            splits = line.split("\t") # split query and labels
            utter = splits[0]
            tokens = splits[0].split()
            l2_list = splits[1].split() # O B-LB1 I-LB1 ....
            if max_length < len(tokens):
                max_length = len(tokens)

            # for each label, make B/I/O labeled target 
            BIO_with_label_dict = {}            
            for i, l in enumerate(l2_list):
                if "B" in l:
                    tag, label = l.split('-')
                    BIO_with_label_dict[label] = ["O" for _ in range(len(l2_list))]
                    BIO_with_label_dict[label][i] = tag
                elif "I" in l:
                    tag, label = l.split('-')
                    BIO_with_label_dict[label][i] = tag

            utter_label_list = list(BIO_with_label_dict.keys())
            BIO_list = list(BIO_with_label_dict.values())

            domain_list.extend([domain for _ in range(len(utter_label_list))])
            utter_list.extend([utter for _ in range(len(utter_label_list))])
            label_list.extend(utter_label_list)
            y_list.extend(BIO_list)

    random.Random(seed).shuffle(domain_list)
    random.Random(seed).shuffle(label_list)
    random.Random(seed).shuffle(utter_list)
    random.Random(seed).shuffle(y_list)
    
    data_dict = {"domain": domain_list, "label": label_list, "utter": utter_list, "y": y_list}
    return data_dict, max_length


def data_binarize(data):
    data_bin = {"domain": [], "label": [], "utter": [], "y": []}
    for domain_list, label_list, utter_list, y_list in zip(data['domain'], data['label'], data['utter'], data['y']):
        y_bin = []
        for y in y_list:
            y_bin.append(y1_set.index(y))
        
        data_bin['domain'].append(domain_list)
        data_bin['label'].append(label_list)
        data_bin['utter'].append(utter_list)
        data_bin['y'].append(y_bin)

    return data_bin

def datareader():
    # logger.info("Loading and processing data ...")

    data = {"AddToPlaylist": {}, "BookRestaurant": {}, "GetWeather": {}, "PlayMusic": {}, "RateBook": {}, "SearchCreativeWork": {}, "SearchScreeningEvent": {}}
    max_length = {"AddToPlaylist": 0, "BookRestaurant": 0, "GetWeather": 0, "PlayMusic": 0, "RateBook": 0, "SearchCreativeWork": 0, "SearchScreeningEvent": 0}
    
    # load data
    data_atp, max_length['AddToPlaylist'] = read_file("data/AddToPlaylist/AddToPlaylist.txt", domain="AddToPlaylist")
    data_br, max_length['BookRestaurant'] = read_file("data/BookRestaurant/BookRestaurant.txt", domain="BookRestaurant")
    data_gw, max_length['GetWeather'] = read_file("data/GetWeather/GetWeather.txt", domain="GetWeather")
    data_pm, max_length['PlayMusic'] = read_file("data/PlayMusic/PlayMusic.txt", domain="PlayMusic")
    data_rb, max_length['RateBook'] = read_file("data/RateBook/RateBook.txt", domain="RateBook")
    data_scw, max_length['SearchCreativeWork'] = read_file("data/SearchCreativeWork/SearchCreativeWork.txt", domain="SearchCreativeWork")
    data_sse, max_length['SearchScreeningEvent'] = read_file("data/SearchScreeningEvent/SearchScreeningEvent.txt", domain="SearchScreeningEvent")

    data["AddToPlaylist"] =  data_binarize(data_atp)
    data["BookRestaurant"] =  data_binarize(data_br)
    data["GetWeather"] =  data_binarize(data_gw)
    data["PlayMusic"] =  data_binarize(data_pm)
    data["RateBook"] =  data_binarize(data_rb)
    data["SearchCreativeWork"] =  data_binarize(data_scw)
    data["SearchScreeningEvent"] =  data_binarize(data_sse)

    # print(max_length)
    return data, max(max_length.values())