
# coding: utf-8

# In[ ]:


#This Enum represents the list of features in a human readable way.
#The number (key) will later be the index of the corresponding entry.
#Author: Thorsten
from enum import Enum

class Features(Enum):
    #First pseudo-features, helpful for reconstructing the structure.
    #Some might help the learner, but be careful, some mustn't be used.
    word=0 #string, just the features belong to
    abstractNr=1 #int, zero-starting index
    sentenceNr=2 #int, zero-starting index
    positionInSentence=3 #int, zero-starting index
    entityIdentifyer=4 #string if it is an entity, None if not
    #the labels
    relationWith=5 #entityIdentifyer, type string, if in a relation, None if not
    relationType=6 #string or None
    relationReverse=7 #boolean or None
    #Now the "real" features.
    #If the value does not exist, like the predecessor of the sentence's first word,
    #the value is None.
    lastLetter=8 #char
    lastButOneLetter=9 #char
    lastButTwoLetter=10 #char
    lastButThreeLetter=11 #char
    lastButFourLetter=12 #char
    firstLetter=13 #char
    secondLetter=14 #char
    thirdLetter=15 #char
    fourthLetter=16 #char
    fifthLetter=17 #char
    wordsInSentence=18 #int
    lastWord=19 #string
    lastButOneWord=20 #string
    lastButTwoWord=21 #string
    nextWord=22 #string
    nextButOneWord=23 #string
    nextButTwoWord=24 #string
    wordLen=25 #int
    distLastEntity=26 #int
    distNextEntity=27 #int
    relativePosition=28 #float in (0, 1], relative position of the word in the sentence.
        #Examples: 3rd word in a 10 word sentence: relativePosition=3./10=0.3
        #First word in a 7 word sentence: relativePosition=1./7=0.142857...
    #The next 11 features are the POS-tags of the entity words, generated by numericalPostagging.
    #Values: int: The number is the index of the POS-tag in the list of all tags.
    #Note: -1 means tag not in list, -2 means entity is not so long. This filling up is for improving handling later.
    #15 values because the longest entity has 15 words, one value per word.
    posTag01=29
    posTag02=30
    posTag03=31
    posTag04=32
    posTag05=33
    posTag06=34
    posTag07=35
    posTag08=36
    posTag09=37
    posTag10=38
    posTag11=39
    posTag12=40
    posTag13=41
    posTag14=42
    posTag15=43
    lastLetterInt=44 #int: the last letter, interpreting the bits not as char but as int
    lastButOneLetterInt=45 #int
    lastButTwoLetterInt=46 #int
    lastButThreeLetterInt=47#int
    lastButFourLetterInt=48 #int
    firstLetterInt=49 #int
    secondLetterInt=50 #int
    thirdLetterInt=51 #int
    fourthLetterInt=52 #int
    fifthLetterInt=53 #int
    #These features represent the words not as strings but as vectors (here lists of floats)
    #using word2vec3.py.
    lastWordVector=54 #list of float
    lastButOneWordVector=55 #list of float
    lastButTwoWordVector=56 #list of float
    nextWordVector=57 #list of float
    nextButOneWordVector=58 #list of float
    nextButTwoWordVector=59 #list of float
    #encoding verb in between:
    lastVerb=60 #string
    lastVerbVector=61 #list of float
    lastVerbDistance=62 #int
    nextVerb=63 #string
    nextVerbVector=64 #list of float
    nextVerbDistance=65 #int
    #If the word/phrase has a wikipedia article. 
    #Notes: The query is done by Sara's Wikipedia.py and for performance reasons
    #executed queries are cashed in a data base which will be created if it doesn't exist.
    hasWikiAricle=66 #boolean
    hasOf=67 #boolean, if 'of' is in the sentence
    hasUse=68 #boolean, also true when the word just begins with use, like used or uses.


# In[ ]:


#Generates the 'real' features for the given word of the given sentence,
#not the pseudo features at the beginning that encode the words's total position.
#Input: Sentence and index of the word that should be tagged (0-starting!),
#   set of indexes of the entities of the sentence
#Output: List with the features defined in Features (see above).
#The index in the list is the value of the feature in the Enum.
#Author: Thorsten, imported code by Sara
#Inspired by http://www.nltk.org/book/ch06.html
import numericalPostagging
import word2vec3
import IsVerb
import Wikipedia
import DB #for saving the wikipedia queries

