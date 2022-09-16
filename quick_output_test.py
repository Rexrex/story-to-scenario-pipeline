#--------------------------------------
# Testing Scripts that according to the users Input performs different operations
# 2021, Manuel Guimarães, Lisbon, Portugal
# email: manuel.m.guimaraes@tecnico.ulisboa.pt
#-------------------------------------

from Pipeline.Repo import iva_information_extractor

def main():

    choice = input("Please select \n a) Manually write a story \n b) Pick a story from a file \n")

    if("a" in choice):

        story = input("Please write a short story: \n")
        iva_information_extractor.computeStory(story)
    else:


        number = input("Story number?: \n")

        if not isinstance(int(number), int):
            iva_information_extractor.computeStoryFromFile("../../StoryExamples/story7.txt")



        if int(number) > 0:

            iva_information_extractor.computeStoryFromFile("../../StoryExamples/story" + number + ".txt")

        else:
            iva_information_extractor.computeStoryFromFile("../../StoryExamples/story1.txt")

main()
