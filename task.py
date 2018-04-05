
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from pdfminer.converter import PDFPageAggregator
from PDFToTextConverter import convertPDFToText

import re

import nltk
from nltk.corpus import stopwords

stopwords = stopwords.words('english')

fileLocation = "C:/Users/Ramkumar/Downloads/Nikila_Radhakrishnan.pdf"
password = ""
pageData = ""
filepointer = open(fileLocation, "rb")
parser = PDFParser(filepointer)
    
    # Store parsed data in PDFDocument object
document = PDFDocument(parser, password)
    
    # Create PDFResourceManager object 
rsrcmgr = PDFResourceManager()
    
    # Set analysis parameters
laparams = LAParams()
    
    # Translates interpreted information into desired format
device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    
    # Create interpreter object to process page content from PDFDocument
interpreter = PDFPageInterpreter(rsrcmgr, device)
    
for page in PDFPage.create_pages(document):
    	interpreter.process_page(page)
    	layout = device.get_result()
    	for layoutObj in layout:
    		if isinstance(layoutObj, LTTextBox) or isinstance(layoutObj, LTTextLine):
    			pageData += layoutObj.get_text()
#print(pageData)

pdfContent = pageData

def extract_contacts(pageData):
    
    r = re.compile(r'([+(]?\d+[)\-]?[ \t\r\f\v]*[(]?\d{2,}[()\-]?[ \t\r\f\v]*\d{2,}[()\-]?[ \t\r\f\v]*\d*[ \t\r\f\v]*\d*[ \t\r\f\v]*)')
    match = r.findall(pdfContent)

    # Used to match mobile numbers like (91) 1234567890 or +91 0987654321 or 91 98765 43210
    match = [re.sub(r'[,.]', '', el) for el in match if len(re.sub(r'[()\-.,\s+]', '', el))>6]
    match = [re.sub(r'\D$', '', el).strip() for el in match]
    match = [el for el in match if len(re.sub(r'\D','',el)) <= 15]
    try:
        for el in list(match):
            if len(el.split('-')) > 3: continue # Remove years
            for x in el.split("-"):
                try:
                    # Error catching for non-number characters
                    if x.strip()[-4:].isdigit():
                        if int(x.strip()[-4:]) in range(1900, 2100):
                            match.remove(el)
                except:
                    pass
    except:
        pass
    number = match
    return match

def extract_email_addresses(pageData):
    r = re.compile(r'[\w\.-]+@[\w\.-]+')
    return r.findall(pageData)


def extract_names(inputString):
        infoDict = {}
        # Reads names from namesdataset.txt
        indianNames = open("C:/Users/Ramkumar/Desktop/college/VI_SEM/bitgram task/namesDataset.txt", "r").read().lower()
        indianNames = set(indianNames.split())
        

        otherNameHits = []
        nameHits = []
        name = None

        try:
            #tokens, lines, sentences = tokens, lines, sentences
            # Try a regex chunk parser
            # grammar = r'NAME: {<NN.*><NN.*>|<NN.*><NN.*><NN.*>}'
            grammar = r'NAME: {<NN.*><NN.*><NN.*>*}'
            # Noun phrase chunk is made out of two or three tags of type NN. (ie NN, NNP etc.) - typical of a name. {2,3} won't work, hence the syntax
            # Note the correction to the rule. Change has been made later.
            chunkParser = nltk.RegexpParser(grammar)
            all_chunked_tokens = []
            for tagged_tokens in lines:
                # Creates a parse tree
                if len(tagged_tokens) == 0: continue # Prevent it from printing warnings
                chunked_tokens = chunkParser.parse(tagged_tokens)
                all_chunked_tokens.append(chunked_tokens)
                for subtree in chunked_tokens.subtrees():
                    #  or subtree.label() == 'S' include in if condition if required
                    if subtree.label() == 'NAME':
                        for ind, leaf in enumerate(subtree.leaves()):
                            if leaf[0].lower() in indianNames and 'NN' in leaf[1]:
                                # Case insensitive matching, as names in lowercase
                                # Take only noun-tagged toke
                                # Pick upto 3 noun entities
                                hit = " ".join([el[0] for el in subtree.leaves()[ind:ind+3]])
                                # Check for the presence of commas, colons, digits - usually markers of non-named entities 
                                if re.compile(r'[\d,:]').search(hit): continue
                                nameHits.append(hit)
                                # Need to iterate through rest of the leaves because of possible mis-matches
            # Going for the first name hit
            if len(nameHits) > 0:
                nameHits = [re.sub(r'[^a-zA-Z \-]', '', el).strip() for el in nameHits] 
                name = " ".join([el[0].upper()+el[1:].lower() for el in nameHits[0].split() if len(el)>0])
                otherNameHits = nameHits[1:]

        except Exception as e:
            #print (e)
            print (e)         

        
        return name

def preprocess(document):
        #print(document)
        #print(document.encode('ascii','ignore'))
        try:
            print("Ulla iruken")
            #document = document.decode()
            print(document)
            # Avoid special characters
            # Newlines are one element of structure in the data
            # Helps limit the context and breaks up the data as is intended in resumes - i.e., into points
            lines = [el.strip() for el in document.split("\\n") if len(el) > 0]  # Splitting on the basis of newlines 
            lines = [nltk.word_tokenize(el) for el in lines]    # Tokenize the individual lines
            lines = [nltk.pos_tag(el) for el in lines]
            print(lines)
            # Below approach is slightly different because it splits sentences not just on the basis of newlines, but also full stops 
            #currently using it only for tokenization of the whole document
            sentences = nltk.sent_tokenize(document)    # Split/Tokenize into sentences (List of strings)
            sentences = [nltk.word_tokenize(sent) for sent in sentences]    # Split/Tokenize sentences into words (List of lists of strings)
            tokens = sentences
            print(tokens)
            sentences = [nltk.pos_tag(sent) for sent in sentences]    # Tag the tokens - list of lists of tuples - each tuple is (<word>, <tag>)
            # Next 4 lines convert tokens from a list of list of strings to a list of strings; basically stitches them together
            dummy = []
            for el in tokens:
                dummy += el
            tokens = dummy
            # tokens - words extracted from the doc, lines - split only based on newlines (may have more than one sentence)
            # sentences - split on the basis of rules of grammar
            return tokens, lines, sentences
        except Exception as e:
            print("Error here")
            print (e) 

def tokenize(pdfContent):
        try:
            tokens, lines, sentences = preprocess(pdfContent)
            return tokens, lines, sentences
        except Exception as e:
            print (e)



def ie_preprocess(document):
    document = ' '.join([i for i in document.split() if i not in stopwords])
    sentences = nltk.sent_tokenize(document)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    sentences = [nltk.pos_tag(sent) for sent in sentences]
    return sentences

def extractas_names(document):
    names = []
    sentences = ie_preprocess(document)
    for tagged_sentence in sentences:
        for chunk in nltk.ne_chunk(tagged_sentence):
            if type(chunk) == nltk.tree.Tree:
                if chunk.label() == 'PERSON':
                    names.append(' '.join([c[0] for c in chunk]))
    return names

if __name__ == '__main__':
    inputString = convertPDFToText(fileLocation)
    print(inputString)
    tokens, lines, sentences = tokenize(inputString)
    
    numbers = extract_contacts(pageData)
    emails = extract_email_addresses(pageData)
    names = extract_names(pageData)

print("Name: ",names)
print("E-mail: ",emails)
print("Phone: ",numbers)