def generateFeatures(sentence, i, s={}):
    result=[]
    #last letters
    x=1
    while(x<=5):
        if(x<=len(sentence[i])):
            result+=sentence[i][-x]
        else:
            result+=[None] #or the indexes won't fit later
        x+=1
    #first letters
    x=0
    while(x<5):
        if(x<len(sentence[i])):
            result+=sentence[i][x]
        else:
            result+=[None]
        x+=1
    
    result+=[len(sentence)]
    
    #last words
    x=1
    while(x<=3):
        if(i-x>=0):
            result+=[sentence[i-x]]
        else:
            result+=[None]
        x+=1
    #next words
    x=1
    while(x<=3):
        if(x+i<len(sentence)):
            result+=[sentence[x+i]]
        else:
            result+=[None]
        x+=1
    #wordLen
    result.append(len(sentence[i]))
    #distLastEntity
    if(len(s)==0):
        result+=[None]
    else:
        x=i-1
        while(True):
            if(s.get(x)!=None):
                result+=[i-x]
                break
            x-=1
            if(x<min(s)):
                result+=[None]
                break
    #distNextEntity
    if(len(s)==0):
        result+=[None]
    else:
        x=i+1
        while(True):
            if(s.get(x)!=None):
                result+=[x-i]
                break
            x+=1
            if(x>max(s)):
                result+=[None]
                break
    #relativePosition
    result+=[(1.+i)/len(sentence)]
    #posTag
    words=sentence[i].strip().split(' ')
    n=0
    for word in words:
        result.append(numericalPostagging.posTag(word))
        n+=1
    if(n>15): #Here's something wrong
        print('Error: Not enough entries for the entity pos-tags:')
        print(words)
        sleep() #This WILL crash the program, what is wanted because this is a really bad error.
    while(n<15): #11 is number of POS-tags, see the enum Feautres for details
        result.append(-2)
        n+=1
    
    #last letters as int
    x=1
    while(x<=5):
        if(x<=len(sentence[i])):
            result+=[ord(sentence[i][-x])]
        else:
            result+=[None] #or the indexes won't fit later
        x+=1
    #first letters
    x=0
    while(x<5):
        if(x<len(sentence[i])):
            result+=[ord(sentence[i][x])]
        else:
            result+=[None]
        x+=1
    
    #word vectors of the last and next words
    for x in range(6):
        if(result[11+x]==None):
            result+=[None]
        else:
            result.extend([word2vec3.Word2Vec(result[11+x])])
    
    #last verb
    x=i-1
    while(x>=0):
        if(IsVerb.posTag(sentence[x])==1):
            result+=[sentence[x]]
            result.extend([word2vec3.Word2Vec(sentence[x])])
            result+=[i-x]
            break
        x-=1
    if(x==-1): #there was no verb before
        result+=[None]
        result+=[None]
        result+=[None]
    #next verb
    x=i+1
    while(x<len(sentence)):
        if(IsVerb.posTag(sentence[x])==1):
            result+=[sentence[x]]
            result.extend([word2vec3.Word2Vec(sentence[x])])
            result+=[x-i]
            break
        x+=1
    if(x==len(sentence)): #there was no verb before
        result+=[None]
        result+=[None]
        result+=[None]
    
    #hasWikiAricle
    temp=DB.get(sentence[i])
    if(temp==None):
        temp=Wikipedia.wiki(sentence[i])
        DB.insert(sentence[i], temp)
    result+=[temp]
    #hasOf
    temp=False
    for word in sentence:
        temp=temp or word=='of' or word=='Of'
    result+=[temp]
    #hasUse
    temp=False
    for word in sentence:
        temp=temp or word.startswith('use') or word.startswith('Use')
    result+=[temp]
        
    return result


# In[ ]:


