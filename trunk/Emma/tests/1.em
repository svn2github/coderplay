for ii = 1, 10 { 
    x = ii
    while x > 0 {
        x = x - 1
        if x % 2 == 0 continue
        print '    ', x, ii
    }
    if ii % 2 == 0 continue
    print ii
}
