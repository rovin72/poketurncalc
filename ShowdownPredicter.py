import copy
import json
with open('moves.json', 'r') as f:
    moves_data = json.load(f)
class Team:
    def __init__(self, pokemon):
        self.pokemon=pokemon
        self.activeIndex=0
        self.availablepokemon=len(pokemon)
    def active(self):
        return self.pokemon[self.activeIndex]
    def switch(self,switchIndex):
        self.active().atkboost=0
        self.active().spaboost=0
        self.active().spdefboost=0
        self.active().defboost=0
        self.active().spdboost=0
        self.activeIndex=switchIndex
    def validswitches(self):
        return [i for i,pkmn in enumerate(self.pokemon) if pkmn.hp>0 and pkmn!=self.active()]
class Move:
    def __init__(self, name, power, accuracy, move_type, category, pp, priority=0):
        self.name = name
        self.power = power
        self.accuracy = accuracy
        self.type = move_type
        self.category = category
        self.pp = pp
        self.priority = priority
class Opponent:
    def __init__(self,name,hp,maxspeed,attack,spattack,defense,spdefense,type1,type2=None,atkboost=0,spaboost=0,defboost=0,spdefboost=0,spdboost=0,knownmoves=[],status=None,maxhp=None,othereffects=[],fainted=False):
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
        self.atkboost=atkboost
        self.spaboost=spaboost
        self.defboost=defboost
        self.spdefboost=spdefboost
        self.spdboost=spdboost
        self.knownmoves=knownmoves
        self.status=status
        self.statuscounter=0
        self.othereffects=othereffects
        self.fainted=fainted
class Player:
    def __init__(self,name,hp,maxspeed,attack,spattack,defense,spdefense,moves,type1,type2=None,atkboost=0,spaboost=0,defboost=0,spdefboost=0,spdboost=0,status=None, maxhp=None,othereffects=[],fainted=False):
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
    def doDamage(self,opponent,move):
        if move.pp <= 0:
            print(f"{self.name} tried to use {move.name}, but it has no PP left!")
            return
        if move.category == "Status":
            statusTable(move, self, opponent)
            move.pp -= 1
        else:
            damage = calculateDamage(self, move, opponent, reducePP=True)
            opponent.hp = max(0, opponent.hp - damage)
            if opponent.hp == 0:
                print(f"{self.name} used {move.name}, {opponent.name} fainted!")
                return True
            else:
                print(f"{self.name} used {move.name} and dealt {damage} damage. {opponent.name} has {opponent.hp} HP left.")
            secondaryEffectTable(move.name, damage, self, opponent)
    def takeDamage(self,opponent,reducePP=True):
        valid_moves = [move for move in opponent.knownmoves if move.pp > 0]
        if reducePP:
            moves_damage=[calculateDamage(opponent,move,self) for move in valid_moves]
        else:
            moves_damage=[calculateDamage(opponent,move,self,reducePP=False) for move in valid_moves]
        if all(move.type!=opponent.type1 for move in valid_moves)  and len(valid_moves)<4:
            if opponent.attack>opponent.spattack:
                moves_damage.append(calculateDamage(opponent,Move("Generic Move 1", 90, 100, opponent.type1,"Physical",16),self))
            else:
                moves_damage.append(calculateDamage(opponent,Move("Generic Move 1", 90, 100, opponent.type1,"Special",16),self))
        if opponent.type2:
            if all(move.type!=opponent.type2 for move in opponent.knownmoves) and len(opponent.knownmoves)<4:
                if opponent.attack>opponent.spattack:
                    moves_damage.append(calculateDamage(opponent,Move("Generic Move 2", 90, 100, opponent.type2,"Physical",16),self))
                else:
                    moves_damage.append(calculateDamage(opponent,Move("Generic Move 2", 90, 100, opponent.type2,"Special",16),self))
        used_move=opponent.knownmoves[moves_damage.index(max(moves_damage))] if moves_damage.index(max(moves_damage))<len(opponent.knownmoves) else "Generic Move"
        if self.hp<=max(moves_damage):
            return [used_move,self.hp]
        return [used_move,max(moves_damage)]
