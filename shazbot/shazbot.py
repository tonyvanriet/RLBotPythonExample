import math

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket


class Shazbot(BaseAgent):

    def initialize_agent(self):
        self.controller_state = SimpleControllerState()

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        action_display = 'just go'
        draw_debug(self.renderer, packet.game_cars[self.index], packet.game_ball, action_display)

        self.controller_state.throttle = 1.0
        self.controller_state.steer = 0

        return self.controller_state

def draw_debug(renderer, car, ball, action_display):
    renderer.begin_rendering()

    car_rotation = car.physics.rotation
    car_rotation_display = 'p:{0:.2f} y:{1:.2f} r:{2:.2f}'.format(car_rotation.pitch, car_rotation.yaw, car_rotation.roll)
    renderer.draw_string_2d(0, 0, 2, 2, car_rotation_display, renderer.white())

    # draw a line from the car to the ball
    renderer.draw_line_3d(car.physics.location, ball.physics.location, renderer.white())
    # print the action that the bot is taking
    renderer.draw_string_3d(car.physics.location, 2, 2, action_display, renderer.white())

    renderer.end_rendering()
