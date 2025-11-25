#imports
import copy
import json

#reads moves using json
with open('moves.json', 'r') as f:
    moves_data = json.load(f)

#creates team class
class Team:
    #Accepts parameter as a list of pokemon objects, declares active pokemon as first one
    def __init__(self, pokemon):
        self.pokemon=pokemon
        self.activeIndex=0
        self.availablepokemon=len(pokemon)

    #active method returns active pokemon
    def active(self):
        return self.pokemon[self.activeIndex]
    
    def switch(self,switchIndex):
        #clears boosts and other effects
        self.active().atkboost=0
        self.active().spaboost=0
        self.active().spdefboost=0
        self.active().defboost=0
        self.active().spdboost=0
        self.active().othereffects=[]
        #changes active index to new index
        self.activeIndex=switchIndex

    def validswitches(self):
        #returns indices of pokemon able to be switched in
        return [i for i,pkmn in enumerate(self.pokemon) if pkmn.hp>0 and pkmn!=self.active()]
    
    def alivePokemon(self):
        return len([i for i in self.pokemon if i.hp>0])
    
class Move:
    #Creates move attributes
    def __init__(self, name, power, accuracy, move_type, category, pp, priority=0):
        self.name = name
        self.power = power
        self.accuracy = accuracy
        self.type = move_type
        self.category = category
        self.pp = pp
        self.priority = priority

class Pokemon:
    #creates pokemon class setting attributes
    def __init__(self,name,hp,maxspeed,attack,spattack,defense,spdefense,type1,type2=None,moves=[],atkboost=0,spaboost=0,defboost=0,spdefboost=0,spdboost=0,status=None, maxhp=None,othereffects=[],fainted=False):
        self.name=name
        self.hp=hp
        if maxhp:
            self.maxhp=maxhp
        else:
            self.maxhp=hp
        self.type1=type1
        self.type2=type2
        self.maxspeed=maxspeed
        self.attack=attack
        self.spattack=spattack
        self.defense=defense
        self.spdefense=spdefense
        self.moves=moves
        self.atkboost=atkboost
        self.spaboost=spaboost
        self.defboost=defboost
        self.spdefboost=spdefboost
        self.spdboost=spdboost
        self.status=status
        self.statuscounter=0
        self.othereffects=othereffects
        self.fainted=fainted

    #function for player damage dealt
    def doDamage(self,opponent,move):
        #PP check
        if move.pp <= 0:
            print(f"{self.name} tried to use {move.name}, but it has no PP left!")
            return
        
        #status check
        if move.category == "Status":
            statusTable(move, self, opponent)
            move.pp -= 1
        else:
            #reduce opp hp
            damage = calculateDamage(self, move, opponent, reducePP=True)
            opponent.hp = max(0, opponent.hp - damage)

            #message printing
            if opponent.hp == 0:
                print(f"{self.name} used {move.name}, {opponent.name} fainted!")
            else:
                print(f"{self.name} used {move.name} and dealt {damage} damage. {opponent.name} has {opponent.hp} HP left.")
            
            #secondary effect check
            secondaryEffectTable(move.name, damage, self, opponent)
        
    #function for predicted opponent Damage Dealt
    def takeDamage(self,opponent,reducePP=True):
        #checks valid moves
        valid_moves = [move for move in opponent.moves if move.pp > 0]

        #checks if pp should be reduced
        if reducePP:
            moves_damage=[calculateDamage(opponent,move,self) for move in valid_moves]
        else:
            moves_damage=[calculateDamage(opponent,move,self,reducePP=False) for move in valid_moves]

        #adds generic 90 base power STAB move(s) using opponent's higher attack stat if no stab move is revealed
        if all(move.type!=opponent.type1 for move in valid_moves)  and len(valid_moves)<4:
            if opponent.attack>opponent.spattack:
                moves_damage.append(calculateDamage(opponent,Move("Generic Move 1", 90, 100, opponent.type1,"Physical",16),self))
            else:
                moves_damage.append(calculateDamage(opponent,Move("Generic Move 1", 90, 100, opponent.type1,"Special",16),self))
        
        if opponent.type2:
            if all(move.type!=opponent.type2 for move in opponent.moves) and len(opponent.moves)<4:
                if opponent.attack>opponent.spattack:
                    moves_damage.append(calculateDamage(opponent,Move("Generic Move 2", 90, 100, opponent.type2,"Physical",16),self))
                else:
                    moves_damage.append(calculateDamage(opponent,Move("Generic Move 2", 90, 100, opponent.type2,"Special",16),self))
        
        #returns move that deals most damage
        used_move=opponent.moves[moves_damage.index(max(moves_damage))] if moves_damage.index(max(moves_damage))<len(opponent.moves) else "Generic Move"
        return [used_move,min(self.hp,max(moves_damage))]
    
