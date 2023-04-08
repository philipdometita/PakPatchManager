import os
import json
import shutil

# function for filtering out files other than the pak patch files
def filterPakPatch(fileName):
    return True if 're_chunk_000.pak.patch' in fileName else False

# function that renames a mod's pak patch file 
# and copies it to the mh rise folder 
# numActiveMods: number of currently active mods
# modName: name of mod to be activated
# modsDic: dictionary of all the mods in the mods folder
def activateMod(numActiveMods, modName, modsDic):
    currDir = os.getcwd()
    mhrDir = os.path.join(currDir, '..')
    PPMModsDir = os.path.join(currDir, 'mods')

    if (numActiveMods >= 10):
        pakName = 're_chunk_000.pak.patch_0{}.pak'.format(str(numActiveMods))
    else:
        pakName = 're_chunk_000.pak.patch_00{}.pak'.format(str(numActiveMods))
    modsDic[modName]['pak'] = pakName
    
    modDir = os.listdir(os.path.join(PPMModsDir, modName))
    
    # rename pak patch file in mods folder
    oldPakFilePath = os.path.join(PPMModsDir, modName, modDir[0])
    newPakFilePath = os.path.join(PPMModsDir, modName, pakName)
    os.rename(oldPakFilePath, newPakFilePath)

    # copy pak patch file from mods folder to mh rise folder
    shutil.copy(newPakFilePath, os.path.join(mhrDir, pakName))

# function that deactivates a given mod
# numActiveMods: number of currently active mods
# modName: name of mod to be activated
# modsDic: dictionary of all the mods in the mods folder
def deactivateMod(activeMods, modName, modsDic):
    currDir = os.getcwd()
    mhrDir = os.path.join(currDir, '..')
    PPMModsDir = os.path.join(currDir, 'mods')

    # remove mod from mh rise folder
    modDir = os.listdir(os.path.join(PPMModsDir, modName))
    pakFileName = modDir[0]
    os.remove(os.path.join(mhrDir, pakFileName))
    
    #rename the paks that follow the removed mod to keep proper sequence names
    removedPakID = int(pakFileName[23:26]) - 1
    mhrFiles = os.listdir(mhrDir)
    mhrPaks = list(filter(filterPakPatch, mhrFiles))
    for i in range(removedPakID, len(mhrPaks)):
        mhrPakID = int(mhrPaks[i][23:26])
        # keep track of paths for both the mhr folder and the mods folder for renaming both and keeping both folders consistent
        oldPakFilePathMHR = os.path.join(mhrDir, mhrPaks[i])
        oldPakFilePathPPM = os.path.join(PPMModsDir, str(activeMods[i]), modsDic[activeMods[i]]['pak'])

        if mhrPakID >= 10:
            pakName = 're_chunk_000.pak.patch_0{}.pak'.format(str(mhrPakID - 1))
        else:
            pakName = 're_chunk_000.pak.patch_00{}.pak'.format(str(mhrPakID - 1))

        newPakFilePathMHR = os.path.join(mhrDir, pakName)
        newPakFilePathPPM = os.path.join(PPMModsDir, str(activeMods[i]), pakName)

        os.rename(oldPakFilePathMHR, newPakFilePathMHR)
        os.rename(oldPakFilePathPPM, newPakFilePathPPM)

        # update the mods dictionary to keep it consistent with the file names in the folders
        modsDic[str(activeMods[i])]['pak'] = pakName

# function that clears all active mods
# activeMods: mods that are currently active
# modsDic: dictionary of all mods in the mods dic        
def clearActiveMods(activeMods, modsDic):
    currDir = os.getcwd()
    mhrDir = os.path.join(currDir, '..')

    mhrDirFiles = os.listdir(mhrDir)
    mhrPaks = list(filter(filterPakPatch, mhrDirFiles))

    # remove the default pak so it is not deleted from the directory
    mhrPaks.pop(0)
    activeMods.pop(0)
    
    # remove all pak patch files from the mhr folder
    for pak in mhrPaks:
        os.remove(os.path.join(mhrDir, pak))
    
    # update the mods dictionary
    for mod in activeMods:
        modsDic[mod]['active'] = False

