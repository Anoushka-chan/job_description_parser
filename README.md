# Job Description Parser #

### Highlights
JD creater


### Important module Links - Refer for documentation


### Dependencies
Python 3.7, flask

### Installation
pip3 install flask
pip3 install pickle
pip3 install pymongo
pip3 install operator
pip3 install colorma
pip3 install nltk
pip3 install numpy
pip3 install pandas
>>>import nltk
>>>nltk.download('stopwords')
>>>nltk.download('punkt')



##From root folder run following command
#prepare for training
python train.py
(it saves a 2D matrix which holds score for the relationship between keywords)

#FLASK API to analyse word
python words_analysing_page.py

<!-- #FLASK API to get best fit sentence
python 
 -->

### Known Issue

##Solved issue
SSL error downloading NLTK data
run command from python terminal
>>>/Applications/Python 3.7/Install Certificates.command


##Key points
* Use Proper indentation. 4 spaces should be there. All ('=', ':') sign of variables should be in same line
    Eg 
	    def get(self, request):
	        serializer = UserSerializer(User.objects.all(), many=True)
	        response = {"users": serializer.data}
	        return Response(response, status=status.HTTP_200_OK)

* All variables and files should be camelcased. Dont use '_' in any variable and filname.
* Always define validations whenever new API is created
* Always update doc whenever new API is created
* Define schema before creating mongo model
* Dont require any file inside any function. Require it on top
* Use logger library for logging of response. No consoles in the committed code please.
* All get API should have limit and offset
