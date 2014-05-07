import sys

__author__ = 'kristian'


class TermsFile:

    def __init__(self):
        """

        :rtype : object
        """
        self.terms = ""
        self.file = open("/Users/kristian/Desktop/54")


    def setFile(self, filename):
        """
        sets the self file name for the object
        :param filename: filename path for the file of terms
        """
        assert isinstance(filename, basestring)
        self.file = open(filename)

    def getTerms(self):
        words = set(line.strip() for line in self.file)  #create a set of words from dictionary file
        self.terms = [w.split('\t', 2)[1] for w in words]

    def compareList(self):
        """


        """
        with open(sys.argv[1].strip) as f:
            file_contents = f.readlines()
            print(file_contents)

    # def compareTerms(self, dataTerms,paperTerms):
    def compareWith(self,paperTerms):
        """
        compare the term on this object with terms on another file
        :param paperTerms: filename path for the file of terms
        """
        # dataTerms = self.file
        # with open("/Users/kristian/Desktop/599") as f2, open("/Users/kristian/Desktop/21252224") as f1:
        # f2 = open(dataTerms)
        f2 = open(paperTerms)
        # words = set(line.strip() for line in f1)  #create a set of words from dictionary file
        # words2 = [w.split('\t', 2)[1] for w in words]
        #why sets? sets provide an O(1) lookup, so overall complexity is O(N)

        #now loop over each line of other file (word, freq file)
        for line in f2:
            word = line.split('\t', 2)[1]  #fetch word,freq
            if word in self.terms:  #if word is found in words set then print it
                assert isinstance(word, basestring)
                print word

    def main(args):
        a = TermsFile()
        a.setFile("/Users/kristian/Desktop/997")
        a.getTerms()
        a.compareWith("/Users/kristian/Desktop/22712534")

# compare("/Users/kristian/Desktop/54", "/Users/kristian/Desktop/21252224")
# compare("/Users/kristian/Desktop/871", "/Users/kristian/Desktop/21106498")
# compare("/Users/kristian/Desktop/880", "/Users/kristian/Desktop/19802714")
# compare("/Users/kristian/Desktop/863", "/Users/kristian/Desktop/Proteolysisofbeta-galactos")
# compare("/Users/kristian/Desktop/1056", "/Users/kristian/Desktop/21815947")
# compare("/Users/kristian/Desktop/995", "/Users/kristian/Desktop/22686585")
# compare("/Users/kristian/Desktop/992", "/Users/kristian/Desktop/22686585")
# compare("/Users/kristian/Desktop/997", "/Users/kristian/Desktop/22712534")
# compare("/Users/kristian/Desktop/1070", "/Users/kristian/Desktop/GlucoseTransport")
# compare("/Users/kristian/Desktop/1069", "/Users/kristian/Desktop/GlucoseTransport")
# compare("/Users/kristian/Desktop/1073", "/Users/kristian/Desktop/GlucoseTransport")
# compare("/Users/kristian/Desktop/832", "/Users/kristian/Desktop/Integrativemodelling")
# compare("/Users/kristian/Desktop/836", "/Users/kristian/Desktop/Integrativemodelling")

#
# import pandas
# publication = pandas.DataFrame.from_csv('/Users/kristian/Desktop/21252224', sep='\t', header=False)
# print(publication["terms"])