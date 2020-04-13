# sample memory accesses to run through cache mapping algorithm
instructions = [0x1A0, 0x1A4, 0x168, 0x16C, 0x234, 0x230, 0x1A0, 0x1A4, 0x158, 0x15C, 0x10C, 0x234]

cache_frequency_sets = [[], []] # order of most recent cache accesses
cache_order_sets = [[], []]     # physical locations of memory in cache

# prints out the physical order of cache memory
def printHelper(cache_sets):
    print("Cache:")
    for cache_set in cache_sets:
        for i in range(len(cache_set)):
            print(str(i) + ": " + str(cache_set[i]) + " " + hex(cache_set[i]).upper())
    
# updates the physical location of cache
def addToCacheFrequency(cache, instruction, setIndex):
    if len(cache) < 4:
        if instruction not in cache:
            cache.append(instruction)
        else:
            cache.insert(len(cache), cache.pop(cache.index(instruction)))
    else:
        if instruction in cache:
            cache.append(instruction)
            cache.remove(instruction)
        else:
            cache.append(instruction)
            cache.remove(cache[0])
            
# updates the physical location of cache
def addToCacheOrder(cache, instruction, setIndex):
    if len(cache) < 4:
        if instruction not in cache:
            cache.append(instruction)
    else:
        if instruction not in cache:
            index = cache.index(cache_frequency_sets[setIndex][0])
            cache[index] = instruction
            
# implements 4-way set associative cache mapping
for i in range(4): # assignment asked to run memory sequence 4 times
    hitCount = 0
    missCount = 0
    for instruction in instructions:
        # 32-bit words and byte addressable (cache has two sections)
        setIndex = int((instruction / 4) % 2)
        if instruction in cache_order_sets[setIndex]:
            hitCount += 1
        else:
            missCount += 1
        addToCacheOrder(cache_order_sets[setIndex], instruction, setIndex)
        addToCacheFrequency(cache_frequency_sets[setIndex], instruction, setIndex)


    # print results
    printHelper(cache_order_sets)
    print("Hits      : " + str(hitCount))
    print("Misses    : " + str(missCount))
    print("Percentage: " + str(hitCount/(hitCount + missCount)))
        