def secondaryEffectTable(move_name,move_damage, attacker, defender,printmessages=True):
    #table to apply secondary effects of some moves
    if move_name == "Drain Punch" or move_name == "Giga Drain" or move_name == "Leech Life" or move_name == "Horn Leech":
        attacker.hp = min(attacker.maxhp,attacker.hp+int(0.5 * move_damage))

        if printmessages:
            print(f"{attacker.name} healed to {attacker.hp} HP using {move_name}.")
    elif move_name == "Draco Meteor" or move_name == "Overheat":
        attacker.spaboost -= 2
    elif move_name == "Brave Bird" or move_name == "Wood Hammer":
        recoil = int(0.33 * move_damage)
        attacker.hp -= recoil

        if printmessages:
            print(f"{attacker.name} took {recoil} recoil damage from {move_name}.")
    elif move_name == "Superpower":
        attacker.atkboost -= 1
        attacker.defboost -= 1
    elif move_name == "Close Combat":
        attacker.defboost -= 1
        attacker.spdefboost -= 1
    elif move_name == "Steel Beam":
        recoil = int(0.5 * attacker.maxhp)
        attacker.hp -= recoil

        if printmessages:
            print(f"{attacker.name} took {recoil} recoil damage from Steel Beam.")
    elif move_name == "Salt Cure":
        defender.othereffects.append("Salt Cure")

    #caps boosts
    attacker.atkboost = min(6, max(-6, attacker.atkboost))
    attacker.defboost = min(6, max(-6, attacker.defboost))
    attacker.spdefboost = min(6, max(-6, attacker.spdefboost))
    attacker.spaboost = min(6, max(-6, attacker.spaboost))
    attacker.spdboost = min(6, max(-6, attacker.spdboost))

def statusTable(move, attacker, defender,printmessages=True):
    #table to deal with effects of status moves
    if move.pp<=0:
        return
    
    if move.name == "Swords Dance":
        attacker.atkboost += 2

        if printmessages:
            print(f"{attacker.name}'s Attack rose sharply!")

    elif move.name == "Calm Mind":  
        attacker.spaboost += 1
        attacker.spdefboost += 1

        if printmessages:
            print(f"{attacker.name}'s Special Attack and Special Defense rose!")

    elif move.name == "Nasty Plot":
        attacker.spaboost += 2

        if printmessages:
            print(f"{attacker.name}'s Special Attack rose sharply!")

    elif move.name == "Moonlight" or move.name=="Recover":
        attacker.hp = min(attacker.maxhp,int(0.5 * attacker.maxhp))

        if printmessages:
            print(f"{attacker.name} healed to {attacker.hp} HP using {move.name}.")
    elif move.name == "Iron Defense":
        attacker.defboost += 2

        if printmessages:
            print(f"{attacker.name}'s Defense rose sharply!")

    elif move.name == "Will-O-Wisp" and defender.status is None and defender.type1!="Fire" and (defender.type2!="Fire" if defender.type2 else True):
        defender.status = "Burn"

        if printmessages:
            print(f"{defender.name} was burned!")

    elif move.name == "Thunder Wave" and defender.status is None and defender.type1 not in ["Electric", "Ground"] and (defender.type2 not in ["Electric", "Ground"] if defender.type2 else True):
        defender.status = "Paralyze"

        if printmessages:  
            print(f"{defender.name} was paralyzed!")

    elif move.name == "Curse" and attacker.type1=="Ghost":
        defender.othereffects.append("Curse")
        attacker.hp = min(0,attacker.hp-int(0.5 * attacker.maxhp))

        if printmessages:
            print(f"{attacker.name} cut down its own HP to place a curse on {defender.name}!")

    elif move.name == "Curse":
        attacker.atkboost += 1
        attacker.defboost += 1
        attacker.spdboost -= 1

        if printmessages:
            print(f"{attacker.name}'s Attack and Defense rose, but Speed fell!")

    elif move.name == "Dragon Dance":
        attacker.atkboost += 1
        attacker.spdboost += 1

        if printmessages:
            print(f"{attacker.name}'s Attack and Speed rose!")
            
    elif move.name == "Roost":
        attacker.hp = min(attacker.maxhp,int(0.5 * attacker.maxhp))

        if printmessages:
            print(f"{attacker.name} healed to {attacker.hp} HP using Roost.")

    elif move.name == "Bulk Up":
        attacker.atkboost += 1
        attacker.defboost += 1

        if printmessages:
            print(f"{attacker.name}'s Attack and Defense rose!")

    elif move.name == "Quiver Dance":
        attacker.spaboost += 1
        attacker.spdefboost += 1
        attacker.spdboost += 1

        if printmessages:
            print(f"{attacker.name}'s Special Attack, Special Defense, and Speed rose!")

    elif move.name == "Leech Seed" and "Leech Seed" not in defender.othereffects and defender.type1!="Grass" and (defender.type2!="Grass" if defender.type2 else True):
        defender.othereffects.append("Leech Seed")

        if printmessages:
            print(f"{defender.name} was seeded with Leech Seed!")
    
    #caps boosts
    attacker.atkboost = min(6, max(-6, attacker.atkboost))
    attacker.defboost = min(6, max(-6, attacker.defboost))
    attacker.spdefboost = min(6, max(-6, attacker.spdefboost))
    attacker.spaboost = min(6, max(-6, attacker.spaboost))
    attacker.spdboost = min(6, max(-6, attacker.spdboost))