def secondaryEffectTable(move_name,move_damage, attacker, defender):
    if move_name == "Drain Punch" or move_name == "Giga Drain" or move_name == "Leech Life" or move_name == "Horn Leech":
        attacker.hp += int(0.5 * move_damage)
        if attacker.hp > attacker.maxhp:
            attacker.hp = attacker.maxhp
        print(f"{attacker.name} healed to {attacker.hp} HP using {move_name}.")
    if move_name == "Draco Meteor" or move_name == "Overheat":
        attacker.spaboost -= 2
    if move_name == "Brave Bird" or move_name == "Wood Hammer":
        recoil = int(0.33 * move_damage)
        attacker.hp -= recoil
        print(f"{attacker.name} took {recoil} recoil damage from {move_name}.")
    if move_name == "Superpower":
        attacker.atkboost -= 1
        attacker.defboost -= 1
    if move_name == "Close Combat":
        attacker.defboost -= 1
        attacker.spdefboost -= 1
    if move_name == "Steel Beam":
        recoil = int(0.5 * attacker.maxhp)
        attacker.hp -= recoil
        print(f"{attacker.name} took {recoil} recoil damage from Steel Beam.")
    if move_name == "Salt Cure":
        defender.othereffects.append("Salt Cure")
    attacker.atkboost = min(6, max(-6, attacker.atkboost))
    attacker.defboost = min(6, max(-6, attacker.defboost))
    attacker.spdefboost = min(6, max(-6, attacker.spdefboost))
    attacker.spaboost = min(6, max(-6, attacker.spaboost))
    attacker.spdboost = min(6, max(-6, attacker.spdboost))
def statusTable(move, attacker, defender,printmessages=True):
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
        heal_amount = int(0.5 * attacker.maxhp)
        attacker.hp += heal_amount
        if attacker.hp > attacker.maxhp:
            attacker.hp = attacker.maxhp
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
        defender.status = " "
        if printmessages:  
            print(f"{defender.name} was paralyzed!")
    elif move.name == "Curse" and attacker.type1=="Ghost":
        defender.othereffects.append("Curse")
        attacker.hp -= int(0.5 * attacker.maxhp)
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
        heal_amount = int(0.5 * attacker.maxhp)
        attacker.hp += heal_amount
        if attacker.hp > attacker.maxhp:
            attacker.hp = attacker.maxhp
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
    attacker.atkboost = min(6, max(-6, attacker.atkboost))
    attacker.defboost = min(6, max(-6, attacker.defboost))
    attacker.spdefboost = min(6, max(-6, attacker.spdefboost))
    attacker.spaboost = min(6, max(-6, attacker.spaboost))
    attacker.spdboost = min(6, max(-6, attacker.spdboost))
def calculateDamage(attacker, move, defender,reducePP=True):
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
    if move.name=="Freeze-Dry":
        typechart["Ice"]["Water"]=2.0
    if move.category == "Physical":
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
    if attacker.status=="Burn" and move.category=="Physical":
        attack_stat*=0.5
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
    base_damage = ((((((2 * 100 / 5 + 2) * move.power * ((attack_stat*AttackBoost) / (defense_stat*DefenseBoost))) / 50) + 2)*move.accuracy/100))*parachance*sleepchance*freezechance
    STABMultiplier = 1.0
    if attacker.type1 == move.type or attacker.type2 == move.type:
        STABMultiplier *= 1.5 # STAB
    type_multiplier = 1.0
    if move.type in typechart:
        type_multiplier*=typechart[move.type].get(defender.type1,1.0)
        if defender.type2:
            type_multiplier*=typechart[move.type].get(defender.type2,1.0)
    if reducePP:
        if move.pp <= 0:
            return 0
        move.pp -= 1
    total_damage = base_damage * STABMultiplier * type_multiplier
    return int(total_damage)