#Removes all empty strings from the three dimensional list abstracts,
#format abstracts[abstract][sentence][word].
#Also removes some special characters - before removing empty strings.
#Empty sentences and empty abstracts are removed after that.
#This is a help function for the feature generation below.
#Input: 3-dim list
#Output: 3-dim list without empty entries
#Author: Thorsten
def filter(abstracts):
    i=0
    while i<len(abstracts):
        j=0
        while j<len(abstracts[i]):
            k=0
            while k<len(abstracts[i][j]):
                #easy cases
                abstracts[i][j][k]=abstracts[i][j][k].replace('(', '')
                abstracts[i][j][k]=abstracts[i][j][k].replace(')', '')
                abstracts[i][j][k]=abstracts[i][j][k].replace('[', '')
                abstracts[i][j][k]=abstracts[i][j][k].replace(']', '')
                abstracts[i][j][k]=abstracts[i][j][k].replace(',', '')
                abstracts[i][j][k]=abstracts[i][j][k].replace(';', '')
                abstracts[i][j][k]=abstracts[i][j][k].replace('?', '')
                abstracts[i][j][k]=abstracts[i][j][k].replace('\'', '')
                abstracts[i][j][k]=abstracts[i][j][k].replace('&', '')
                abstracts[i][j][k]=abstracts[i][j][k].replace('*', '')
                abstracts[i][j][k]=abstracts[i][j][k].replace('~', '')
                abstracts[i][j][k]=abstracts[i][j][k].replace('\n', '')
                abstracts[i][j][k]=abstracts[i][j][k].replace('\r', '')
                abstracts[i][j][k]=abstracts[i][j][k].replace('  ', ' ')
                abstracts[i][j][k]=abstracts[i][j][k].strip()
                #more complicated, because needed at some points, e. g. to mark entities
                oldLength=0
                while(oldLength!=len(abstracts[i][j][k]) & len(abstracts[i][j][k])>0):
                    oldLength=len(abstracts[i][j][k])
                    char=abstracts[i][j][k][0]
                    if((char=='=') | (char=='/') | (char==':') | (char=='-')):
                        abstracts[i][j][k]=abstracts[i][j][k][1:].strip()
                        continue
                    char=abstracts[i][j][k][-1]
                    if((char=='=') | (char=='/') | (char==':') | (char=='-')):
                        abstracts[i][j][k]=abstracts[i][j][k][:-1].strip()
                if(abstracts[i][j][k]==''):
                    del abstracts[i][j][k]
                    continue
                k+=1
            if(len(abstracts[i][j])==0):
                del abstracts[i][j]
                continue
            j+=1
        if(len(abstracts[i])==0):
            del abstracts[i]
            continue
        i+=1
    return abstracts


# In[ ]:


#Stems all words in abstracts.
#Input: 3-dim list abstracts[abstract][sentence][word]
#Output: 3-dim list (like input)
#This function is part of PreprocessingStemming.py by Sara,
#were you could call it only together with other operations and
#only for a complete text file.
#Author: Thorsten, based on Sara's code
from nltk.stem import PorterStemmer
ps=PorterStemmer() 
def stem(abstracts):
    i=0
    while i<len(abstracts):
        j=0
        while j<len(abstracts[i]):
            k=0
            while k<len(abstracts[i][j]):
                abstracts[i][j][k]=ps.stem(abstracts[i][j][k])
                k+=1
            j+=1
        i+=1
    return abstracts


# In[ ]:


#Removes all stop words in abstracts.
#Input: 3-dim list abstracts[abstract][sentence][word]
#Output: 3-dim list (like input)
#This function is part of PreprocessingStemming.py by Sara,
#were you could call it only together with other operations and
#only for a complete text file.
#Author: Thorsten, based on Sara's code
def removeStopwords(abstracts):
    from nltk.corpus import stopwords
    import nltk
    #print('start download stopword list (check other windows)')
    #nltk.download()
    #print('end download')
    stop_words = set(stopwords.words('english'))
    i=0
    while i<len(abstracts):
        j=0
        while j<len(abstracts[i]):
            k=0
            while k<len(abstracts[i][j]):
                if(abstracts[i][j][k] in stop_words):
                    del abstracts[i][j][k]
                    continue
                k+=1
            if(len(abstracts[i][j])==0):
                del abstracts[i][j]
                continue
            j+=1
        if(len(abstracts[i])==0):
            del abstracts[i]
            continue
        i+=1
    return abstracts


# In[ ]:


#Generate all features, combine them with the class labels
#and export the result into a csv file.
#The output is the input of the learner, encoding is utf-8.
#Autor: Thorsten
#import InputForFeatureGenerationAbstractWise
import ReadAbstracts
import InterpretEntities
import csv
import copy


# In[ ]:


#Imports the data
print("Start reading the abstracts.")
abstracts=ReadAbstracts.parse('1.2.test.text.xml')
print("Completed reading the abstracts.")
abstracts=filter(abstracts)
#abstracts=correct(abstracts)


