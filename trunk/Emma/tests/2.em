for ii = 1, 10 { 
    x = ii+5
    while x > 0 {
        x = x - 1
        if x < 2 break
        print '    ', x, ii
    }
    if ii % 2 == 0 continue
    if ii == 9 break
    print ii
}
