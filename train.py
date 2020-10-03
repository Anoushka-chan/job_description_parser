from colorama import Fore, Back, Style 
import os
import pickle
import nltk
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
import numpy as np
import pandas as pd
import xlrd
import re
import sys
from nltk.corpus import stopwords
import string
from dotenv import load_dotenv
load_dotenv()
    
# sys.path.append("scr")

# from file import function


''' THE MAIN.PY WILL CALL ALL THE 
    FUNCTIONS THAT ARE PRESENT IN SCR DIRECTORY
    DATA THAT IS PRESENT IN DATA FOLDER '''

# MODULE 1






# MODULE 2

def read_tags_recursive(word_list, nested_dict):
#     print(word_list)
    if(len(word_list) == 0):
        return
    elif word_list[0].lower() not in nested_dict:
        nested_dict[word_list[0].lower()] = {}
        read_tags_recursive(word_list[1:],nested_dict[word_list[0].lower()])
    else:
        read_tags_recursive(word_list[1:],nested_dict[word_list[0].lower()])
    return


def read_tags(words_dir, nested_dict):
    # files = [os.path.join(words_dir, fi) for fi in os.listdir(words_dir)]

    # features_matrix = np.zeros((len(files), 3000))
    loc = os.getenv('BASE_ROOT_PATH') + '/tags_with_alias.xlsx'
    wb = xlrd.open_workbook(loc)
    sheet = wb.sheet_by_index(0)
    end_row = sheet.nrows
    docID = 0;
    tagss = {}
    for iterator in range(1,end_row):
        word = sheet.cell_value(iterator, 0)
        word = word.rstrip()
        word = word.lstrip()
        read_tags_recursive(word.lower().split(), nested_dict)
    return



#######################    MODULE 3
# currently this module return all the words that are matched from the dictionary created in module 2
# adding line number and distance from previous word in the next step...

def clean(line):
    return line.replace("/", " / ")

def stitch(word1, word2):
#     THIS FUNCTION WILL JOIN THE WORD BEFORE TO THE CURRENT WORD TO MAKE A COUPLE
#     THE SAME FUNCTIONALITY CAN BE APPLIED TO WORD DEPTH 3 OR 4 TO INCREASE THE NUMBER OF FEATURES FOR NLP
    if word1 == '':
        return
    return word1+' '+word2

def color_text(word_dict, text, start_index, word):
    index = start_index
    temp_word = word
    if index>=len(text):
        return index, temp_word
#         print(index, ' -> ', text[index:])
    if text[index].lower() in word_dict:
        # print(Fore.GREEN + text[index], end = ' ')
        word = word + ' ' + text[index]
#         print(Fore.BLACK + word)
        index, temp_word = color_text(word_dict[text[index].lower()], text, index+1, word)
#         print(Fore.BLACK + temp_word)
    return index, str(temp_word)

def read_jd(words_dir, non_recognized_words, stopword, nested_dict):
    found_words_all = []
    
    files = [os.path.join(words_dir, fi) for fi in os.listdir(words_dir)]

    # features_matrix = np.zeros((len(files), 3000))
    docID = 0;
    tagss = {}
    for fil_num,fil in enumerate(files):
        docID+=1
        with open(fil, errors='ignore') as fi:
            found_words = []
            for i, line in enumerate(fi):
                print()
#                 temp = line.split()
                line = clean(line)
                temp = word_tokenize(line)
#                 print((temp))
                j = 0
                prev = ''
                while (j < len(temp)):
                    if temp[j].lower() in nested_dict:
                        # print(Fore.RED + temp[j] , end = ' ')
                        word = temp[j]
                        temp_word = temp[j]
#                         j, temp_Word = color_text(nested_dict[temp[j].lower()], temp , j+1, word)
#                         x = 
                        found_words.append([fil_num, i, color_text(nested_dict[temp[j].lower()], temp , j+1, word)])
                        j=found_words[-1][2][0]
                        prev = ''
#                         print(Fore.RED + i)

#       ------------------------------------------------------------------------------------------
                    elif temp[j].lower() in stopword:
                        prev = ''
                        # print(Fore.BLACK + temp[j], end=' ')
                        j+=1
                        continue
#       ------------------------------------------------------------------------------------------          
                    
                    else:
                        if j<len(temp):
                            if temp[j].lower() in non_recognized_words:
                                non_recognized_words[temp[j].lower()] += 1
                            else:
                                non_recognized_words[temp[j].lower()] = 1
#                             for the stitched word
                            if stitch(prev, temp[j]):
                                couple_word = stitch(prev, temp[j])
                                # cw.append(couple_word)
                                if couple_word.lower() in non_recognized_words:
                                    non_recognized_words[couple_word.lower()] += 1
                                else:
                                    non_recognized_words[couple_word.lower()] = 1
                            # print(Fore.BLUE + temp[j], end=' ')
                            prev = temp[j]
                        j+=1
            found_words_all.append(found_words)
    return found_words_all







