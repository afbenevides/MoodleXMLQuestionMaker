__author__ = 'johanhenkens'
import sys, argparse
from xml.dom.minidom import *

class XMLNode:
    def __init__(self,nodetype,attrDict={},children=[],value='',cdata=False):
        self.nodetype = nodetype
        self.attributesDictionary = attrDict
        self.children = children
        self.value = value
        self.cdata = cdata

    def toXMLElement(self,xmlDocument):
        result = xmlDocument.createElement(self.nodetype)
        for key in self.attributesDictionary.keys():
            result.setAttribute(key,self.attributesDictionary[key])
        if self.nodetype == 'text' or len(self.value)>0:
            temp = Text()
            if self.cdata and len(self.value)>0:
                temp=CDATASection()
            temp.data = self.value
            result.appendChild(temp)
        for child in self.children:
            result.appendChild(child.toXMLElement(xmlDocument))

        result.nodeValue="Hello World!"
        return result

class MoodleQuestion:
    def __init__(self,name):
        self.values = {'name': name}

    def createNameNode(self):
        return XMLNode('name',{},[XMLNode('text',{},[],self.values['name'])])



    # Represents a Moodle XML True False Question, the first question type tried
    # Values are stored in a dictionary. Attributes should be added to values
    # in order for question to be fully filled out
    # Possible values with description:
    #
    # name
    #       name of the question
    # defaultQuestionGrade
    #       default grade for the question. Typically 1
    #       TODO, elaborate on this!
    # questionText
    #       moodle question text, should be passed in as a string, properly
    #       formatted for moodle #TODO: Expand on this concept!
    # questionTextType
    #       should be set to one of the following strings:
    #       moodle_auto_format
    #       html
    #       plain_text
    #       markdown
    # image
    #       NOTE: CURRENTLY UNSUPPORTED. TODO: Figure out how this works
    # generalFeedback
    #       string holding information for general feedback from the problem
    # answer
    #       true/false boolean representing the correct answer
    # trueFeedback
    #       feedback given for the response true, in string format
    # falseFeedback
    #       see trueFeedback
    #

class MoodleXMLTrueFalseQuestion(MoodleQuestion):
    def __init__(self,name,correctAnswer,defaultQuestionGrade='1'):
        MoodleQuestion.__init__(self,name)
        self.values['correctAnswer'] = correctAnswer
        self.values['defaultQuestionGrade'] = defaultQuestionGrade
        self.values['questionTextType'] = 'moodle_auto_format'
        self.values['questionText'] = ''
        self.values['generalFeedback'] = ''
        self.values['trueFeedback'] = ''
        self.values['falseFeedback'] = ''
        self.defaultQuestionGrade=defaultQuestionGrade
        self.nodes = []

    def createQuestionTextNode(self):
        return XMLNode('questiontext',
            {'format':self.values['questionTextType']},
            [XMLNode('text',{},[],self.values['questionText'],True)])

    def createImageNode(self):
        return XMLNode('image')

    def createGeneralFeedbackNode(self):
        return XMLNode('generalfeedback',{},
            [XMLNode('text',{},[],self.values['generalFeedback'],True)])

    def createDefaultGradeNode(self):
        return XMLNode('defaultgrade',{},[],self.values['defaultQuestionGrade'])

    def createPenaltyNode(self):
        return XMLNode('penalty',{},[],'1')

    def createHiddenNode(self):
        return XMLNode('hidden',{},[],'0')

    def createShuffleAnswersNode(self):
        return XMLNode('hidden',{},[],'0')

    def createTrueAnswerNode(self):
        frac = "100"
        if not self.values['correctAnswer']:
            frac = "0"
        return XMLNode('answer',{'fraction':frac},
            [XMLNode('text',{},[],'true'),
             XMLNode('feedback',{},
                 [XMLNode('text',{},[],self.values['trueFeedback'],True)])])

    def createFalseAnswerNode(self):
        frac = "0"
        if not self.values['correctAnswer']:
            frac = "100"
        return XMLNode('answer',{'fraction':frac},
            [XMLNode('text',{},[],'false'),
             XMLNode('feedback',{},
                 [XMLNode('text',{},[],self.values['falseFeedback'],True)])])

    def createAnswersNodes(self):
        return [self.createTrueAnswerNode(),self.createFalseAnswerNode()]

    def prepareNodes(self):
        self.nodes = []
        self.nodes.append(self.createNameNode())
        self.nodes.append(self.createQuestionTextNode())
        self.nodes.append(self.createImageNode())
        self.nodes.append(self.createGeneralFeedbackNode())
        self.nodes.append(self.createDefaultGradeNode())
        self.nodes.append(self.createPenaltyNode())
        self.nodes.append(self.createHiddenNode())
        self.nodes.append(self.createShuffleAnswersNode())
        for answer in self.createAnswersNodes():
            self.nodes.append(answer)

    def toXMLElement(self,xmlDocument):
        #Create Question object and set type to true/false
        self.prepareNodes()
        question = xmlDocument.createElement('question')
        question.setAttribute('type','truefalse')
        for node in self.nodes:
            question.appendChild(node.toXMLElement(xmlDocument))
        return question


