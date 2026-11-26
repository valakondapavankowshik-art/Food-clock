import unittest
from rescue_engine import allocate
class TestRescue(unittest.TestCase):
    def setUp(self):
        self.b=[dict(name='A',meals=80,minutes=55,x=0,y=0,storage='Hot-held',verified=True),dict(name='B',meals=120,minutes=110,x=4,y=0,storage='Hot-held',verified=True)]
        self.r=[dict(name='Near',demand=100,capacity=100,x=1,y=0,storage='Hot-held',active=True),dict(name='Far',demand=100,capacity=100,x=-5,y=0,storage='Hot-held',active=True)]
    def test_maximum(self):
        p=allocate(self.b,self.r); self.assertEqual(sum(x['meals'] for x in p),200); self.assertTrue(all(x['latest_start_in_minutes']>=0 for x in p))
    def test_delay(self): self.assertEqual(allocate(self.b,self.r,delay=200),[])
    def test_capacity(self):
        self.r[0]['capacity']=10; self.assertLessEqual(sum(x['meals'] for x in allocate(self.b,self.r) if x['recipient']=='Near'),10)
    def test_ineligible(self):
        self.b[0]['verified']=False; self.r[1]['active']=False; self.assertTrue(all(x['batch']=='B' and x['recipient']=='Near' for x in allocate(self.b,self.r)))
    def test_storage(self):
        for r in self.r:r['storage']='Chilled'
        self.assertEqual(allocate(self.b,self.r),[])
if __name__=='__main__':unittest.main()
