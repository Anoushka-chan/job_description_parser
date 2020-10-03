from flask import Flask
from flask import jsonify
import os
import pickle
import heapq
import numpy
import json
import xlrd
import openpyxl
import os
import bisect
import datetime
# import pickle
import operator
import json
import bisect
import pprint 
import os
import re
# import pickle
import nltk
from nltk.corpus import stopwords
import string
from nltk.tokenize import word_tokenize
import math
import logging
pp = pprint.PrettyPrinter(indent=4)
from dotenv import load_dotenv
load_dotenv()
from elasticsearch import Elasticsearch


from flask import request
import requests

app = Flask(__name__)
# app.config["DEBUG"]=True

@app.route('/')
def hello_world():
	return 'Hello World'


@app.route('/connect_elasticsearch')
def connect_elasticsearch():
   	# es = None
    # es = Elasticsearch(HOST='es.shrofile.com', PORT=9200)
    if es.ping():
        print('Yay Connect')
    else:
        print('Awww it could not connect!')
    return jsonify({'es': 1})

    
@app.route('/add_stopwords', methods = ['POST'])
def add_stopwords():

	if request.method == 'POST':
			
		data = json.loads(request.data)
		if 'input_string' not in data:
			return 'data is required'

		INPUT_WORD = data['input_string']

		# convert this to mongo db
		# dir_path = os.getcwd()
		file_path = os.getenv('BASE_ROOT_PATH') + '/stopwords.pkl'
		
		if os.path.isfile(file_path):
			with open(os.getenv('BASE_ROOT_PATH') + 'stopwords.pkl', 'rb') as f:
				stopword = pickle.load(f)
			stopword.append(INPUT_WORD)
			with open(os.getenv('BASE_ROOT_PATH') + 'stopwords.pkl', 'wb') as f:
				pickle.dump(stopword, f)

		else:
			stop = stopwords.words('english')
			punctuations = list(string.punctuation)
			stopword = stop + punctuations
			stopword.append(INPUT_WORD)
			with open(os.getenv('BASE_ROOT_PATH') + 'stopwords.pkl', 'wb') as f:
				pickle.dump(stopword, f)

		file_path = os.getenv('BASE_ROOT_PATH') + '/non_recognized_words.pkl'
		if os.path.isfile(file_path):

			with open(os.getenv('BASE_ROOT_PATH') + 'non_recognized_words.pkl', 'rb') as f:
				non_recognized_words = pickle.load(f)

			if INPUT_WORD in non_recognized_words:
				del non_recognized_words[INPUT_WORD]
			
			with open(os.getenv('BASE_ROOT_PATH') + 'non_recognized_words.pkl', 'wb') as f:
				pickle.dump(non_recognized_words, f)

	with open(os.getenv('BASE_ROOT_PATH') + 'stopwords.pkl', 'rb') as f:
		stopwords = pickle.load(f)
		return jsonify(stopwords)


	x = {'success':0}
	return jsonify(x)


# the JSON can add more features other than jst input_string of the word as the data increases.
# TEST JSON FILE TO BE PASSED
# {
# 	"input_string" : "sql"
# }


@app.route('/add_word_to_db', methods = ['POST'])
def add_word_to_db():

	if request.method == 'POST':

		data = json.loads(request.data)
		if 'input_string' not in data:
			return 'data is required'

		INPUT_WORD = data['input_string']
	
		# convert this to mongo db
		# dir_path = os.getcwd()
		# print(dir_path)
		file_path = os.getenv('BASE_ROOT_PATH') + '/non_recognized_words.pkl'
	
		if os.path.isfile(file_path):

			with open(os.getenv('BASE_ROOT_PATH') + 'non_recognized_words.pkl', 'rb') as f:
				non_recognized_words = pickle.load(f)

			if INPUT_WORD in non_recognized_words:
				del non_recognized_words[INPUT_WORD]
			
			with open(os.getenv('BASE_ROOT_PATH') + 'non_recognized_words.pkl', 'wb') as f:
				pickle.dump(non_recognized_words, f)

			# files = [os.path.join(os.getenv('BASE_ROOT_PATH') + os.getenv('TAG_DIR'), fi) for fi in os.listdir(os.getenv('BASE_ROOT_PATH') + os.getenv('TAG_DIR'))]

			# for fil in files:
			# 	f = open(fil, "a+")
			# 	f.write(INPUT_WORD + ', ')

			loc = os.getenv('BASE_ROOT_PATH') + '/tags_with_alias.xlsx'
			wb = xlrd.open_workbook(loc)
			sheet = wb.sheet_by_index(0)
			end_row = sheet.nrows

			wb = openpyxl.load_workbook(os.getenv('BASE_ROOT_PATH') + '/tags_with_alias.xlsx')
			sheet = wb.active
			c1 = sheet.cell(row = end_row, column = 1) 
			c1.value = INPUT_WORD
			wb.save(os.getenv('BASE_ROOT_PATH') + '/tags_with_alias.xlsx')			

		else:
			return {'file (non_recognized_words) not found' : 1}

	with open(os.getenv('BASE_ROOT_PATH') + 'non_recognized_words.pkl', 'rb') as f:
		non_recognized_words = pickle.load(f)
		return jsonify(non_recognized_words)

	# x = {'added':1}
	# return jsonify(x)

