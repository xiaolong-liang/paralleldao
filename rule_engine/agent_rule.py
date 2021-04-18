from durable.engine import MessageNotHandledException
from durable.lang import *
from enum import Enum


class Action(Enum):
    VoteYes = 'vote_yes'


def callback(c):
    print('risk7 fraud detected')


def clean(c):
    c.delete_state()


def action(_action):
    def vote_yes(c):
        print('vote yes')
        c.s['result'] = [{
            'name': 'vote',
            'args': {'amount': c.m['score']},
        }]
        pass

    switch = {
        Action.VoteYes: vote_yes
    }
    return switch[_action]


# the rule
rule_set = {
    'agent_vote': {
        'suspect': {
            'run': callback,
            'all': [
                {
                    'm': {
                        'action': 'none'
                    }
                }
            ]
        },
        'stop_rule': {
            'run': clean,
            'all': [
                {
                    'm': {
                        'action': 'clean'
                    }
                }
            ]
        },
        'vote_yes': {
            'run': action(Action.VoteYes),
            'all': [
                {
                    'm': {
                        'like': 'yes'
                    }
                }
            ]
        }
    }
}

get_host().set_rulesets(
    rule_set
)


def reason(facts):
    rule_set = 'agent_vote'
    post(rule_set, {'action': 'clean'})
    try:
        result = post(rule_set, facts)
        return result['result']
    except MessageNotHandledException as e:
        return {}


if __name__ == '__main__':
    print(reason([{
        'like': 'yes',
        'score': 11
    }]))
