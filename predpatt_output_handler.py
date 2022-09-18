import en_core_web_md
from recordtype import recordtype

nlp = en_core_web_md.load()
Data = recordtype('Data', 'original pos type', default="")
Event = recordtype('Event', 'initiator action target aux type frames')
global events
events = []


def addEventToList(event):
    global events
    events.append(event)


# Read complete analysis to the PredPatt's output
def readPredPattOutput(output):
    # trying to extract event from text, all events have an initiator, an action and a target. Additionally they might have a location
    for event in output:
        if len(event.instances) > 0:
            addEventToList(EventOutputHandler(event, 0))


def EventOutputHandler(event, currentIndex):
    core = event.instances[currentIndex]
    if core.root.tag == 'VERB':
        return ComputeCorePredicate(core, currentIndex, event)
    # Sometimes PredPatt is dumb and the root of an event is either an Adjective or a Noun
    elif core.root.tag == 'ADJ' or core.root.tag == 'NOUN':
        return ComputeCoreAdjNoun(core, currentIndex, event)


def ComputeCorePredicate(core, currentIndex, event):
    initiator = ""
    root = core.root.text
    doc = nlp(root)
    root = doc[0].lemma_

    # John goes to the movies
    # root: goes
    # Arguments: John | movies
    # How to handle basic cases: Start with the root

    action = Data(original=root, pos=core.root.tag, type='root')

    # What happens when there is only one argument
    if (len(core.arguments) == 1):
        arg1 = core.arguments[0]
        initatorText = arg1.root.text
        initiator = Data(original=initatorText, pos=arg1.root.tag, type='initiator')
        target = Data(original="something", pos="NOUN", type='target')

    elif (len(core.arguments) == 2):

        arg1 = core.arguments[0]
        arg2 = core.arguments[1]

        initiator = Data(original=arg1.root.text, pos=arg1.root.tag, type='initiator')

        # OBL is a location
        if (arg2.root.gov_rel == 'obl'):
            targetText = arg2.root.text
            target = Data(original=targetText, pos=arg2.root.tag, type='location')
        # OBJ is a noun
        elif arg2.root.gov_rel == 'obj':
            targetText = arg2.root.text
            target = Data(original=targetText, pos=arg2.root.tag, type='object')

        elif 'comp' in arg2.root.gov_rel:
            # complex event
            evenAux = EventOutputHandler(event, currentIndex + 1)
            return Event(initiator=initiator, action=action, target=evenAux, aux="", type="complex", frames="")

    elif (len(core.arguments) == 3):

        arg1 = core.arguments[0]
        arg2 = core.arguments[1]
        arg3 = core.arguments[0]

        initiator = Data(original=arg1.root.text, pos=arg1.root.tag, type='initiator')

        # OBL is a location
        if (arg2.root.gov_rel == 'obl'):
            targetText = arg2.root.text
            target = Data(original=targetText, pos=arg2.root.tag, type='location')
        # OBJ is a noun
        elif arg2.root.gov_rel == 'obj':
            targetText = arg2.root.text
            target = Data(original=targetText, pos=arg2.root.tag, type='object')

        elif 'comp' in arg2.root.gov_rel:
            # complex event
            evenAux = EventOutputHandler(event, currentIndex + 1)
            return Event(initiator=initiator, action=action, target=evenAux, aux="", type="complex", frames="")

        else:
            targetText = arg2.root.text
            target = Data(original=targetText, pos=arg2.root.tag, type='unknown')
            auxText = arg3.root.text
            aux = Data(original=auxText, pos=arg3.root.tag, type='unknown')
            return Event(initiator=initiator, action=action, target=target, aux=aux, type="simple", frames="")

    return Event(initiator=initiator, action=action, target=target, aux="", type="simple", frames="")


def ComputeCoreAdjNoun(core, currentIndex, event):
    initiator = ""
    action = ""
    target = ""
    # How do we separate "is angry at John" and "Sarah is cute" let's go for the amount of arguments
    if len(core.arguments) == 1:
        root = "be"
        action = Data(original=root, pos='VERB', type='root')

        targetText = core.root.text
        target = Data(original=targetText, pos=core.root.tag, type='target')

        # how to find the initiator:
        for arg in core.arguments:
            if (arg.root.gov_rel == 'nsubj'):
                agentText = arg.root.text
                initiator = Data(original=agentText, pos=arg.root.tag, type='initiator')

        # If there is still no initiator we have to go deeper
        if "" == initiator:
            for dep in core.arguments[0].root.dependents:
                if (arg.root.gov_rel == 'nsubj'):
                    agentText = arg.root.text
                    initiator = Data(original=agentText, pos=arg.root.tag, type='initiator')

    if len(core.arguments) == 2:
        arg1 = core.arguments[0]
        arg2 = core.arguments[1]
        action = Data(original=core.root.text, pos=core.root.tag, type='root')
        initiator = Data(original=arg1.root.text, pos=arg1.root.tag, type='initiator')

        # OBL is a location
        if (arg2.root.gov_rel == 'obl'):
            targetText = arg2.root.text
            target = Data(original=targetText, pos=arg2.root.tag, type='location')

        # OBJ is a noun
        elif arg2.root.gov_rel == 'obj':
            targetText = arg2.root.text
            target = Data(original=targetText, pos=arg2.root.tag, type='object')

        elif 'comp' in arg2.root.gov_rel:
            ## Handle Complex Events
            evenAux = EventOutputHandler(event, currentIndex + 1)
            return Event(initiator=initiator, action=action, target=evenAux, aux="", type="complex", frames="")

        else:
            targetText = arg2.root.text
            target = Data(original=targetText, pos=arg2.root.tag, type='unknown')


    elif len(core.arguments) == 3:

        arg1 = core.arguments[0]
        arg2 = core.arguments[1]
        arg3 = core.arguments[0]

        initiator = Data(original=arg1.root.text, pos=arg1.root.tag, type='initiator')

        # OBL is a location
        if (arg2.root.gov_rel == 'obl'):
            targetText = arg2.root.text
            target = Data(original=targetText, pos=arg2.root.tag, type='location')
        # OBJ is a noun
        elif arg2.root.gov_rel == 'obj':
            targetText = arg2.root.text
            target = Data(original=targetText, pos=arg2.root.tag, type='object')

        elif 'comp' in arg2.root.gov_rel:
            # complex event
            evenAux = EventOutputHandler(event, currentIndex + 1)
            return Event(initiator=initiator, action=action, target=evenAux, aux="", type="complex", frames="")

        else:
            targetText = arg2.root.text
            target = Data(original=targetText, pos=arg2.root.tag, type='unknown')

            auxText = arg3.root.text
            aux = Data(original=auxText, pos=arg3.root.tag, type='unknown')
            return Event(initiator=initiator, action=action, target=target, aux=aux, type="simple", frames="")

    return Event(initiator=initiator, action=action, target=target, aux="", type="simple", frames="")
