
from Eventify.event_extraction_stanza import EventExtractor
import time
from recordtype import recordtype
from nltk.stem import WordNetLemmatizer
from FramenetData.framenetMaster import main
from Pipeline import GPT3Handler
from Pipeline.Repo import iva_scenario_translator
import neuralcoref
import en_core_web_md
from Pipeline.Repo import predpatt_output_handler

# Initializing every tool we are going to use
Data = recordtype('Data', 'original pos type length', default="")
Event = recordtype('Event', 'initiator action target location frames')
framenetData = main.main(
    "../../FramenetData/framenetMaster/fndata-1.7/fndata-1.7/")
framenetFrames = framenetData[0]
nlp = en_core_web_md.load()
lemmatizer = WordNetLemmatizer()
neuralcoref.add_to_pipe(nlp)

global EE

global events

# EE = EventExtractor(language='en', processors='tokenize, mwt, pos, lemma, depparse, ner')
EE = EventExtractor(language='en', processors='tokenize, pos, lemma, depparse')
events = {}


# The objective of this function is to retrieve frames from framenet according to the PoS of the word
def getFrames(word, type):
    frames = ""
    if (type == "VERB"):
        simpleVerb = word
        simpleVerb += ".v"
        frames = ""
        targetFrames = framenetFrames.get_frames_from_lu(simpleVerb)
        if (targetFrames):
            for f in targetFrames:
                frames += f.name + "|"

        if (frames == ''):
            actualVerb = lemmatizer.lemmatize(word)
            actualVerb += ".v"
            targetFrames = framenetFrames.get_frames_from_lu(actualVerb)
            if (targetFrames):
                for f in targetFrames:
                    frames += f.name + "|"

    elif (type == "ADJ"):
        actualAdj = word
        actualAdj += ".a"
        targetFrames = framenetFrames.get_frames_from_lu(actualAdj)
        if (targetFrames):
            for f in targetFrames:
                frames += f.name + "|"

    elif (type == "NOUN"):
        actualAdj = word
        actualAdj += ".n"
        targetFrames = framenetFrames.get_frames_from_lu(actualAdj)
        if (targetFrames):
            for f in targetFrames:
                frames += f.name + "|"
    return frames




def computeOutput(output):
    start_time = time.time()
    global events
    events = {}
    predpatt_output_handler.readPredPattOutput(output)
    events = predpatt_output_handler.events
    predPattTime = round(time.time() - start_time, 2)
    # print("----PredPatt %s seconds ---" % predPattTime)

    ## -------Framenet ---------------------##
    start_time2 = time.time()
    index = 0
    for event in events.values():
        index = 0
        while index < len(event):

            if (len(event[index]) < 1):
                continue

            # Check for the frames by getting the main verb of a sentence
            word = event[index].action.original
            type = event[index].action.pos
            event[index].frames = getFrames(word, type)
            index += 1

    frameTime = round(time.time() - start_time2, 2)
    # print("----Framenet  %s seconds ---" % frameTime)

    return events


def processCoReferences(toProcess, doc):
    corefDic = {}
    for coref in doc._.coref_clusters:
        for name in coref:

            auxKey = name.string.replace(" ", "")
            auxValue = coref.main.string.replace(" ", "")
            if (auxKey == auxValue):
                continue
            if (auxKey.lower() == 'his ' or auxKey.lower() == 'her '):
                continue
            if (auxKey in corefDic.keys() and auxValue not in corefDic[auxKey]):
                continue
            elif (auxKey not in corefDic.keys()):
                corefDic[auxKey] = auxValue

    lineIndex = 0
    originalText = toProcess
    for word in corefDic.keys():
        if (" " + word in originalText):
            originalText = originalText.replace(" " + word + " ", " " + corefDic[word] + " ")

    return originalText


def computeStory(story):
    text = ''
    story = story.split('\n')
    text = ''.join(story)
    return computeText(text)


def computeStoryFromFile(storyFilePath):
    with open(storyFilePath) as f:
        toProcess = f.readlines()
    text = ''.join(toProcess)
    text = text.replace("\n", " ")
    return computeText(text)


def computeText(text, useGpt=False):
    EE.clean()
    if useGpt:
        gptOutput = GPT3Handler.sendStory(text)
        print("GPT3 Output \n" + str(gptOutput))
    doc = nlp(text)
    # Deal with the references: His/Her etc...
    text = processCoReferences(text, doc)
    print(text)
    iva_scenario_translator.initialize()
    EE.extract(text)
    output = EE.predpatt_output
    events = computeOutput(output)
    text = text.split('.')
    originalText = []
    for e in events:
        similarityIndex = getEventIndex(e, text)
        originalText.append(text[similarityIndex])
        # print("FINAL: " + str(e) + " " + str(text[similarityIndex]))
    result = iva_scenario_translator.translate(events, originalText)
    return result


def getEventIndex(e, text):
    index = 0
    maxValue = 0
    retIndex = 0
    for t in text:
        if (len(e) < 3):
            return
        if (len(t) < 3):
            continue
        newEvent = nlp(e)
        originalEvent = nlp(t)
        value = originalEvent.similarity(newEvent)
        # print(str(newEvent) + " " + str(originalEvent) + " v: " + str(value))
        if (value > maxValue):
            maxValue = value
            retIndex = index
        index += 1
    return retIndex