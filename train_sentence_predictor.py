import bisect
import pprint 
import operator
import os
import pickle
import xlrd
from nltk.tokenize import word_tokenize
import math
pp = pprint.PrettyPrinter(indent=4)
from dotenv import load_dotenv
load_dotenv()

from colorama import Fore, Back, Style 
import nltk
from nltk.tokenize import sent_tokenize
import re
import sys


def cnd(w, nested_dict):
#     print(w)
    if(len(w) == 0):
        return
    elif w[0].lower() not in nested_dict:
        nested_dict[w[0].lower()] = {}
        cnd(w[1:],nested_dict[w[0].lower()])
    else:
        cnd(w[1:],nested_dict[w[0].lower()])
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
		cnd(word.lower().split(), nested_dict)
    
	return docID, tagss

# read the db and creates dictionary
 



def color_text(word_dict, text, start_index, word):
    i = start_index
    temp_word = word
    if i>=len(text):
        return [i, temp_word]
#         print(i, ' -> ', text[i:])
    if text[i].lower() in word_dict:
        # print(Fore.GREEN + text[i], end = ' ')
        word = word + ' ' + text[i]
#         print(Fore.BLACK + word)
        i, temp_word = color_text(word_dict[text[i].lower()], text, i+1, word)
#         print(Fore.BLACK + temp_word)
    return [i, str(temp_word)]


def read_jd(words_dir, nested_dict):
    found_words_all = []
    files = [os.path.join(words_dir, fi) for fi in os.listdir(words_dir)]

    # features_matrix = np.zeros((len(files), 3000))
    docID = 0;
    tagss = {}
    for fil in files:
        file_name = os.getenv('PATH_PREMIUM_TAGS') + fil.split('\\')[1]
        f= open(file_name,"w+", encoding="utf-8")
        with open(fil, errors='ignore') as fi:
            found_words = []
            for i, line in enumerate(fi):
                print()
#                 temp = line.split()
                temp = word_tokenize(line)
#                 print((temp))
                j = 0
                while (j < len(temp)):
                    if temp[j].lower() in nested_dict:
                        # print(Fore.RED + temp[j] , end = ' ')
                        word = temp[j]
                        temp_word = temp[j]
#                         j, temp_Word = color_text(nested_dict[temp[j].lower()], temp , j+1, word)
                        found_words.append(color_text(nested_dict[temp[j].lower()], temp , j+1, word))
                        j=found_words[-1][0]
                        k = found_words[-1][1]
                        f.write(k)
                        f.write(',')

#                         print(Fore.RED + i)
                    else:
                        if j<len(temp):
                            print(Fore.BLUE + temp[j], end=' ')
                        j+=1    
                
            found_words_all.append(found_words)
        f.close()
    return found_words_all









# remove all spaces
def clean_text(word):
	temp = []
	for i in word:
		i=i.lower()
		i = i.rstrip()
		i = i.lstrip()
		temp.append(i)
	return temp

def read_words(words_dir):

	words_dir = os.getenv('BASE_ROOT_PATH') + words_dir

	files = [os.path.join(words_dir, fi) for fi in os.listdir(words_dir)]

#features_matrix = np.zeros((len(files), 3000))
	docID = 0;
	all_words = {}
	word_set = set()
	for fil in files:
		f=open(fil, "r")
		text =f.read()
		word = text.split(',')
		word = clean_text(word)
		all_words[docID] = word
		word_set.update(word)
		docID+=1

	pp.pprint(all_words)
	return all_words, word_set

def read_sentences(tag_dir, words_dictionary):

	tag_dir = os.getenv('BASE_ROOT_PATH') + tag_dir

	files = [os.path.join(tag_dir, fi) for fi in os.listdir(tag_dir)]	
	docID = 0
	sentences = {}
	for ID,fil in enumerate(files):
		f=open(fil, "r")
		contents =f.read()
		contents = contents.rstrip()
		contents = contents.lstrip()
		# print(contents)
		count_total_words_in_sentence = len(word_tokenize(contents))
		count_meaningful_words = len(words_dictionary[ID])
		if count_meaningful_words == 1 or count_meaningful_words == 0:
			count_meaningful_words +=1

		# print(docID, " -> ", contents )
		initial_value = float(math.log(count_meaningful_words)/math.log(count_total_words_in_sentence))

		# print(initial_value)

		sentences[docID] = [contents, initial_value]
		docID+=1
	return sentences, docID

def draw_keyword_to_sentence_dict(words_dictionary):
	keyword_to_sentence_dict = {}

	for i in words_dictionary:
		for key in words_dictionary[i]:
			if key in keyword_to_sentence_dict:
				bisect.insort(keyword_to_sentence_dict[key],i)
			else:
				keyword_to_sentence_dict[key] = [i]
	return keyword_to_sentence_dict


def main():
	# this input word will be taken from the front end
	nested_dict = {}
	doc_id, tags = read_tags('tags', nested_dict)
	words= read_jd('premium_sentences', nested_dict)

	print(nested_dict)

	input_word = 'industry experience, people management experience'

	words_dictionary, word_set = read_words('premium_tags')
	sentence_dictionary, docID = read_sentences('premium_sentences' ,words_dictionary)
	# dataFrame1 = np.ones((len(all_rows), len(sentence_dictionary))
	# df1 = pd.DataFrame(data = dataFrame1, index = all_rows, columns = all_cols, dtype='float64')
	
	# pp.pprint(words_dictionary)
	# pp.pprint(sentence_dictionary)
	keyword_to_sentence_dict = draw_keyword_to_sentence_dict(words_dictionary)
	# pp.pprint(keyword_to_sentence_dict)

	with open(os.getenv('BASE_ROOT_PATH') + 'words_dictionary.pkl', 'wb') as f:
		pickle.dump(words_dictionary, f)

	with open(os.getenv('BASE_ROOT_PATH') + 'sentence_dictionary.pkl', 'wb') as f:
		pickle.dump(sentence_dictionary, f)

	with open(os.getenv('BASE_ROOT_PATH') + 'keyword_to_sentence_dict.pkl', 'wb') as f:
		pickle.dump(keyword_to_sentence_dict, f)



main()