# function that reads the mods folder and creates / updates mods dictionary and mods.json
# modsDic: the mods dictionary
# modDir: the path to the mods folder
# returns a new mod dictionary after dumping it to the JSON file
def readModsFolder(modsDic, modDir):
    mods = os.listdir(modDir)

    # add any new keys
    newModsDic = modsDic
    for i in range(len(mods)):
        modPak = os.listdir(os.path.join(modDir, mods[i]))
        if (mods[i] not in modsDic):
            modDic = {
                'pak': modPak[0],
                'active': False
            }
            newModsDic[mods[i]] = modDic
    
    #removes any key to mod that was removed
    keysToBeRemoved = []
    for modName in modsDic:
        if modName not in mods:
            keysToBeRemoved.append(modName)
    
    for key in keysToBeRemoved:
        newModsDic.pop(key)

    dumpModsToJSON(newModsDic) 
    return newModsDic

# function that dumps the mods dictionary to a JSON file (mods.json)
# modsDic the mod dictionary to be dumped into the JSON
def dumpModsToJSON(modsDic):
    currDir = os.getcwd()
    modDir = os.path.join(currDir, 'mods')
    
    with open('mods.json', 'w') as modsJSON:
        json.dump(modsDic, modsJSON, indent = 4)

# function that loads the mods dictionary from mods.json
# returns the mod dictionary
def loadModsFromJSON():
    with open('mods.json') as modsJSON:
        modDic = json.load(modsJSON)
    
    return modDic

# function that returns number of active mods
def findActiveMods(modsDic):
    # add default pak after Capcom added a required pak patch file
    activeMods = ['MHRDefaultPak']
    for mod in modsDic:
        if modsDic[mod]['active']:
            activeMods.append(mod)

    return activeMods

    
def main():
    currDir = os.getcwd()
    modDir = os.path.join(currDir, 'mods')
    mods = os.listdir(modDir)
    modsDic = loadModsFromJSON()
    modsDic = readModsFolder(modsDic, modDir)
    activeMods = findActiveMods(modsDic)
    numActiveMods = len(activeMods)
    done = False

    delimiter = "=" * 50
    while not done:
        print("Mods:\n")
        for i in range(len(mods)):
            modNumAndName = str(i) + ' - ' + mods[i] + ': '
            activeState = 'active' if modsDic[mods[i]]['active'] else 'not active'
            modLine = "{0:<25}{1:>20}".format(modNumAndName, activeState)
            print(modLine)
        
        print('\nActions:')
        print('number - activate or deactivate mod.')
        print('c - deactivate all mods')
        print('r - re read mods from mods folder')
        print('d - close the program\n')
        userIn = input('enter action: ')

        # activate / deactivate mods
        if (userIn.isnumeric()):
            if int(userIn) < len(mods) and int(userIn) >= 0:
                modsDic[mods[int(userIn)]]['active'] = not modsDic[mods[int(userIn)]]['active']
                if not modsDic[mods[int(userIn)]]['active']:
                    print('Deactivating ' + mods[int(userIn)])
                    activeMods.remove(mods[int(userIn)])
                    numActiveMods -= 1
                    deactivateMod(activeMods, mods[int(userIn)], modsDic)
                else:
                    print('Activating ' + mods[int(userIn)])
                    activeMods.append(mods[int(userIn)])
                    numActiveMods += 1
                    activateMod(numActiveMods, mods[int(userIn)], modsDic)
                dumpModsToJSON(modsDic)
            else: 
                print("Please enter a valid action")
        # deactivates all active mods
        elif (userIn.lower() == 'c'):
            clearActiveMods(activeMods, modsDic)
            activeMods = ['MHRDefaultPak']
            numActiveMods = 0
            dumpModsToJSON(modsDic)
        # end loop and the program
        elif (userIn.lower() == 'd'):
            print('Closing')
            done = True
        # re read the mods folder
        elif (userIn.lower() == 'r'):
            print('re reading mods folder')
            modsDic = readModsFolder(modsDic, modDir)
            mods = os.listdir(modDir)
        else:
            print("Please enter a valid action")
        print(delimiter)
            

if __name__ == "__main__" :
    main()
