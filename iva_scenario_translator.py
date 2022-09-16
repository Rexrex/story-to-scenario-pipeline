#--------------------------------------
# The objective of this script is to translate the information gathered in IExtractor.py into Social Agent concepts
# such as actions, beliefs, emotions and goals. It features a list: domainKnowledge that contains all information
# translated by the different methods
# 2021, Manuel Guimarães, Lisbon, Portugal
# email: manuel.m.guimaraes@tecnico.ulisboa.pt
#-------------------------------------

from recordtype import recordtype

from Pipeline.Repo import predpatt_output_handler
from Pipeline.WordLabeler import FindHypernym
from Pipeline.AppraisalLabeler import IdentifyEmotion
from Pipeline.AppraisalLabeler import TranslateIntoOCCEmotion
global domainKnowledge


def initialize():
    global domainKnowledge
    domainKnowledge = {"Agents": {}, "Concepts": {}, "Actions": {}, "EmotionalRules": {}, "Dialogues": []}


Agent = recordtype('Agent', 'beliefs status goals emotions')
Action = recordtype('Action', 'target target_category location')
EmotionRule = recordtype('Emotion', 'event initiator action target appraisal_variables values')
Emotion = recordtype('Emotion', 'event emotion initiator value target')
Status = recordtype('Status', 'name type')
Goal = recordtype('Goal', 'name type')

# Auxiliary function that prints all of the results, useful for debugging
def printResults():
    print("\n Domain Knowledge ")
    print("Agents:")
    for a in domainKnowledge["Agents"].keys():
        print(str(a))
        if len(domainKnowledge["Agents"][a].beliefs) > 0:
            print("     Beliefs: " + domainKnowledge["Agents"][a].beliefs)
        if len(domainKnowledge["Agents"][a].status) > 0:
            print("     Status: " + domainKnowledge["Agents"][a].status)
        if len(domainKnowledge["Agents"][a].goals) > 0:
            print("     Goals: " + domainKnowledge["Agents"][a].goals)
        if len(domainKnowledge["Agents"][a].emotions) > 0:
            print("     Emotions: " + domainKnowledge["Agents"][a].emotions)

    print("-------------------------------------------------------")
    print("Actions:")
    for c in domainKnowledge["Actions"].keys():
        print(str(c) + " target:" + str(domainKnowledge["Actions"][c].target) +  " type:" + str(domainKnowledge["Actions"][c].target_category) + " location:" + str(domainKnowledge["Actions"][c].location))
    print("-------------------------------------------------------")
    print("Emotional Rules:")
    for c in domainKnowledge["EmotionalRules"].keys():
        print(str(c) + " emotion:" + str(domainKnowledge["EmotionalRules"][c].event) + " initiator:"
              + str(domainKnowledge["EmotionalRules"][c].initiator) + " action:" + str(domainKnowledge["EmotionalRules"][c].action)
              + " target:" + str(domainKnowledge["EmotionalRules"][c].target + " appraisal-variable:"
                                 + str(domainKnowledge["EmotionalRules"][c].appraisal_variables) + " values:" + str(domainKnowledge["EmotionalRules"][c].values)))

        #print(str(c) + " emotion:" + str(domainKnowledge["EmotionalRules"][c].emotion) + " action:" + str(domainKnowledge["EmotionalRules"][c].action) + " target:" + str(domainKnowledge["EmotionalRules"][c].target))
    print("-------------------------------------------------------")
    print("Concepts:")
    for c in domainKnowledge["Concepts"].keys():
        print(str(c) + " - type:" + str(domainKnowledge["Concepts"][c]))

    print("-------------------------------------------------------")
    print("Dialogues:")
    for c in domainKnowledge["Dialogues"]:
        print(str(c))

# Adds an agent to the Domain Knowledgfe
def addDomainAgent(agent):
    if agent not in domainKnowledge["Agents"]:
        beliefs = {}
        status = {}
        goals = {}
        domainKnowledge["Agents"][agent] = (Agent(beliefs="", status="", goals="", emotions=""))

# Adds all the initiators from the event list to the domain Knowledge as agents
def loadAgents(events):
        for e in events:
            if e.initiator.original not in domainKnowledge["Agents"].keys():
                addDomainAgent(e.initiator.original)


# Adds Goal detailed by action to the agent
def addGoal(agent, action, target):
    self = domainKnowledge["Agents"][agent.original]
    print(agent.original + " " + action.original)
    addConcept(target.original)
    self.goals += action.original + "(" + target.original + ")" + "|"


# Adds Belief to the initiator agent
def addBelief(self, initiator, action, target):
    agent = domainKnowledge["Agents"][self.original]
    print("Add Belief: " + str(initiator) + " " + str(action) + " " + str(target))
    if(target == ""):
        return
    if(target != ""):
        result = addConcept(target.original, False)
        if(result == 'feeling'):
            addEmotion(self, target, self)
            return
        if(result == 'feeling'):
            addEmotion(self, action, target)
            return


        addConcept(target.original)
        agent.beliefs += action.original + "(" + initiator.original + "," + target.original + ")=True|"
        return

    if self.original in target.original:
        targetAux = target.original.replace(self.original, '')
        agent.beliefs += action.original + "(" + targetAux + ")=" + initiator.original + "|"
    else:
        targetAux = target.original
        agent.beliefs += action.original + "(" + targetAux + ")=" + initiator.original + "|"


