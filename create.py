from easyAI import MCTS, MTDf, MTDstep, SSS, Negamax, DictTT, TT, HashTT
from mcts.mcts_pure import MCTSPlayer
import sys
import argparse

import sys
import argparse

def Human(*args, **kwargs):
    return 'Human'

players_dict = {
    'MTDf': MTDf,
    'MTDstep': MTDstep,
    'SSS': SSS,
    'Negamax': Negamax,
    'Human': Human,
    'MCTSPlayer': MCTSPlayer
}

def parse_args(parser, commands):
    # Divide argv by commands
    split_argv = [[]]

    size = int(sys.argv[2])
    sys.argv = sys.argv[2:]

    for c in sys.argv[1:]:
        if c in commands.choices:
            split_argv.append([c])
        else:
            split_argv[-1].append(c)
    # Initialize namespace
    args = argparse.Namespace()
    for c in commands.choices:
        setattr(args, c, None)
    # Parse each command
    parser.parse_args(split_argv[0], namespace=args)  # Without command
    for argv in split_argv[1:]:  # Commands
        n = argparse.Namespace()
        setattr(args, argv[0], n)
        parser.parse_args(argv, namespace=n)
    
    return size, args


def create_players(parser):
    commands = parser.add_subparsers(title='sub-commands')

    for i in range(2):
        sub_parser = commands.add_parser(f'player{i+1}')
        sub_parser.add_argument('--type')
        sub_parser.add_argument('--depth', type=int)
        sub_parser.add_argument('--iterations', type=int)
        sub_parser.add_argument('--time_limit', type=int)
        sub_parser.add_argument('--tt', type=bool)

    size, args = parse_args(parser, commands)
    players = [None] * 2
    args = vars(args)

    for i in range(2):
        args_player = args[f'player{i+1}']
        args_player = vars(args_player)
        player_type = args_player.pop("type")
        args_player = {k: v for k, v in args_player.items() if v is not None}
        if "tt" in args_player:
            args_player.pop("tt")
            player = players_dict[player_type](win_score=100, tt=TT(), **args_player)
        else:
            player = players_dict[player_type](win_score=100, **args_player)

        players[i] = player

    return size, players

def game():
    parser = argparse.ArgumentParser()
    size, players = create_players(parser)
    
    return size, players


