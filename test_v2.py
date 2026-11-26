import unittest
from rescue_engine import allocate, explain
class TestV2(unittest.TestCase):
    def setUp(self):
        self.b=[dict(name='A',meals=80,minutes=40,x=0,y=0,storage='Hot-held',verified=True),dict(name='B',meals=120,minutes=40,x=4,y=0,storage='Hot-held',verified=True)]
        self.r=[dict(name='Near',demand=100,capacity=100,x=1,y=0,storage='Hot-held',active=True),dict(name='Far',demand=100,capacity=100,x=-5,y=0,storage='Hot-held',active=True)]
    def test_optimization_advantage(self):
        self.assertEqual(sum(p['meals'] for p in allocate(self.b,self.r)),180)
        self.assertEqual(sum(p['meals'] for p in allocate(self.b,self.r,optimized=False)),100)
    def test_explain(self):
        self.assertEqual(sum(p['unallocated_meals'] for p in explain(self.b,self.r,allocate(self.b,self.r))),20)
    def test_empty(self):
        self.assertEqual(allocate(self.b,[]),[])
        self.assertEqual(len(explain(self.b,[],[])),2)
    def test_delay(self):
        self.assertEqual(allocate(self.b,self.r,delay=60),[])
if __name__=='__main__': unittest.main()
