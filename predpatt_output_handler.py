
import en_core_web_md
from recordtype import recordtype


nlp = en_core_web_md.load()
Data = recordtype('Data', 'original pos type length', default="")
Event = recordtype('Event', 'initiator action target location frames')
global events
events = {}

def addEventToList(initiator, action, target, location, connectedEvent, connectedEventName):
    global events
    print(str(initiator) + " " + str(action) + " " + str(target))
    if (target != "" and initiator!= ""):
        event = initiator.original + " " + action.original + " " + target.original
    else:
        event = initiator.original + " " + action.original + connectedEventName

    if (event not in events.keys()):
        events[event] = []
        events[event].append(Event(initiator=initiator, action=action, target=target, location=location, frames=""))
        if connectedEventName != "":
            events[event].append(connectedEvent)
        action = ""
        target = ""



#Compute complex events  example: "Peter loves going to the park"
def ComputeComplexEvent(core, event, mainInitiator, mainAction, mainTarget, mainLocation):
    secondaryInitiator = ""
    secondaryAction = ""
    secondaryTarget = ""
    secondaryLocation = ""
    complements = ""
    print("Event: " + str(event))
    for i in event.instances[1:]:
        for arg in i.arguments:

            if (arg.root.gov_rel == 'nsubj'):
                agentText = arg.root.text
                secondaryInitiator = Data(original=agentText, pos=arg.root.tag, type='initiator',
                                          length=len(agentText.split(' ')))

            elif (arg.root.gov_rel == 'obl'):
                locationText = arg.root.text
                secondaryLocation = Data(original=locationText, pos=arg.root.tag, type='location',
                                         length=len(locationText.split(' ')))
                if (secondaryTarget == ""):
                    secondaryTarget = secondaryLocation

            elif arg.root.gov_rel == 'obj':
                targetText = arg.root.text
                secondaryTarget = Data(original=targetText, pos=arg.root.tag, type='target',
                                       length=len(targetText.split(' ')))

        if (i.root.gov_rel == 'root' or i.root.gov_rel == 'conj' or 'comp' in i.root.gov_rel):
            if (i.root.tag == "ADJ" or i.root.tag == "NOUN"):  # Catching 'is' statements
                posAction = "VERB"
                secondaryAction = Data(original="be", pos=posAction, type='root', length=len("be"))
                secondaryTarget = Data(original=i.root.text, pos=i.root.tag, type='target',
                                       length=len(i.root.text.split(' ')))
            else:
                action = i.root.text
                doc = nlp(action)
                action = doc[0].lemma_
                posAction = i.root.tag
                for dep in i.root.dependents:
                    complements += " " + dep.dep.text
                    complements += " " + i.root.text

                secondaryAction = Data(original=action, pos=posAction, type='root', length=len(i.root.text.split(' ')))

    if secondaryInitiator == '' and secondaryTarget != '':
        secondaryInitiator = secondaryTarget
    elif secondaryInitiator == '' and secondaryTarget == '' and secondaryAction != '':
        secondaryInitiator = secondaryAction

    if (mainTarget == "" and secondaryTarget != ""):
        mainTarget = Data(original="CONNECTED", pos="comp", type='comp', length=5)
        eventName = mainInitiator.original + " " + mainAction.original + " " + secondaryAction.original + " " + secondaryTarget.original
        connectedEvent = Event(initiator=secondaryInitiator, action=secondaryAction, target=secondaryTarget,
                               location=secondaryLocation, frames="")
        connectedEventName = eventName
        addEventToList(mainInitiator, mainAction, mainTarget, mainLocation, connectedEvent, connectedEventName)

    if (mainTarget == "" and secondaryTarget == ""):
        mainTarget = Data(original="something", pos="comp", type='comp', length=1)
        secondaryTarget = Data(original="somewhere", pos="noun", type='target',
                               length=1)
        eventName = mainInitiator.original + " " + mainAction.original + " " + secondaryAction.original + " " + secondaryTarget.original
        connectedEvent = Event(initiator=secondaryInitiator, action=secondaryAction, target=secondaryTarget,
                               location=secondaryLocation, frames="")
        connectedEventName = eventName
        addEventToList(mainInitiator, mainAction, mainTarget, mainLocation, connectedEvent, connectedEventName)



    eventName = mainInitiator.original + " " + mainAction.original + " " + mainTarget.original
    connectedEvent = Event(initiator=secondaryInitiator, action=secondaryAction, target=secondaryTarget,
                           location=secondaryLocation, frames="")
    connectedEventName = eventName
    addEventToList(mainInitiator, mainAction, mainTarget, mainLocation, connectedEvent, connectedEventName)


