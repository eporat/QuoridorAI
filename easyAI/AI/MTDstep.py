#contributed by mrfesol (Tomasz Wesolowski)

from easyAI.AI.MTdriver import mtd

class MTDstep:
    """
    This implements MTD-step algorithm. The following example shows
    how to setup the AI and play a Connect Four game:
    
        >>> from easyAI import Human_Player, AI_Player, MTDstep
        >>> AI = MTDstep(7)
        >>> game = ConnectFour([AI_Player(AI),Human_Player()])
        >>> game.play()
    
    Parameters
    -----------
    
    depth:
      How many moves in advance should the AI think ?
      (2 moves = 1 complete turn)
    
    scoring:
      A function f(game)-> score. If no scoring is provided
         and the game object has a ``scoring`` method it ill be used.
    
    win_score:
      Score LARGER than the largest score of game, but smaller than inf. 
      It's required to run algorithm.
        
    tt:
      A transposition table (a table storing game states and moves)
      scoring: can be none if the game that the AI will be given has a
      ``scoring`` method.
          
    step_size:
      Size of jump from one bound to next
      
    Notes
    -----
   
    The score of a given game is given by
    
    >>> scoring(current_game) - 0.01*sign*current_depth
    
    for instance if a lose is -100 points, then losing after 4 moves
    will score -99.96 points but losing after 8 moves will be -99.92
    points. Thus, the AI will chose the move that leads to defeat in
    8 turns, which makes it more difficult for the (human) opponent.
    This will not always work if a ``win_score`` argument is provided.
    
    """
    
    def __init__(self, depth, scoring=None, win_score=10000, tt=None, step_size = 100):
        self.scoring = scoring        
        self.depth = depth
        self.tt = tt
        self.win_score = win_score
        self.step_size = step_size
    
    def __call__(self,game):
        """
        Returns the AI's best move given the current state of the game.
        """
        
        scoring = self.scoring if self.scoring else (
                       lambda g: g.scoring() ) # horrible hack
        
        
        first = (lambda game, tt: self.win_score)
        next = (lambda lowerbound, upperbound, bestValue, bound: max(lowerbound + 1, bestValue - self.step_size)) 
        
        self.alpha = mtd(game, 
                         first, next,
                         self.depth, 
                         scoring,
                         self.tt)
        
        return game.ai_move
