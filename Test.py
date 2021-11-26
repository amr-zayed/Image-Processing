a=['tea', 'tea', 'act']
b=['ate', 'toe', 'acts']

anagramList = []
for i in range(len(a)):
    str1 = a[i]
    str2 = b[i]
    if len(str1)!=len(str2):
        anagramList.append(-1)
        continue
    str1 = sorted(str1)
    str2 = sorted(str2)
    if str1 == str2:
        anagramList.append(0)
        continue

    modification_count = 0
    char_count = [0] * 26     
    for i in range(26):
        char_count[i] = 0
    for i in range(len(str1)):
        char_count[ord(str1[i]) - ord('a')] += 1
    for i in range(len(str2)):
        char_count[ord(str2[i]) - ord('a')] -= 1
    for i in range(26):
        if char_count[i] != 0:
            modification_count += abs(char_count[i])
    anagramList.append(modification_count/2)

#return this list
anagramList