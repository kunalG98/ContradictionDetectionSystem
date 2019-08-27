import spacy
from nltk.corpus import wordnet
#nlp = spacy.load('en')
from spacy import displacy
from collections import Counter
import en_core_web_sm
from nltk.tokenize import word_tokenize

import sys
from collections import defaultdict

from pprint import pprint

_do_print_debug_info = False

def _print_table(rows):
    col_widths = [max(len(s) for s in col) for col in zip(*rows)]
    fmt = ' '.join('%%-%ds' % width for width in col_widths)
    rows.insert(1, ['─' * width for width in col_widths])
    for row in rows:
        # Uncomment this version to see code points printed out (for debugging).
        # print(list(map(hex, map(ord, list(fmt % tuple(row))))))
        print(fmt % tuple(row))

def _start_end(arrow):
    start, end = arrow['from'].i, arrow['to'].i
    mn = min(start, end)
    mx = max(start, end)
    return start, end, mn, mx

def print_parse_info(nlp, sent):
    """ Print the dependency tree of `sent` (sentence), along with the lemmas
        (de-inflected forms) and parts-of-speech of the words.

        The input `sent` is expected to be a unicode string (of type unicode in
        Python 2; of type str in Python 3). The input `nlp` (for natural
        language parser) is expected to be the return value from a call to
        spacy.load(), in other words, it's the callable instance of a spacy
        language model.
    """

    unicode_type = unicode if sys.version_info[0] < 3 else str
    assert type(sent) is unicode_type    
# Parse our sentence.
    doc = nlp(sent)

    # Build a list of arrow heights (distance from tokens) per token.
    heights = [[] for token in doc]

    # Build the arrows.

    # Set the from and to tokens for each arrow.
    arrows = [{'from': src, 'to': dst, 'underset': set()}
              for src in doc
              for dst in src.children]

    # Set the base height; these may increase to allow room for arrowheads after this.
    arrows_with_deps = defaultdict(set)
    for i, arrow in enumerate(arrows):
        if _do_print_debug_info:
            print('Arrow %d: "%s" -> "%s"' % (i, arrow['from'], arrow['to']))
        num_deps = 0
        start, end, mn, mx = _start_end(arrow)
        for j, other in enumerate(arrows):
            if arrow is other:
                continue
            o_start, o_end, o_mn, o_mx = _start_end(other)
            if ((start == o_start and mn <= o_end <= mx) or
                (start != o_start and mn <= o_start <= mx)):
                num_deps += 1
                if _do_print_debug_info:
                    print('%d is over %d' % (i, j))
                arrow['underset'].add(j)
        arrow['num_deps_left'] = arrow['num_deps'] = num_deps
        arrows_with_deps[num_deps].add(i)

    if _do_print_debug_info:
        print('')
        print('arrows:')
        pprint(arrows)

        print('')
        print('arrows_with_deps:')
        pprint(arrows_with_deps)    
# Render the arrows in characters. Some heights will be raised to make room for arrowheads.

    lines = [[] for token in doc]
    num_arrows_left = len(arrows)
    while num_arrows_left > 0:

        assert len(arrows_with_deps[0])

        arrow_index = arrows_with_deps[0].pop()
        arrow = arrows[arrow_index]
        src, dst, mn, mx = _start_end(arrow)

        # Check the height needed.
        height = 3
        if arrow['underset']:
            height = max(arrows[i]['height'] for i in arrow['underset']) + 1
        height = max(height, 3, len(lines[dst]) + 3)
        arrow['height'] = height

        if _do_print_debug_info:
            print('')
            print('Rendering arrow %d: "%s" -> "%s"' % (arrow_index,
                                                        arrow['from'],
                                                        arrow['to']))
            print('  height = %d' % height)

        goes_up = src > dst

        # Draw the outgoing src line.
        if lines[src] and len(lines[src]) < height:
            lines[src][-1].add('w')
        while len(lines[src]) < height - 1:
            lines[src].append(set(['e', 'w']))
        if len(lines[src]) < height:
            lines[src].append({'e'})
        lines[src][height - 1].add('n' if goes_up else 's')

        # Draw the incoming dst line.
        lines[dst].append(u'►')
        while len(lines[dst]) < height:
            lines[dst].append(set(['e', 'w']))
        lines[dst][-1] = set(['e', 's']) if goes_up else set(['e', 'n'])
    
    
 # Draw the adjoining vertical line.
        for i in range(mn + 1, mx):
            while len(lines[i]) < height - 1:
                lines[i].append(' ')
            lines[i].append(set(['n', 's']))

        # Update arrows_with_deps.
        for arr_i, arr in enumerate(arrows):
            if arrow_index in arr['underset']:
                arrows_with_deps[arr['num_deps_left']].remove(arr_i)
                arr['num_deps_left'] -= 1
                arrows_with_deps[arr['num_deps_left']].add(arr_i)

        num_arrows_left -= 1

    arr_chars = {'ew'  : u'─',
                 'ns'  : u'│',
                 'en'  : u'└',
                 'es'  : u'┌',
                 'enw' : u'┴',
                 'ensw': u'┼',
                 'esw' : u'┬'}

# Convert the character lists into strings.
    max_len = max(len(line) for line in lines)
    for i in range(len(lines)):
        lines[i] = [arr_chars[''.join(sorted(ch))] if type(ch) is set else ch for ch in lines[i]]
        lines[i] = ''.join(reversed(lines[i]))
        lines[i] = ' ' * (max_len - len(lines[i])) + lines[i]

# Compile full table to print out.
    rows = [['Dep tree', 'Token', 'Dep type', 'Lemma', 'Part of Sp']]
    for i, token in enumerate(doc):
        rows.append([lines[i], token, token.dep_, token.lemma_, token.pos_])
    _print_table(rows)
    
