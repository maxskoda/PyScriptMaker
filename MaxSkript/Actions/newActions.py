class sample:


def test(samp):
    print('ok')

samplist = ['S1', 'S2']
for samp in ['sample_' + s for s in samplist]:
    test(samp)