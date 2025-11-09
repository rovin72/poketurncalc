import copy
class Move:
    def __init__(self, name, power, accuracy, move_type, category, pp):
        self.name = name
        self.power = power
        self.accuracy = accuracy
        self.type = move_type
        self.category = category
        self.pp = pp
class opponent:
    def __init__(self,name,hp,maxspeed,attack,spattack,defense,spdefense,atkboost,spaboost,defboost,spdefboost,spdboost,type1,type2=None,knownmoves=None,status=None):
        self.name=name
        self.hp=hp
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
        self.knownmoves=knownmoves or []
        self.status=status
        if self.status=="Burn":
            self.attack=int(self.attack*0.5)
        elif self.status=="Paralyze":
            self.maxspeed=int(self.maxspeed*0.5)
class player:
    def __init__(self,name,hp,maxspeed,attack,spattack,defense,spdefense,moves,atkboost,spaboost,defboost,spdefboost,spdboost,type1,type2=None,status=None):
        self.name=name
        self.hp=hp
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
        if self.status=="Burn":
            self.attack=int(self.attack*0.5)
        elif self.status=="Paralyze":
            self.maxspeed=int(self.maxspeed*0.5)
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
            else:
                print(f"{self.name} used {move.name} and dealt {damage} damage. {opponent.name} has {opponent.hp} HP left.")
            secondaryEffectTable(move.name, damage, self, opponent)
    def takeDamage(self,opponent,reducePP=True,simulate=False):
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
        used_move=opponent.knownmoves[moves_damage.index(max(moves_damage))].name if moves_damage.index(max(moves_damage))<len(opponent.knownmoves) else "Generic Move"
        if self.hp<=max(moves_damage):
            return [used_move,self.hp]
        if not simulate:
            print(f"{opponent.name} attacks {self.name} for {max(moves_damage)} damage.")
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
    elif move.name == "Will-O-Wisp":
        defender.status = "Burn"
        defender.attack = int(defender.attack * 0.5)
        if printmessages:
            print(f"{defender.name} was burned!")
    elif move.name == "Thunder Wave":
        defender.status = "Paralyze"
        defender.maxspeed = int(defender.maxspeed * 0.5)
        if printmessages:  
            print(f"{defender.name} was paralyzed!")
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
    base_damage = ((((((2 * 100 / 5 + 2) * move.power * ((attack_stat*AttackBoost) / (defense_stat*DefenseBoost))) / 50) + 2)*move.accuracy/100))
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
    player_speed = player.maxspeed * ((2 + player.spdboost) / 2 if player.spdboost > 0 else 2 / (2 - player.spdboost) if player.spdboost < 0 else 1)
    opponent_speed = opponent.maxspeed * ((2 + opponent.spdboost) / 2 if opponent.spdboost > 0 else 2 / (2 - opponent.spdboost) if opponent.spdboost < 0 else 1)
    if opponent_speed>=player_speed: 
        taken_damage=player.takeDamage(opponent,reducePP=True)
        player.hp = max(0, player.hp - taken_damage[1])
        if player.hp==0:
            print(f"{opponent.name} used {taken_damage[0]}, {player.name} fainted!")
            return
        else:
            print(f"{opponent.name} used {taken_damage[0]} and dealt {taken_damage[1]} damage. {player.name} has {player.hp} HP left.")
        secondaryEffectTable(taken_damage[0],taken_damage[1],opponent,player)
        if player.hp>0:
            player.doDamage(opponent,planned_move)
    else:
        player.doDamage(opponent,planned_move)
        if opponent.hp>0:
            taken_damage=player.takeDamage(opponent,reducePP=True)
            player.hp = max(0, player.hp - taken_damage[1])
            if player.hp==0:
                print(f"{opponent.name} used {taken_damage[0]}, {player.name} fainted!")
            else:
                print(f"{opponent.name} used {taken_damage[0]} and dealt {taken_damage[1]} damage. {player.name} has {player.hp} HP left.")
            secondaryEffectTable(taken_damage[0],taken_damage[1],opponent,player)