def calculateDamage(attacker, move, defender,reducePP=True):
    #type chart
    typechart = {
        "Fire": {"Fire": 0.5, "Grass": 2.0, "Water": 0.5, "Ice": 2.0, "Bug": 2.0, "Steel": 2.0, "Rock": 0.5, "Dragon": 0.5},
        "Water": {"Water": 0.5, "Fire": 2.0, "Grass": 0.5, "Ground": 2.0, "Rock": 2.0, "Dragon": 0.5},
        "Grass": {"Grass": 0.5, "Water": 2.0, "Fire": 0.5, "Poison": 0.5, "Ground": 2.0, "Rock": 2.0, "Bug": 0.5, "Dragon": 0.5, "Flying": 0.5, "Steel": 0.5},
        "Electric": {"Water": 2.0, "Grass": 0.5, "Electric": 0.5,"Flying": 2.0, "Ground": 0.0, "Dragon": 0.5},
        "Ice": {"Fire": 0.5,"Grass": 2.0, "Water": 0.5, "Ice": 0.5, "Flying": 2.0, "Ground": 2.0, "Dragon": 2.0, "Steel": 0.5},
        "Fighting": {"Normal": 2.0, "Ice": 2.0, "Rock": 2.0, "Dark": 2.0, "Steel": 2.0, "Poison": 0.5, "Psychic": 0.5, "Flying": 0.5, "Bug": 0.5, "Fairy": 0.5},
        "Poison": {"Grass": 2.0, "Fairy": 2.0, "Steel": 0.0, "Poison": 0.5, "Ground": 0.5, "Rock": 0.5, "Ghost": 0.5},
        "Ground": {"Fire": 2.0, "Electric": 2.0, "Grass": 0.5, "Bug": 0.5, "Rock": 2.0, "Flying": 0.0, "Steel": 2.0},
        "Flying": {"Grass": 2.0, "Fighting": 2.0, "Bug": 2.0, "Electric": 0.5, "Rock": 0.5, "Steel": 0.5},
        "Psychic": {"Fighting": 2.0, "Poison": 2.0, "Psychic": 0.5, "Dark": 0.0, "Steel": 0.5},
        "Bug": {"Grass": 2.0, "Psychic": 2.0, "Dark": 2.0, "Fire": 0.5, "Fighting": 0.5, "Poison": 0.5, "Flying": 0.5, "Ghost": 0.5, "Fairy": 0.5, "Steel": 0.5},
        "Rock": {"Fire": 2.0, "Ice": 2.0, "Flying": 2.0, "Bug": 2.0, "Fighting": 0.5, "Ground": 0.5, "Steel": 0.5},
        "Ghost": {"Psychic": 2.0, "Ghost": 2.0, "Dark": 0.5, "Normal": 0.0},
        "Dragon": {"Dragon": 2.0, "Fairy": 0.0, "Steel": 0.5},
        "Dark": {"Psychic": 2.0, "Ghost": 2.0, "Fighting": 0.5, "Dark": 0.5, "Fairy": 0.5},
        "Fairy": {"Fighting": 2.0, "Dragon": 2.0, "Dark": 2.0, "Fire": 0.5, "Poison": 0.5, "Steel": 0.5},
        "Steel": {"Fairy": 2.0, "Ice": 2.0, "Rock": 2.0, "Fire": 0.5, "Water": 0.5, "Electric": 0.5, "Steel": 0.5},
        "Normal": {"Rock": 0.5, "Steel": 0.5, "Ghost": 0.0},
        }
    
    #changes water to be weak to ice if move is freeze-dry
    if move.name=="Freeze-Dry":
        typechart["Ice"]["Water"]=2.0

    #sets attack and defense stats based on move category
    if move.category == "Physical":
        #makes body press use def stat
        if move.name=="Body Press":
            attack_stat = attacker.defense
            AttackBoost = attacker.defboost
        else:
            attack_stat = attacker.attack
            AttackBoost = attacker.atkboost

        defense_stat = defender.defense
        DefenseBoost = defender.defboost

    elif move.category == "Special":
        attack_stat = attacker.spattack
        defense_stat = defender.spdefense
        AttackBoost = attacker.spaboost
        DefenseBoost = defender.spdefboost

    else:
        return 0
    #applies attack and def boosts using formula
    if DefenseBoost > 0:
        DefenseBoost = (2 + DefenseBoost) / 2
    elif DefenseBoost < 0:
        DefenseBoost =  2 / (2 - DefenseBoost)
    else:
        DefenseBoost = 1

    if AttackBoost > 0:
        AttackBoost =  (2+AttackBoost)/2
    elif AttackBoost < 0:
        AttackBoost = 2/(2-AttackBoost)
    else:
        AttackBoost = 1

    #applies burn debuff
    if attacker.status=="Burn" and move.category=="Physical":
        attack_stat*=0.5

    #applies status not moving chance
    if attacker.status=="Paralyze":
        parachance=0.75
    else:
        parachance=1.0

    sleepchance=1.0
    if attacker.status=="Sleep" and move.name not in ["Sleep Talk", "Snore", "Rest"]:
        sleepchance=0.0
        if attacker.statuscounter>=1:
            sleepchance=1/(4-attacker.statuscounter)
        if sleepchance>1.0:
            sleepchance=1.0

    freezechance=1.0
    if attacker.status=="Freeze" and (move.type!="Fire"or move.name not in ["Scald", "Matcha Gotcha", "Scorching Sands"]):
        freezechance=0.2

    #calculates base damage using damage formula
    base_damage = ((((((2 * 100 / 5 + 2) * move.power * ((attack_stat*AttackBoost) / (defense_stat*DefenseBoost))) / 50) + 2)*move.accuracy/100))*parachance*sleepchance*freezechance
    
    #adds stab multiplier
    STABMultiplier = 1.0
    if attacker.type1 == move.type or attacker.type2 == move.type:
        STABMultiplier *= 1.5 # STAB
    
    #adds type effectiveness
    type_multiplier = 1.0
    if move.type in typechart:
        type_multiplier*=typechart[move.type].get(defender.type1,1.0)

        if defender.type2:
            type_multiplier*=typechart[move.type].get(defender.type2,1.0)

    #reduces pp if the flag is enabled
    if reducePP:
        if move.pp <= 0:
            return 0
        move.pp -= 1

    #accounts for type and stab and returns truncated damage
    total_damage = base_damage * STABMultiplier * type_multiplier
    return int(total_damage)