def read_jd_2(words_dir, nested_dict):
    found_words_all = []
    files = [os.path.join(words_dir, fi) for fi in os.listdir(words_dir)]

    # features_matrix = np.zeros((len(files), 3000))
    docID = 0;
    tagss = {}
    for fil_num, fil in enumerate(files):
        docID+=1
        with open(fil, errors='ignore') as fi:
            found_words = []
            clean = fi.read().replace('\n', '')
            
#             for word in clean:
#                 print()
#                 temp = line.split()
            temp = word_tokenize(clean)
#             print((temp))
            temp_index = 0
            while (temp_index < len(temp)):
                if temp[temp_index].lower() in nested_dict:
                    # print(Fore.RED + temp[temp_index] , end = ' ')
                    word = temp[temp_index]
                    temp_word = temp[temp_index]
#                         j, temp_Word = color_text(nested_dict[temp[j].lower()], temp , j+1, word)
#                         x = 
                    found_words.append([fil_num,color_text(nested_dict[temp[temp_index].lower()], temp , temp_index+1, word)])
                    temp_index=found_words[-1][1][0]
#                         print(Fore.RED + i)
                else:
                    # if temp_index<len(temp):
                        # print(Fore.BLUE + temp[temp_index], end=' ')
                    temp_index+=1
        found_words_all.append(found_words)
    return found_words_all




#  MODULE 4
# df1 is the first matrix
# this first matrix holds rows ad JD's and columns as tags
# value of the matrix is the occurance of that keyword (column heading in the  row (JD)

# this sould be changed to reading from excel sheet or mongoDB
def fetch_col_for_mat_1(words_dir):
#     files = [os.path.join(words_dir, fi) for fi in os.listdir(words_dir)]

#     # features_matrix = np.zeros((len(files), 3000))
#     tagss = []
#     for fil in files:
#         with open(fil, errors='ignore') as fi:
#             for i, line in enumerate(fi):
#                 words = line.split(',')
# #                 print(temp)
#                 for word in words:
# #                     word = re.sub('[^A-Za-z0-9]+', '', word)
# #                     word = re.sub(r'^\s+', ' ',   word)
#                     word = word.rstrip()
#                     word = word.lstrip()
# #                     print(word)
#                     tagss.append(word)


    loc = os.getenv('BASE_ROOT_PATH') + words_dir
    wb = xlrd.open_workbook(loc)
    sheet = wb.sheet_by_index(0)
    end_row = sheet.nrows
    docID = 0;
    tagss = set()
    tag_list = []
    for iterator in range(1,end_row):
        word = sheet.cell_value(iterator, 0)
        word = word.rstrip()
        word = word.lstrip()
        tagss.add(word)

    for name in tagss:
        tag_list.append(name)
    return tag_list

def fetch_row_for_mat_1(words_dir):
    jd_text = []
    files = [os.path.join(words_dir, fi) for fi in os.listdir(words_dir)]

    # features_matrix = np.zeros((len(files), 3000))
    for fil in files:
        with open(fil, errors='ignore') as fi:
            clean = fi.read().replace('\n', '')
            jd_text.append(clean)
    return jd_text
    


def update_matrix_1(df, text, all_rows):
    for words in text:
        if(len(words) == 0):
            continue
        for word in words:
            if word[1][1].lower() in df.columns:
                # df.set_value(all_rows[word[0]], word[1][1].lower(), 1)
                df.at[all_rows[word[0]], word[1][1].lower()] = 1
                print('yoo')
            print(word)
            print()
    return df



# MODULE 5

def make_matrix_2(words_dir):
    found_words_all = []
    files = [os.path.join(words_dir, fi) for fi in os.listdir(words_dir)]

    # features_matrix = np.zeros((len(files), 3000))
    docID = 0;
    tagss = {}
    for fil in files:
        docID+=1
        with open(fil, errors='ignore') as fi:
            found_words = []
            # for i, line in enumerate(fi):




#  MODULE 6
#  THE CLUSTER ANALYSIS TO BE THOUGHT UPON

    

# MODULE 7



def matrix_2(lower_all_cols, all_cols, depths):
    word_to_word_dist_mat = np.zeros((len(lower_all_cols), len(lower_all_cols), len(depths)))
    return word_to_word_dist_mat

def fill_matrix_2(lower_all_cols, depths, words_in_file, word_to_word_dist_mat, all_words, non_recognized_words):
#     THIS LOOP UPDATES THE DEPTH VECTOR IN 3D MATRIX.
    for all_words_iterator in words_in_file:
        if(len(all_words_iterator)==0):
            continue
#         for words i find in each JD, i will calculate the distance of each word from all others in same file.
        print(all_words_iterator)
        index_of_row_word = 0
        index_of_col_word = 0
        for word_1 in all_words_iterator:
            if word_1[1][1].lower() not in lower_all_cols:
                if word_1[1][1].lower() not in non_recognized_words:
                    non_recognized_words[word_1[1][1].lower()] = 1
                else:
                    non_recognized_words[word_1[1][1].lower()] += 1
            else:
                index_of_row_word = lower_all_cols.index(word_1[1][1].lower())  
                for word_2 in all_words_iterator:
                    if word_2==word_1:
                        continue
                    else:
                        if word_2[1][1].lower() not in lower_all_cols:
                            continue
                        index_of_col_word = lower_all_cols.index(word_2[1][1].lower())
                        temp = 0
                        absolute_distance = abs(word_2[1][0] - word_1[1][0])
                        if absolute_distance < 7:
                            temp = 1
                        elif absolute_distance < 15:
                            temp = 2
                        else:
                            temp = 3
                        word_to_word_dist_mat[index_of_row_word, index_of_col_word, temp] += 1
