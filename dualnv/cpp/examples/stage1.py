"""
[s1] stage 1 full life model
@author: infinity, cz <chuwen@shanshu.ai>

s1 solves a pattern-generation problem

a pattern is a series pi_t that depicts the actions along timeline.
"""
from multiprocessing import Pool
from typing import *

from .policy import *
from ..util import *

logger.setLevel(logging.DEBUG)


class TailCounter(object):
    def __init__(self):
        self.num = 0

    def apply(self, llp_keys, mod_keys, c_rate, t_rate, ct_array,
              fixed_kwargs, slot):
        self.llp_keys = llp_keys
        self.mod_keys = mod_keys
        self.c_rate = c_rate
        self.t_rate = t_rate
        self.ct_array = ct_array
        self.fixed_kwargs = fixed_kwargs
        self.slot = slot


# constants

# all in weeks
DEFAULT_TC = TailCounter()
DEFAULT_TAT = 12
DEFAULT_SCALE = 40
DEFAULT_SLOT = 4
DEFAULT_NUM_PATTERNS = 3
DEFALUT_MINIMUM_UPTIME = 12
#
DEFAULT_MAXIMUM_CYC = 40000
DEFAULT_LB = 2000
DEFAULT_REWARD = 5e5

# alias
s_to_e = serialize_states_to_engine
e_to_s = serialize_engine_to_states
# alias
tc = DEFAULT_TC


class TailProblem(object):
    def __init__(self,
                 overall: np.ndarray,
                 llp: np.ndarray,
                 mod: np.ndarray,
                 tat: int,
                 n: int,
                 reward=DEFAULT_REWARD):
        self.overall = overall
        self.llp = llp
        self.mod = mod
        self.remaining_tat = np.int(tat)
        self.n = n
        self.idx = tc.num
        self.hash = self.__calhash__()
        self.str = self.__calstr__()
        self.engine: Optional[Engine] = None
        self.reward = reward
        # increment default counter
        tc.num += 1

    def __copy__(self):
        return copy.deepcopy(self)

    # def __hash__(self):
    #     return self.hash

    def __calhash__(self):
        _arr = np.hstack(([self.n], self.overall, self.llp, self.mod))
        _key = tuple(np.minimum(i, DEFAULT_MAXIMUM_CYC).astype(int) for i in _arr)
        return _key

    def __calstr__(self):
        return f"Tail: {self.hash}"

    def __repr__(self):
        return self.str

    def __str__(self):
        return self.str

    def dp_name(self):
        """
        The id used in the DP algorithm
        Returns:
        """
        return self.idx, self.n

    @classmethod
    def from_engine(cls, engine: Engine, tat, n, reward=DEFAULT_REWARD):
        (tso, cso), llp, mod = e_to_s(engine, **tc.fixed_kwargs)
        cl = cls(np.array([tso, cso]), llp, mod, tat, n, reward)
        cl.add_engine(engine)
        return cl

    def add_engine(self, engine: Engine):
        self.engine = engine

    def _apply_wait(self):
        """
        NOT USED
        Returns:
        """
        _llp = self.llp
        _mod = self.mod
        _overall = self.overall
        _new_engine = s_to_e(*_overall, _llp, _mod, self.engine, **tc.fixed_kwargs)
        return _overall, _llp, _mod, _new_engine

    def _apply_work(self):
        _llp = self.llp - tc.c_rate
        _mod = self.mod - tc.c_rate
        _overall = self.overall - tc.ct_array
        _new_engine = s_to_e(*_overall, _llp, _mod, self.engine, **tc.fixed_kwargs)
        return _overall, _llp, _mod, _new_engine

    def _apply_policy(self, action: Policy):
        _new_engine = self.engine.get_after_fix_engine(action)
        _overall, _llp, _mod = e_to_s(_new_engine, **tc.fixed_kwargs)
        return _overall, _llp, _mod, _new_engine

    def apply(self, action: Union[None, int, Policy] = None):
        """
        Apply action and return result target period, lifespan, engine
        An action is, either a Policy or Int (0, 1)
            1: Working
            0: i.e., going though a Policy
            Policy: start maintenance right now
        Args:
            action (Union[Policy, int]): [description]
        Returns:

        """
        if action is None:
            return 1, (self.overall, self.llp, self.mod, self.engine)
        if action == 1:
            # goes to next stage
            return np.ceil(DEFALUT_MINIMUM_UPTIME / tc.slot).astype(np.int16), self._apply_work()
        elif isinstance(action, Policy):
            # goes to next stage
            return 1, self._apply_policy(action)
        raise ValueError(f"Action self.action must be of Union[Policy, int], "
                         f"\n {type(action)} found")

    def evaluate(self, action: Union[None, int, Policy] = None):
        # EVALUATE current problem with self.action
        if action == 1:
            # goes to next stage
            return self.reward
        elif isinstance(action, Policy):
            # goes to next stage
            return - action.price
        elif action is None:
            return 0
        raise ValueError(f"Action self.action must be of Union[Policy, int], "
                         f"\n {type(action)} found")


tfe = TailProblem.from_engine


class TailQueue(object):
    def __init__(self):
        self.queue = []
        self.keys = set()
        self.f_out = open("/tmp/debug", 'w')

    def get_last(self):
        return self.queue[-1]

    def pop(self):
        k, v = self.queue.pop(-1)
        return k, v

    def add(self, k, v):
        if k in self.keys:
            # already in queue
            # self.f_out.write(f"@already defined!{k}\n")
            return 0
        self.keys.add(k)
        self.queue.append((k, v))
        # self.f_out.write(f"defined!{k}\n")
        return 1

    def empty(self):
        return self.queue.__len__() == 0