#function to calculate turn outcome
def turnDamage(player,opponent,planned_move):

    #if action chosen is switch passes to switch turn function
    if isinstance(planned_move, tuple) and planned_move[0] == "switch":
        return switchTurn(player, opponent, planned_move[1])
    
    #Asks what move the opponent ended up using 
    used_move_name, newmove=getOpponentMove(opponent)

    #if opponent switched pass that function
    if used_move_name=="switch":
        oppSwitch()
        #sets opponent to active pokemon on opponents team
        opponent=opponent_team.active()

        #player gets free hit
        player.doDamage(opponent,planned_move)

        #does after turn effects
        if player.hp>0:
            afterturneffects(player,opponent)
        if opponent.hp>0:
            afterturneffects(opponent,player)

        #asks to recalc
        return True
    
    #gets move based on opponent input
    used_move = next((move for move in opponent.moves if move.name == used_move_name), None)

    #checks for priority, making user with higher priority go first
    if planned_move.priority>used_move.priority:
        playerfirst=True
    elif used_move.priority>planned_move.priority:
        playerfirst=False
    else:
        #if equal priority calcs speed and makes player go first if faster
        player_speed, opponent_speed = getSpeed(player, opponent)
        playerfirst=opponent_speed<player_speed

    #if the player is faster
    if playerfirst:
        #player attacks first
        player.doDamage(opponent,planned_move)

        #checks if opponent is alive and lets them attack
        if opponent.hp>0:
            oppAttack(opponent,player,used_move)

    else:
        #opponent attacks first
        oppAttack(opponent,player,used_move)

        #player attacks if alive
        if player.hp>0:
            player.doDamage(opponent,planned_move)

    #applies after turn effects if alive
    if player.hp>0:
        afterturneffects(player,opponent)
    else:
        return True
    if opponent.hp>0:
        afterturneffects(opponent,player)
    else:
        return True

    #checks if new move was discovered if so recalcs
    if newmove:
        return True
    return False