#                         a statistical computation is required here
    
#     THIS LOOP WILL UPDATE THE SAME LINE FEATURE AT INDEX 0 IN 3D
    for word_1 in all_words:
        if(len(word_1)==0):
            continue
#         for words i find in each JD, i will calculate the distance of each word from all others in same file.
        file_num = word_1[0][0]
        index_of_row_word = 0
        index_of_col_word = 0
        for word_2 in word_1:
            if word_2[2][1].lower() not in lower_all_cols:
                continue
            else:
                index_of_row_word = lower_all_cols.index(word_2[2][1].lower())  
                for word_3 in word_1:
                    if word_3==word_2 or word_3[2][1].lower() not in lower_all_cols:
                        continue
                    else:
                        index_of_col_word = lower_all_cols.index(word_3[2][1].lower())
                        temp = 0
                        if word_2[1] == word_3[1]:
                            word_to_word_dist_mat[index_of_row_word, index_of_col_word, 0] += 1
    
    
    return word_to_word_dist_mat
                        



# SCORING

def matrix_3(lower_all_cols, all_cols):
    word_to_word_scoring_mat = np.zeros((len(lower_all_cols), len(lower_all_cols)))
    return word_to_word_scoring_mat

def fill_matrix_3(word_to_word_dist_mat, word_to_word_scoring_mat):
    for q1,i in enumerate(word_to_word_dist_mat):
#         print(i)
        for q2,j in enumerate(i):
            list_1 = j
            score = list_1[0]*0.5 + list_1[1]*0.25 + list_1[2]*0.15 + list_1[3]*0.05
            word_to_word_scoring_mat[q1][q2] += score
            # print(score)
    return word_to_word_scoring_mat



def main():

    # here i declare a dictionary of words that occur very often but are not stored in the dictionary
    non_recognized_words = {}
    nested_dict = {}
    if not os.path.isfile(os.getenv('BASE_ROOT_PATH') + 'stopwords.pkl'):
        stop = stopwords.words('english') 
        punctuations = list(string.punctuation)
        stopword = stop + punctuations
    else:
        with open(os.getenv('BASE_ROOT_PATH') + 'stopwords.pkl', 'rb') as f:
            stopword = pickle.load(f)

    # depths for matrix-2
    depths = ['same_line', 'A_dist_away', 'B_dist_away', 'C_dist_away'] 

    # all columns headig in lower case
    lower_all_cols = []

    # read the db and creates dictionary
    read_tags('/tags_with_alias.xlsx', nested_dict)   
    print()
    print('--------------------------------------------------------------------------------------')     
    print(nested_dict)
    print()
    print()
    all_words = read_jd('jd_dir', non_recognized_words, stopword, nested_dict)
    words_in_file = read_jd_2('jd_dir', nested_dict)

    all_cols = fetch_col_for_mat_1('/tags_with_alias.xlsx')
    all_rows = fetch_row_for_mat_1('jd_dir')
    print('--------------------------------------------------')
    print(all_rows)

    # print(all_words)
    print('----------------------------------------------------------------------------------')
    # print(words_in_file)

    lc = set()
    for column_iterator in all_cols:
    #     print(type(i))
        lc.add(column_iterator.lower())

    for column_iterator in lc:
        lower_all_cols.append(column_iterator.lower())

    dataFrame1 = np.zeros((len(all_rows), len(lower_all_cols)))
    df1 = pd.DataFrame(data = dataFrame1, index = all_rows, columns = lower_all_cols, dtype='int64')
    df1[:] = 0
    update_matrix_1(df1, words_in_file, all_rows)

    word_to_word_dist_mat = matrix_2(lower_all_cols, all_cols, depths)
    word_to_word_dist_mat = fill_matrix_2(lower_all_cols, depths, words_in_file, word_to_word_dist_mat, all_words, non_recognized_words)
    # print((word_to_word_dist_mat.shape))
    
    with open('all_columns.pkl', 'wb') as f:
        pickle.dump(lower_all_cols, f)


    word_to_word_scoring_mat = matrix_3(lower_all_cols, all_cols)
    word_to_word_scoring_mat = fill_matrix_3(word_to_word_dist_mat, word_to_word_scoring_mat)
    print(word_to_word_scoring_mat)

    with open('scoring_matrix.pkl', 'wb') as f:
        pickle.dump(word_to_word_scoring_mat, f)
    
    with open('non_recognized_words.pkl', 'wb') as f:
        pickle.dump(non_recognized_words, f)
        
    print(non_recognized_words)

main()