import math
import time
from rlbot.agents.base_agent import  SimpleControllerState
from Util import *


class calcShot:
    def __init__(self):
        self.expired = False

    def available(self,agent):
        ball_is_away_from_either_back_wall = abs(agent.ball.location.data[1]) < 5050
        car_is_far_enough_behind_ball = ballProject(agent) > (500 - (distance2D(agent.ball,agent.me)/2))

        return (
            ballReady(agent)
            and ball_is_away_from_either_back_wall
            and car_is_far_enough_behind_ball
        )

    def execute(self,agent):
        agent.controller = calcController

        #getting the coordinates of the goalposts
        leftPost = Vector3([-sign(agent.team)*700 , 5100*-sign(agent.team), 200])
        rightPost = Vector3([sign(agent.team)*700, 5100*-sign(agent.team), 200])
        center = Vector3([0, 5150*-sign(agent.team), 200])

        #time stuff that we don't worry about yet
        time_guess = 0
        bloc = future(agent.ball,time_guess)

        #vectors from the goalposts to the ball & to Gosling
        ball_left = angle2(bloc,leftPost)
        ball_right = angle2(bloc,rightPost)
        agent_left = angle2(agent.me,leftPost)
        agent_right = angle2(agent.me,rightPost)

        #determining if we are left/right/inside of cone
        if agent_left > ball_left and agent_right > ball_right:
            goal_target = rightPost
        elif agent_left > ball_left and agent_right < ball_right:
            goal_target = None
        elif agent_left < ball_left and agent_right < ball_right:
            goal_target = leftPost
        else:
            goal_target = None

        if goal_target != None:
            #if we are outside the cone, this is the same as Gosling's old code
            goal_to_ball = (agent.ball.location - goal_target).normalize()
            goal_to_agent = (agent.me.location - goal_target).normalize()
            difference = goal_to_ball - goal_to_agent
            error = cap(abs(difference.data[0])+ abs(difference.data[1]),1,10)
        else:
            #if we are inside the cone, our line to follow is a vector from the ball to us (although it's still named 'goal_to_ball')
            goal_to_ball = (agent.me.location - agent.ball.location).normalize()
            error = cap( distance2D(bloc,agent.me) /1000,0,1)

        #this is measuring how fast the ball is traveling away from us if we were stationary
        ball_dpp_skew = cap(abs(dpp(agent.ball.location, agent.ball.velocity, agent.me.location, [0,0,0]))/80, 1,1.5)

        #same as Gosling's old distance calculation, but now we consider dpp_skew which helps us handle when the ball is moving
        target_distance =cap( (40 + distance2D(agent.ball.location,agent.me)* (error**2))/1.8, 0,4000)
        target_location = agent.ball.location + Vector3([(goal_to_ball.data[0]*target_distance) * ball_dpp_skew, goal_to_ball.data[1]*target_distance,0])

       #this also adjusts the target location based on dpp
        ball_something = dpp(target_location,agent.ball.velocity, agent.me,[0,0,0])**2

        if ball_something > 100: #if we were stopped, and the ball is moving 100uu/s away from us
            ball_something = cap(ball_something,0,80)
            correction = agent.ball.velocity.normalize()
            correction = Vector3([correction.data[0]*ball_something,correction.data[1]*ball_something,correction.data[2]*ball_something])
            target_location += correction #we're adding some component of the ball's velocity to the target position so that we are able to hit a faster moving ball better
            #it's important that this only happens when the ball is moving away from us.


        #another target adjustment that applies if the ball is close to the wall
        extra = 4120 - abs(target_location.data[0])
        if extra < 0:
            # we prevent our target from going outside the wall, and extend it so that Gosling gets closer to the wall before taking a shot, makes things more reliable
            target_location.data[0] = cap(target_location.data[0],-4120,4120)
            target_location.data[1] = target_location.data[1] + (-sign(agent.team)*cap(extra,-500,500))

        #getting speed, this would be a good place to modify because it's not very good
        target_local = toLocal(agent.ball.location,agent.me)
        angle_to_target = cap(math.atan2(target_local.data[1], target_local.data[0]),-3,3)
        distance_to_target = distance2D(agent.me, target_location)
        speed=  2000 - (100*(1+angle_to_target)**2)

        #picking our rendered target color based on the speed we want to go
        colorRed = cap(int( (speed/2300) * 255),0,255)
        colorBlue =cap(255-colorRed,0,255)

        #see the rendering tutorial on github about this, just drawing lines from the posts to the ball and one from the ball to the target
        agent.renderer.draw_line_3d(bloc.data, leftPost.data, agent.renderer.create_color(255,255,0,0))
        agent.renderer.draw_line_3d(bloc.data, rightPost.data, agent.renderer.create_color(255,0,255,0))

        agent.renderer.draw_line_3d(agent.ball.location.data,target_location.data, agent.renderer.create_color(255,colorRed,0,colorBlue))
        agent.renderer.draw_rect_3d(target_location.data, 10,10, True, agent.renderer.create_color(255,colorRed,0,colorBlue))

        if  ballReady(agent) == False or abs(agent.ball.location.data[1]) > 5050:
            self.expired = True
        return agent.controller(agent,target_location,speed)


