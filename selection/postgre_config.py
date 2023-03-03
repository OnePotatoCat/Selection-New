from multipledispatch import dispatch

class TestClass(object):

    @dispatch()
    def test(self):
        print("Here")

    @dispatch(float)
    def test(self, te):
        print(te)

    @dispatch(float, float)
    def test(self, te, tc):
        print(te + tc)





if __name__ == "__main__":
    TestClass.test(10.0, 10.0)