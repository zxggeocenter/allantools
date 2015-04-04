"""
  NBS14 test for allantools (https://github.com/aewallin/allantools)

  nbs14 datasets are from http://www.ieee-uffc.org/frequency-control/learning-riley.asp
  
  Stable32 was used to calculate the deviations we compare against.

  The small dataset and deviations are from
  http://www.ieee-uffc.org/frequency-control/learning-riley.asp
  http://www.wriley.com/paper1ht.htm
  
  see also:
  NIST Special Publication 1065
  Handbook of Frequency Stability Analysis
  http://tf.nist.gov/general/pdf/2220.pdf
  around page 107
"""
import math
import time
import sys

import allantools as allan


nbs14_phase = [ 0.00000, 103.11111, 123.22222, 157.33333, 166.44444, 48.55555,-96.33333,-2.22222, 111.88889, 0.00000 ]
nbs14_f     = [892,809,823,798,671,644,883,903,677]
nbs14_devs= [ (91.22945,115.8082),  # ADEV(tau=1,tau=2)
              (91.22945, 85.95287), # OADEV 
              (91.22945,74.78849),  # MDEV
              (91.22945,98.31100),  # TOTDEV
              (70.80608,116.7980),  # HDEV
              (52.67135,86.35831),  # TDEV 
              (70.80607, 85.61487)] # OHDEV
              # (100.9770, 102.6039)  # Standard Deviation (sample, not population)
              
              # (70.80607, 91.16396 ) # HTOTDEV
              # (75.50203, 75.83606)  # MTOTDEV
              # (43.59112, 87.56794 ) # TTOTDEV
              
# 1000 point deviations from:
# http://www.ieee-uffc.org/frequency-control/learning-riley.asp    Table III
# http://www.wriley.com/paper1ht.htm
# http://tf.nist.gov/general/pdf/2220.pdf  page 108
nbs14_1000_devs = [ [2.922319e-01, 9.965736e-02, 3.897804e-02],  # ADEV 1, 10, 100 
                    [2.922319e-01, 9.159953e-02, 3.241343e-02],  # OADEV
                    [2.922319e-01, 6.172376e-02, 2.170921e-02],  # MDEV 
                    [2.922319e-01, 9.172131e-02, 3.501795e-02],  # TOTDEV, http://www.ieee-uffc.org/frequency-control/learning-riley.asp
                    # "Calculated using bias-corrected reflected method from endpoint-matched phase data"
                    
                    # 2.922319e-01, 9.134743e-02, 3.406530e-02    # TOTDEV, http://tf.nist.gov/general/pdf/2220.pdf page 108
                    # "Calculated using doubly reflected TOTVAR method"
                    
                    [2.943883e-01, 1.052754e-01, 3.910860e-02],  # HDEV
                    [1.687202e-01, 3.563623e-01, 1.253382e-00],  # TDEV
                    [2.943883e-01, 9.581083e-02, 3.237638e-02] ] # OHDEV
                    # 2.884664e-01, 9.296352e-02, 3.206656e-02   # standard deviation,  sample (not population)
                    # 2.943883e-01, 9.614787e-02, 3.058103e-02   # HTOTDEV
                    # 2.418528e-01, 6.499161e-02, 2.287774e-02   # MTOTDEV
                    # 1.396338e-01, 3.752293e-01, 1.320847e-00   # TTOTDEV
                    
# this generates the nbs14 1000 point frequency dataset. 
# random number generator described in 
# http://www.ieee-uffc.org/frequency-control/learning-riley.asp
# http://tf.nist.gov/general/pdf/2220.pdf   page 107
def nbs14_1000():
    n = [0]*1000
    n[0] = 1234567890
    for i in range(999):
        n[i+1] = (16807*n[i]) % 2147483647
    # the first three numbers are given in the paper, so check them:
    assert( n[1] ==  395529916 and n[2] == 1209410747 and  n[3] == 633705974 )
    n = [x/float(2147483647) for x in n] # normalize so that n is in [0, 1]
    return n