def switchTurn(player,opponent,switcher):
    #prints switching message
    print(f"{player.name} switched out into {switcher.name}")

    #switches player into switcher
    player=switcher
    player_team.switch(player_team.pokemon.index(switcher))

    #gets opponents attacks
    used_move_name, newmove=getOpponentMove(opponent)

    #if opponent switches switches them then applies after turn effects recalcs
    if used_move_name=="switch":
            oppSwitch()
            opponent=opponent_team.active()

            if player.hp>0:
                afterturneffects(player,opponent)
            if opponent.hp>0:
                afterturneffects(opponent,player)
            return True
    
    #checks move opponent uses and lets opponent attack
    used_move = next((move for move in opponent.moves if move.name == used_move_name), None)

    oppAttack(opponent,player,used_move)

    if player.hp>0:
        afterturneffects(player,opponent)
    if opponent.hp>0:
        afterturneffects(opponent,player)
    return newmove

def oppSwitch():
    #asks which pokemon opponent switched in
    switchpkmn=input("Which pokemon was switched in? ")

    #adds new pokemon to opponent team if not present taking user input for every parameter
    if switchpkmn not in [pkmn.name for pkmn in opponent_team.pokemon] and len(opponent_team.pokemon)<6:
        newpkmnhp=int(input("What is the pokemon's hp? "))
        newpkmnatk=int(input("What is the pokemon's attack? "))
        newpkmnspa=newpkmnhp=int(input("What is the pokemon's special attack? "))
        newpkmndef=int(input("What is the pokemon's defense? "))
        newpkmnspdef=int(input("What is the pokemon's special defense? "))
        newpkmnspd=int(input("What is the pokemon's speed? "))
        newpkmntype1=input("What is the pokemon's 1st type? ")
        newpkmntype2=input("What is the pokemon's 2nd type? (leave empty if NA)")
        if newpkmntype2=="":
            newpkmntype2=None

        opponent_team.pokemon.append(Pokemon(name=switchpkmn, hp=newpkmnhp, attack=newpkmnatk, defense=newpkmndef, spattack=newpkmnspa,spdefense=newpkmnspdef,maxspeed=newpkmnspd,type1=newpkmntype1,type2=newpkmntype2))
    
    #switches in inputted pokemon
    for pkmn in opponent_team.pokemon:
        if pkmn.name==switchpkmn and pkmn.hp>0:
            opponent_team.switch(opponent_team.pokemon.index(pkmn))
            break

def oppAttack(opponent,player,used_move):
        if used_move:
            #calculates amount of damage opponent did
            damage = calculateDamage(opponent, used_move, player)

            #uses status table if status move
            if used_move.category=="Status":
                statusTable(used_move,opponent,player)

            #subtracts damage from players hp
            player.hp = max(0, player.hp - damage)

            #returns appropriate message
            if player.hp==0:
                print(f"{opponent.name} used {used_move.name}, {player.name} fainted!")
            else:
                print(f"{opponent.name} used {used_move.name} and dealt {damage} damage. {player.name} has {player.hp} HP left.")

            #calcs secondary effects
            secondaryEffectTable(used_move.name,damage,opponent,player)
            if player.hp==0:
                return True
            return False

