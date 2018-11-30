import unittest
from Shazling import *
from rlbot.agents.base_agent import BaseAgent, SimpleControllerState

if __name__ == '__main__':
    unittest.main()

class TestShazling(unittest.TestCase):

    def test_agent_has_a_me(self):
        agent = Shazling('name', 0, 0)
        agent.initialize_agent()
        self.assertTrue(agent.me is not None)

    # https://docs.python.org/3/library/unittest.html