def nbs14_tester( function, fdata, correct_devs ):
    rate=1.0
    taus =[1, 10, 100]
    (taus2, devs, deverrs, ns) = function( fdata, rate, taus)
    for i in range(3):
        assert( check_devs( devs[i], correct_devs[i] ) )

# TODO: this does not work!!
def nbs14_totdev_test():
    rate=1.0
    taus =[1, 10, 100]
    fdata = nbs14_1000()
    correct_devs = nbs14_1000_devs[3] 
    (taus2, devs, deverrs, ns) = allan.totdev( fdata, rate, taus)
    (taus2, adevs, adeverrs, ans) = allan.adev( fdata, rate, taus)
    for i in range(3):
        totdev_corrected = devs[i]
        if i != 0:
            # bias removal is used in the published results
            a = 0.481 # flicker frequency-noise
            #a = 0.750 # flicker frequency-noise
            ratio = pow(devs[i],2)/pow(adevs[i],2)
            print ratio-1
            print -a*taus2[i]/((len(fdata)+1)*(1/float(rate)))
            ratio_corrected = ratio*( 1-a* taus2[i]/((len(fdata)+1)*(1/float(rate))) ) # WRONG!?!
            totdev_corrected = ratio_corrected * pow(adevs[i],2)
            totdev_corrected = math.sqrt( totdev_corrected )
            print totdev_corrected, devs[i], correct_devs[i]
        assert( check_devs( totdev_corrected, correct_devs[i] ) )

def nbs14_1000_test():
    fdata = nbs14_1000()

    nbs14_tester( allan.adev, fdata, nbs14_1000_devs[0] )
    print "nbs14_1000 adev"

    nbs14_tester( allan.oadev, fdata, nbs14_1000_devs[1] )
    print "nbs14_1000 oadev"

    nbs14_tester( allan.mdev, fdata, nbs14_1000_devs[2] )
    print "nbs14_1000 mdev"

    #print "nbs13 totdev" # this test does not work, becaus we don't know how to do bias correction
    #nbs14_totdev_test()

    nbs14_tester( allan.hdev, fdata, nbs14_1000_devs[4] )
    print "nbs14_1000 hdev"

    nbs14_tester( allan.tdev, fdata, nbs14_1000_devs[5] )
    print "nbs14_1000 tdev"

    nbs14_tester( allan.ohdev, fdata, nbs14_1000_devs[6] )
    print "nbs14_1000 ohdev"
        
    #########################################################
    # now we test the same data, calling the _phase functions
    pdata = allan.frequency2phase(fdata, 1.0)
    
    nbs14_tester( allan.adev_phase, pdata, nbs14_1000_devs[0] )
    print "nbs14_1000 adev_phase"

    nbs14_tester( allan.oadev_phase, pdata, nbs14_1000_devs[1] )
    print "nbs14_1000 oadev_phase"

    nbs14_tester( allan.mdev_phase, pdata, nbs14_1000_devs[2] )
    print "nbs14_1000 mdev_phase"

    #print "nbs13 totdev" # this test does not work, becaus we don't know how to do bias correction
    #nbs14_totdev_test()

    nbs14_tester( allan.hdev_phase, pdata, nbs14_1000_devs[4] )
    print "nbs14_1000 hdev_phase"

    nbs14_tester( allan.tdev_phase, pdata, nbs14_1000_devs[5] )
    print "nbs14_1000 tdev_phase"

    nbs14_tester( allan.ohdev_phase, pdata, nbs14_1000_devs[6] )
    print "nbs14_1000 ohdev_phase"
        
    print "nbs14_1000 all tests OK"

def check_devs(dev2, dev1):
    rel_error = (dev2-dev1)/dev1
    tol = 1e-6
    verbose = 1

    if ( abs(rel_error) < tol ):
        if verbose:
            print "OK   %0.6f \t    %0.6f \t %0.6f" % (dev1,dev2, rel_error)
        return True
    else:
        print "ERROR   %0.6f \t %0.6f \t %0.6f" % (dev1,dev2, rel_error)
        return False

