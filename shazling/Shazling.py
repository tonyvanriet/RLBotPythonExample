import math
import time
from Util import *
from States import *

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

'''
Gosling by ddthj
Episode 5 Code

*now with comments!*
'''


class Shazling(BaseAgent):

    def initialize_agent(self):
        self.me = obj()
        self.ball = obj()
        self.players = [] #holds other players in match
        self.start = time.time()

        self.state = calcShot()
        self.controller = calcController

    def checkState(self):
        if self.state.expired:
            if self.team == 0:
                self.findStateForBlue()
            else:
                self.findStateForOrange()

    def findStateForBlue(self):
        if calcShot().available(self):
            self.state = calcShot()
        # elif quickShot().available(self):
        #     self.state = quickShot()
        elif getBoost().available(self):
            self.state = getBoost()
        elif rotateBack().available(self):
            self.state = rotateBack()
        elif wait().available(self):
            self.state = wait()
        else:
            self.state = quickShot()

    def findStateForOrange(self):
        if calcShot().available(self):
            self.state = calcShot()
        elif quickShot().available(self):
            self.state = quickShot()
        elif getBoost().available(self):
            self.state = getBoost()
        # elif rotateBack().available(self):
        #     self.state = rotateBack()
        elif wait().available(self):
            self.state = wait()
        else:
            self.state = quickShot()

    def get_output(self, game: GameTickPacket) -> SimpleControllerState:
        self.preprocess(game)
        self.checkState()

        self.renderer.begin_rendering()
        self.drawDebugInfo(game)

        controllerState = self.state.execute(self)

        self.renderer.end_rendering()

        return controllerState

    def drawDebugInfo(self, game):
        car_state_display = type(self.state).__name__
        car_ball_project_display = 'car->ball project: {0:4.0f}'.format(ballProject(self))
        car_to_ball = 'car->ball: {0:4.0f}'.format(distance2D(self.ball,self.me))

        car_display = '\n'.join([
            car_state_display,
            # car_ball_project_display,
            # car_to_ball
        ])
        self.renderer.draw_string_3d(self.me.location.data, 2, 2, car_display, self.renderer.white())

        ball_time_z_display = 'time z: {0:.2f}'.format(timeZ(self.ball))

        ball_display = '\n'.join([
            ball_time_z_display
        ])
        self.renderer.draw_string_3d(self.ball.location.data, 2, 2, ball_display, self.renderer.white())

        stationary_display = '\n'.join([
        ])
        stationary_display_x = 1000 * self.team
        self.renderer.draw_string_2d(stationary_display_x, 0, 2, 2, stationary_display, self.renderer.white())

    def preprocess(self,game):
        self.players = []
        car = game.game_cars[self.index]
        self.me.location.data = [car.physics.location.x, car.physics.location.y, car.physics.location.z]
        self.me.velocity.data = [car.physics.velocity.x, car.physics.velocity.y, car.physics.velocity.z]
        self.me.rotation.data = [car.physics.rotation.pitch, car.physics.rotation.yaw, car.physics.rotation.roll]
        self.me.rvelocity.data = [car.physics.angular_velocity.x, car.physics.angular_velocity.y, car.physics.angular_velocity.z]
        self.me.matrix = rotator_to_matrix(self.me)
        self.me.boost = car.boost

        ball = game.game_ball.physics
        self.ball.location.data = [ball.location.x, ball.location.y, ball.location.z]
        self.ball.velocity.data = [ball.velocity.x, ball.velocity.y, ball.velocity.z]
        self.ball.rotation.data = [ball.rotation.pitch, ball.rotation.yaw, ball.rotation.roll]
        self.ball.rvelocity.data = [ball.angular_velocity.x, ball.angular_velocity.y, ball.angular_velocity.z]

        self.ball.local_location = to_local(self.ball,self.me)

        #collects info for all other cars in match, updates objects in self.players accordingly
        for i in range(game.num_cars):
            if i != self.index:
                car = game.game_cars[i]
                temp = obj()
                temp.index = i
                temp.team = car.team
                temp.location.data = [car.physics.location.x, car.physics.location.y, car.physics.location.z]
                temp.velocity.data = [car.physics.velocity.x, car.physics.velocity.y, car.physics.velocity.z]
                temp.rotation.data = [car.physics.rotation.pitch, car.physics.rotation.yaw, car.physics.rotation.roll]
                temp.rvelocity.data = [car.physics.angular_velocity.x, car.physics.angular_velocity.y, car.physics.angular_velocity.z]
                self.me.boost = car.boost
                flag = False
                for item in self.players:
                    if item.index == i:
                        item = temp
                        flag = True
                        break
                if flag:
                    self.players.append(temp)