class quickShot:
    def __init__(self):
        self.expired = False

    def available(self,agent):
        if ballProject(agent) > -(distance2D(agent.ball,agent.me)/2):
            return True
        return False

    def execute(self,agent):
        agent.controller = shotController
        left_post = Vector3([sign(agent.team)*GOAL_WIDTH/2,-sign(agent.team)*FIELD_LENGTH/2,100])
        right_post = Vector3([-sign(agent.team)*GOAL_WIDTH/2,-sign(agent.team)*FIELD_LENGTH/2,100])

        ball_left = angle2(agent.ball.location,left_post)
        ball_right = angle2(agent.ball.location,right_post)

        our_left = angle2(agent.me.location,left_post)
        our_right = angle2( agent.me.location,right_post)

        offset = (agent.ball.location.data[0] / FIELD_WIDTH) * 3.14
        x = agent.ball.location.data[0] +90 * abs(math.cos(offset)) * sign(offset)
        y = agent.ball.location.data[1] + 90 * abs(math.sin(offset)) * sign(agent.team)
        target_location = toLocation([x,y,agent.ball.location.data[2]])

        location = toLocal(target_location,agent.me)
        angle_to_target = math.atan2(location.data[1],location.data[0])
        distance_to_target = distance2D(agent.me, target_location)

        speedCorrection =  ((2+ abs(angle_to_target)**2) * 350)
        speed = 2400 - speedCorrection

        if self.available(agent) == False:
            self.expired = True
        elif calcShot().available(agent) == True:
            self.expired = True

        return agent.controller(agent,target_location, speed)

class getBoost():
    def __init__(self):
        self.expired = False

    def available(self, agent):
        return timeZ(agent.ball) > 1.5 and agent.me.boost < 50

    def execute(self,agent):
        #taking a rough guess at where the ball will be in the future, based on how long it will take to hit the ground
        ball_future = future(agent.ball, timeZ(agent.ball))

        closest = 0
        closest_distance =  distance2D(boosts[0], ball_future)

        #going through every large pad to see which one is closest to our ball_future guesstimation
        for i in range(1,len(boosts)):
            if distance2D(boosts[i], ball_future) < closest_distance:
                closest = i
                closest_distance =  distance2D(boosts[i], ball_future)

        target = boosts[closest]
        speed = 2300

        if ballReady(agent) or agent.me.boost > 80:
            self.expired = True

        return frugalController(agent,target,speed)

class wait():
    def __init__(self):
        self.expired = False

    def available(self, agent):
        if timeZ(agent.ball) > 1.5:
            return True

    def execute(self,agent):
        #taking a rough guess at where the ball will be in the future, based on how long it will take to hit the ground
        ball_future = future(agent.ball, timeZ(agent.ball))

        #if we have boost, we just go towards the ball_future position, and slow down just like in exampleATBA as we get close
        target = ball_future
        current = velocity2D(agent.me)
        ratio = distance2D(agent.me,target)/(current + 0.01)

        speed = cap(600 * ratio,0,2300)

        if speed <= 100:
            speed = 0

        if ballReady(agent):
            self.expired = True

        return frugalController(agent,target,speed)

class rotateBack:
    def __init__(self):
        self.expired = False

    def available(self,agent):
        own_goal_location = Vector3([0, 5150*sign(agent.team), 0])
        return (abs(distance2D(agent.me.location.data, own_goal_location)) > 700)

    def execute(self,agent):
        agent.controller = frugalController
        own_goal_location = Vector3([0, 5150*sign(agent.team), 200])
        target_location = own_goal_location

        location = toLocal(target_location,agent.me)
        angle_to_target = math.atan2(location.data[1],location.data[0])
        distance_to_target = distance2D(agent.me, target_location)

        speedCorrection =  ((2+ abs(angle_to_target)**2) * 350)
        speed = 2400 - speedCorrection

        self.expired = True

        return agent.controller(agent, target_location, speed)