# the JSON can add more features other than jst input_string of a word as the league scoring part is implemented...

# TEST JSON FILE TO BE PASSED
# {
# 	"input_string" : "sql"
# }


@app.route('/predict_near_words', methods = ['POST'])

def return_predictions():

	if request.method == 'POST':
	
		data = json.loads(request.data)
		if 'input_string' not in data:
			return 'data is required'

		input_words = data['input_string']

		with open(os.getenv('BASE_ROOT_PATH') + 'all_columns.pkl', 'rb') as f:
			all_columns = pickle.load(f)
		
		with open(os.getenv('BASE_ROOT_PATH') + 'scoring_matrix.pkl', 'rb') as f:
			scoring_matrix = pickle.load(f)

		predicted_words = []
		predictions = {}

		for word in input_words:
			word = word.rstrip()
			word = word.lstrip()

			index = all_columns.index(word)
			# gives top 10 results in O(n + k.logk) time complexity)
			ans = heapq.nlargest(10, range(len(scoring_matrix[index])), scoring_matrix[index].take)    

			for i in ans:
				if  all_columns[i] == word:
					continue
				if all_columns[i] not in predictions:
					predictions[all_columns[i]] = scoring_matrix[index][i]

				else:
					predictions[all_columns[i]] += scoring_matrix[index][i]    

		for word in input_words:
			word = word.rstrip()
			word = word.lstrip()
			if word in predictions:
				del predictions[word]

		sorted_output = sorted(predictions.items(), key=operator.itemgetter(1))
		sorted_output.reverse()

	# return predicted_words
		return jsonify(sorted_output)

	else:
		'Invalid Method'

# one can input all the comma separated words and these will be converted to 
# main('sql, php, java, python')

# TEST JSON FILE TO BE PASSED
# {
# 	"words" : [
# 		"sql, php, java, python"
# 		]
# }



''' ---------------------------------------------

        CURRENTLY I AM ADDING THE PROBABILITY OF OCCURANCE OF MAXIMUM PROBABLE WORDS,
        LATER THE LOGIC OF HOW PROBABILITIES ADD UP ON ENTERING MULTIPLE WORDS CAN BE CHANGED TO ANYTHING.

    ----------------------------------------------

'''

@app.route('/accept_sentence', methods = ['POST'])
def accept_sentence():
	
	data = json.loads(request.data)
	if 'ID' not in data:
		return 'data is required'

	ID = data['ID']

	with open(os.getenv('BASE_ROOT_PATH') + 'sentence_dictionary.pkl', 'rb') as f:
		sentence_dictionary = pickle.load(f)

	print(sentence_dictionary[ID[0]][1])
	sentence_dictionary[ID[0]][1] = ((sentence_dictionary[ID[0]][1] * 1000) + 1) / 1001
	print(sentence_dictionary[ID[0]][1])

	with open(os.getenv('BASE_ROOT_PATH') + 'sentence_dictionary.pkl', 'wb') as f:
		pickle.dump(sentence_dictionary, f)

	x = {'success':1}
	return jsonify(x)

# required json
# {
# 	"ID" : [2, 0.511916049619631]
# }
# [
#         6,
#         [
#             0.511916049619631,
#             "Hands-on programming experience in one of the following: Java, php or Python."
#         ]
#     ]


@app.route('/reject_sentence', methods = ['POST'])
def reject_sentence():
	
	data = json.loads(request.data)
	
	if 'ID' not in data:
		return 'data is required'

	ID = data['ID']

	with open(os.getenv('BASE_ROOT_PATH') + 'sentence_dictionary.pkl', 'rb') as f:
		sentence_dictionary = pickle.load(f)

	print(sentence_dictionary[ID[0]][1])
	sentence_dictionary[ID[0]][1] = ((sentence_dictionary[ID[0]][1] * 1000) - 1) / 1001
	print(sentence_dictionary[ID[0]][1])

	with open(os.getenv('BASE_ROOT_PATH') + 'sentence_dictionary.pkl', 'wb') as f:
		pickle.dump(sentence_dictionary, f)

	x = {'success':1}
	return jsonify(x)