# In[ ]:


#import labels
labels=[]
print("Start reading the labels.")
with open('TestTask1.2Label.csv') as csvLabels: #change file name as needed
    labs = csv.reader(csvLabels)
    for row in labs:
        row[2]=(row[2]=='True')
        labels.append(row)
print("Completed reading the labels.")


# In[ ]:


#generate the features
#first: the result lists
resultNormal=[]
#headers
resultNormal.append([])
for name in Features:
    resultNormal[0]+=[name.name]
resultStemmed=copy.deepcopy(resultNormal)
resultWithoutStopwords=copy.deepcopy(resultNormal)
resultStemmedWithoutStopwords=copy.deepcopy(resultNormal)


# In[ ]:


#data normal
#just calling the above functions is not enough, becuase also data
#about the word position (abstractNr, sentenceNr) and the label
#should be stored.
labelPosition=1 #line 0 is the header
#getMaxLen(abstracts)
for i in range(len(abstracts)):
    for j in range(len(abstracts[i])):
        sen=InterpretEntities.interpretEntities(abstracts[i][j])
        for k in sen[0]:
            #terrible, but the format must match
            #for finding in the labels and for the next pipeline steps
            sen[0][k]=sen[0][k].replace(':', '.')
        for k in range(len(abstracts[i][j])):
            tmp=[sen[1][k], i, j, k, sen[0].get(k)]
            if(sen[0].get(k)==None): #no entity
                continue
                #tmp.extend([None, None, None])
            else:
                #search in the label file for this entry
                if(labelPosition<len(labels) and labels[labelPosition][0]==sen[0][k]):
                    tmp.extend([labels[labelPosition][1], labels[labelPosition][3], labels[labelPosition][2]])
                elif(labelPosition<len(labels) and labels[labelPosition][1]==sen[0][k]):
                    tmp.extend([labels[labelPosition][0], labels[labelPosition][3], labels[labelPosition][2]])
                    labelPosition+=1
                else: #this entity is not part of a relation, no further action
                    tmp.extend([None, None, None])
            tmp.extend(generateFeatures(sen[1], k, sen[0]))
            resultNormal.append(tmp)
if(labelPosition<len(labels)):
    print('Error: Not al labels were assigned.\nlabelPosition: ', labelPosition, '\nlen(labels): ', len(labels))
    print(labels[labelPosition])
    sleep() #this WILL crash the program, but it's wanted because a bad error occured


# In[ ]:


#export
print("Start writing normal.")
with open('Features.csv', 'w', encoding='utf-8') as csvOutput: #change file name as needed
    writer=csv.writer(csvOutput, lineterminator='\n')
    for i in range(len(resultNormal)):
        writer.writerow(resultNormal[i])
print("Writing normal complete.")
del resultNormal


# In[ ]:


#without stopwords
abstractStopwords=removeStopwords(copy.deepcopy(abstracts))
#getMaxLen(abstractStopwords)
labelPosition=1
for i in range(len(abstractStopwords)):
    for j in range(len(abstractStopwords[i])):
        sen=InterpretEntities.interpretEntities(abstractStopwords[i][j])
        for k in sen[0]:
            #terrible, but the format must match
            #for finding in the labels and for the next pipeline steps
            sen[0][k]=sen[0][k].replace(':', '.')
        for k in range(len(abstractStopwords[i][j])):
            tmp=[sen[1][k], i, j, k, sen[0].get(k)]
            if(sen[0].get(k)==None):
                continue
                #tmp.extend([None, None, None])
            else:
                #search in the label file for this entry
                if(labelPosition<len(labels) and labels[labelPosition][0]==sen[0][k]):
                    tmp.extend([labels[labelPosition][1], labels[labelPosition][3], labels[labelPosition][2]])
                elif(labelPosition<len(labels) and labels[labelPosition][1]==sen[0][k]):
                    tmp.extend([labels[labelPosition][0], labels[labelPosition][3], labels[labelPosition][2]])
                    labelPosition+=1
                else: #this entity is not part of a relation, no further action
                    tmp.extend([None, None, None])
            tmp.extend(generateFeatures(sen[1], k, sen[0]))
            resultWithoutStopwords.append(tmp)