def moveEval(player_team, opponent, lookahead=3,switchEval=False):
    #starts best sequence val at -inf
    max_value = -float('inf')

    #list of best sequence of moves
    best_sequence = []

    #creates action list (all possible moves and switches for active pokemon), stores move object and switch's index on team
    if switchEval==False:
        allActions=[("move",m) for m in player_team.active().moves if m.pp>0]+[("switch",s) for s in player_team.validswitches()]
    else:
        allActions=[("move",m) for m in player_team.active().moves if m.pp>0]
    #loops through every possible action
    for action_type,action_obj in allActions:
        #copies player team and opponent
        player_copy = copy.deepcopy(player_team)
        opponent_copy = copy.deepcopy(opponent)

        #sets current eval val to 0
        total_value=0
        damage=0
        prevhp=player_copy.active().hp
        if action_type=="move":
            #copies move used to avoid affecting actual turn
            move=action_obj
            move_copy = next(m for m in player_copy.active().moves if m.name == move.name)
            move_copy.pp -= 1

            #predicts opponents highest damaging move
            opp_move_name, opp_damage = player_copy.active().takeDamage(opponent_copy, reducePP=False)
            opponent_move = next((m for m in opponent_copy.moves if m.name == opp_move_name), None)

            #checks if predicted move has higher priority, if so affects turn order
            opponent_priority = opponent_move.priority if opponent_move else 0
            if move.priority > opponent_priority:
                first = True
            elif opponent_priority > move.priority:
                first = False
            else:
                player_speed, opponent_speed = getSpeed(player_copy.active(), opponent_copy)
                first = player_speed > opponent_speed

            #checks if going first
            if first:
                #calcs damage done by move increasing score by the perent dealt, and subtracting that amount from opp
                if move.category == "Status":
                    statusTable(move, player_copy.active(), opponent_copy, printmessages=False)
                    damage = calculateDamage(player_copy.active(), move, opponent_copy, reducePP=False)
                else:
                    damage = calculateDamage(player_copy.active(), move, opponent_copy, reducePP=False)
                    damage = min(damage, opponent_copy.hp)
                    opponent_copy.hp -= damage
                    total_value += damage/opponent_copy.maxhp

                #applies secondary effects
                secondaryEffectTable(move.name, damage, player_copy.active(), opponent_copy, printmessages=False)
                
                #if opponent survives lets them attack
                if opponent_copy.hp > 0:
                    player_copy.active().hp = max(0, player_copy.active().hp - opp_damage)

                    if player_copy.active().hp == 0:
                        total_value -= 1 + (prevhp / player_copy.active().maxhp) * 999 #penalty if dead

                else:
                    total_value += 9999 #reward for killing opp

            else:
                player_copy.active().hp = max(0, player_copy.active().hp - opp_damage) #takes damage from opp
                if player_copy.active().hp == 0: #penalizes if dead
                    total_value -= 1 + (prevhp / player_copy.active().maxhp) * 999
                else:     
                    #deals damage
                    if move.category == "Status":
                        statusTable(move, player_copy.active(), opponent_copy, printmessages=False)
                        damage = calculateDamage(player_copy.active(), move, opponent_copy, reducePP=False)
                    else:
                        damage = calculateDamage(player_copy.active(), move, opponent_copy, reducePP=False)
                        #increases score by % of hp dealt
                        damage = min(damage, opponent_copy.hp)
                        opponent_copy.hp -= damage
                        
                    #rewards if ko on opp
                    if opponent_copy.hp == 0:
                        total_value += 9999
                    
                    secondaryEffectTable(move.name, damage, player_copy.active(), opponent_copy, printmessages=False) #calcs secondary effect
        elif action_type=="switch":
            #switches player out
            player_copy.switch(action_obj)
            
            #gives opponent free attack
            opp_move_name, opp_damage = player_copy.active().takeDamage(opponent_copy, reducePP=False)
            player_copy.active().hp = max(0, player_copy.active().hp - opp_damage)
            
            if player_copy.active().hp == 0:
                total_value -= 1 + (prevhp / player_copy.active().maxhp) * 999 #penalty if user faints 
        
        #applies afterturn effects
        if player_copy.active().hp>0:
            afterturneffects(player_copy.active(),opponent_copy,printmessages=False)
        if opponent_copy.hp>0:
            afterturneffects(opponent_copy,player_copy.active(), printmessages=False)
        
        #updates total value
        total_value += damage/opponent_copy.maxhp
        total_value -= opp_damage/player_copy.active().maxhp

        #if still looking ahead recurses, reducing lookahead by 1
        if lookahead > 1 and opponent_copy.hp > 0 and player_copy.active().hp > 0:
            next_value, next_sequence = moveEval(player_copy, opponent_copy, lookahead=lookahead - 1)

            #adds output from lowest val to total
            total_value += next_value
            #adds move to front of sequence
            move_sequence = [(action_type, action_obj)] + next_sequence
        else:
            #otherwise sets move sequence end to the last object
            move_sequence = [(action_type,action_obj)]

        #if the current val is > than the max sets it to the max
        if total_value > max_value:
            best_sequence = move_sequence
            max_value = total_value

    #returns the max val and best sequence
    return max_value, best_sequence

