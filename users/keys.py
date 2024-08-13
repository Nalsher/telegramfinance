import random


async def generate_random_string(length:int,key:str):
    letters = key
    rand_string = ''.join(random.choice(letters) for i in range(length))
    return rand_string