def estimate_tat(policy: Policy):
    # todo: change to use an estimator
    return np.ceil(DEFAULT_TAT / tc.slot).astype(np.int16)


def validate(delta_n, _overall, _llp, _mod, _new_engine, lb=DEFAULT_LB):
    if any(_overall < lb):
        return False
    if any(_llp < lb):
        return False
    if any(_mod < lb):
        return False
    return True


def single_dp(engine: Engine, scale=DEFAULT_SCALE, slot=DEFAULT_SLOT, top_n=DEFAULT_NUM_PATTERNS, fleet_type=None,
              module_type_dict=None):
    logger.info(f"Run DP for engine@{engine.engine_id} with N:={scale} slot:={slot}")
    # ===============
    #  INITIALIZATION
    # ===============
    llp_keys = [k for k, v in engine.parts.items() if v.is_llp]
    mod_keys = [k for k in engine.modules]
    c_rate = engine.period_cycle_average * slot
    t_rate = engine.period_hour_average * slot
    ct_array = np.array([t_rate, c_rate])
    fixed_kwargs = dict(llp_keys=llp_keys, mod_keys=mod_keys)
    # apply to tc: TailCounter
    tc.apply(llp_keys, mod_keys, c_rate, t_rate, ct_array, fixed_kwargs, slot=slot)
    # total number of stages
    N = scale // slot

    tails_queue = TailQueue()

    vals = dict()
    tails = dict()
    actions = dict()

    # to initialize
    _init = tfe(engine, tat=0, n=0)
    tails_queue.add(_init.hash, _init)

    while not tails_queue.empty():
        # start search
        k, pr = tails_queue.get_last()

        # logger.debug(pr)

        # this is the final
        if pr.n >= N:
            vals[k] = pr.evaluate()
            actions[k] = []
            tails_queue.pop()
            continue

        _tails = tails.get(pr.hash, -1)

        if _tails != -1:
            # tail problems known
            # already generated
            pass
        else:
            _tails = []
            # ============================
            # UNKNOWN TAILS
            #   generate all tail problems
            # ============================
            #
            # problem: without policy (on-wing)
            delta_n, (_overall, _llp, _mod, _new_engine) = pr.apply(action=1)
            tail_stage = pr.n + delta_n
            # validate
            bool_valid = validate(delta_n, _overall, _llp, _mod, _new_engine)
            if bool_valid:
                _tail_using_problem = tfe(_new_engine, tat=0, n=tail_stage)
                # not solved
                if _tail_using_problem.hash not in vals:
                    _tails.append((_tail_using_problem, 1))
                    tails_queue.add(_tail_using_problem.hash, _tail_using_problem)

            #
            # problem: with policy
            policies = get_current_policy(
                engine=engine,
                fleet_type=fleet_type,
                module_type_dict=module_type_dict
            )

            for k, policy in policies.items():
                _tat = estimate_tat(policy)
                delta_n, (_overall, _llp, _mod, _new_engine) = pr.apply(action=policy)
                tail_stage = pr.n + _tat
                # validate
                bool_valid = validate(delta_n, _overall, _llp, _mod, _new_engine)
                if bool_valid:
                    _tail_maintain_problem = tfe(_new_engine, tat=0, n=tail_stage)
                    # not solved
                    if _tail_maintain_problem.hash not in vals:
                        _tails.append((_tail_maintain_problem, policy))
                        tails_queue.add(_tail_maintain_problem.hash, _tail_maintain_problem)

            # record parent and its children
            tails[pr.hash] = _tails
            continue

        # all tail problems has been solved
        #  do value eval
        try:
            _vals = ((_tail_ac, _tail_pr, pr.evaluate(action=_tail_ac) + vals[_tail_pr.hash])
                     for _tail_pr, _tail_ac in _tails)
            # maximization
            _sorted_vals = sorted(_vals, key=lambda x: x[-1], reverse=True)

            if pr.n != 0:
                _best_ac, _best_tail, _best_val = _sorted_vals[0]

                vals[pr.hash] = _best_val
                actions[pr.hash] = [_best_ac] + actions[_best_tail.hash]
            else:
                # for the first problem
                # = save top-n solutions
                ac = {}
                va = {}
                for idx, (_best_ac, _best_tail, _best_val) in enumerate(_sorted_vals[:top_n]):
                    va[idx] = _best_val
                    ac[idx] = [_best_ac] + actions[_best_tail.hash]
                vals[pr.hash] = va
                actions[pr.hash] = ac
        except Exception as e:
            logger.debug(f"invalid {pr}")
            raise e

        tails_queue.pop()

    # summarize
    top_n_sol = actions[_init.hash]
    top_n_val = vals[_init.hash]
    logger.info(f"finished after #{tails_queue.keys.__len__()} subproblems solved")
    return top_n_val, top_n_sol, vals, actions


def stage1_model(off_engine_dict, scale=DEFAULT_SCALE, slot=DEFAULT_SLOT,
                 mp=True, top_n=DEFAULT_NUM_PATTERNS, fleet_type=None, module_type_dict=None, **kwargs):
    values = {}
    patterns = {}

    if mp:
        pool = Pool()
        results = (
            (engine_key, pool.apply_async(single_dp, (engine, scale, slot, top_n, fleet_type, module_type_dict)))
            for engine_key, engine in off_engine_dict.items()
        )
        for engine_key, r in results:
            val, sol, vals, actions, *_ = r.get()
            values[engine_key] = val
            patterns[engine_key] = sol

    else:
        for engine_key, engine in off_engine_dict.items():
            val, sol, vals, actions, *_ = single_dp(engine, scale, slot, top_n, fleet_type, module_type_dict)
            values[engine_key] = val
            patterns[engine_key] = sol

    return values, patterns