if(labelPosition<len(labels)):
    print('Error: Not al labels were assigned.\nlabelPosition: ', labelPosition, '\nlen(labels): ', len(labels))
    print(labels[labelPosition])
    sleep() #this WILL crash the program, but it's wanted because a bad error occured
del abstractStopwords#


# In[ ]:


#export
print("Start writing without stopwords.")
with open('FeaturesWithoutStopwords.csv', 'w', encoding='utf-8') as csvOutput: #change file name as needed
    writer=csv.writer(csvOutput, lineterminator='\n')
    for i in range(len(resultWithoutStopwords)):
        writer.writerow(resultWithoutStopwords[i])
print("Writing without stopwords complete.")
del resultWithoutStopwords


# In[ ]:


#stemmed
abstracts=stem(abstracts)   


# In[ ]:


labelPosition=1
#getMaxLen(abstracts)
for i in range(len(abstracts)):
    for j in range(len(abstracts[i])):
        sen=InterpretEntities.interpretEntities(abstracts[i][j])
        for k in sen[0]:
            #terrible, but the format must match
            #for finding in the labels and for the next pipeline steps
            sen[0][k]=sen[0][k].replace(':', '.')
            sen[0][k]=sen[0][k].upper()
        for k in range(len(abstracts[i][j])):
            tmp=[sen[1][k], i, j, k, sen[0].get(k)]
            if(sen[0].get(k)==None):
                continue
                #tmp.extend([None, None, None])
            else:
                #search in the label file for this entry
                if(labelPosition<len(labels) and labels[labelPosition][0]==sen[0][k]):
                    tmp.extend([labels[labelPosition][1], labels[labelPosition][3], labels[labelPosition][2]])
                elif(labelPosition<len(labels) and labels[labelPosition][1]==sen[0][k]):
                    tmp.extend([labels[labelPosition][0], labels[labelPosition][3], labels[labelPosition][2]])
                    labelPosition+=1
                else: #this entity is not part of a relation, no further action
                    tmp.extend([None, None, None])
            tmp.extend(generateFeatures(sen[1], k, sen[0]))
            resultStemmed.append(tmp)
if(labelPosition<len(labels)):
    print('Error: Not al labels were assigned.\nlabelPosition: ', labelPosition, '\nlen(labels): ', len(labels))
    print(labels[labelPosition])
    sleep() #this WILL crash the program, but it's wanted because a bad error occured


# In[ ]:


#export
print("Start writing stemmed.")
with open('FeaturesStemmed.csv', 'w', encoding='utf-8') as csvOutput: #change file name as needed
    writer=csv.writer(csvOutput, lineterminator='\n')
    for i in range(len(resultStemmed)):
        writer.writerow(resultStemmed[i])
print("Writing stemmed complete.")
del resultStemmed


# In[ ]:


#stemming + without stopwords
abstracts=removeStopwords(abstracts)
labelPosition=1
#getMaxLen(abstracts)
for i in range(len(abstracts)):
    for j in range(len(abstracts[i])):
        sen=InterpretEntities.interpretEntities(abstracts[i][j])
        for k in sen[0]:
            #terrible, but the format must match
            #for finding in the labels and for the next pipeline steps
            sen[0][k]=sen[0][k].replace(':', '.')
            sen[0][k]=sen[0][k].upper()
        for k in range(len(abstracts[i][j])):
            tmp=[sen[1][k], i, j, k, sen[0].get(k)]
            if(sen[0].get(k)==None):
                continue
                #tmp.extend([None, None, None])
            else:
                #search in the label file for this entry
                if(labelPosition<len(labels) and labels[labelPosition][0]==sen[0][k]):
                    tmp.extend([labels[labelPosition][1], labels[labelPosition][3], labels[labelPosition][2]])
                elif(labelPosition<len(labels) and labels[labelPosition][1]==sen[0][k]):
                    tmp.extend([labels[labelPosition][0], labels[labelPosition][3], labels[labelPosition][2]])
                    labelPosition+=1
                else: #this entity is not part of a relation, no further action
                    tmp.extend([None, None, None])
            tmp.extend(generateFeatures(sen[1], k, sen[0]))
            resultStemmedWithoutStopwords.append(tmp)
if(labelPosition<len(labels)):
    print('Error: Not al labels were assigned.\nlabelPosition: ', labelPosition, '\nlen(labels): ', len(labels))
    print(labels[labelPosition])
    sleep() #this WILL crash the program, but it's wanted because a bad error occured