# required json
# {
# 	"ID" : [2, 0.513863514326272]
# }


@app.route('/delete_sentence', methods = ['POST'])
def delete_sentence():
	
	data = json.loads(request.data)
	
	if 'ID' not in data:
		return 'data is required'

	ID = data['ID']
	deleted_sentences = []
	# if pkl file elready exists then get its data
	if os.path.isfile(os.getenv('BASE_ROOT_PATH') + 'deleted_sentences.pkl'):
		
		with open(os.getenv('BASE_ROOT_PATH') + 'deleted_sentences.pkl', 'rb') as f:
			deleted_sentences = pickle.load(f)
		
	deleted_sentences.append(ID)

	# restore pkl file data along with new delete_sentence
	with open(os.getenv('BASE_ROOT_PATH') + 'deleted_sentences.pkl', 'wb') as f:
		pickle.dump(deleted_sentences, f)


	# delete requested data from sentence_dictionary.pkl
	with open(os.getenv('BASE_ROOT_PATH') + 'sentence_dictionary.pkl', 'rb') as f:
		sentence_dictionary = pickle.load(f)

	del sentence_dictionary[ID[0]]
	
	with open(os.getenv('BASE_ROOT_PATH') + 'sentence_dictionary.pkl', 'wb') as f:
				pickle.dump(sentence_dictionary, f)


	x = {'success':1}
	return jsonify(x)

# required json
# {
# 	"ID" : [2, 0.513863514326272]
# }

@app.route('/get-non-recognized-words')
def non_recognized_words():

	score = {}
	# if pkl file elready exists then get its data
	if os.path.isfile(os.getenv('BASE_ROOT_PATH') + 'non_recognized_words.pkl'):
		
		with open(os.getenv('BASE_ROOT_PATH') + 'non_recognized_words.pkl', 'rb') as f:
			non_recognized_words = pickle.load(f)


		print(non_recognized_words)
		print()
		print()

		for key in non_recognized_words:
			# print(key, '-------->>>>>', len(word_tokenize(key)))
			score[key] = len(word_tokenize(key)) * non_recognized_words[key]
			print(score[key], " ", key, " ", len(word_tokenize(key)), " ", non_recognized_words[key])
		sorted_output = sorted(score.items(), key=operator.itemgetter(1))
		sorted_output.reverse()

	return jsonify(sorted_output)


@app.route('/getsearch', methods = ['POST'])
def getsearch():

	
	if request.method == 'POST':

		data = json.loads(request.data)
		if 'name' not in data or 'index' not in data or 'field' not in data:
			return 'data is required'

		input_index = data['index']
		input_field = data['field']
		input_name = data['name']

		url = os.getenv('ES_HOST') + ':' + os.getenv('ES_PORT') + '/' + input_index + '/_search?q=name' + ':*' + input_name + '* OR name-alias:*' + input_name + '*'
		response = requests.get(url)
		results = json.loads(response.text)
		return jsonify({'es': results})

# {
# 	"name" : "mohit"
# }


@app.route('/putsearch', methods = ['POST'])
def putsearch():


	# input_json={
	# 	"index" :
	# 	"name" : "mohit"
	# }

	if request.method == 'POST':

		data = json.loads(request.data)
		if 'name' not in data or 'index' not in data or 'type' not in data or 'id' not in data:
			return 'data is required'

		input_id = data['id']
		input_index = data['index']
		input_type = data['type']
		input_name = data['name']
		input_alias = data['name-alias']

	url = os.getenv('ES_HOST') + ':' + os.getenv('ES_PORT') + '/' + input_index + '/' + input_type + '/' + input_id
	payload = {
		"name" : input_name ,
		"name-alias" : input_alias
	}

	headers = {'content-type': 'application/json'}
	response = requests.put(url, data=json.dumps(payload), headers=headers)
	results = json.loads(response.text)
	return jsonify({'esput': results})



@app.route('/postsearch', methods = ['POST'])
def postsearch():

	if request.method == 'POST':

		data = json.loads(request.data)
		if 'name' not in data or 'index' not in data or 'type' not in data:
			return 'data is required'

		input_index = data['index']
		input_type = data['type']
		input_name = data['name']
		input_alias = data['name-alias']

		url = os.getenv('ES_HOST') + ':' + os.getenv('ES_PORT') + '/' + input_index + '/' + input_type
		payload = {
			"name" : input_name ,
			"name-alias" : input_alias
		}

		print('url============', url)
		print('payload==============', payload)
		headers = {'content-type': 'application/json'}
		response = requests.post(url, data=json.dumps(payload), headers=headers)
		results = json.loads(response.text)
		return jsonify({'esput': results})


