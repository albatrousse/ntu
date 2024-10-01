from game.players import BasePokerPlayer
import random

class MyPokerPlayer(BasePokerPlayer):
    def __init__(self):
        super().__init__()
        self.opponent_actions = []

    def declare_action(self, valid_actions, hole_card, round_state):
        hand_strength = self.evaluate_hand(hole_card, round_state)
        action, amount = self.decide_action(valid_actions, hand_strength, round_state)
        self.opponent_actions.append(round_state['action_histories'])
        return action, amount

    def evaluate_hand(self, hole_card, round_state):
        card_ranks = {
            '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
            '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14
        }
        rank1 = card_ranks[hole_card[0][1]]
        rank2 = card_ranks[hole_card[1][1]]
        strength = (rank1 + rank2) / 28.0

        if 'community_card' in round_state:
            community_cards = round_state['community_card']
            strength += self.evaluate_community_cards(hole_card, community_cards)
        
        if rank1 == rank2:
            strength += 0.2
        if hole_card[0][0] == hole_card[1][0]:
            strength += 0.1

        return min(1.0, strength)

    def evaluate_community_cards(self, hole_card, community_cards):
        strength = 0
        for card in community_cards:
            if card[1] in [hole_card[0][1], hole_card[1][1]]:
                strength += 0.1
        return strength

    def decide_action(self, valid_actions, hand_strength, round_state):
        current_street = round_state['street']
        pot_size = round_state['pot']['main']['amount']

        if current_street == 'preflop':
            if hand_strength > 0.8:
                return valid_actions[2]['action'], valid_actions[2]['amount']['max']
            elif hand_strength > 0.4:
                return valid_actions[1]['action'], valid_actions[1]['amount']
            else:
                return valid_actions[0]['action'], valid_actions[0]['amount']

        if current_street in ['flop', 'turn', 'river']:
            if hand_strength > 0.7:
                return valid_actions[2]['action'], valid_actions[2]['amount']['max']
            elif hand_strength > 0.4:
                if random.random() > 0.5:
                    return valid_actions[1]['action'], valid_actions[1]['amount']
                else:
                    return valid_actions[2]['action'], valid_actions[2]['amount']['min']
            else:
                if random.random() > 0.8:
                    return valid_actions[2]['action'], valid_actions[2]['amount']['min']
                else:
                    return valid_actions[0]['action'], valid_actions[0]['amount']
        
        return valid_actions[0]['action'], valid_actions[0]['amount']

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        self.opponent_actions.append(action)
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

    def _pick_unused_card(self, card_num, used_card):
        used = [self._card_str_to_id(card) for card in used_card]
        unused = [card_id for card_id in range(1, 53) if card_id not in used]
        choiced = random.sample(unused, card_num)
        return [self._card_id_to_str(card_id) for card_id in choiced]

    def _fill_community_card(self, base_cards, used_card):
        need_num = 5 - len(base_cards)
        return base_cards + self._pick_unused_card(need_num, used_card)

    def _card_str_to_id(self, card):
        rank_map = {'2': 0, '3': 1, '4': 2, '5': 3, '6': 4, '7': 5, '8': 6, '9': 7, 'T': 8, 'J': 9, 'Q': 10, 'K': 11, 'A': 12}
        suit_map = {'S': 0, 'H': 1, 'D': 2, 'C': 3}
        return suit_map[card[1]] * 13 + rank_map[card[0]] + 1

    def _card_id_to_str(self, card_id):
        rank_map = '23456789TJQKA'
        suit_map = 'SHDC'
        rank = rank_map[(card_id - 1) % 13]
        suit = suit_map[(card_id - 1) // 13]
        return rank + suit

def setup_ai():
    return MyPokerPlayer()