#Antonyms finder function
synonyms = []
antonyms = []
#word="went"
def antysyn(word):
    from nltk.corpus import wordnet
    for syn in wordnet.synsets(word):
        #print(syn)
        for l in syn.lemmas():
            #print(l)
            synonyms.append(l.name())
            if l.antonyms():
                antonyms.append(l.antonyms()[0].name())
    #print("Synonym:",set(synonyms))
    print("Antonym:",set(antonyms))
    
#Taking the sentences as input
#sent1=input("Input the first sentence:")
#sent2=input("Input the second sentence:")
nlp = en_core_web_sm.load()
sent1="I slept till noon."
sent2="I woke up early in the morning."
print_parse_info(nlp,sent1)
print("\n")
print_parse_info(nlp,sent2)
doc1 = nlp(sent1)
doc2 = nlp(sent2)

#Initializing required variables and lists.
wrdlist=list()
antony=list()
contr_tracker=0
antonym_tracker=0

negdoc1=0
negdoc2=0
verb1=""
verb2=""
num_contr_tracker=0

#Processing sentence 1
for token in doc1:
    if(token.dep_=="neg"):
        negdoc1=1
        verb1+="NOT "
    #Storing the antonyms of root words
    if(token.pos_=="VERB" and token.dep_=="ROOT"):
        print(token.text)
        verb1+=token.lemma_
        antysyn(token.lemma_)
        for anton in antonyms:
            antony.append(anton)

#Processing Sentence 2
for token in doc2:
    if(token.dep_=="neg"):
        negdoc2=1
        verb2+="NOT "
    if(token.pos_=="VERB" and token.dep_=="ROOT"):
        verb2+=token.lemma_
        if(token.lemma_ in antony):
            antonym_tracker=1

#Function for checking negation
def checknegationcontradiction(antonym_tracker,negdoc1,negdoc2):
    temp_var=negdoc1+negdoc2+antonym_tracker
    if(temp_var%2!=0 and temp_var<3):
        return 1
    else:
        return 0
    
#Checking contradiction due to negation
contr_tracker=checknegationcontradiction(antonym_tracker,negdoc1,negdoc2)

#Finding numerical mismatch
checklist_more=['more than ', 'greater than ', 'above']
checklist_less=['less than ', 'lesser than ', 'below']

def check_words(doc):
    merged_word=""
    #tokens = word_tokenize(doc)
    WordNum  = len(doc)
    print("WordNum is:"+str(WordNum))
    for i in range(WordNum):
        print(i,doc[i],doc[i].ent_type_)
        print(str.isdigit(doc[i].text))
        if(doc[i].ent_type_=="CARDINAL" or doc[i].pos_=="NUM"):
             merged_word = doc[i].text
        if((doc[i].ent_type_=="CARDINAL" or doc[i].pos_=="NUM") and str.isdigit(doc[i].text)):
            if(not(str.isdigit(doc[i-1].text))):
                if(not(str.isdigit(doc[i-2].text))):
                    merged_word= doc[i-2].text+' '+doc[i-1].text+' '+doc[i].text
    return merged_word

def check_values(t1,t2):
    for phrase in checklist_more:
        if(t1.find(phrase)!=-1 and t2.find(phrase)==-1):
            num1 = t1.replace(phrase,'')
            num2 = [int(s) for s in str.split(t2) if s.isdigit()]
            num2=num2[0]
            if int(num1)>num2:
                print("case1")
                return('Contradiction')
            else:
                return("No Contradiction")
        else:
            return("No Contradiction")
    for phrase in checklist_more:
        if(t2.find(phrase)!=-1 and t1.find(phrase)==-1):
            num2 = t2.replace(phrase,'')
            num1 = [int(s) for s in str.split(t2) if s.isdigit()]
            num1=num1[0]
            if int(num2)>num1:
                print("case2")
                return('Contradiction') 
            else:
                return("No Contradiction")
        else:
            return("No Contradiction")
    for phrase in checklist_less:
        if(t1.find(phrase)!=-1 and t2.find(phrase)==-1):
            num1 = t1.replace(phrase,'')
            num2 = [int(s) for s in str.split(t2) if s.isdigit()]
            num2=num2[0]
            if int(num1)<num2:
                print("case3")
                return('Contradiction')
            else:
                return("No Contradiction")
        else:
                return("No Contradiction")
    for phrase in checklist_less:
        if(t2.find(phrase)!=-1 and t1.find(phrase)==-1):
            num2 = t2.replace(phrase,'')
            num1 = [int(s) for s in str.split(t2) if s.isdigit()]
            num1=num1[0]
            if int(num1)>num2:
                print("case4")
                return('Contradiction')
            else: 
                return("No Contradiction")
        else:
                return("No Contradiction")
    else:
        if(t1!=t2):
            return('Contradiction')
            

x1 = check_words(doc1)
print(x1)

y1 = check_words(doc2)
print("Second Sentence:",y1)

number_contr_tracker=check_values(x1,y1)
if(number_contr_tracker=='Contradiction'):
    num_contr_tracker=1
else:
    num_contr_tracker=0

if contr_tracker==1:
    print("\n","->",verb1.upper(),"and",verb2.upper(),"can't happen simultaneously.")
    print("->Antonymity/Negation contradiction FOUND.")
else:
    print("\n->Antonymity/Negation contradiction NOT found.")

if num_contr_tracker==1:
    print("->Numeric Mismatch Contradiction FOUND.")
else:
    print("->Numeric Mismatch Contradiction NOT Found.")