def loadMove(move_name):
    #makes move object from info in json file, else returns error
    move_info = moves_data.get(move_name)

    if move_info:
        return Move(
            name=move_name,
            power=move_info['power'],
            accuracy=move_info['accuracy'],
            move_type=move_info['type'],
            category=move_info['category'],
            pp=move_info['pp'],
            priority=move_info.get('priority', 0)
        )
    else:
        raise ValueError(f"Move '{move_name}' not found in moves data.")

def getOpponentMove(opponent):
    #asks if opponent switched if so returns switch
    switch=input("Did the opponent switch? (Y/N)")

    if switch=="Y":
        return "switch",True
    
    #Asks for opponent's move adds move if not present
    chosenmove=input("What move did the opponent use? ")
    newmove=False

    if chosenmove not in [move.name for move in opponent.moves]:
        opponent.moves.append(loadMove(chosenmove))
        newmove=True

    #returns chosen move and if a new move is revealed
    return chosenmove,newmove

def afterturneffects(pokemon1,pokemon2,printmessages=True):
    #applies status damage/sleep curing
    if pokemon1.status=="Burn":
        burndamage=int(0.0625*pokemon1.maxhp)
        pokemon1.hp=max(0,pokemon1.hp-burndamage)

        if printmessages:
            print(f"{pokemon1.name} is hurt by its burn and loses {burndamage} HP! It now has {pokemon1.hp} HP.")

    elif pokemon1.status=="Poison":
        poisondamage=int(0.0625*pokemon1.maxhp)
        pokemon1.hp=max(0,pokemon1.hp-poisondamage)

        if printmessages:
            print(f"{pokemon1.name} is hurt by poison and loses {poisondamage} HP! It now has {pokemon1.hp} HP.")

    elif pokemon1.status=="Badly Poisoned":
        #makes toxic damage increase with each turn
        pokemon1.statuscounter+=1

        if pokemon1.statuscounter>15:
            pokemon1.statuscounter=15
        toxdamage=int(pokemon1.statuscounter/16*pokemon1.maxhp)
        pokemon1.hp=max(0,pokemon1.hp-toxdamage)

        if printmessages:
            print(f"{pokemon1.name} is hurt by toxic and loses {toxdamage} HP! It now has {pokemon1.hp} HP.")

    elif pokemon1.status=="Sleep":
        pokemon1.statuscounter+=1

    #if there are other effects applies them
    if pokemon1.othereffects != []:
        for effect in pokemon1.othereffects:
            if effect=="Leech Seed":
                leechdamage=int(0.0625*pokemon1.maxhp)
                pokemon1.hp=max(0,pokemon1.hp-leechdamage)
                pokemon2.hp=min(pokemon2.maxhp,pokemon2.hp+leechdamage)

                if printmessages:
                    print(f"{pokemon1.name} is hurt by Leech Seed and loses {leechdamage} HP! It now has {pokemon1.hp} HP. {pokemon2.name} heals {leechdamage} HP and now has {pokemon2.hp} HP.")

            if effect=="Salt Cure":
                if pokemon1.type1 in ["Water","Steel"] or (pokemon1.type2 and pokemon1.type2 in ["Water","Steel"]):
                    saltdamage=int(0.25*pokemon1.maxhp)
                else:
                    saltdamage=int(0.125*pokemon1.maxhp)

                pokemon1.hp=max(0,pokemon1.hp-saltdamage)

                if printmessages:
                    print(f"{pokemon1.name} is hurt by Salt Cure and loses {saltdamage} HP! It now has {pokemon1.hp} HP.")

            if effect=="Curse":
                cursedamage=int(0.25*pokemon1.maxhp)
                pokemon1.hp=max(0,pokemon1.hp-cursedamage)

                if printmessages:
                    print(f"{pokemon1.name} is hurt by Curse and loses {cursedamage} HP! It now has {pokemon1.hp} HP.")

    #prints if pokemon dies
    if pokemon1.hp==0:

        if printmessages:
            print(f"{pokemon1.name} fainted due to after-turn effects!")
        #TODO implement fainting switch
        return True

