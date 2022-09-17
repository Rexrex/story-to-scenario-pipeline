#--------------------------------------
# Creates server to host Information Extraction and Translation Pipeline
# Supports Gets, Posts and Handshake operations. Maintains a registry of acknowledged IPs to track requests and replies
# 2021, Manuel Guimarães, Lisbon, Portugal
# email: manuel.m.guimaraes@tecnico.ulisboa.pt
#-------------------------------------

import http.server
import socketserver
import traceback
from http.server import BaseHTTPRequestHandler
import iva_information_extractor
from Pipeline import GPT3Handler

PORT = 8080
Handler = http.server.BaseHTTPRequestHandler
import json
import socket

storyData = {}
dialogData = {}

def dict_to_binary(the_dict):
    str = json.dumps(the_dict)
    binary = ' '.join(format(ord(letter), 'b') for letter in str)
    return binary


def binary_to_dict(the_binary):
    jsn = ''.join(chr(int(x, 2)) for x in the_binary.split())
    d = json.loads(jsn)
    return d

def saveToJson(domainKnowledge):
    json_object = "{"

    for agentK in domainKnowledge["Agents"].keys():
        json_object += "Agent: " + agentK + "\n"
        beliefs = domainKnowledge["Agents"][agentK].beliefs
        goals = domainKnowledge["Agents"][agentK].goals
        status = domainKnowledge["Agents"][agentK].status
        emotions = domainKnowledge["Agents"][agentK].emotions
        if len(beliefs) > 1:
            json_object += "\t Beliefs: " + beliefs + "\n"
        if len(goals) > 1:
            json_object += "\t Goals: " + goals + "\n"
        if len(status) > 1:
            json_object += "\t Status: " + status + "\n"
        if len(emotions) > 1:
            json_object += "\t Emotions: " + emotions + "\n\n"
    json_object += "}\n{"

    for actionK in domainKnowledge["Actions"].keys():
        json_object += "Action: " + actionK + " \n"
        target = domainKnowledge["Actions"][actionK].target
        target_category = domainKnowledge["Actions"][actionK].target_category
        location = domainKnowledge["Actions"][actionK].location

        if len(target) > 1:
            json_object += "\t Target: " + target + "\n"
        if len(target_category) > 1:
            json_object += "\t TargetType: " + target_category + "\n"
        if len(location) > 1:
            json_object += "\t Location: " + location + "\n\n"

    json_object += "}\n{"

    for emotionK in domainKnowledge["EmotionalRules"].keys():
        json_object += "Appraisal Rule: " + domainKnowledge["EmotionalRules"][emotionK].event + " \n"
        initiator = domainKnowledge["EmotionalRules"][emotionK].initiator
        action = domainKnowledge["EmotionalRules"][emotionK].action
        target = domainKnowledge["EmotionalRules"][emotionK].target
        appraisal_variables = domainKnowledge["EmotionalRules"][emotionK].appraisal_variables
        values = domainKnowledge["EmotionalRules"][emotionK].values
        if len(initiator) > 1:
            json_object += "\t Subject: " + initiator + "\n"
        if len(action) > 1:
            json_object += "\t Action: " + action + "\n"
        if len(target) > 1:
            json_object += "\t Target: " + target + "\n"
        if len(appraisal_variables) > 1:
            json_object += "\t AppraisalVariables: " + appraisal_variables + "\n"
        if len(values) > 1:
            json_object += "\t AppraisalVariableValues: " + values + "\n\n"

    json_object += "}\n{"


    for conceptK in domainKnowledge["Concepts"].keys():
        concept = domainKnowledge["Concepts"][conceptK]
        if len(concept) > 1:
            json_object += "Concept: " + conceptK + "=" + concept + " \n"

    json_object += "}\n{"

    for dialog in domainKnowledge["Dialogues"]:
        if len(dialog) > 1:
            json_object += "Dialogue: " + dialog + " \n"


    json_object += "}"
    return json_object


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def _set_response(self):
        try:
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
        except Exception:
            self.send_error(500, traceback.format_exc())


# Perform GET requests, creates a JSON file with the organised extracted information from the Post request
    def do_GET(self):
        try:
            self.send_response(200)
            self.end_headers()
            print("GET Request")
            origin = self.headers['User-Agent']
            print("Origin " + str(origin))

          #  self.wfile.write(b"received get request")

            if origin in storyData.keys() and storyData[origin] != "":


                storyJson = storyData[origin]

                domainKnowledge  = iva_information_extractor.computeStory(storyJson)
                #domainKnowledge  = IExtractor.computeStory("temp.txt")

                json_object = saveToJson(domainKnowledge)

                storyData.pop(origin)
                self.wfile.write(json_object.encode('utf-8'))

            elif origin in dialogData.keys() and dialogData[origin] != "":

                dialogJson = dialogData[origin]

                dialogueResult  = GPT3Handler.sendDialogue(dialogJson)
                #json_object = saveToJson(dialogueResult)
                print("Sending Dialogues" + str(dialogueResult))
                dialogData.pop(origin)
                self.wfile.write(dialogueResult.encode('utf-8'))

        except Exception:
            self.send_error(500, traceback.format_exc())


# Writes POST request content into a JSON file that is then read upon the Get request
    def do_POST(self):

        try:
            print("Received Posted")
            content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
            origin = self.headers['User-Agent']
            print("Origin " + str(origin))
            post_data = self.rfile.read(content_length)  # <--- Gets the data itself

            if(len(post_data) <2): #Checking if there is any content in the message
                print("No content")
                self.send_response(204)
                return

            elif (len(post_data) < 6): #If its a handshake message we send it back
                print("Hello")
                self.send_response(200)
                response = 'Hello, world!\n'
                self.send_header("Content-type", "text/unknown")
                self.send_header("Content-Length", len(response))
                self.end_headers()
                self.wfile.write(b"received Handshake")
                return

            post_data = post_data.decode("utf-8")

            ## Handle Output

            if('Description: ' in post_data):
                storyData[origin] = post_data
            elif('Dialogues: ' in post_data):
                dialogData[origin] = post_data


            self.send_response(200)
            response = 'Hello, world!\n'
            self.send_header("Content-type", "text/unknown")
            self.send_header("Content-Length", len(response))
            self.end_headers()
            self.wfile.write(b"response")
            self.wfile.write(b"received post request")

        except Exception:
            self.send_error(500, traceback.format_exc())

        #os.remove("temp.txt")
        return


def startServer():
    with socketserver.TCPServer(("", PORT), SimpleHTTPRequestHandler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()




## getting the hostname by socket.gethostname() method
hostname = socket.gethostname()
## getting the IP address using socket.gethostbyname() method
ip_address = socket.gethostbyname(hostname)
## printing the hostname and ip_address
print(f"Hostname: {hostname}")
print(f"IP Address: {ip_address}")

startServer()