def turnDamage(player,opponent,planned_move):
    if isinstance(planned_move, tuple) and planned_move[0] == "switch":
        return switchTurn(player, opponent, planned_move[1])
    recalc=False
    used_move_name, newmove=getOpponentMove(opponent)
    if used_move_name=="switch":
        oppSwitch()
        opponent=opponent_team.active()
        player.doDamage(opponent,planned_move)
        if player.hp>0:
            afterturneffects(player,opponent)
        if opponent.hp>0:
            afterturneffects(opponent,player)
        return True
    used_move = next((move for move in opponent.knownmoves if move.name == used_move_name), None)
    if planned_move.priority>used_move.priority:
        playerfirst=True
    elif used_move.priority>planned_move.priority:
        playerfirst=False
    else:
        player_speed, opponent_speed = getSpeed(player, opponent)
        playerfirst=opponent_speed<player_speed
    if playerfirst:
        player.doDamage(opponent,planned_move)
        if opponent.hp>0:
            if used_move:
                damage = calculateDamage(opponent, used_move, player)
                if used_move.category=="Status":
                    statusTable(used_move,opponent,player)
                player.hp = max(0, player.hp - damage)
                if player.hp==0:
                    print(f"{opponent.name} used {used_move_name}, {player.name} fainted!")
                    return True
                else:
                    print(f"{opponent.name} used {used_move_name} and dealt {damage} damage. {player.name} has {player.hp} HP left.")
                secondaryEffectTable(used_move_name,damage,opponent,player)
    else:
        if used_move:
            damage = calculateDamage(opponent, used_move, player)
            if used_move.category=="Status":
                statusTable(used_move,opponent,player)
            player.hp = max(0, player.hp - damage)
            if player.hp==0:
                print(f"{opponent.name} used {used_move_name}, {player.name} fainted!")
                return False
            else:
                print(f"{opponent.name} used {used_move_name} and dealt {damage} damage. {player.name} has {player.hp} HP left.")
            secondaryEffectTable(used_move_name,damage,opponent,player)
        if player.hp>0:
            player.doDamage(opponent,planned_move)
    if player.hp>0:
        afterturneffects(player,opponent)
    if opponent.hp>0:
        afterturneffects(opponent,player)
    else:return True
    if newmove:
        recalc=True
    return recalc
def switchTurn(player,opponent,switcher):
    print(f"{player.name} switched out into {switcher.name}")
    player=switcher
    player_team.switch(player_team.pokemon.index(switcher))
    used_move_name, newmove=getOpponentMove(opponent)
    if used_move_name=="switch":
            oppSwitch()
            opponent=opponent_team.active()
            if player.hp>0:
                afterturneffects(player,opponent)
            if opponent.hp>0:
                afterturneffects(opponent,player)
            return True
    used_move = next((move for move in opponent.knownmoves if move.name == used_move_name), None)
    if used_move:
            damage = calculateDamage(opponent, used_move, player)
            if used_move.category=="Status":
                statusTable(used_move,opponent,player)
            player.hp = max(0, player.hp - damage)
            if player.hp==0:
                print(f"{opponent.name} used {used_move_name}, {player.name} fainted!")
                return False
            else:
                print(f"{opponent.name} used {used_move_name} and dealt {damage} damage. {player.name} has {player.hp} HP left.")
            secondaryEffectTable(used_move_name,damage,opponent,player)
    if player.hp>0:
        afterturneffects(player,opponent)
    if opponent.hp>0:
        afterturneffects(opponent,player)
    return newmove
def oppSwitch():
    switchpkmn=input("Which pokemon would you like to switch in? ")
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
        opponent_team.pokemon.append(Opponent(name=switchpkmn, hp=newpkmnhp, attack=newpkmnatk, defense=newpkmndef, spattack=newpkmnspa,spdefense=newpkmnspdef,maxspeed=newpkmnspd,type1=newpkmntype1,type2=newpkmntype2))
    for pkmn in opponent_team.pokemon:
        if pkmn.name==switchpkmn:
            opponent_team.switch(opponent_team.pokemon.index(pkmn))