def ComputeCorePredicate(core, event):
    initiator = ""
    action = ""
    target = ""
    location = ""
    connectedEvent = ""
    connectedEventName = ""
    root = core.root.text
    doc = nlp(root)
    root = doc[0].lemma_
    complex = False
    action = Data(original=root, pos=core.root.tag, type='root', length=len(root.split(' ')))

    for arg in core.arguments:

        if (arg.root.gov_rel == 'nsubj'):
            agentText = arg.root.text
            initiator = Data(original=agentText, pos=arg.root.tag, type='initiator', length=len(agentText.split(' ')))

        elif (arg.root.gov_rel == 'obl'):
            locationText = arg.root.text
            location = Data(original=locationText, pos=arg.root.tag, type='location',
                            length=len(locationText.split(' ')))
            if target == "":
                target = location

        elif arg.root.gov_rel == 'obj':
            targetText = arg.root.text
            target = Data(original=targetText, pos=arg.root.tag, type='target', length=len(targetText.split(' ')))

        elif 'comp' in arg.root.gov_rel:
            complex = True
            ComputeComplexEvent(core, event, initiator, action, target, location)
            # aux[index - 1] += "CCOMP[" + str(index) + "]"
    if not complex:
        ## lets make sure nothing is missing

        if initiator == '' and target != '':
            initiator = target

        addEventToList(initiator, action, target, location, connectedEvent, connectedEventName)


def ComputeCoreAdjNoun(core):
    initiator = ""
    action = ""
    target = ""
    location = ""
    # How do we separate "is angry at John" and "Sarah is cute" let's go for the amount of arguments
    if len(core.arguments) == 2:
        action = core.root.text
        initiator = core.arguments[0].root.text
        target = core.arguments[1].root.text
        action = Data(original=action, pos=core.root.tag, type='root', length=1)
        initiator = Data(original=initiator, pos=core.arguments[0].root.tag, type='initiator',
                         length=len(initiator.split(' ')))
        target = Data(original=target, pos=core.arguments[1].root.tag, type='target', length=len(target.split(' ')))

    elif len(core.arguments) == 1:
        root = "be"
        action = Data(original=root, pos='VERB', type='root', length=1)

        targetText = core.root.text
        target = Data(original=targetText, pos=core.root.tag, type='target', length=len(targetText.split(' ')))

        #how to find the initiator:
        for arg in core.arguments:
            if (arg.root.gov_rel == 'nsubj'):
                agentText = arg.root.text
                initiator = Data(original=agentText, pos=arg.root.tag, type='initiator',
                                 length=len(agentText.split(' ')))

        # If there is still no initiator we have to go deeper
        if "" == initiator:
            for dep in core.arguments[0].root.dependents:
                if (arg.root.gov_rel == 'nsubj'):
                    agentText = arg.root.text
                    initiator = Data(original=agentText, pos=arg.root.tag, type='initiator',
                                     length=len(agentText.split(' ')))

    if(initiator != ""):
        addEventToList(initiator, action, target, "", "", "")


# Read complete analysis to the PredPatt's output
def readPredPattOutput(output):
    # trying to extract event from text, all events have an initiator, an action and a target. Additionally they might have a location
    for event in output:
        for core in event.instances:  # Is is a complex event?
            # If core is a verb we can assume stuff
            if core.root.tag == 'VERB':
                ComputeCorePredicate(core, event)
            # Sometimes PredPatt is dumb and the root of an event is either an Adjective or a Noun
            elif core.root.tag == 'ADJ' or core.root.tag == 'NOUN':
                ComputeCoreAdjNoun(core)