class MoodleXMLCategory:
    def __init__(self):
        self.__categoryName = ['$course$']
        self.questions = []

    def getCategoryNameString(self):
        return '/'.join(self.__categoryName)

    def getCategoryNameList(self):
        return self.__categoryName

    def setCategoryNameList(self,categoryNameList):
        assert(categoryNameList[0] == "$course$")
        self.__categoryName = categoryNameList

    def addQuestion(self,question):
        self.questions.append(question)

    def toXMLElements(self,xmlDocument):
        result = []
        catQuestion = XMLNode('question',{'type':'category'},
        [XMLNode('category',{},
        [XMLNode('text',{},[],self.getCategoryNameString())])])
        result.append(catQuestion.toXMLElement(xmlDocument))
        for question in self.questions:
            result.append(question.toXMLElement(xmlDocument))
        return result

class MoodleXMLFile:
    def __init__(self):
        self.__categoriesList = [];

    def getCategories(self):
        return self.__categoriesList;

    def addCategory(self,category):
        self.addCategoryAtPos(category,len(self.__categoriesList))

    def addCategoryAtPos(self,category,position):
        self.__categoriesList.insert(position,category)

    def removeCategory(self,index):
        self.__categoriesList.pop(index)

    def toXMLDocument(self):
        result = Document()
        xmlQuiz = result.createElement('quiz')
        result.appendChild(xmlQuiz)
        for category in self.__categoriesList:
            elements = category.toXMLElements(result)
            for element in elements:
                xmlQuiz.appendChild(element)
        return result



#
#    def __init__(self, XMLFile)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Utility to create and export Moodle XML question files')
    parser.add_argument('filename', type=argparse.FileType(mode='r'))
    args = parser.parse_args()
    dom1 =  parse(args.filename)
    print('Hello World!')

    q1 = MoodleXMLTrueFalseQuestion('TestAF',False)
    q1.values['questionText']='<div>Just doing some testing</div>\n<div>&nbsp;</div>\n<div><strong>asdfasdf</strong></div>'
    q1.values['generalFeedback']='<div>This is on the first line.</div>\n<div>This is on a second line.</div>\n<div>&nbsp;</div>\n<div><strong>This is on the fourth line, and bold.</strong></div>'
    q1.values['falseFeedback']='<div>This is on the first line.</div>\n<div>This is on a second line.</div>\n<div>&nbsp;</div>\n<div><strong>This is on the fourth line, and bold.</strong></div>'
    q1.values['trueFeedback']='<div>This is on the first line.</div>\n<div>This is on a second line.</div>\n<div>&nbsp;</div>\n<div><strong>This is on the fourth line, and bold.</strong></div>'
    c1 = MoodleXMLCategory()
    temp = c1.getCategoryNameList()
    temp.append('CS196TestQuestionsGenerated')
    c1.setCategoryNameList(temp)
    c1.addQuestion(q1)
    f1 = MoodleXMLFile()
    f1.addCategory(c1)
    d1 = f1.toXMLDocument()

    fout = open('tmp.xml','wb')
    a = d1.toprettyxml(indent='    ',encoding='utf-8')
    fout.write(a)