def moveEval(player_team, opponent, lookahead=3):
    max_value = -float('inf')
    best_sequence = []
    allActions=[("move",m) for m in player_team.active().moves if m.pp>0]+[("switch",s) for s in player_team.validswitches()]
    for action_type,action_obj in allActions:
        player_copy = copy.deepcopy(player_team)
        opponent_copy = copy.deepcopy(opponent)
        total_value=0
        if action_type=="move":
            move=action_obj
            move_copy = next(m for m in player_copy.active().moves if m.name == move.name)
            move_copy.pp -= 1
            opp_move_name, opp_damage = player_copy.active().takeDamage(opponent_copy, reducePP=False)
            opponent_move = next((m for m in opponent_copy.knownmoves if m.name == opp_move_name), None)
            opponent_priority = opponent_move.priority if opponent_move else 0
            if move.priority > opponent_priority:
                first = True
            elif opponent_priority > move.priority:
                first = False
            else:
                player_speed, opponent_speed = getSpeed(player_copy.active(), opponent_copy)
                first = player_speed > opponent_speed
            if first:
                if move.category == "Status":
                    statusTable(move, player_copy.active(), opponent_copy, printmessages=False)
                    damage = calculateDamage(player_copy.active(), move, opponent_copy, reducePP=False)
                else:
                    damage = calculateDamage(player_copy.active(), move, opponent_copy, reducePP=False)
                    damage = min(damage, opponent_copy.hp)
                    opponent_copy.hp -= damage
                    total_value += damage
                secondaryEffectTable(move.name, damage, player_copy.active(), opponent_copy)
                if opponent_copy.hp > 0:
                    player_copy.active().hp = max(0, player_copy.active().hp - opp_damage)
                    if player_copy.active().hp == 0:
                        total_value -= 1000
                    else:
                        total_value -= opp_damage
                else:
                    total_value += 9999
            else:
                player_copy.active().hp = max(0, player_copy.active().hp - opp_damage)
                if player_copy.active().hp == 0:
                    total_value -= 1000
                else:
                    total_value -= opp_damage
                if move.category == "Status":
                    statusTable(move, player_copy.active(), opponent_copy, printmessages=False)
                    damage = calculateDamage(player_copy.active(), move, opponent_copy, reducePP=False)
                else:
                    damage = calculateDamage(player_copy.active(), move, opponent_copy, reducePP=False)
                    damage = min(damage, opponent_copy.hp)
                    opponent_copy.hp -= damage
                    total_value += damage
                if opponent_copy.hp == 0:
                    total_value += 9999
                secondaryEffectTable(move.name, damage, player_copy.active(), opponent_copy)
        elif action_type=="switch":
            player_copy.switch(action_obj)
            opp_move_name, opp_damage = player_copy.active().takeDamage(opponent_copy, reducePP=False)
            player_copy.active().hp = max(0, player_copy.active().hp - opp_damage)
            if player_copy.active().hp == 0:
                    total_value -= 1000
        if player_copy.active().hp>0:
            afterturneffects(player_copy.active(),opponent_copy,printmessages=False)
        if opponent_copy.hp>0:
            afterturneffects(opponent_copy,player_copy.active(), printmessages=False)
        if lookahead > 1 and opponent_copy.hp > 0 and player_copy.active().hp > 0:
            next_value, next_sequence = moveEval(player_copy, opponent_copy, lookahead=lookahead - 1)
            total_value += next_value
            move_sequence = [(action_type, action_obj)] + next_sequence
        else:
            move_sequence = [(action_type,action_obj)]
        if total_value > max_value:
            best_sequence = move_sequence
            max_value = total_value
    return max_value, best_sequence
def loadMove(move_name):
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
    switch=input("Did the opponent switch? (Y/N)")
    if switch=="Y":
        return "switch",True
    chosenmove=input("What move did the opponent use? ")
    newmove=False
    if chosenmove not in [move.name for move in opponent.knownmoves]:
        opponent.knownmoves.append(loadMove(chosenmove))
        newmove=True
    return chosenmove,newmove
