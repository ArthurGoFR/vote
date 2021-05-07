red_letters = [
"E",
"P",
"O",
"D",
"U",
"O",
"A",
"P",
"S",
"E",
"D",
"E",
"S",
"A",
"N",
]

pink_letters = [
"U",
"R",
"R",
"S",
"D",
"F",
"L",
"P",
"N",
"S",
"D",
"V",
"I",
"C"  
]

from enigma.models import Word

def add_word(word_str):
    word = Word()
    word.text = word_str    
    word.taille = len(word_str)
    try:
        word.l0 = word_str[0]
    except:
        pass

    try:
        word.l1 = word_str[1]
    except:
        pass

    try:
        word.l2 = word_str[2]
    except:
        pass

    try:
        word.l3 = word_str[3]
    except:
        pass

    try:
        word.l4 = word_str[4]
    except:
        pass

    try:
        word.l5 = word_str[5]
    except:
        pass

    try:
        word.l6 = word_str[6]
    except:
        pass

    try:
        word.l1 = word_str[7]
    except:
        pass

    try:
        word.l1 = word_str[8]
    except:
        pass

    try:
        word.l1 = word_str[9]
    except:
        pass

    word.save()


def test():

    while True:
        letters_red = ["E","A","S","E","A","N","S"]
        letters_pink = ["R","D","P","V","I","C"]
        import random
        import time
        random_string=""

        for i in range(0,5):
            if i%2 ==0:
                letters = letters_red
                alen = len(letters)
                rando = random.randint(0, alen - 1)
                random_string=random_string+str(letters[rando])
                letters.pop(rando)
            if i%2 == 1:
                letters = letters_pink
                alen = len(letters)
                rando = random.randint(0, alen - 1)
                random_string=random_string+str(letters[rando])
                letters.pop(rando)     

        random_string = random_string + " "
            
        for i in range(1,9):
            if i%2 ==0:
                letters = letters_red
                alen = len(letters)
                rando = random.randint(0, alen - 1)
                random_string=random_string+str(letters[rando])
                letters.pop(rando)
            if i%2 == 1:
                letters = letters_pink
                alen = len(letters)
                rando = random.randint(0, alen - 1)
                random_string=random_string+str(letters[rando])
                letters.pop(rando)  

        print(random_string)

        
        time.sleep(0.3)