def getSpeed(player, opponent):
    playerparamult=1.0
    opponentparamult=1.0

    #halves speed if para
    if player.status=="Paralyze":
        playerparamult=0.5
    if opponent.status=="Paralyze":
        opponentparamult=0.5

    #calcs speed accounting for boosts
    player_speed = player.maxspeed * ((2 + player.spdboost) / 2 if player.spdboost > 0 else 2 / (2 - player.spdboost) if player.spdboost < 0 else 1) * playerparamult
    opponent_speed = opponent.maxspeed * ((2 + opponent.spdboost) / 2 if opponent.spdboost > 0 else 2 / (2 - opponent.spdboost) if opponent.spdboost < 0 else 1) * opponentparamult
    
    #returns speeds
    return player_speed, opponent_speed

def predictSwitch(player_team):
    #declares max score and best switch
    max_score=-float('inf')
    best_switch=-1
    #stimulates every switch with 1 turn ahead
    for i in player_team.validswitches():
        player_copy=copy.deepcopy(player_team)
        player_copy.switch(i)
        score=moveEval(player_copy,opponent_team.active(),lookahead=1,switchEval=True)[0]
        if score>max_score:
            max_score=score
            best_switch=i
    #switches in best pokemon
    if best_switch>-1:
        player_team.switch(best_switch)
        print(player_team.active().name+" was switched in")
    else:
        print("Opponent wins")

#creates player and opponent teams
#TODO implement with frontend
player_team =Team([
    Pokemon(
        name="Dragonite",
        hp=386, maxspeed=259, attack=328, spattack=236, defense=226, spdefense=236,
        moves=[
        loadMove("Dragon Dance"),loadMove("Extreme Speed"),loadMove("Ice Punch"),loadMove("Roost")], 
        type1="Dragon", type2="Flying"),
    Pokemon(
        name="Metagross",
        hp=364, maxspeed=176,attack=405,defense=296,spattack=203,spdefense=217,
        moves=[loadMove("Psychic Fangs"),loadMove("Bullet Punch"),loadMove("Iron Head"),loadMove("Earthquake")],
        type1="Steel",type2="Psychic")])

opponent_team = Team([
    Pokemon(
        name="Togekiss",
        hp=350, maxspeed=260, attack=182, spattack=200, defense=200, spdefense=250,
        type1="Fairy", type2="Flying",
        moves=[loadMove("Air Slash")]),
    Pokemon(
        name="Great Tusk",
        hp=371,attack=361,defense=298,spattack=127,spdefense=143,maxspeed=300,
        type1="Ground",type2="Fighting"
)])

#asks for number of lookahead turns
lookaheadturns=int(input("Enter number of lookahead turns (suggested 2-4): "))

# Plan the next turns before starting
max_value, move_plan = moveEval(player_team, opponent_team.active(), lookahead=lookaheadturns)
print(f"Initial plan: {[("switch",player_team.pokemon[m[1]].name)if m[0]=="switch" else m[1].name for m in move_plan]} (Score: {max_value})")

#keeps track of plan len to know if recalc is needed
turn_index = 0

#loops until either player dies TODO make it continue until team dies
while player_team.alivePokemon() > 0 and opponent_team.alivePokemon() > 0:
    # replan if we've exhausted the current move plan
    if turn_index >= len(move_plan):
        max_value, move_plan = moveEval(player_team, opponent_team.active(), lookahead=lookaheadturns)
        print(f"\nReplanning... new sequence: {[("switch",player_team.pokemon[m[1]].name)if m[0]=="switch" else m[1].name for m in move_plan]} (Score: {max_value})")
        turn_index = 0

    #checks if switching or using a move passes appropriate args into turn damage
    planned_action = move_plan[turn_index]
    if planned_action[0]=="switch":
        switch_target = player_team.pokemon[planned_action[1]]
        recalc=turnDamage(player_team.active(), opponent_team.active(), ("switch", switch_target))
    else:
        planned_move = planned_action[1]
        recalc = turnDamage(player_team.active(), opponent_team.active(), planned_move)
    if opponent_team.active().hp==0:
        oppSwitch()
        recalc=True
    if player_team.active().hp==0:
        predictSwitch(player_team)
        recalc=True
    #if recalc is returned recalcs
    if recalc and player_team.active().hp>0 and opponent_team.active().hp>0:
        max_value, move_plan = moveEval(player_team, opponent_team.active(), lookahead=lookaheadturns)
        print(f"\nReplanning... new sequence: {[("switch",player_team.pokemon[m[1]].name)if m[0]=="switch" else m[1].name for m in move_plan]} (Score: {max_value})")
        turn_index = -1

    turn_index += 1