def afterturneffects(pokemon1,pokemon2,printmessages=True):
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
        pokemon1.statuscounter+=1
        if pokemon1.statuscounter>15:
            pokemon1.statuscounter=15
        toxdamage=int(pokemon1.statuscounter/16*pokemon1.maxhp)
        pokemon1.hp=max(0,pokemon1.hp-toxdamage)
        if printmessages:
            print(f"{pokemon1.name} is hurt by toxic and loses {toxdamage} HP! It now has {pokemon1.hp} HP.")
    elif pokemon1.status=="Sleep":
        pokemon1.statuscounter+=1
    if pokemon1.othereffects:
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
    if pokemon1.hp==0:
        if printmessages:
            print(f"{pokemon1.name} fainted due to after-turn effects!")
        return True
def getSpeed(player, opponent):
    playerparamult=1.0
    opponentparamult=1.0
    if player.status=="Paralyze":
        playerparamult=0.5
    if opponent.status=="Paralyze":
        opponentparamult=0.5
    player_speed = player.maxspeed * ((2 + player.spdboost) / 2 if player.spdboost > 0 else 2 / (2 - player.spdboost) if player.spdboost < 0 else 1) * playerparamult
    opponent_speed = opponent.maxspeed * ((2 + opponent.spdboost) / 2 if opponent.spdboost > 0 else 2 / (2 - opponent.spdboost) if opponent.spdboost < 0 else 1) * opponentparamult
    return player_speed, opponent_speed
playerpkm1_moves = [
    loadMove("Dragon Dance"),
    loadMove("Extreme Speed"),
    loadMove("Thunder Punch"),
    loadMove("Roost")
]
player_team =Team([Player(
    name="Dragonite",
    hp=386, maxspeed=259, attack=328, spattack=236, defense=226, spdefense=236,
    moves=playerpkm1_moves, type1="Dragon", type2="Flying"),
    Player(name="Metagross",
    hp=364, maxspeed=176,attack=405,defense=296,spattack=203,spdefense=217,
    moves=[loadMove("Psychic Fangs"),loadMove("Bullet Punch"),loadMove("Iron Head"),loadMove("Earthquake")],type1="Steel",type2="Psychic")])
opponent_team = Team([Opponent(
    name="Togekiss",
    hp=350, maxspeed=260, attack=182, spattack=200, defense=200, spdefense=250,
    type1="Fairy", type2="Flying",
    knownmoves=[
        loadMove("Air Slash")
    ]
),Opponent(
    name="Great Tusk",
    hp=371,attack=361,defense=298,spattack=127,spdefense=143,maxspeed=300,
    type1="Ground",type2="Fighting"
)])

lookaheadturns=int(input("Enter number of lookahead turns (suggested 2-4): "))
# Plan the next turns before starting
max_value, move_plan = moveEval(player_team, opponent_team.active(), lookahead=lookaheadturns)
print(f"Initial plan: {[("switch",player_team.pokemon[m[1]].name)if m[0]=="switch" else m[1].name for m in move_plan]} (Score: {max_value})")
turn_index = 0
while player_team.active().hp > 0 and opponent_team.active().hp > 0:
    # replan if we've exhausted the current move plan
    if turn_index >= len(move_plan):
        max_value, move_plan = moveEval(player_team, opponent_team.active(), lookahead=lookaheadturns)
        print(f"\nReplanning... new sequence: {[("switch",player_team.pokemon[m[1]].name)if m[0]=="switch" else m[1].name for m in move_plan]} (Score: {max_value})")
        turn_index = 0
    planned_action = move_plan[turn_index]
    if planned_action[0]=="switch":
        switch_target = player_team.pokemon[planned_action[1]]
        recalc=turnDamage(player_team.active(), opponent_team.active(), ("switch", switch_target))
    else:
        planned_move = planned_action[1]
        recalc = turnDamage(player_team.active(), opponent_team.active(), planned_move)
    if recalc:
        max_value, move_plan = moveEval(player_team, opponent_team.active(), lookahead=lookaheadturns)
        print(f"\nReplanning... new sequence: {[("switch",player_team.pokemon[m[1]].name)if m[0]=="switch" else m[1].name for m in move_plan]} (Score: {max_value})")
        turn_index = -1
    turn_index += 1