@app.route('/train')
# REQUIRE NO INPUT PARAMETER
# this is for training of premium sentences

def train_sentence_predictor():
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

	# this input word will be taken from the front end
	# input_word = 'industry experience, people management experience'

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

	return "PREMIUM SENTENCE TRAINING DONE!!!!"


@app.route('/give_feedback', methods = ['POST'])
def feedback_sentence_addition():
	if request.method == 'POST':
		data = json.loads(request.data)

		if 'new_sentences' not in data or 'old_sentences' not in data or 'search_string' not in data:
			return 'data is required'

		old_sentences = data['old_sentences']
		new_sentences = data['new_sentences']
		search_string = data['search_string']
		search_string_list = search_string.split(',')

		old_sentences = str(old_sentences)
		new_sentences = str(new_sentences)

		old_sentences = old_sentences.split('.')
		new_sentences = new_sentences.split('.')
		for new_s in new_sentences:
			new_s = new_s.lstrip()
			new_s = new_s.rstrip()
			flag = 0
			for old_s in old_sentences:
				old_s = old_s.lstrip()
				old_s = old_s.rstrip()
				if old_s == new_s:
					flag = 1
					break
				else:
					continue

			if flag == 0:
				now = datetime.datetime.now()
				now = str(now)
				now = re.sub(r"[^\w\s]", '', now)
				# now.replace(" ", "")
				
				import random
				temp = random.randint(1,101)

				file_name = os.getenv('PATH_PREMIUM_SENTENCE') + now + '.txt'
				f= open(file_name,"w+", encoding="utf-8")
				f.write(new_s)
				f.close() 
				tag_list = []
				for each in search_string_list:
					each = each.lstrip()
					each = each.rstrip()
					if each in new_s:
						tag_list.append(each)

				file_name = os.getenv('PATH_PREMIUM_TAGS') + now + '.txt'
				f= open(file_name,"w+", encoding="utf-8")
				for each in tag_list:					
					f.write(each)
					f.write(',')
				f.close()


			else:
				continue

	dict1 = {
		'old': old_sentences, 
		'new': new_sentences
		}

	return jsonify(dict1)

@app.route('/predict_sentence', methods = ['POST'])
def predict_sentence():
	# this input word will be taken from the front end

	if request.method == 'POST':

		# input_word = 'industry experience, people management experience'
		data = json.loads(request.data)
		if 'words' not in data:
			return 'data is required'

		input_word = data['words']

		# print(input_word)
		
		with open(os.getenv('BASE_ROOT_PATH') + 'words_dictionary.pkl', 'rb') as f:
			words_dictionary = pickle.load(f)

		with open(os.getenv('BASE_ROOT_PATH') + 'sentence_dictionary.pkl', 'rb') as f:
			sentence_dictionary = pickle.load(f)

		with open(os.getenv('BASE_ROOT_PATH') + 'keyword_to_sentence_dict.pkl', 'rb') as f:
			keyword_to_sentence_dict = pickle.load(f)	
		# print(keyword_to_sentence_dict['people management experience'])
		# print('------------------')
		# words = input_word.split(',')
		
		words = input_word
		output_sentence_score = {}
		for word in words:
			word = word.lstrip()
			word = word.rstrip()
			indices = keyword_to_sentence_dict[word]
			for i in indices:
				if i in output_sentence_score:
					output_sentence_score[i][0] += 1
				else:
					if i in sentence_dictionary:
						output_sentence_score[i] = [sentence_dictionary[i][1], sentence_dictionary[i][0]]


		pp.pprint(output_sentence_score)
		print('--------------111')
		print(output_sentence_score)
		# return output_sentence_score

		sorted_output = list(output_sentence_score)
		sorted_output = sorted(output_sentence_score.items(), key=operator.itemgetter(1))
		sorted_output.reverse()
		pp.pprint(sorted_output)
		# myDict = {}
		# print('--------------')
		# for ID in sorted_output:
		# 	myDict[ID[1]] = [ID[0], sentence_dictionary[ID[0]][0]]

		# sorted_output is a list of pairs of the form ((a0,b0), (a1,b1), (a2,b2))
		# 	a: id the index in the pickle file
		# 	b: final score made.
		# 	(the sentence can be searched by the index a on the front end directly searching from the db)

		return jsonify(sorted_output)
	else:
		"Invalid Method"



if __name__ == '__main__':
	app.run(host='0.0.0.0', port='4997')


# # rpn
# one on one
# # for accuracy
# intersection of union
# rcnn


# command of importing dataset to cloud from google drive
# stack overflow link
