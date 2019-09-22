
name_list = [
    "Arnd Pralle"
    ,"Arto V.Nurmikko"
    ,"Charles M.Lieber"
    ,"Dae-Hyeong Kim"
    ,"Daryl Kipke"
    ,"Gaurav Sharma"
    ,"George Malliaras"
    ,"Grégoire Courtine"
    ,"John Rogers"
    ,"Kullervo Hynynen"
    ,"Kristin Zhao"
    ,"Lee E Miller"
    ,"Leigh Hochberg"
    ,"Miguel Nicolelis"
    ,"Serge Picaud"
    ,"Tamar Makin"
    ,"Xiaojie Duan"
    ,"Xinyan Tracy Cui"
    ,"Zhenan Bao"
    ]

c = open('speakers/2.html', 'r')
content = c.read()
print(content)
for i in range(19):
    if i == 1:
        continue
    file = open("%d.html" %(i+1), 'w')
    file.write(content)
    file.close()
c.close()