def moveEval(player,opponent,lookahead=3):
    max_value=-float('inf')
    best_sequence=[]
    for move in player.moves:
        if move.pp<=0:
            continue
        player_copy=copy.deepcopy(player)
        opponent_copy=copy.deepcopy(opponent)
        move_copy = next(m for m in player_copy.moves if m.name == move.name)
        move_copy.pp -= 1
        total_value=0
        player_speed = player_copy.maxspeed * ((2 + player_copy.spdboost) / 2 if player_copy.spdboost > 0 else 2 / (2 - player_copy.spdboost) if player_copy.spdboost < 0 else 1)
        opponent_speed = opponent_copy.maxspeed * ((2 + opponent_copy.spdboost) / 2 if opponent_copy.spdboost > 0 else 2 / (2 - opponent_copy.spdboost) if opponent_copy.spdboost < 0 else 1)
        if player_speed>opponent_speed:
            if move.category=="Status":
                statusTable(move,player_copy,opponent_copy,printmessages=False)
                damage = calculateDamage(player_copy, move, opponent_copy, reducePP=False)
            else:
                damage = calculateDamage(player_copy, move, opponent_copy, reducePP=False)
                damage = min(damage, opponent_copy.hp)
                opponent_copy.hp -= damage
                total_value+=damage
            secondaryEffectTable(move.name,damage,player_copy,opponent_copy)
            opp_move, opp_damage = player_copy.takeDamage(opponent_copy,reducePP=False,simulate=True)
            player_copy.hp = max(0, player_copy.hp - opp_damage)
            if 0 == player_copy.hp:
                total_value -= 1000 
            else:
                total_value -= opp_damage
        else:
            opp_move, opp_damage = player_copy.takeDamage(opponent_copy,reducePP=False,simulate=True)
            player_copy.hp = max(0, player_copy.hp - opp_damage)
            if 0 == player_copy.hp:
                total_value -= 1000 
            else:
                total_value -= opp_damage
            if move.category=="Status":
                statusTable(move,player_copy,opponent_copy,printmessages=False)
                damage = calculateDamage(player_copy, move, opponent_copy, reducePP=False)
            else:
                damage = calculateDamage(player_copy, move, opponent_copy, reducePP=False)
                damage = min(damage, opponent_copy.hp)
                opponent_copy.hp -= damage
                total_value+=damage
            secondaryEffectTable(move.name,damage,player_copy,opponent_copy)
        if lookahead>1 and opponent_copy.hp>0 and player_copy.hp>0:
           next_value, next_sequence = moveEval(player_copy, opponent_copy, lookahead=lookahead-1)
           total_value += next_value
           move_sequence = [move] + next_sequence
        else:
            move_sequence = [move]
        if total_value>max_value:
            best_sequence=move_sequence
            max_value=total_value
        best_sequence_names = [m.name if hasattr(m, "name") else m for m in best_sequence]
    return max_value, best_sequence_names
#player_moves = [Move("Freeze-Dry", 70, 100, "Ice", "Special", 16), Move("Ice Beam", 90, 100, "Ice", "Special", 16), Move("Draco Meteor", 130, 90, "Dragon", "Special", 8),Move("Earth Power", 90, 100, "Ground", "Special", 16)]
#player_pokemon = player(name="Kyurem",hp=391, maxspeed=318, attack=238, spattack=359, defense=216, spdefense=217, moves=player_moves, atkboost=0, spaboost=0, defboost=0, spdefboost=0, type1="Dragon", type2="Ice")
player_moves = [
    Move("Dragon Dance", 0, 100, "Dragon", "Status", 20),
    Move("Earthquake", 100, 100, "Ground", "Physical", 16),
    Move("Fire Punch", 75, 100, "Fire", "Physical", 24),
    Move("Roost", 0, 100, "Flying", "Status", 8)
]

player_pokemon = player(
    name="Dragonite",
    hp=386, maxspeed=259, attack=328, spattack=236, defense=226, spdefense=236,
    moves=player_moves, atkboost=0, spaboost=0, defboost=0, spdefboost=0, spdboost=0,
    type1="Dragon", type2="Flying"
)
#opponent_pokemon = opponent(name="Primarina",hp=321, maxspeed=200, attack=165, spattack=386, defense=184, spdefense=268, atkboost=0, spaboost=0, defboost=0, spdefboost=0, type1="Water", type2="Fairy", knownmoves=[Move("Moonblast", 95, 100, "Fairy", "Special", 16), Move("Surf", 90, 100, "Water", "Special", 16)])
#opponent_pokemon = opponent(name="Iron Hands",hp=449, maxspeed=100, attack=416, spattack=112, defense=252,spdefense=215, atkboost=0, spaboost=0, defboost=0, spdefboost=0, type1="Fighting", type2="Electric", knownmoves=[Move("Drain Punch", 75, 100, "Fighting", "Physical", 16), Move("Thunder Punch", 75, 100, "Electric", "Physical", 16)])
# opponent_pokemon = opponent(
#     name="Tinkaton",
#     hp=354, maxspeed=320, attack=200, spattack=172, defense=200, spdefense=295,
#     atkboost=0, spaboost=0, defboost=0, spdefboost=0, spdboost=0,
#     type1="Fairy", type2="Steel",
#     knownmoves=[
#         Move("Play Rough", 90, 90, "Fairy", "Physical", 16),
#         Move("Gigaton Hammer", 160, 100, "Steel", "Physical", 5)
#     ]
# )
opponent_pokemon = opponent(
    name="Togekiss",
    hp=350, maxspeed=240, attack=182, spattack=200, defense=200, spdefense=250,
    atkboost=0, spaboost=0, defboost=0, spdefboost=0, spdboost=0,
    type1="Fairy", type2="Flying",
    knownmoves=[
        Move("Dazzling Gleam", 80, 100, "Fairy", "Special", 16),
        Move("Air Slash", 75, 95, "Flying", "Special", 16)
    ]
)

max_value, move_plan = moveEval(player_pokemon, opponent_pokemon, lookahead=4)
print(f"Initial plan: {[m for m in move_plan]} (Score: {max_value})")

turn_index = 0

while player_pokemon.hp > 0 and opponent_pokemon.hp > 0:
    if turn_index >= len(move_plan):
        max_value, move_plan = moveEval(player_pokemon, opponent_pokemon, lookahead=4)
        print(f"\nReplanning... new sequence: {[m for m in move_plan]} (Score: {max_value})")
        turn_index = 0

    planned_move_name = move_plan[turn_index]
    planned_move = next(m for m in player_pokemon.moves if m.name == planned_move_name)
    turnDamage(player_pokemon, opponent_pokemon, planned_move)
    print(f"Turn {turn_index}: {player_pokemon.name} HP={player_pokemon.hp}, {opponent_pokemon.name} HP={opponent_pokemon.hp}")
    turn_index += 1
