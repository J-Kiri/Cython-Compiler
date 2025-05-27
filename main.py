from lexic import Lexic
from syntactic import Syntactic

class Translator:
    def __init__(self, file_name):
        self.file_name = file_name

    def inicialize(self):
        self.file = open(self.file_name, 'r')
        self.lexic = Lexic(self.file)
        self.syntactic = Syntactic(self.lexic)

    def translate(self):
        self.syntactic.translate()

    def finalize(self):
        self.file.close()

if __name__ == '__main__':
    tests = [
        # "test.cy",
        "testSliceList.cy"
        # ,"testForWrite.cy"
        # ,"testIfElseElif.cy"
        # ,"testMain.cy"
        # ,"testVecAtrib.cy"
        # ,"testInvFuncNoPar.cy"
        # ,"testInvIfNoPar.cy"
        # ,"testInvSemiCol.cy"
    ]

    for test in tests:
        print("Testing " + test)
        trans = Translator(test)
        trans.inicialize()
        trans.translate()

        trans.finalize()
        print("\n")