def addPossession(self, target):
    agent = domainKnowledge["Agents"][self.original]
    quantity = 1
    addConcept(target.original)
    agent.beliefs += "has(" + target.original + ")=" + str(quantity) + "|"


def addEmotion(self, emotion, target):
    agent = domainKnowledge["Agents"][self.original]
    value = 5
    addConcept(target.original)
    occEmotion = TranslateIntoOCCEmotion(emotion.original)
    agent.emotions += occEmotion + "(" + target.original + ")=" + str(value) + "|"

def addStatus(self, initiator, target):
    agent = domainKnowledge["Agents"][self.original]
    addConcept(target.original)
    agent.status += "is(" + initiator.original + "," + target.original + ")=" + "True|"

def addEmotionalRule(initiator, emotion, action, target):
    event_name = initiator.original + " " + emotion.original + " " + action.original + " " + target.original
    if event_name not in domainKnowledge["EmotionalRules"].keys():
        appraisalVariable, value = IdentifyEmotion(emotion.original)
        print(str(event_name) + str(appraisalVariable) + str(value))
        domainKnowledge["EmotionalRules"][event_name] = (EmotionRule(event= event_name, initiator=initiator.original, action=action.original,
                                                                     target=target.original, appraisal_variables=appraisalVariable, values=value))

def addAction(action, target):
    if action.original not in domainKnowledge["Actions"].keys():

        if(target.type == 'location'):
            domainKnowledge["Actions"][action.original] = (Action(target=target.original, target_category="location", location=target.original))
        else:
            category = addConcept(target.original)
            domainKnowledge["Actions"][action.original] = (Action(target=target.original, target_category=category, location="*"))


def addDialogueAction(target):
    if "Speak" not in domainKnowledge["Actions"].keys():
        if(target.original == ""):
            domainKnowledge["Actions"]["Speak"] = (Action(target="Agent", target_category="Person",  location="*"))
        else:
            domainKnowledge["Actions"]["Speak"] = (Action(target=target.original, target_category="Person", location="*"))

def addDialogue(action, target, text):
    original = text.split(' ')
    index = 0

    while(target.original not in original[index]):
        index += 1
    index+=1

    dialogue = original[index:]

    if len(dialogue) < 2 :
        return

    actualDialogue = ""
    for d in dialogue:
        actualDialogue += d + " "
    actualDialogue += "."
    domainKnowledge["Dialogues"].append(actualDialogue)
    addDialogueAction(target)


def addConcept(concept, save=True):
    if concept in domainKnowledge["Agents"].keys():
        return "AGENT"
    if concept not in domainKnowledge["Concepts"].keys():
        category = FindHypernym(concept)
        if(save):
            domainKnowledge["Concepts"][concept] = category
        return category
    if(concept in domainKnowledge["Concepts"].keys()):
        return domainKnowledge["Concepts"][concept]


# Dealing with complex events such as 'John thinks Sarah is cute'
def complexEventHandler(event, originalText):
    # Main action such as John thinks
    event_frames = event[0].frames
    core_action = event[0].action
    self = event[0].initiator
    core_target = event[0].target
    #Sub action such as Sarah is cute
    sub_action = event[1].action
    sub_initiator = event[1].initiator
    sub_target = event[1].target

    if ("require" in event_frames.lower() or "desiring" in event_frames.lower()):
        addGoal(self, sub_action, sub_target)

    elif ("Experiencer_focus" in event_frames or "opinion" in event_frames.lower()):
        if(self != sub_initiator):
            addBelief(self, sub_initiator, sub_action, sub_target)
        else:
            addAction(sub_action, sub_target)
            addEmotionalRule(self, core_action, sub_action, sub_target)

    elif ("Speak" in event_frames or "Questioning" in event_frames  or "Communication" in event_frames):
        addDialogue(sub_action, sub_target, originalText)


# Dealing with simple events such as 'John goes to the beach'
def eventHandler(event, originalText):

    event_frames = event.frames
    action = event.action
    initiator = event.initiator
    target = event.target
    print(str(action.original) + "  frames:" + str(event_frames))
    # Goal related Event
    if ("require" in event_frames.lower() or "desiring" in event_frames.lower()):
        addGoal(initiator, action, target)

    elif ("Experiencer_focus" in event_frames or "opinion" in event_frames.lower()):
        addBelief(initiator, initiator, action, target)

    elif ("Emotion" in event_frames):
        addEmotion(initiator, action, target)

    elif "possession" in event_frames.lower():
        addPossession(initiator, target)

    elif ("performers" in event_frames.lower()):  ## Status, there are different types of beliefs
        addStatus(initiator, initiator, target)

    elif ("Speak" in event_frames or "Questioning" in event_frames  or "Communication" in event_frames):
        addDialogue(action, target, originalText)

    else:
            addAction(action, target)


# Main translator function that calls the event handler and tries to translate each event
def translate(events, originalText):
    print("-------Translator-------")
    loadAgents(events)
    index = 0
    for event in events:

        if (event.target.type != "complex"):
            eventHandler(event, originalText[index])
        else:
            complexEventHandler(event, originalText[index])
        index+= 1
    printResults()
    return domainKnowledge