# In[ ]:


#export
print("Start writing stemmed without stopwords.")
with open('FeaturesStemmedWithoutStopwords.csv', 'w', encoding='utf-8') as csvOutput: #change file name as needed
    writer=csv.writer(csvOutput, lineterminator='\n')
    for i in range(len(resultStemmedWithoutStopwords)):
        writer.writerow(resultStemmedWithoutStopwords[i])
print("Writing stemmed without stopwords complete.")
del resultStemmedWithoutStopwords


# In[ ]:


DB.close()


# In[ ]:


#Get the max length of all entries in abstracts[a][b][c], needed because
#entity entries can have more than one word.
#Not needed for the final program, but for getting the length of the longest entity
#what is necessary for creating the features enum and fill the features.
#Input: abstracts, 3-dim list: abstracts[abstract][sentence][word]
#Output: int: Words in the longest entity
#Author: Thorsten
def getMaxLen(abstracts):
    maxLen=0
    for i in range(len(abstracts)):
        for j in range(len(abstracts[i])):
            for k in range(len(abstracts[i][j])):
                #need to substract -1 from length because the entity tag also has a ' '
                #so it's also splitted and counted
                if(maxLen<len(abstracts[i][j][k].strip().split(' '))-1):
                    maxLen=len(abstracts[i][j][k].strip().split(' '))-1
                    print(maxLen, 'in:', i, j, k)
    return maxLen


# In[ ]:


#Help function for testing, not needed in the final program.
#Counts the words in the given "abstracts".
#Input: abstracts, 3-dim list: abstracts[abstract][sentence][word]
#Output: int: Number of words in the given abstracts
#Author: Thorsten
def countWords(abstracts):
    wordCount=0
    for i in range(len(abstracts)):
        for j in range(len(abstracts[i])):
            wordCount+=len(abstracts[i][j])
    return wordCount


# In[ ]:


#Not needed since ReadAbstracts.py is used.
#Becasue of a bug when reading using InputForFeatureGenerationAbstractWise,
#strings like '<entity id=<abstract>[some words] </entity>' occur.
#This function detects these mistakes and corrects them by replacing the "word" by a list of the right words.
#Input: abstracts, 3-dim list: abstracts[abstract][sentence][word]
#Output: abstracts, 3-dim list: abstracts[abstract][sentence][word]
#Note: Calls the filter function after the work itself is done.
def correct(abstracts):
    i=0
    while i<len(abstracts):
        j=0
        while j<len(abstracts[i]):
            k=0
            while k<len(abstracts[i][j]):
                if(abstracts[i][j][k]=='<entity id=</abstract></entity>'):
                    del abstracts[i][j][k]
                    continue
                if(abstracts[i][j][k]=='<entity'):
                    del abstracts[i][j][k]
                    continue
                if(abstracts[i][j][k]=='id=<SectionTitle/>'):
                    del abstracts[i][j][k]
                    continue
                if(abstracts[i][j][k]=='<entity id=Keywords:</abstract></entity>'):
                    del abstracts[i][j][k]
                    continue
                if(abstracts[i][j][k]=='<entity id=quot</abstract></entity>'):
                    del abstracts[i][j][k]
                    continue
                if(abstracts[i][j][k]=='<entity id= </abstract></entity>'):
                    del abstracts[i][j][k]
                    continue
                #little more complicated
                if('<entity id=<' in abstracts[i][j][k]):
                    temp=abstracts[i][j][k].replace('<entity id=<abstract>', '')
                    temp=temp.replace('</entity>', '').strip()
                    temp=temp.split(' ')
                    for l in range(len(temp)):
                        temp[l]=temp[l].strip()
                    newList=abstracts[i][j][:k]+temp+abstracts[i][j][k+1:]
                    abstracts[i][j]=newList
                    continue
                if('<entity id= ' in abstracts[i][j][k]):
                    temp=abstracts[i][j][k].replace('<entity id ', '')
                    temp=temp.replace('</abstract></entity>', '').strip()
                    temp=temp.split(' ')
                    for l in range(len(temp)):
                        temp[l]=temp[l].strip()
                    newList=abstracts[i][j][:k]+temp+abstracts[i][j][k+1:]
                    abstracts[i][j]=newList
                    continue
                k+=1
            j+=1
        i+=1    
    return filter(abstracts)

