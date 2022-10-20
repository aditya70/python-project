def reachingPoints(x1,y1,x2,y2):
    if x1 > x2 or y1 > y2:
        return "No"
    if x1 == x2 and y1 == y2:
        return "Yes"

    while x2 > x1 and y2 > y1:
        if x2 > y2:
            x2 = x2 % y2
        else:
            y2 = y2 % x2
        if x2 == x1 and (y2 - y1 + x1) % x1 == 0:
            return "Yes"
        elif y2 == y1 and (x2 - x1 + y1) % y1 == 0:
            return "Yes"
        else:
            return "No"



sx,sy = 1,1
dx,dy = 5,2
print(reachingPoints(sx,sy,dx,dy))