def nbs14_test():
    taus = [1, 2]
    devs = []
    tol = 1e-4
    
    # first tests that call the _phase functions
    print "nbs14 tests for _phase() functions"
    
    (taus2,adevs2,aerrs2,ns2) = allan.adev_phase( nbs14_phase, 1.0, taus)
    adevs = nbs14_devs[0]
    assert( check_devs( adevs2[0], adevs[0] ) )
    assert( check_devs( adevs2[1], adevs[1] ) )
    print "nbs14 adev"
    (taus2,adevs2,aerrs2,ns2) = allan.oadev_phase( nbs14_phase, 1.0, taus)
    oadevs = nbs14_devs[1]
    assert( check_devs( adevs2[0], oadevs[0] ) )
    assert( check_devs( adevs2[1], oadevs[1] ) )
    print "nbs14 oadev"
    (taus2,adevs2,aerrs2,ns2) = allan.mdev_phase( nbs14_phase, 1.0, taus)
    mdevs = nbs14_devs[2]
    assert( check_devs( adevs2[0], mdevs[0] ) )
    assert( check_devs( adevs2[1], mdevs[1] ) )
    print "nbs14 mdev"
    (taus2,adevs2,aerrs2,ns2) = allan.hdev_phase( nbs14_phase, 1.0, taus)
    hdevs = nbs14_devs[4]
    assert( check_devs( adevs2[0], hdevs[0] ) )
    assert( check_devs( adevs2[1], hdevs[1] ) )
    print "nbs14 hdev"
    (taus2,adevs2,aerrs2,ns2) = allan.tdev_phase( nbs14_phase, 1.0, taus)
    tdevs = nbs14_devs[5]
    assert( check_devs( adevs2[0], tdevs[0] ) )
    assert( check_devs( adevs2[1], tdevs[1] ) )
    print "nbs14 tdev"

    # then the same tests for frequency data
    print "nbs14 tests for frequency data"

    f_fract = [ float(f) for f in nbs14_f]
    (taus2,adevs2,aerrs2,ns2) = allan.adev( f_fract, 1.0, taus)
    adevs = nbs14_devs[0]
    assert( check_devs( adevs2[0], adevs[0] ) )
    assert( check_devs( adevs2[1], adevs[1] ) )
    print "nbs14 freqdata adev"

    (taus2,adevs2,aerrs2,ns2) = allan.oadev( f_fract, 1.0, taus)
    oadevs = nbs14_devs[1]
    assert( check_devs( adevs2[0], oadevs[0] ) )
    assert( check_devs( adevs2[1], oadevs[1] ) )
    print "nbs14 freqdata oadev"

    (taus2,adevs2,aerrs2,ns2) = allan.mdev( f_fract, 1.0, taus)
    mdevs = nbs14_devs[2]
    assert( check_devs( adevs2[0], mdevs[0] ) )
    assert( check_devs( adevs2[1], mdevs[1] ) )
    print "nbs14 freqdata mdev"

    (taus2,adevs2,aerrs2,ns2) = allan.hdev( f_fract, 1.0, taus)
    hdevs = nbs14_devs[4]
    assert( check_devs( adevs2[0], hdevs[0] ) )
    assert( check_devs( adevs2[1], hdevs[1] ) )
    print "nbs14 freqdata hdev"

    (taus2,adevs2,aerrs2,ns2) = allan.tdev( f_fract, 1.0, taus)
    tdevs = nbs14_devs[5]
    assert( check_devs( adevs2[0], tdevs[0] ) )
    assert( check_devs( adevs2[1], tdevs[1] ) )
    print "nbs14 freqdata tdev"

    (taus2,adevs2,aerrs2,ns2) = allan.ohdev( f_fract, 1.0, taus)
    tdevs = nbs14_devs[6]
    assert( check_devs( adevs2[0], tdevs[0] ) )
    assert( check_devs( adevs2[1], tdevs[1] ) )
    print "nbs14 freqdata ohdev"


    print "nbs14 all test OK"

def run():
    nbs14_test()
    nbs14_1000_test()


if __name__ == "__main__":
    run()