def frugalController(agent,target,speed):
    controller_state = SimpleControllerState()
    location = toLocal(target,agent.me)
    angle_to_target = math.atan2(location.data[1],location.data[0])

    controller_state.steer = steer(angle_to_target)

    current_speed = velocity2D(agent.me)
    if current_speed < speed:
        controller_state.throttle = 1.0
    elif current_speed - 50 > speed:
        controller_state.throttle = -1.0
    else:
        controller_state.throttle = 0

    time_difference = time.time() - agent.start
    if time_difference > 2.2 and distance2D(target,agent.me) > (velocity2D(agent.me)*2.3) and abs(angle_to_target) < 1 and current_speed < speed:
        agent.start = time.time()
    elif time_difference <= 0.1:
        controller_state.jump = True
        controller_state.pitch = -1
    elif time_difference >= 0.1 and time_difference <= 0.15:
        controller_state.jump = False
        controller_state.pitch = -1
    elif time_difference > 0.15 and time_difference < 1:
        controller_state.jump = True
        controller_state.yaw = controller_state.steer
        controller_state.pitch = -1

    return controller_state

def calcController(agent, target_object,target_speed):
    location = toLocal(target_object,agent.me)
    controller_state = SimpleControllerState()
    angle_to_ball = math.atan2(location.data[1],location.data[0])

    current_speed = velocity2D(agent.me)
    controller_state.steer = steer(angle_to_ball)

    #throttle
    if target_speed > current_speed:
        controller_state.throttle = 1.0
        if target_speed > 1400 and agent.start > 2.2 and current_speed < 2250:
            controller_state.boost = True
    elif target_speed < current_speed:
        controller_state.throttle = -1.0
    return controller_state

def shotController(agent, target_object,target_speed):
    goal_local = toLocal([0,-sign(agent.team)*FIELD_LENGTH/2,100],agent.me)
    goal_angle = math.atan2(goal_local.data[1],goal_local.data[0])

    location = toLocal(target_object,agent.me)
    controller_state = SimpleControllerState()
    angle_to_target = math.atan2(location.data[1],location.data[0])

    current_speed = velocity2D(agent.me)
    #steering
    controller_state.steer = steer(angle_to_target)

    #throttle
    if target_speed > 1400 and target_speed > current_speed and agent.start > 2.5 and current_speed < 2250:
        controller_state.boost = True
    if target_speed > current_speed:
        controller_state.throttle = 1.0
    elif target_speed < current_speed:
        controller_state.throttle = 0

    #dodging
    time_difference = time.time() - agent.start
    if ballReady(agent) and time_difference > 2.2 and distance2D(target_object,agent.me) <= 270:
        agent.start = time.time()
    elif time_difference <= 0.1:
        controller_state.jump = True
        controller_state.pitch = -1
    elif time_difference >= 0.1 and time_difference <= 0.15:
        controller_state.jump = False
        controller_state.pitch = -1
    elif time_difference > 0.15 and time_difference < 1:
        controller_state.jump = True
        controller_state.yaw = math.sin(goal_angle)
        controller_state.pitch = -abs(math.cos(goal_angle))

    return controller_state

class exampleATBA:
    def __init__(self):
        self.expired = False
    def execute(self, agent):
        target_location = agent.ball
        target_speed = velocity2D(agent.ball) + (distance2D(agent.ball,agent.me)/1.5)

        return agent.controller(agent, target_location, target_speed)

def exampleController(agent, target_object,target_speed):
    location = toLocal(target_object,agent.me)
    controller_state = SimpleControllerState()
    angle_to_ball = math.atan2(location.data[1],location.data[0])

    current_speed = velocity2D(agent.me)
    #steering
    controller_state.steer = steer(angle_to_ball)

    #throttle
    if target_speed > current_speed:
        controller_state.throttle = 1.0
        if target_speed > 1400 and agent.start > 2.2 and current_speed < 2250:
            controller_state.boost = True
    elif target_speed < current_speed:
        controller_state.throttle = 0

    #dodging
    time_difference = time.time() - agent.start
    if time_difference > 2.2 and distance2D(target_object,agent.me) > (velocity2D(agent.me)*2.5) and abs(angle_to_ball) < 1.3:
        agent.start = time.time()
    elif time_difference <= 0.1:
        controller_state.jump = True
        controller_state.pitch = -1
    elif time_difference >= 0.1 and time_difference <= 0.15:
        controller_state.jump = False
        controller_state.pitch = -1
    elif time_difference > 0.15 and time_difference < 1:
        controller_state.jump = True
        controller_state.yaw = controller_state.steer
        controller_state.pitch = -1

    return controller_state
