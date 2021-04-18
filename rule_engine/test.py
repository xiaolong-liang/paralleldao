from durable.lang import *

with ruleset('test'):
    @when_all(m.subject == 'World')
    def say_hello(c):
        print("Hello {0}".format(c.m.subject))
        pass

post('test', {'subject': 'World'})


def callback(c):
    print('risk7 fraud detected')
    c.s['result'] = "hello world"
    # c.m.s = 'hellow world'
    # return "hhhh"


def stop(c):
    c.delete_state()
    pass


rule_dict = {'risk7': {
    'suspect': {
        # 'run': callback,
        'all': [
            {'first': {'t': 'purchase'}},
            {'second': {'$neq': {'location': {'first': 'location'}}}}
        ],
    },
    'rul_1': {
        'run': stop,
        'all': [
            {
                'm': {
                    's': 1
                }
            }
        ]
    }
}}

rule_dict['risk7']['suspect']['run'] = callback

get_host().set_rulesets(
    rule_dict
)

result = post('risk7', [{'t': 'purchase', 'location': 'US', 's': 0}, {'t': 'purchase', 'location': 'CA', 's': 0}])
print(result)
# post('risk7', {'t': 'purchase', 'location': 'CA', 's': 0})
# post('risk7', {'t': 'purchase', 'location': 'US', 's': 0})
# post('risk7', {'s': 1})
# post('risk7', {'t': 'purchase', 'location': 'CA', 's': 0})
